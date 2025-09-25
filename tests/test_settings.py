"""Tests for settings module."""

import os
import tempfile
from pathlib import Path

from secure_query.settings import DEFAULT_KEYS_DIR, Settings


def test_default_settings():
    """Test default settings configuration."""
    settings = Settings()
    assert settings.keys_dir == DEFAULT_KEYS_DIR
    assert settings.private_key_file == settings.keys_dir / "private_key.pem"
    assert settings.public_key_file == settings.keys_dir / "public_key.pem"


def test_custom_keys_dir():
    """Test settings with custom keys directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_dir = Path(temp_dir) / "custom_keys"
        settings = Settings(custom_dir)

        # Use resolved paths for comparison to handle symlinks (macOS /tmp)
        expected_keys_dir = custom_dir.resolve()
        assert settings.keys_dir == expected_keys_dir
        assert settings.keys_dir.exists()  # Should be created
        assert settings.private_key_file == expected_keys_dir / "private_key.pem"
        assert settings.public_key_file == expected_keys_dir / "public_key.pem"


def test_keys_dir_creation():
    """Test that keys directory is created if it doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        nonexistent_dir = Path(temp_dir) / "nested" / "keys"
        assert not nonexistent_dir.exists()

        settings = Settings(nonexistent_dir)
        assert nonexistent_dir.exists()
        assert settings.keys_dir == nonexistent_dir.resolve()


def test_environment_variable_override():
    """Test that SECURE_QUERY_KEYS_DIR environment variable is respected."""
    with tempfile.TemporaryDirectory() as temp_dir:
        env_dir = Path(temp_dir) / "env_keys"

        # Set environment variable
        old_env = os.environ.get("SECURE_QUERY_KEYS_DIR")
        os.environ["SECURE_QUERY_KEYS_DIR"] = str(env_dir)

        try:
            # Import settings module to get fresh DEFAULT_KEYS_DIR
            import importlib

            import secure_query.settings

            importlib.reload(secure_query.settings)

            settings = secure_query.settings.Settings()
            assert settings.keys_dir == env_dir.resolve()
            assert settings.keys_dir.exists()

        finally:
            # Restore original environment
            if old_env is not None:
                os.environ["SECURE_QUERY_KEYS_DIR"] = old_env
            elif "SECURE_QUERY_KEYS_DIR" in os.environ:
                del os.environ["SECURE_QUERY_KEYS_DIR"]

            # Reload settings to restore original state
            importlib.reload(secure_query.settings)


def test_string_keys_dir():
    """Test that string keys_dir parameter works correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        string_dir = str(Path(temp_dir) / "string_keys")
        settings = Settings(string_dir)

        assert settings.keys_dir == Path(string_dir).resolve()
        assert settings.keys_dir.exists()


def test_relative_path_resolution():
    """Test that relative paths are resolved correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory BEFORE creating Settings
        old_cwd = os.getcwd()

        try:
            os.chdir(temp_dir)

            # Now create Settings with relative path
            # It should resolve to temp directory
            settings = Settings("relative_keys")

            # Check if the path exists and is within the temp directory
            assert settings.keys_dir.exists()

            # Ensure the path is either absolute or resolves correctly
            resolved_path = settings.keys_dir.resolve()
            expected_parent = Path(temp_dir).resolve()

            # The resolved path should be within the temp directory
            assert resolved_path.parent == expected_parent
            assert resolved_path.name == "relative_keys"

        finally:
            os.chdir(old_cwd)


def test_keys_dir_permissions():
    """Test that keys directory has appropriate permissions."""
    with tempfile.TemporaryDirectory() as temp_dir:
        keys_dir = Path(temp_dir) / "test_keys"
        Settings(keys_dir)  # Create settings to initialize directory

        # Check that directory was created and is accessible
        assert keys_dir.exists()
        assert keys_dir.is_dir()

        # Should be able to create files in the directory
        test_file = keys_dir / "test.txt"
        test_file.write_text("test")
        assert test_file.read_text() == "test"
