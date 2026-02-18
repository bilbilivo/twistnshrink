# Plan: CI/CD, Testing, and Release Workflow

## Configuration
- **Python minimum**: 3.9+
- **Release trigger**: Git tag push (e.g., `v1.0.0`)
- **Release artifacts**: Windows `.exe` only; Linux/macOS from source
- **CI matrix**: Python 3.9, 3.10, 3.11, 3.12 on Ubuntu

---

## Phase 0: Foundational Fixes

### pyproject.toml
- Add `[build-system]` table with setuptools
- Bump `requires-python` from `>=3.7` to `>=3.9`
- Update ruff `target-version` from `py37` to `py39`
- Add `[project.optional-dependencies]` with `dev` (ruff, pytest) and `build` (pyinstaller)
- Add `[tool.pytest.ini_options]` with `testpaths = ["tests"]`

### requirements.txt
- Add a comment noting it's kept in sync with pyproject.toml
- Keep the same deps (Pillow, piexif)

### .gitignore
- Add `pic_resizer.ini` to the "Application runtime files" section

### pic_resizer.py
- Update `dict[str, str]` type hint to use `Dict[str, str]` from typing OR leave as-is since we're targeting 3.9+ (builtin dict generics available in 3.9+, so it's fine)

---

## Phase 1: Unit Tests

### Create `tests/` directory with:

#### tests/conftest.py
- Shared fixtures: sample PIL Image, sample image with EXIF, tmp config path

#### tests/test_image_processing.py
Tests for the 4 pure functions:

1. **`test_rotate_image_90`** - 200x100 image -> 100x200
2. **`test_rotate_image_180`** - dimensions stay same, pixels flipped
3. **`test_rotate_image_270`** - 200x100 -> 100x200
4. **`test_rotate_image_invalid_angle`** - returns unchanged image
5. **`test_resize_image_within_target`** - output size <= target
6. **`test_resize_image_preserves_jpeg`** - output is valid JPEG
7. **`test_resize_image_with_exif`** - EXIF bytes included in output
8. **`test_resize_image_without_exif`** - works with None exif
9. **`test_resize_image_quality_floor`** - very small target still produces output
10. **`test_fix_orientation_no_exif`** - returns image unchanged
11. **`test_fix_orientation_values`** - test orientation values 2-8
12. **`test_load_exif_safe_no_exif`** - returns None for plain image
13. **`test_load_exif_safe_with_exif`** - returns bytes, orientation stripped
14. **`test_load_exif_safe_corrupt`** - returns None

#### tests/test_config.py
Tests for load_config:

1. **`test_load_config_creates_file`** - creates config when none exists
2. **`test_load_config_fills_missing_keys`** - adds missing defaults
3. **`test_load_config_preserves_existing`** - doesn't overwrite existing values
4. **`test_load_config_returns_configparser`** - correct type returned

These tests will need to monkeypatch `pic_resizer.CONFIG_FILE` to use `tmp_path`.

---

## Phase 2: GitHub Actions CI Workflow

### .github/workflows/ci.yml
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff
      - run: ruff check .

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: sudo apt-get update && sudo apt-get install -y python3-tk
      - run: pip install .[dev]
      - run: pytest -v
```

---

## Phase 3: GitHub Actions Release Workflow

### .github/workflows/release.yml
```yaml
name: Release

on:
  push:
    tags:
      - "v*"

permissions:
  contents: write

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install .[build]
      - run: pyinstaller --onefile --noconsole pic_resizer.py
      - uses: actions/upload-artifact@v4
        with:
          name: pic_resizer-windows
          path: dist/pic_resizer.exe

  create-release:
    needs: build-windows
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: pic_resizer-windows
          path: release-assets/
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
          files: |
            release-assets/pic_resizer.exe
```

---

## Phase 4: Documentation Updates

### README.md
- Add CI badge: `![CI](https://github.com/USER/pic_resizer/actions/workflows/ci.yml/badge.svg)`
- Add "Download" section pointing to GitHub Releases page
- Update Python version requirement from 3.7 to 3.9
- Mention running tests: `pip install .[dev] && pytest`

### CONTRIBUTING.md
- Add Windows venv activation: `venv\Scripts\activate`
- Add linting step: `ruff check .`
- Add testing step: `pytest -v`
- Update Python version requirement

### CHANGELOG.md
- Move `[Unreleased]` entries to `[1.0.0] - 2026-02-17`
- Add new `[Unreleased]` section for future changes
- Add entries for: unit tests, CI/CD workflows, Python 3.9+ requirement

### BUILDING.md
- Add note about automated CI builds
- Mention that releases are now published via GitHub Actions on tag push

---

## Phase 5: Verify

- Create venv with `python3 -m venv venv`
- Install dev deps: `pip install .[dev]`
- Run `ruff check .` — should pass
- Run `pytest -v` — should pass
- Review all new/modified files for correctness

---

## Files to Create
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_image_processing.py`
- `tests/test_config.py`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`

## Files to Modify
- `pyproject.toml`
- `requirements.txt`
- `.gitignore`
- `README.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `BUILDING.md`
