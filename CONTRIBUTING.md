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

3. Make sure `python3-tk` is installed on your system (see [README.md](README.md#quick-start)).

4. Run the app to verify your setup:

   ```bash
   python twistnshrink.py
   ```

## Making Changes

Contributions follow a branch → pull request → merge after CI passes. Do not commit directly to `main`.

1. Start from an up-to-date `main` branch and create a focused feature or fix branch:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/my-feature
   ```

2. Make your changes and keep commits focused. Use [Conventional Commits](https://www.conventionalcommits.org/) for every commit, for example:

   ```text
   feat: add batch image compression
   fix: preserve EXIF orientation metadata
   docs: clarify installation instructions
   ```

3. Run the linter and tests before pushing:

   ```bash
   ruff check .
   pytest -v
   ```

4. Test your changes manually with a variety of JPEG images (with and without EXIF data, different orientations, different sizes).

5. Push the branch and open a pull request (PR) against `main`:

   ```bash
   git push -u origin feature/my-feature
   ```

6. Ensure all required CI checks pass. Address review feedback and keep the branch current with `main` if requested.

7. Merge after the required `CI Gate` check passes, the branch is up to date with `main`, and all review conversations are resolved. The sole maintainer may merge their own PR without approval from another person. Request a review when another maintainer is available; approval is optional under the current branch protection rules.

## Documentation-Only Contributions

Documentation changes follow the same branch, PR, CI, and merge process as code changes. Use a `docs:` Conventional Commit and a descriptive branch name, for example:

```bash
git checkout main
git pull origin main
git checkout -b docs/improve-contributing-guide
git add CONTRIBUTING.md
git commit -m "docs: clarify documentation contribution workflow"
git push -u origin docs/improve-contributing-guide
```

Mark the PR as documentation-only and describe the files changed. Documentation-only changes do not normally require a release tag unless they are intentionally included in a release.

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

Releases are created only from a merged PR on `main` after required CI checks pass. After the merge:

1. Wait for CI on the merge commit to complete successfully (see the GitHub Actions tab).
2. Create and push the version tag from that passing `main` commit:

   ```bash
   git checkout main
   git pull origin main
   git tag v2026.2
   git push origin v2026.2
   ```

3. The release workflow creates the corresponding GitHub Release with generated release notes and the Windows executable attached.

> **Why?**
> This ensures releases are only created from code that passed CI on `main`; it also makes releases easier to audit and roll back.

If CI fails on `main`, do not tag or deploy—fix issues and re-verify first.

## Reporting Issues

- Use [GitHub Issues](https://github.com/bilbilivo/twistnshrink/issues) to report bugs or request features.
- Include your OS, Python version, and steps to reproduce.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
