# Building a Windows Executable

Use [PyInstaller](https://pyinstaller.org/) to bundle the application into a standalone `.exe`.

## Prerequisites

Install PyInstaller and the project dependencies:

```bash
pip install pyinstaller
pip install -r requirements.txt
```

## Build

Navigate to the project directory and run:

```bash
pyinstaller --onefile --noconsole pic_resizer.py
```

| Flag | Purpose |
|---|---|
| `--onefile` | Packages everything into a single `.exe` |
| `--noconsole` | Hides the console window (appropriate for a GUI app) |

### With a custom icon

```bash
pyinstaller --onefile --noconsole --icon=pic_resizer.ico pic_resizer.py
```

A pre-made `.spec` file is also included in the repository for reproducible builds:

```bash
pyinstaller pic_resizer.spec
```

## Output

The executable will be created at `dist/pic_resizer.exe`. Copy `pic_resizer.ini` into the same directory if you want to ship default settings alongside it.

## Troubleshooting

- **Missing dependencies** -- Ensure all dependencies (Pillow, piexif) are installed in the environment used to build.
- **Hidden imports** -- If the `.exe` fails at runtime, PyInstaller may have missed a module. Use `--hidden-import`:

  ```bash
  pyinstaller --onefile --noconsole --hidden-import=tkinter pic_resizer.py
  ```
