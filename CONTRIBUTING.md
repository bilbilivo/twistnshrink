# Contributing to TwistnShrink

Thanks for your interest in contributing! Here's how to get started.

## Getting Started

1. Fork the repository and clone your fork:

   ```bash
   git clone https://github.com/<your-username>/twistnshrink.git
   cd twistnshrink
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   pip install ".[dev]"

   # Windows
   python -m venv venv
   venv\Scripts\activate
   pip install ".[dev]"
   ```

3. Make sure `python3-tk` is installed on your system (see [README.md](README.md#installation)).

4. Run the app to verify your setup:

   ```bash
   python twistnshrink.py
   ```

## Making Changes

1. Create a feature branch from `main`:

   ```bash
   git checkout -b my-feature
   ```

2. Make your changes. Keep commits focused and write clear commit messages.

3. Run the linter and tests before pushing:

   ```bash
   ruff check .
   pytest -v
   ```

4. Test your changes manually with a variety of JPEG images (with and without EXIF data, different orientations, different sizes).

5. Push your branch and open a pull request.

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions.
- Run `ruff check .` to lint your code (configuration is in `pyproject.toml`).
- Add type hints to all function signatures.
- Add docstrings to all public functions.
- Keep the codebase compatible with Python 3.9+.

## Testing

- Add tests for new logic in the `tests/` directory.
- Tests use [pytest](https://docs.pytest.org/) -- run with `pytest -v`.
- CI runs the test suite on Python 3.9, 3.10, 3.11, and 3.12.

## Release Workflow & Tagging Expectations

Before creating a release (by pushing a tag such as `v2026.2` or a release branch):

1. Push changes to `main` first.
2. Wait for all CI workflows to complete and ensure they pass (see Actions tab in GitHub).
3. Only then, create and push a release tag (e.g., `git tag v2026.2 && git push origin v2026.2`).

> **Why?**
> This ensures releases are only created from a healthy, passing main branch, prevents accidental deployment of broken code, and makes releases easier to audit and roll back.

If CI fails on `main`, do not tag or deploy—fix issues and re-verify first.

## Reporting Issues

- Use [GitHub Issues](https://github.com/bilbilivo/twistnshrink/issues) to report bugs or request features.
- Include your OS, Python version, and steps to reproduce.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
