"""Tests for crypto module including security edge cases."""

import base64
import json
import tempfile
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from secure_query.crypto import (
    _b64url_to_bytes,
    decrypt_b64url_payload,
    ensure_keys,
    get_public_key_pem,
)
from secure_query.settings import Settings


@pytest.fixture
def temp_keys_dir():
    """Create temporary directory for test keys."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_settings(temp_keys_dir):
    """Create test settings with temporary keys directory."""
    return Settings(temp_keys_dir)


def test_ensure_keys_creates_keypair(test_settings, monkeypatch):
    """Test that ensure_keys creates a new keypair when none exists."""
    monkeypatch.setattr("secure_query.crypto.settings", test_settings)

    assert not test_settings.private_key_file.exists()
    assert not test_settings.public_key_file.exists()

    ensure_keys()

    assert test_settings.private_key_file.exists()
    assert test_settings.public_key_file.exists()


def test_ensure_keys_preserves_existing_keys(test_settings, monkeypatch):
    """Test that ensure_keys doesn't overwrite existing keys."""
    monkeypatch.setattr("secure_query.crypto.settings", test_settings)

    # Create initial keys
    ensure_keys()
    initial_private = test_settings.private_key_file.read_bytes()
    initial_public = test_settings.public_key_file.read_bytes()

    # Call ensure_keys again
    ensure_keys()

    # Keys should be unchanged
    assert test_settings.private_key_file.read_bytes() == initial_private
    assert test_settings.public_key_file.read_bytes() == initial_public


def test_get_public_key_pem(test_settings, monkeypatch):
    """Test public key retrieval."""
    monkeypatch.setattr("secure_query.crypto.settings", test_settings)
    ensure_keys()

    pem = get_public_key_pem()
    assert pem.startswith("-----BEGIN PUBLIC KEY-----")
    assert pem.endswith("-----END PUBLIC KEY-----\n")


def test_b64url_to_bytes():
    """Test base64url decoding with padding."""
    # Test cases with different padding requirements
    test_cases = [
        ("AQAB", b"\x01\x00\x01"),  # No padding needed
        ("YWJj", b"abc"),  # No padding needed
        ("YWI", b"ab"),  # 1 padding char needed
        ("YQ", b"a"),  # 2 padding chars needed
    ]

    for b64url_str, expected_bytes in test_cases:
        assert _b64url_to_bytes(b64url_str) == expected_bytes


def test_decrypt_b64url_payload_success(test_settings, monkeypatch):
    """Test successful decryption of valid payload."""
    monkeypatch.setattr("secure_query.crypto.settings", test_settings)
    ensure_keys()

    # Load the public key for encryption
    public_key = serialization.load_pem_public_key(
        test_settings.public_key_file.read_bytes()
    )

    # Create test payload
    test_payload = {"user": "alice", "action": "query", "data": [1, 2, 3]}
    plaintext = json.dumps(test_payload).encode("utf-8")

    # Encrypt with RSA-OAEP
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

    # Decrypt and verify
    decrypted_payload = decrypt_b64url_payload(ciphertext_b64url)
    assert decrypted_payload == test_payload


def test_decrypt_b64url_payload_invalid_base64():
    """Test decryption failure with invalid base64."""
    with pytest.raises(Exception):
        decrypt_b64url_payload("invalid!@#$%")


def test_decrypt_b64url_payload_invalid_ciphertext(test_settings, monkeypatch):
    """Test decryption failure with invalid ciphertext."""
    monkeypatch.setattr("secure_query.crypto.settings", test_settings)
    ensure_keys()

    # Valid base64 but invalid ciphertext
    invalid_ciphertext = (
        base64.urlsafe_b64encode(b"invalid ciphertext").decode("ascii").rstrip("=")
    )

    with pytest.raises(Exception):
        decrypt_b64url_payload(invalid_ciphertext)


def test_decrypt_b64url_payload_wrong_key(test_settings, monkeypatch):
    """Test decryption failure with wrong key."""
    monkeypatch.setattr("secure_query.crypto.settings", test_settings)
    ensure_keys()

    # Generate a different keypair
    different_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    different_public = different_key.public_key()

    # Encrypt with different key
    test_payload = {"test": "data"}
    plaintext = json.dumps(test_payload).encode("utf-8")

    ciphertext = different_public.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    ciphertext_b64url = base64.urlsafe_b64encode(ciphertext).decode("ascii").rstrip("=")

    # Should fail to decrypt
    with pytest.raises(Exception):
        decrypt_b64url_payload(ciphertext_b64url)


def test_decrypt_b64url_payload_malformed_json(test_settings, monkeypatch):
    """Test decryption failure with malformed JSON."""
    monkeypatch.setattr("secure_query.crypto.settings", test_settings)
    ensure_keys()

    # Load the public key for encryption
    public_key = serialization.load_pem_public_key(
        test_settings.public_key_file.read_bytes()
    )

    # Create malformed JSON
    plaintext = b'{"invalid": json}'  # Missing quotes around json

    ciphertext = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    ciphertext_b64url = base64.urlsafe_b64encode(ciphertext).decode("ascii").rstrip("=")

    # Should fail to parse JSON
    with pytest.raises(Exception):
        decrypt_b64url_payload(ciphertext_b64url)


def test_large_payload_encryption_decryption(test_settings, monkeypatch):
    """Test encryption/decryption of maximum size payload for RSA-2048."""
    monkeypatch.setattr("secure_query.crypto.settings", test_settings)
    ensure_keys()

    # RSA-2048 with OAEP-SHA256 can encrypt up to 190 bytes
    # Test with payload near the limit
    large_data = "x" * 150  # Should work
    test_payload = {"data": large_data}

    public_key = serialization.load_pem_public_key(
        test_settings.public_key_file.read_bytes()
    )

    plaintext = json.dumps(test_payload).encode("utf-8")

    ciphertext = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    ciphertext_b64url = base64.urlsafe_b64encode(ciphertext).decode("ascii").rstrip("=")

    decrypted_payload = decrypt_b64url_payload(ciphertext_b64url)
    assert decrypted_payload == test_payload


def test_oversized_payload_fails(test_settings, monkeypatch):
    """Test that oversized payloads fail encryption (expected behavior)."""
    monkeypatch.setattr("secure_query.crypto.settings", test_settings)
    ensure_keys()

    public_key = serialization.load_pem_public_key(
        test_settings.public_key_file.read_bytes()
    )

    # Create payload too large for RSA-2048 OAEP (>190 bytes)
    large_data = "x" * 200
    test_payload = {"data": large_data}
    plaintext = json.dumps(test_payload).encode("utf-8")

    # Should fail during encryption
    with pytest.raises(ValueError):
        public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
