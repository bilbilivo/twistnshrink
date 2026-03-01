# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/). This project uses [calendar versioning](https://calver.org/) in the format `YYYY.##` (e.g., `2026.1`, `2026.2`).

## [Unreleased]

## [2026.7] - 2026-02-28

### Added
- Help menu with **Donate via PayPal** and **About** dialog (clickable PayPal link).
- `.github/FUNDING.yml` — GitHub Sponsor button linking to PayPal.
- PayPal donate badge in README.
- Application icon replaced with monochrome Material Icons "image" icon (Apache 2.0).

### Fixed
- Progress window close button is now disabled during processing, preventing a crash (`TclError`) if the user dismisses it mid-batch.
- Numeric inputs (Max Frame Size, Target Size KB) are now validated to be positive before processing begins.
- Output files that already exist are now skipped with a warning instead of being silently overwritten.
- Config file writes are now wrapped in `try/except OSError` so a read-only filesystem no longer crashes the app.
- `FileSuffix` is sanitised to strip path-separator characters, preventing directory traversal.
- `fix_orientation` now catches `Exception` broadly (previously `AttributeError, KeyError, IndexError`) to handle all malformed EXIF cases.
- Replaced private `image._getexif()` Pillow API with the public `image.getexif()` (available since Pillow 6.0).
- Progress bar updates now use `.configure()` instead of `.__setitem__()` dunder calls; named functions replace tuple-returning lambdas.
- Release workflow now uses `pyinstaller twistnshrink.spec` so released `.exe` files include the application icon.
- CI `paths-ignore` cleaned up: removed redundant `CHANGELOG.md` entry (already matched by `**/*.md`) and nonexistent `docs/**` path.
- `launch.sh` icon conversion now passes paths via environment variables instead of embedding shell variables in a Python string literal.
- Removed stale `twistnshrink.ini` and `.opencode/plans/ci-cd-and-testing.md` from version control.
- Unused `sample_jpeg_bytes` test fixture removed from `tests/conftest.py`.
- Copyright year updated to 2025-2026 in LICENSE and README.

## [2026.6] - 2026-02-18

### Changed
- Dependency management is now handled solely via `pyproject.toml` (PEP 621). `requirements.txt` has been removed and launcher/install documentation and scripts updated. The launcher will upgrade pip to 23.1+ if needed and use `pip install .` for installs. This modernizes and simplifies all future maintenance.

## [2026.5] - 2026-02-18

### Fixed
- Linux (GNOME/Ubuntu) app launcher now installs its .desktop file to the correct directory (`~/.local/share/applications/`), ensuring the app can be launched from the Applications menu. The prior approach (leaving the .desktop file in the repo) often failed to register with desktop environments.
## [2026.4] - 2026-02-18

### Added
- Comprehensive release workflow documentation in BUILDING.md and CONTRIBUTING.md.

### Changed
- CI workflow now ignores markdown and documentation files on push and pull request events to improve efficiency.
- GUI: Shortened window title and aligned resize/rotate section buttons for improved visual consistency.

## [2026.2] - 2026-02-17

### Fixed

- Fixed release workflow to ensure `.exe` file is uploaded correctly

## [2026.1] - 2026-02-17

### Added
- Unit test suite with pytest covering image processing and configuration functions.
- GitHub Actions CI workflow (lint with ruff, test with pytest on Python 3.9-3.12).
- GitHub Actions release workflow -- automatically builds Windows `.exe` and publishes to GitHub Releases on tag push.
- `[build-system]` table and `[project.optional-dependencies]` in `pyproject.toml`.
- pytest configuration in `pyproject.toml`.
- Module docstring and function docstrings throughout `twistnshrink.py`.
- Type hints on all functions.
- `if __name__ == "__main__"` guard so the module can be imported without launching the GUI.
- `CONTRIBUTING.md` with contribution guidelines.
- `CHANGELOG.md` (this file).
- `BUILDING.md` with PyInstaller build instructions (replaces `convert_to_exe.txt`).
- `pyproject.toml` with project metadata and ruff linter configuration.

### Fixed
- Config file path is now resolved relative to the script location, not the working directory.
- Rotate operation now reports errors to the user via a dialog instead of silently printing to stdout.
- Images without EXIF data no longer cause a crash during resize.
- Rotate operation now preserves EXIF metadata (previously it was silently stripped).

### Changed
- Minimum Python version bumped from 3.7 to 3.9.
- Config file is only rewritten when missing keys are detected (previously rewritten on every launch).
- Default config values are defined in a single place (`DEFAULT_CONFIG` dict) to avoid duplication.
- JPEG quality parameters (initial, floor, step) are now named constants.
- Dependencies in `requirements.txt` are now pinned to compatible version ranges.
- Improved `.gitignore` with comprehensive patterns for Python, IDE, and OS files.
- `dist/twistnshrink.exe` removed from version control; distributed via GitHub Releases instead.
- `twistnshrink.ini` added to `.gitignore` (runtime-generated file).
