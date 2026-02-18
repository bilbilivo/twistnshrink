# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/). This project uses [calendar versioning](https://calver.org/) in the format `YYYY.##` (e.g., `2026.1`, `2026.2`).

## [Unreleased]

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
- Module docstring and function docstrings throughout `pic_resizer.py`.
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
- `dist/pic_resizer.exe` removed from version control; distributed via GitHub Releases instead.
- `pic_resizer.ini` added to `.gitignore` (runtime-generated file).
