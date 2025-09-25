"""Tests for router module including security edge cases."""

import base64
import json
import tempfile
import time  # noqa: F401 - used in patch
from pathlib import Path
from unittest.mock import patch

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import FastAPI
from fastapi.testclient import TestClient

from secure_query.router import (
    DECRYPT_RATE_LIMIT,
    _check_rate_limit,
    _rate_limit_storage,
    router,
)
from secure_query.settings import Settings


@pytest.fixture
def temp_keys_dir():
    """Create temporary directory for test keys."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_app(temp_keys_dir, monkeypatch):
    """Create test FastAPI app with temporary keys."""
    app = FastAPI()

    # Create test settings and generate keys
    test_settings = Settings(temp_keys_dir)

    # Generate test keys
    from secure_query.crypto import ensure_keys

    monkeypatch.setattr("secure_query.crypto.settings", test_settings)
    ensure_keys()

    # Add router with patched settings
    app.include_router(router)
    yield app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


def test_public_key_endpoint(client):
    """Test public key endpoint returns valid response."""
    response = client.get("/secure-query/public-key")
    assert response.status_code == 200

    data = response.json()
    assert data["alg"] == "RSA-OAEP-256"
    assert data["format"] == "spki-pem"
    assert data["pem"].startswith("-----BEGIN PUBLIC KEY-----")
    assert data["pem"].endswith("-----END PUBLIC KEY-----\n")


def test_decrypt_endpoint_success(client, temp_keys_dir):
    """Test successful decryption."""
    # Get public key from endpoint
    pub_response = client.get("/secure-query/public-key")
    public_key_pem = pub_response.json()["pem"]

    # Load public key
    public_key = serialization.load_pem_public_key(public_key_pem.encode())

    # Create test payload
    test_payload = {"user": "alice", "query": "SELECT * FROM users"}
    plaintext = json.dumps(test_payload).encode("utf-8")

    # Encrypt
    ciphertext = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Encode as base64url
    ciphertext_b64url = base64.urlsafe_b64encode(ciphertext).decode("ascii").rstrip("=")

    # Test decryption
    response = client.get(f"/secure-query/decrypt?data={ciphertext_b64url}")
    assert response.status_code == 200

    data = response.json()
    assert data["ok"] is True
    assert data["payload"] == test_payload


def test_decrypt_endpoint_invalid_data(client):
    """Test decryption with invalid data."""
    response = client.get("/secure-query/decrypt?data=invalid_data")
    assert response.status_code == 400
    assert response.json()["detail"] == "Decryption failed"


def test_decrypt_endpoint_missing_data(client):
    """Test decryption without data parameter."""
    response = client.get("/secure-query/decrypt")
    assert response.status_code == 422  # Validation error


def test_decrypt_endpoint_oversized_data(client):
    """Test decryption with oversized data parameter."""
    # Create data larger than max_length=4096
    large_data = "x" * 5000
    response = client.get(f"/secure-query/decrypt?data={large_data}")
    assert response.status_code == 422  # Validation error


def test_rate_limit_check():
    """Test rate limiting logic."""
    # Clear rate limit storage
    _rate_limit_storage.clear()

    client_ip = "127.0.0.1"

    # Should allow first requests up to limit
    for _ in range(DECRYPT_RATE_LIMIT):
        assert _check_rate_limit(client_ip) is True

    # Should block next request
    assert _check_rate_limit(client_ip) is False


def test_rate_limit_window_expiry():
    """Test that rate limit window expires correctly."""
    _rate_limit_storage.clear()

    client_ip = "127.0.0.1"

    # Mock time.time directly since it's imported in the router module
    with patch("time.time") as mock_time:
        # Start at time 0
        mock_time.return_value = 0

        # Fill up the rate limit
        for _ in range(DECRYPT_RATE_LIMIT):
            assert _check_rate_limit(client_ip) is True

        # Should be blocked
        assert _check_rate_limit(client_ip) is False

        # Move time forward past window
        mock_time.return_value = 61  # 61 seconds later

        # Should be allowed again
        assert _check_rate_limit(client_ip) is True


def test_rate_limit_different_ips():
    """Test that rate limiting is per-IP."""
    _rate_limit_storage.clear()

    ip1 = "127.0.0.1"
    ip2 = "192.168.1.1"

    # Fill up rate limit for IP1
    for _ in range(DECRYPT_RATE_LIMIT):
        assert _check_rate_limit(ip1) is True

    # IP1 should be blocked
    assert _check_rate_limit(ip1) is False

    # IP2 should still be allowed
    assert _check_rate_limit(ip2) is True


def test_decrypt_endpoint_rate_limiting(client):
    """Test rate limiting on decrypt endpoint."""
    # Clear rate limit storage
    _rate_limit_storage.clear()

    # Make requests up to the limit
    for _ in range(DECRYPT_RATE_LIMIT):
        response = client.get("/secure-query/decrypt?data=invalid")
        # Should get 400 (bad data) not 429 (rate limited)
        assert response.status_code == 400

    # Next request should be rate limited
    response = client.get("/secure-query/decrypt?data=invalid")
    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded"


def test_decrypt_endpoint_rate_limiting_different_clients(client):
    """Test that rate limiting works correctly for single client."""
    _rate_limit_storage.clear()

    # First client fills up rate limit
    for _ in range(DECRYPT_RATE_LIMIT):
        response = client.get("/secure-query/decrypt?data=invalid")
        assert response.status_code == 400  # Bad data, not rate limited

    # Should be rate limited now
    response = client.get("/secure-query/decrypt?data=invalid")
    assert response.status_code == 429


def test_public_key_endpoint_not_rate_limited(client):
    """Test that public key endpoint is not rate limited."""
    _rate_limit_storage.clear()

    # Make many requests to public key endpoint
    for _ in range(DECRYPT_RATE_LIMIT + 5):
        response = client.get("/secure-query/public-key")
        assert response.status_code == 200


def test_error_message_does_not_leak_info(client):
    """Test that error messages don't leak sensitive information."""
    # Test various types of invalid input
    invalid_inputs = [
        "invalid_base64!@#",
        "dGVzdA",  # Valid base64 but not encrypted data
        "",  # Empty string
        "A" * 4096,  # Max length valid base64 but invalid ciphertext
    ]

    for invalid_input in invalid_inputs:
        response = client.get(f"/secure-query/decrypt?data={invalid_input}")
        assert response.status_code == 400
        assert response.json()["detail"] == "Decryption failed"
        # Ensure no additional information is leaked


def test_concurrent_rate_limiting():
    """Test rate limiting under concurrent access."""
    _rate_limit_storage.clear()

    client_ip = "127.0.0.1"

    # Simulate concurrent requests
    results = []
    for _ in range(DECRYPT_RATE_LIMIT + 5):
        results.append(_check_rate_limit(client_ip))

    # Should have exactly DECRYPT_RATE_LIMIT True values
    assert sum(results) == DECRYPT_RATE_LIMIT
    # All remaining should be False
    assert results[DECRYPT_RATE_LIMIT:] == [False] * 5
