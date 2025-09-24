"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture(autouse=True)
def isolate_rate_limiting():
    """Ensure rate limiting storage is isolated between tests."""
    from secure_query.router import _rate_limit_storage

    # Clear before each test
    _rate_limit_storage.clear()

    yield

    # Clear after each test
    _rate_limit_storage.clear()


@pytest.fixture
def clean_environment(monkeypatch):
    """Provide a clean environment for settings tests."""
    # Remove any existing SECURE_QUERY_KEYS_DIR
    monkeypatch.delenv("SECURE_QUERY_KEYS_DIR", raising=False)
    yield
