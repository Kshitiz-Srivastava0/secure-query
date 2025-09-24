#!/usr/bin/env python3
"""
Script to help set up GitHub repository for secure-query package.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description, capture_output=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")

    if capture_output:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent)

        if result.returncode != 0:
            print(f"❌ Failed: {description}")
            print(f"Error: {result.stderr}")
            return False

        print(f"✅ Success: {description}")
        if result.stdout.strip():
            print(result.stdout.strip())
    else:
        result = subprocess.run(cmd, shell=True, cwd=Path(__file__).parent)
        if result.returncode != 0:
            print(f"❌ Failed: {description}")
            return False
        print(f"✅ Success: {description}")

    return True


def update_urls(username, repo_name="secure-query"):
    """Update GitHub URLs in pyproject.toml."""
    pyproject_file = Path(__file__).parent / "pyproject.toml"
    content = pyproject_file.read_text()

    # Replace placeholder URLs
    content = content.replace("YOUR_USERNAME", username)

    pyproject_file.write_text(content)
    print(f"✅ Updated URLs for GitHub user: {username}")


def main():
    """Set up GitHub repository."""
    print("🚀 Setting up GitHub repository for secure-query")

    # Check if git is installed
    if not run_command("git --version", "Checking Git installation"):
        print("❌ Git is not installed. Please install Git first.")
        return 1

    # Check if gh CLI is installed
    gh_available = run_command("gh --version", "Checking GitHub CLI", capture_output=True)

    print("\n" + "="*60)
    print("GITHUB REPOSITORY SETUP")
    print("="*60)

    # Get GitHub username
    username = input("Enter your GitHub username: ").strip()
    if not username:
        print("❌ Username is required")
        return 1

    repo_name = input("Enter repository name (default: secure-query): ").strip() or "secure-query"

    # Update URLs in pyproject.toml
    update_urls(username, repo_name)

    # Initialize git repository
    if not Path(".git").exists():
        if not run_command("git init", "Initializing Git repository"):
            return 1

    # Add all files
    if not run_command("git add .", "Adding files to Git"):
        return 1

    # Initial commit
    if not run_command('git commit -m "Initial commit: Secure Query package"', "Creating initial commit"):
        return 1

    # Set main branch
    if not run_command("git branch -M main", "Setting main branch"):
        return 1

    print(f"\n📋 Next steps:")
    print(f"1. Go to https://github.com/new")
    print(f"2. Create a repository named '{repo_name}'")
    print(f"3. Make it public (recommended for open source)")
    print(f"4. Don't initialize with README (we have one)")

    if gh_available:
        print(f"\n🎯 OR use GitHub CLI to create repository automatically:")
        print(f"   gh repo create {repo_name} --public --source=. --push")

        create_now = input(f"\nCreate repository '{repo_name}' now with GitHub CLI? (y/N): ").strip().lower()
        if create_now == 'y':
            if run_command(f"gh repo create {repo_name} --public --source=. --push", "Creating GitHub repository", capture_output=False):
                print(f"🎉 Repository created successfully!")
                print(f"🔗 View at: https://github.com/{username}/{repo_name}")
                return 0
    else:
        print(f"\n5. Run these commands after creating the repository:")
        print(f"   git remote add origin https://github.com/{username}/{repo_name}.git")
        print(f"   git push -u origin main")

    print(f"\n🔧 After repository is created:")
    print(f"1. Go to repository Settings → Secrets and variables → Actions")
    print(f"2. Add these secrets for automated publishing:")
    print(f"   - PYPI_API_TOKEN: Your PyPI API token")
    print(f"   - TEST_PYPI_API_TOKEN: Your TestPyPI API token")
    print(f"3. Push a tag to trigger publishing: git tag v0.1.0 && git push origin v0.1.0")

    return 0


if __name__ == "__main__":
    sys.exit(main())