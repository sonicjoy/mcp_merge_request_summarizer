# Publishing Guide

This guide covers how to publish the MCP Merge Request Summarizer to various platforms.

## 📦 PyPI (Python Package Index)

### Prerequisites

1. **Create PyPI Accounts**:
   - [PyPI](https://pypi.org/account/register/) - Production
   - [TestPyPI](https://test.pypi.org/account/register/) - Testing

2. **Generate API Tokens**:
   - Go to Account Settings → API tokens
   - Create a token with "Entire account" scope
   - Save the token securely

3. **Install Build Tools**:
   ```bash
   pip install build twine
   ```

### Publishing Steps

1. **Update Version** (in `pyproject.toml`):
   ```toml
   version = "1.0.0"  # Increment as needed
   ```

2. **Update Author Information** (in `pyproject.toml`):
   ```toml
   authors = [
       {name = "Your Real Name", email = "your.real.email@example.com"}
   ]
   ```

3. **Build the Package**:
   ```bash
   python -m build
   ```

4. **Test on TestPyPI**:
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

5. **Test Installation**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ mcp-merge-request-summarizer
   ```

6. **Publish to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

### Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: python -m twine upload dist/*
```

## 🎯 Cursor MCP Store

Currently, Cursor doesn't have a dedicated MCP store, but you can:

### 1. **GitHub Release with MCP Configuration**

1. **Create a Release** on GitHub
2. **Include MCP Configuration** in the release notes
3. **Provide Installation Instructions**

### 2. **Cursor Community Integration**

1. **Submit to Cursor Community**: Contact Cursor team about MCP integration
2. **Documentation**: Ensure your README has clear Cursor setup instructions
3. **Examples**: Provide working examples for Cursor users

## 🔧 Alternative Distribution Methods

### 1. **GitHub Releases**

1. **Tag a Release**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Create GitHub Release** with:
   - Release notes
   - Installation instructions
   - MCP configuration examples

### 2. **Docker Distribution**

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -e .

ENTRYPOINT ["python", "-m", "mcp_mr_summarizer.server"]
```

### 3. **Homebrew (macOS)**

Create a Homebrew formula for easy installation on macOS.

## 📋 Pre-Publishing Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update author information
- [ ] Test installation from TestPyPI
- [ ] Run all tests: `python -m pytest tests/`
- [ ] Check documentation is up to date
- [ ] Verify MCP server works correctly
- [ ] Test with Cursor/VSCode
- [ ] Update CHANGELOG.md (if you have one)

## 🚀 Post-Publishing

1. **Update Documentation**:
   - Update installation instructions
   - Add PyPI installation option
   - Update examples

2. **Announce**:
   - GitHub release
   - Social media
   - Developer communities

3. **Monitor**:
   - PyPI download statistics
   - GitHub stars/issues
   - User feedback

## 🔒 Security Considerations

- Never commit API tokens to version control
- Use environment variables for sensitive data
- Consider code signing for releases
- Keep dependencies updated

## 📞 Support

- **PyPI Issues**: Contact PyPI support
- **Cursor Integration**: Contact Cursor team
- **General Questions**: GitHub issues
