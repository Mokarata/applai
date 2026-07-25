# UV Package Management Guide

This project uses **uv** as the primary package manager for streamlined dependency management.

## Why UV?

- ⚡ **10-100x faster** than pip
- 🔒 **Reproducible builds** with `uv.lock`
- 🎯 **Single tool** for venv + package management
- 🔄 **Automatic dependency resolution**
- 📦 **No need for pip, pip-tools, or virtualenv**

## Quick Start

```bash
# Initialize project (creates venv + installs dependencies)
cd backend && uv sync --python 3.12

# This automatically:
# ✅ Creates .venv with Python 3.12
# ✅ Generates uv.lock for reproducible builds
# ✅ Installs all dependencies from pyproject.toml
```

## Common Commands

### Running the Application

```bash
# Start FastAPI server
uv run uvicorn app.main:app --reload

# Run any Python script
uv run python script.py

# Run alembic migrations
uv run alembic upgrade head

# Run tests
uv run pytest

# Run code formatters
uv run black .
uv run isort .
```

### Managing Dependencies

```bash
# Add a new dependency (updates pyproject.toml + uv.lock)
uv add requests

# Add a dev dependency
uv add --dev pytest

# Add with version constraint
uv add "fastapi>=0.115.0"

# Remove a dependency
uv remove requests

# Update all dependencies
uv sync --upgrade

# Update specific package
uv add fastapi@latest

# Install from updated pyproject.toml
uv sync
```

### Working with Lock File

```bash
# Generate/update lock file
uv lock

# Install from lock file (reproducible)
uv sync

# Update lock file with latest versions
uv lock --upgrade
```

### Environment Management

```bash
# Create venv with specific Python version
uv venv --python 3.12

# Activate venv (optional - uv run handles this)
source .venv/bin/activate

# Check installed packages
uv pip list

# Show dependency tree
uv tree
```

## Migration from pip

| Old (pip)                          | New (uv)                    |
|------------------------------------|-----------------------------|
| `pip install -e .`                 | `uv sync`                   |
| `pip install requests`             | `uv add requests`           |
| `pip install -r requirements.txt`  | `uv sync`                   |
| `pip list`                         | `uv pip list`               |
| `python script.py`                 | `uv run python script.py`   |
| `python -m pytest`                 | `uv run pytest`             |

## Project Structure

```
backend/
├── pyproject.toml   # Dependencies defined here
├── uv.lock          # Lock file (commit to git)
├── .venv/           # Virtual environment (gitignored)
└── app/             # Application code
```

## Best Practices

1. **Always use `uv sync`** after pulling changes to sync dependencies
2. **Commit `uv.lock`** to git for reproducible builds
3. **Use `uv run`** instead of activating venv manually
4. **Add dependencies via `uv add`** instead of editing pyproject.toml manually
5. **Pin Python version** in pyproject.toml (`requires-python = ">=3.12"`)

## Troubleshooting

### Lock file out of sync
```bash
uv lock --upgrade
```

### Dependencies not resolving
```bash
# Clear cache and retry
uv cache clean
uv sync
```

### Wrong Python version
```bash
# Recreate venv with correct version
rm -rf .venv
uv venv --python 3.12
uv sync
```

## Additional Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [UV GitHub](https://github.com/astral-sh/uv)
