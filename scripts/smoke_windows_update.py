"""Exercise replacement of an actual running PyInstaller Windows executable."""

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def main() -> None:
    """Keep the old executable locked, then verify helper replacement/restart."""
    executable = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix="twistnshrink smoke ") as directory:
        staging = Path(directory)
        target = staging / "smoke-target.exe"
        helper = staging / "helper.exe"
        download = staging / "download.exe"
        for path in (target, helper, download):
            shutil.copy2(executable, path)
        digest = hashlib.sha256(download.read_bytes()).hexdigest()
        environment = {**os.environ, "PYINSTALLER_RESET_ENVIRONMENT": "1"}
        old = subprocess.Popen([str(target)], env=environment)
        worker = None
        try:
            time.sleep(5)
            assert old.poll() is None, "Packaged app failed to start"
            worker = subprocess.Popen([str(helper), "--apply-update", str(target),
                                       str(download), digest, str(old.pid)], env=environment)
            time.sleep(5)
            assert worker.poll() is None, "Helper did not wait for the running app"
            assert not target.with_suffix(".exe.bak").exists()
            subprocess.run(["taskkill", "/PID", str(old.pid), "/T", "/F"], check=True)
            assert worker.wait(timeout=120) == 0, "Helper failed"
            assert target.with_suffix(".exe.bak").is_file(), "Backup missing"
            assert hashlib.sha256(target.read_bytes()).hexdigest() == digest
            time.sleep(5)
            running = subprocess.run(["tasklist", "/FI", "IMAGENAME eq smoke-target.exe"],
                                     capture_output=True, text=True, check=True)
            assert "smoke-target.exe" in running.stdout, "Updated app did not restart"
        finally:
            subprocess.run(["taskkill", "/IM", "smoke-target.exe", "/T", "/F"],
                           capture_output=True)
            if worker is not None and worker.poll() is None:
                subprocess.run(["taskkill", "/PID", str(worker.pid), "/T", "/F"],
                               capture_output=True)
            old.wait(timeout=30)
            time.sleep(3)
    print("Packaged Windows update, backup and restart verified")


if __name__ == "__main__":
    main()
