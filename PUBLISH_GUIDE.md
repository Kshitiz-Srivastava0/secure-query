# Publishing Guide - Making Secure Query Globally Accessible

This guide walks you through publishing your `secure-query` package to make it globally accessible via PyPI.

## 🎯 Quick Start (No GitHub Required)

If you just want to publish to PyPI without GitHub:

### 1. Create PyPI Accounts
- **PyPI**: [pypi.org/account/register/](https://pypi.org/account/register/)
- **TestPyPI**: [test.pypi.org/account/register/](https://test.pypi.org/account/register/) (for testing)

### 2. Get API Tokens
1. Go to Account Settings → API tokens
2. Create tokens for both PyPI and TestPyPI
3. Set environment variables:
```bash
# Windows
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-your-api-token-here

# Linux/Mac
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here
```

### 3. Publish Package
```bash
# Test upload first (recommended)
python publish.py --test

# Production upload
python publish.py
```

### 4. Install Globally
After publishing, anyone can install:
```bash
pip install secure-query
```

## 🐙 GitHub Integration (Recommended)

For automated publishing and professional setup:

### 1. Run Setup Script
```bash
python setup_repo.py
```
This will:
- Ask for your GitHub username
- Update URLs in pyproject.toml
- Initialize git repository
- Guide you through GitHub repo creation

### 2. Create GitHub Repository
**Option A: Manual**
1. Go to [github.com/new](https://github.com/new)
2. Create repository named `secure-query`
3. Make it public
4. Don't initialize with README

**Option B: GitHub CLI (if installed)**
```bash
gh repo create secure-query --public --source=. --push
```

### 3. Push Your Code
```bash
git remote add origin https://github.com/YOUR_USERNAME/secure-query.git
git push -u origin main
```

### 4. Configure Secrets
In your GitHub repository:
1. Go to Settings → Secrets and variables → Actions
2. Add secrets:
   - `PYPI_API_TOKEN`
   - `TEST_PYPI_API_TOKEN`

### 5. Automated Publishing
GitHub Actions will automatically:
- Run tests on every push
- Publish to TestPyPI on pre-release tags (`v0.1.0-beta`)
- Publish to PyPI on release tags (`v0.1.0`)

```bash
# Create and push a release
git tag v0.1.0
git push origin v0.1.0
```

## 📦 Publishing Options

### Local Publishing (No GitHub)
```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

### Automated Publishing (GitHub)
- Push tags trigger automatic builds and publishing
- Tests run on multiple Python versions
- Security scanning included
- Automatic GitHub releases created

## 🔄 Updating Your Package

### 1. Update Version
Edit `pyproject.toml`:
```toml
version = "0.1.1"  # Increment version
```

### 2. Update Changelog
Add changes to `CHANGELOG.md`:
```markdown
## [0.1.1] - 2024-09-25
### Fixed
- Bug fixes and improvements
```

### 3. Publish Update
**Local:**
```bash
python publish.py
```

**GitHub:**
```bash
git tag v0.1.1
git push origin v0.1.1
```

## 🛡️ Security Best Practices

### API Token Security
- Never commit API tokens to code
- Use environment variables or GitHub Secrets
- Rotate tokens regularly
- Use scoped tokens (PyPI project-specific)

### Package Security
- All dependencies are security-scanned
- Code is automatically linted for security issues
- Tests ensure no regressions

## 📊 After Publishing

### Monitor Your Package
- **PyPI Stats**: [pypi.org/project/secure-query/](https://pypi.org/project/secure-query/)
- **Download Analytics**: Available in PyPI dashboard
- **GitHub Insights**: Repository traffic and clones

### Maintenance
- Respond to issues and pull requests
- Keep dependencies updated
- Monitor security advisories
- Regular testing on new Python versions

## 🚀 Global Usage

Once published, anyone worldwide can use your package:

```python
# Install
pip install secure-query

# Use in their projects
from secure_query import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
```

## 🎉 Success Metrics

Your package is successfully global when:
- ✅ Available on PyPI: `pip install secure-query` works
- ✅ Documentation accessible on GitHub
- ✅ Tests pass on multiple Python versions
- ✅ Security scanned and verified
- ✅ Easy to install and use

## 🆘 Troubleshooting

### Common Issues

**"Package already exists"**
- Package name might be taken
- Change name in `pyproject.toml`

**"Invalid token"**
- Check token is correctly set
- Verify token hasn't expired
- Ensure correct token for PyPI vs TestPyPI

**"Tests failing"**
- Run `pytest -v` locally first
- Fix any failing tests before publishing

**"GitHub Actions failing"**
- Check secrets are properly set
- Verify token permissions
- Check workflow syntax

### Getting Help
- Create issues on your GitHub repository
- Check [PyPI Help](https://pypi.org/help/)
- Review [packaging.python.org](https://packaging.python.org/)

---

## 📋 Quick Checklist

**Before Publishing:**
- [ ] Tests pass: `pytest -v`
- [ ] Package builds: `python -m build`
- [ ] Package validates: `python -m twine check dist/*`
- [ ] Version incremented
- [ ] Changelog updated

**For Global Distribution:**
- [ ] PyPI account created
- [ ] API tokens configured
- [ ] GitHub repository created (optional)
- [ ] Secrets configured (if using GitHub)
- [ ] Published successfully
- [ ] Installation verified: `pip install secure-query`

Your package is now ready to go global! 🌍