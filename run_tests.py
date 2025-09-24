#!/usr/bin/env python3
"""Test runner script for secure-query."""
import subprocess
import sys
from pathlib import Path


def main():
    """Run tests with appropriate setup."""
    project_root = Path(__file__).parent

    # Install test dependencies
    print("Installing test dependencies...")
    result = subprocess.run([
        sys.executable, "-m", "pip", "install", "-e", ".[test]"
    ], cwd=project_root)

    if result.returncode != 0:
        print("Failed to install dependencies")
        return 1

    # Run tests
    print("Running tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", "-v"
    ], cwd=project_root)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())