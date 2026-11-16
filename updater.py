"""GitHub release updates for the portable Windows application."""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import Request, urlopen

REPOSITORY = "bilbilivo/twistnshrink"
API_URL = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
MAX_DOWNLOAD = 150 * 1024 * 1024


def version_tuple(value: str) -> tuple[int, int]:
    """Parse calendar versions numerically, rejecting unsupported tags."""
    match = re.fullmatch(r"v?(\d{4})\.(\d+)", value)
    if not match:
        raise ValueError("Unsupported release version")
    return tuple(map(int, match.groups()))


def latest_release(current: str) -> dict | None:
    """Find a newer stable release with an executable and SHA-256 digest."""
    request = Request(API_URL, headers={
        "Accept": "application/vnd.github+json", "User-Agent": f"TwistnShrink/{current}",
    })
    with urlopen(request, timeout=15) as response:
        release = json.loads(response.read(1024 * 1024))
    if release.get("draft") or release.get("prerelease"):
        return None
    if version_tuple(release["tag_name"]) <= version_tuple(current):
        return None
    expected_url = (f"https://github.com/{REPOSITORY}/releases/download/"
                    f"{release['tag_name']}/twistnshrink.exe")
    for asset in release.get("assets", []):
        digest = asset.get("digest", "") or ""
        if (asset.get("name") == "twistnshrink.exe"
                and asset.get("browser_download_url") == expected_url
                and re.fullmatch(r"sha256:[0-9a-f]{64}", digest)
                and 0 < asset.get("size", 0) <= MAX_DOWNLOAD):
            return {"version": release["tag_name"], "url": expected_url,
                    "sha256": digest.removeprefix("sha256:"), "size": asset["size"]}
    raise ValueError("This release has no verified Windows executable")


def verify_file(path: Path, digest: str) -> None:
    """Reject incomplete or altered executable downloads."""
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("Invalid SHA-256 digest")
    with path.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != digest:
        raise ValueError("Update verification failed; the current app was not changed")


def download_release(release: dict, directory: Path) -> Path:
    """Download into staging, with a size limit, then verify the digest."""
    destination = directory / "download.exe"
    request = Request(release["url"], headers={"User-Agent": "TwistnShrink"})
    try:
        total = 0
        with urlopen(request, timeout=30) as response, destination.open("wb") as output:
            while chunk := response.read(128 * 1024):
                total += len(chunk)
                if total > MAX_DOWNLOAD or total > release["size"]:
                    raise ValueError("Update download exceeds the expected size")
                output.write(chunk)
        if total != release["size"]:
            raise ValueError("Incomplete update download")
        verify_file(destination, release["sha256"])
        return destination
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def start_update(release: dict, cache: Path) -> None:
    """Stage a verified update and start an independent copy as its helper."""
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        raise RuntimeError("In-app installation is available in the Windows executable")
    target = Path(sys.executable).resolve()
    if not os.access(target.parent, os.W_OK):
        raise PermissionError("Move the app to a writable folder before updating")
    cache.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="update-", dir=cache))
    try:
        download = download_release(release, staging)
        helper = staging / "helper.exe"
        shutil.copy2(target, helper)
        subprocess.Popen(
            [str(helper), "--apply-update", str(target), str(download), release["sha256"], str(os.getpid())],
            env={**os.environ, "PYINSTALLER_RESET_ENVIRONMENT": "1"},
            close_fds=True,
        )
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def replace_executable(target: Path, download: Path, digest: str) -> None:
    """Wait for Windows to unlock the old app, replace it, and restart."""
    verify_file(download, digest)
    backup = target.with_name(target.name + ".bak")
    # Stage on the destination filesystem before moving the original.
    candidate = target.with_name(target.name + ".new")
    shutil.copy2(download, candidate)
    verify_file(candidate, digest)
    deadline = time.monotonic() + 90
    while True:
        try:
            target.replace(backup)
            break
        except PermissionError:
            if time.monotonic() >= deadline:
                candidate.unlink(missing_ok=True)
                raise TimeoutError("The application is still open; close all copies and try again") from None
            time.sleep(0.5)
    try:
        candidate.replace(target)
        subprocess.Popen([str(target)], cwd=target.parent,
                         env={**os.environ, "PYINSTALLER_RESET_ENVIRONMENT": "1"})
    except Exception:
        backup.replace(target)
        subprocess.Popen([str(target)], cwd=target.parent,
                         env={**os.environ, "PYINSTALLER_RESET_ENVIRONMENT": "1"})
        raise


def wait_for_exit(pid: int) -> None:
    """Wait for the application process before attempting any replacement."""
    import ctypes
    from ctypes import wintypes

    if pid <= 0 or pid == os.getpid():
        raise ValueError("Invalid application process")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.OpenProcess(0x00100000, False, pid)
    if not handle:
        if ctypes.get_last_error() == 87:  # Process has already exited.
            return
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        result = kernel.WaitForSingleObject(handle, 90000)
        if result == 258:
            raise TimeoutError("The application did not exit; close it and try again")
        if result != 0:
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        kernel.CloseHandle(handle)


def apply_update(arguments: list[str]) -> int:
    """Run the update helper without creating the main application window."""
    try:
        if len(arguments) != 4 or sys.platform != "win32" or not getattr(sys, "frozen", False):
            raise ValueError("Invalid updater invocation")
        target, download = (Path(arg).resolve() for arg in arguments[:2])
        if target.suffix.lower() != ".exe" or target == Path(sys.executable).resolve():
            raise ValueError("Invalid update target")
        if download.parent != Path(sys.executable).resolve().parent:
            raise ValueError("Invalid staged download")
        verify_file(download, arguments[2])
        wait_for_exit(int(arguments[3]))
        replace_executable(target, download, arguments[2])
        return 0
    except Exception as error:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, f"Update failed: {error}\nYour previous app is retained.",
                                        "TwistnShrink Update", 0x10)
        return 1
