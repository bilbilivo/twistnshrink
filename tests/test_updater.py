"""Update metadata, download integrity and rollback regression tests."""

import hashlib
import io
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

import updater

DIGEST = hashlib.sha256(b"new app").hexdigest()


def metadata():
    """A stable GitHub release with its expected Windows asset."""
    return {"tag_name": "v2026.10", "draft": False, "prerelease": False,
            "assets": [{"name": "twistnshrink.exe", "size": 7,
                        "browser_download_url": "https://github.com/bilbilivo/twistnshrink/releases/download/v2026.10/twistnshrink.exe",
                        "digest": f"sha256:{DIGEST}"}]}


def test_numeric_version_comparison(monkeypatch):
    monkeypatch.setattr(updater, "urlopen", lambda *a, **kw: io.BytesIO(json.dumps(metadata()).encode()))
    assert updater.latest_release("2026.9")["version"] == "v2026.10"
    assert updater.latest_release("2026.10") is None
    assert updater.latest_release("2026.11") is None


@pytest.mark.parametrize("change", ["prerelease", "draft", "url", "digest", "missing"])
def test_reject_untrusted_or_incomplete_release(monkeypatch, change):
    data = metadata()
    if change in ("prerelease", "draft"):
        data[change] = True
    elif change == "url":
        data["assets"][0]["browser_download_url"] = "https://example.com/bad.exe"
    elif change == "digest":
        data["assets"][0]["digest"] = None
    else:
        data["assets"] = []
    monkeypatch.setattr(updater, "urlopen", lambda *a, **kw: io.BytesIO(json.dumps(data).encode()))
    if change in ("prerelease", "draft"):
        assert updater.latest_release("2026.9") is None
    else:
        with pytest.raises(ValueError):
            updater.latest_release("2026.9")


@pytest.mark.parametrize("payload", [b"new app", b"bad app", b"short", b"too long"])
def test_download_verifies_size_and_digest(tmp_path, monkeypatch, payload):
    monkeypatch.setattr(updater, "urlopen", lambda *a, **kw: io.BytesIO(payload))
    release = {"url": "https://example.com/app", "sha256": DIGEST, "size": 7}
    if payload == b"new app":
        assert updater.download_release(release, tmp_path).read_bytes() == payload
    else:
        with pytest.raises(ValueError):
            updater.download_release(release, tmp_path)
        assert not (tmp_path / "download.exe").exists()


def test_replacement_keeps_backup_and_restarts(tmp_path, monkeypatch):
    target, download = tmp_path / "app.exe", tmp_path / "download.exe"
    target.write_bytes(b"old app")
    download.write_bytes(b"new app")
    launch = Mock()
    monkeypatch.setattr(updater.subprocess, "Popen", launch)
    updater.replace_executable(target, download, DIGEST)
    assert target.read_bytes() == b"new app"
    assert target.with_suffix(".exe.bak").read_bytes() == b"old app"
    assert launch.call_args.kwargs["env"]["PYINSTALLER_RESET_ENVIRONMENT"] == "1"


def test_failed_restart_restores_previous_app(tmp_path, monkeypatch):
    target, download = tmp_path / "app.exe", tmp_path / "download.exe"
    target.write_bytes(b"old app")
    download.write_bytes(b"new app")
    launch = Mock(side_effect=[OSError("cannot launch"), Mock()])
    monkeypatch.setattr(updater.subprocess, "Popen", launch)
    with pytest.raises(OSError):
        updater.replace_executable(target, download, DIGEST)
    assert target.read_bytes() == b"old app"
    assert launch.call_count == 2


def test_bad_digest_leaves_original_untouched(tmp_path):
    target, download = tmp_path / "app.exe", tmp_path / "download.exe"
    target.write_bytes(b"old app")
    download.write_bytes(b"corrupt")
    with pytest.raises(ValueError):
        updater.replace_executable(target, download, DIGEST)
    assert target.read_bytes() == b"old app"
    assert not target.with_suffix(".exe.bak").exists()


def test_waits_for_windows_file_lock(tmp_path, monkeypatch):
    target, download = tmp_path / "app.exe", tmp_path / "download.exe"
    target.write_bytes(b"old app")
    download.write_bytes(b"new app")
    original = Path.replace
    attempts = []

    def locked_once(path, destination):
        if path == target and not attempts:
            attempts.append(True)
            raise PermissionError("locked")
        return original(path, destination)

    monkeypatch.setattr(Path, "replace", locked_once)
    monkeypatch.setattr(updater.time, "sleep", Mock())
    monkeypatch.setattr(updater.subprocess, "Popen", Mock())
    updater.replace_executable(target, download, DIGEST)
    assert attempts and target.read_bytes() == b"new app"


def test_update_prompt_waits_for_processing(monkeypatch):
    import queue

    import twistnshrink as app

    events = queue.Queue()
    events.put(("checked", ({"version": "v2026.10"}, True)))
    root = Mock()
    monkeypatch.setattr(app, "UPDATE_EVENTS", events)
    monkeypatch.setattr(app, "PROCESSING", 1)
    monkeypatch.setattr(app, "root", root, raising=False)
    app.poll_updates()
    assert events.qsize() == 1
    root.after.assert_called_once_with(500, app.poll_updates)


def test_timed_out_lock_keeps_previous_app(tmp_path, monkeypatch):
    target, download = tmp_path / "app.exe", tmp_path / "download.exe"
    target.write_bytes(b"old app")
    download.write_bytes(b"new app")
    monkeypatch.setattr(Path, "replace", Mock(side_effect=PermissionError("locked")))
    monkeypatch.setattr(updater.time, "monotonic", Mock(side_effect=[0, 91]))
    with pytest.raises(TimeoutError):
        updater.replace_executable(target, download, DIGEST)
    assert target.read_bytes() == b"old app"
    assert not target.with_suffix(".exe.new").exists()
