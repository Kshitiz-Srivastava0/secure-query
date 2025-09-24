#!/usr/bin/env python3
"""
Script to build and publish secure-query package to PyPI.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        print(f"Error: {result.stderr}")
        return False

    print(f"✅ Success: {description}")
    if result.stdout.strip():
        print(result.stdout)
    return True


def main():
    """Build and publish the package."""
    project_root = Path(__file__).parent
    os.chdir(project_root)

    print("📦 Starting secure-query package build and publish process")

    # Step 1: Clean previous builds
    print("\n1. Cleaning previous builds...")
    subprocess.run("rm -rf dist/ build/ *.egg-info", shell=True, capture_output=True)

    # Step 2: Install/upgrade build tools
    if not run_command(
        "python -m pip install --upgrade build twine",
        "Installing/upgrading build tools"
    ):
        return 1

    # Step 3: Run tests
    if not run_command("python -m pytest -v", "Running test suite"):
        print("⚠️  Tests failed. Fix tests before publishing.")
        return 1

    # Step 4: Build the package
    if not run_command("python -m build", "Building package"):
        return 1

    # Step 5: Check the built package
    if not run_command("python -m twine check dist/*", "Validating package"):
        return 1

    # Step 6: Show what will be uploaded
    print("\n📋 Files to be uploaded:")
    dist_files = list(Path("dist").glob("*"))
    for file in dist_files:
        print(f"  - {file.name}")

    # Step 7: Confirm upload
    print(f"\n🚀 Ready to upload {len(dist_files)} files to PyPI")

    # Check if we're doing a test upload or real upload
    test_upload = "--test" in sys.argv

    if test_upload:
        print("📍 Uploading to TestPyPI...")
        upload_cmd = "python -m twine upload --repository testpypi dist/*"
        print("ℹ️  Install from TestPyPI with: pip install -i https://test.pypi.org/simple/ secure-query")
    else:
        response = input("Are you sure you want to upload to PyPI? (yes/no): ")
        if response.lower() != "yes":
            print("❌ Upload cancelled")
            return 0

        print("📍 Uploading to PyPI...")
        upload_cmd = "python -m twine upload dist/*"

    # Step 8: Upload
    if not run_command(upload_cmd, "Uploading package"):
        return 1

    print("\n🎉 Package published successfully!")

    if not test_upload:
        print("📦 Install with: pip install secure-query")
        print("📖 View on PyPI: https://pypi.org/project/secure-query/")

    return 0


if __name__ == "__main__":
    sys.exit(main())