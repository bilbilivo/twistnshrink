# Contributing to Pic Resizer

Thanks for your interest in contributing! Here's how to get started.

## Getting Started

1. Fork the repository and clone your fork:

   ```bash
   git clone https://github.com/<your-username>/pic_resizer.git
   cd pic_resizer
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/macOS
   pip install -r requirements.txt
   ```

3. Make sure `python3-tk` is installed on your system (see [README.md](README.md#installation)).

4. Run the app to verify your setup:

   ```bash
   python pic_resizer.py
   ```

## Making Changes

1. Create a feature branch from `main`:

   ```bash
   git checkout -b my-feature
   ```

2. Make your changes. Keep commits focused and write clear commit messages.

3. Test your changes manually with a variety of JPEG images (with and without EXIF data, different orientations, different sizes).

4. Push your branch and open a pull request.

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions.
- Add type hints to all function signatures.
- Add docstrings to all public functions.
- Keep the codebase compatible with Python 3.7+.

## Reporting Issues

- Use [GitHub Issues](https://github.com/bilbilivo/pic_resizer/issues) to report bugs or request features.
- Include your OS, Python version, and steps to reproduce.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
