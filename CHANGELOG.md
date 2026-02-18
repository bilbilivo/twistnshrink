# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed
- Config file path is now resolved relative to the script location, not the working directory.
- Rotate operation now reports errors to the user via a dialog instead of silently printing to stdout.
- Images without EXIF data no longer cause a crash during resize.
- Rotate operation now preserves EXIF metadata (previously it was silently stripped).

### Changed
- Config file is only rewritten when missing keys are detected (previously rewritten on every launch).
- Default config values are defined in a single place (`DEFAULT_CONFIG` dict) to avoid duplication.
- JPEG quality parameters (initial, floor, step) are now named constants.
- Dependencies in `requirements.txt` are now pinned to compatible version ranges.
- Improved `.gitignore` with comprehensive patterns for Python, IDE, and OS files.

### Added
- Module docstring and function docstrings throughout `pic_resizer.py`.
- Type hints on all functions.
- `if __name__ == "__main__"` guard so the module can be imported without launching the GUI.
- `CONTRIBUTING.md` with contribution guidelines.
- `CHANGELOG.md` (this file).
- `BUILDING.md` with PyInstaller build instructions (replaces `convert_to_exe.txt`).
- `pyproject.toml` with project metadata and ruff linter configuration.
