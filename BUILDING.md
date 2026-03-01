# Building a Windows Executable

Use [PyInstaller](https://pyinstaller.org/) to bundle the application into a standalone `.exe`.

> **Note:** Releases are built automatically by GitHub Actions when you push a version tag (e.g., `v2026.1`). The `.exe` is attached to the [GitHub Release](https://github.com/bilbilivo/twistnshrink/releases). Manual builds are only needed for local testing.

## Prerequisites

Install PyInstaller and the project dependencies:

```bash
pip install ".[build]"
```

## Build

Navigate to the project directory and run:

```bash
pyinstaller --onefile --noconsole twistnshrink.py
```

| Flag | Purpose |
|---|---|
| `--onefile` | Packages everything into a single `.exe` |
| `--noconsole` | Hides the console window (appropriate for a GUI app) |

### With a custom icon

```bash
pyinstaller --onefile --noconsole --icon=twistnshrink.ico twistnshrink.py
```

A pre-made `.spec` file is also included in the repository for reproducible builds:

```bash
pyinstaller twistnshrink.spec
```

## Output

The executable will be created at `dist/twistnshrink.exe`. Copy `twistnshrink.ini` into the same directory if you want to ship default settings alongside it.

## Automated Builds (CI)

**Important release workflow best practice:**

> Before pushing a version tag to trigger a release build, always push to `main`, wait for all CI checks to pass (see GitHub Actions), and only then create and push the version tag. This ensures the release is created from a fully tested, healthy main branch.

When you push a git tag matching `v*` (e.g., `v2026.1`), the [release workflow](.github/workflows/release.yml) will:

1. Run lint and test checks.
2. Build the Windows `.exe` on a Windows runner.
3. Create a GitHub Release with the `.exe` attached.

To create a release (ensure the tag version matches the push command and only do this after CI passes on main):

```bash
git tag v2026.2
git push origin v2026.2
```

## Troubleshooting

- **Missing dependencies** -- Ensure all dependencies (Pillow, piexif) are installed in the environment used to build.
- **Hidden imports** -- If the `.exe` fails at runtime, PyInstaller may have missed a module. Use `--hidden-import`:

  ```bash
  pyinstaller --onefile --noconsole --hidden-import=tkinter twistnshrink.py
  ```
