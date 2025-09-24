#!/usr/bin/env python3
"""
Debug script to help troubleshoot GitHub Actions issues.
Run this script to simulate the GitHub Actions environment locally.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and show output."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, shell=True, text=True, cwd=Path(__file__).parent)

    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        return False
    else:
        print(f"✅ Success: {description}")
        return True


def main():
    """Simulate GitHub Actions environment."""
    print("🐙 GitHub Actions Debug Script")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")

    # Step 1: Check Python and pip
    if not run_command("python --version", "Check Python version"):
        return 1

    if not run_command("pip --version", "Check pip version"):
        return 1

    # Step 2: Upgrade pip and install build tools
    if not run_command("python -m pip install --upgrade pip", "Upgrade pip"):
        return 1

    if not run_command("python -m pip install build", "Install build tools"):
        return 1

    # Step 3: Install package in development mode
    if not run_command("python -m pip install -e .[test]", "Install package with test dependencies"):
        return 1

    # Step 4: Verify installation
    if not run_command("python -c \"import secure_query; print('Package imported successfully')\"", "Verify package import"):
        return 1

    if not run_command("python -c \"from secure_query import ensure_keys, get_public_key_pem; print('Functions imported successfully')\"", "Verify function imports"):
        return 1

    # Step 5: Show installed packages
    if not run_command("pip list", "Show installed packages"):
        return 1

    # Step 6: Run tests
    if not run_command("pytest -v --tb=short", "Run tests"):
        return 1

    # Step 7: Run linting (if tools available)
    print(f"\n{'='*60}")
    print("🧹 Linting checks")
    print(f"{'='*60}")

    # Install linting tools
    run_command("pip install black isort flake8", "Install linting tools")

    # Run linting
    run_command("black --check src/ tests/ --line-length=88 --target-version=py39", "Check code formatting")
    run_command("isort --check-only src/ tests/ --profile=black", "Check import sorting")
    run_command("flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503", "Lint with flake8")

    print(f"\n🎉 All checks completed successfully!")
    print("Your package should work fine in GitHub Actions.")

    return 0


if __name__ == "__main__":
    sys.exit(main())