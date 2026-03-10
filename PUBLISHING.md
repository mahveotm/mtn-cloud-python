# Publishing to PyPI with Hatch

This guide explains how to publish the `mtn-cloud` package to PyPI when ready.

## Prerequisites

1. **Install Hatch** (if not already installed):
   ```bash
   pip install hatch
   ```

2. **Create PyPI Account**:
   - Production: https://pypi.org/account/register/
   - Test: https://test.pypi.org/account/register/

3. **Create API Token**:
   - Go to https://pypi.org/manage/account/token/
   - Create a token with scope "Entire account" or project-specific
   - Save the token securely

## Configuration

### Option 1: Environment Variables (Recommended)

```bash
# For PyPI
export HATCH_INDEX_USER=__token__
export HATCH_INDEX_AUTH=pypi-xxxxxxxxxxxx

# For Test PyPI
export HATCH_INDEX_USER=__token__
export HATCH_INDEX_AUTH=pypi-xxxxxxxxxxxx
```

### Option 2: Configure in ~/.pypirc

```ini
[pypi]
username = __token__
password = pypi-xxxxxxxxxxxx

[testpypi]
username = __token__
password = pypi-xxxxxxxxxxxx
```

## Publishing Steps

### 1. Test Locally First

```bash
cd /path/to/mtn-cloud

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Check linting
ruff check src tests
ruff format src tests --check

# Type checking
mypy src
```

### 2. Update Version

Edit `pyproject.toml`:
```toml
version = "0.1.0"  # Update this
```

Or in `src/mtn_cloud/__init__.py`:
```python
__version__ = "0.1.0"  # Keep in sync
```

### 3. Build the Package

```bash
# Clean previous builds
rm -rf dist/

# Build
hatch build

# This creates:
# dist/mtn_cloud-0.1.0-py3-none-any.whl
# dist/mtn_cloud-0.1.0.tar.gz
```

### 4. Test on Test PyPI First (Recommended)

```bash
# Publish to Test PyPI
hatch publish -r test

# Test installation from Test PyPI
pip install -i https://test.pypi.org/simple/ mtn-cloud

# Verify it works
python -c "from mtn_cloud import MTNCloud; print('Success!')"
```

### 5. Publish to Production PyPI

```bash
# Publish to PyPI
hatch publish

# Or explicitly specify repository
hatch publish -r main
```

### 6. Verify Installation

```bash
# Install from PyPI
pip install mtn-cloud

# Verify
python -c "from mtn_cloud import MTNCloud; print('Success!')"
```

## Version Bumping

Hatch can manage versions for you:

```bash
# Show current version
hatch version

# Bump patch (0.1.0 -> 0.1.1)
hatch version patch

# Bump minor (0.1.0 -> 0.2.0)
hatch version minor

# Bump major (0.1.0 -> 1.0.0)
hatch version major

# Set specific version
hatch version 0.2.0
```

## Complete Release Workflow

```bash
#!/bin/bash
set -e

# 1. Ensure clean state
git status  # Should be clean

# 2. Run all checks
ruff check src tests
ruff format src tests --check
mypy src
pytest

# 3. Bump version
hatch version patch  # or minor/major

# 4. Build
rm -rf dist/
hatch build

# 5. Publish to Test PyPI first
hatch publish -r test

# 6. Test installation
pip install -i https://test.pypi.org/simple/ mtn-cloud --upgrade
python -c "from mtn_cloud import MTNCloud; print('Test PyPI: OK')"

# 7. If all good, publish to production
hatch publish

# 8. Tag the release
VERSION=$(hatch version)
git add .
git commit -m "Release v$VERSION"
git tag "v$VERSION"
git push origin main --tags

echo "Released v$VERSION!"
```

## GitHub Actions Publishing

This project includes a `publish.yml` workflow that can publish to PyPI automatically:

1. **On Release**: Automatically publishes to PyPI when you create a GitHub release
2. **Manual**: Run the workflow manually from Actions tab to publish to TestPyPI or PyPI

### Setup for GitHub Actions Publishing

1. Go to your repository settings
2. Create two environments: `testpypi` and `pypi`
3. For each environment, add the trusted publisher on PyPI:
   - Go to https://pypi.org/manage/account/publishing/
   - Add GitHub as trusted publisher
   - Repository: `mahveotm/mtn-cloud-python`
   - Workflow: `publish.yml`

## Troubleshooting

### "File already exists" Error
You cannot overwrite an existing version on PyPI. Bump the version number.

### Authentication Failed
- Ensure you're using `__token__` as username
- Ensure token starts with `pypi-`
- Check token has correct scope

### Package Not Found After Publishing
- Wait a few minutes for PyPI to index
- Clear pip cache: `pip cache purge`
- Try: `pip install mtn-cloud --no-cache-dir`

## Useful Commands

```bash
# Check what would be published
hatch build
tar -tzf dist/*.tar.gz | head -20

# Check package metadata
pip show mtn-cloud

# View on PyPI
open https://pypi.org/project/mtn-cloud/
```

## Links

- [Hatch Documentation](https://hatch.pypa.io/)
- [PyPI](https://pypi.org/)
- [Test PyPI](https://test.pypi.org/)
- [Packaging Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)

