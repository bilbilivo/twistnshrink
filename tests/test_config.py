"""Unit tests for configuration loading in TwistnShrink."""

import configparser
import os

import twistnshrink


class TestLoadConfig:
    """Tests for load_config()."""

    def test_creates_config_when_missing(self, tmp_path, monkeypatch):
        """When no config file exists, one should be created with defaults."""
        config_path = str(tmp_path / "twistnshrink.ini")
        monkeypatch.setattr(twistnshrink, "CONFIG_FILE", config_path)

        config = twistnshrink.load_config()

        assert os.path.exists(config_path)
        assert isinstance(config, configparser.ConfigParser)

    def test_default_values_populated(self, tmp_path, monkeypatch):
        """Created config should contain all default values."""
        config_path = str(tmp_path / "twistnshrink.ini")
        monkeypatch.setattr(twistnshrink, "CONFIG_FILE", config_path)

        config = twistnshrink.load_config()

        for key, value in twistnshrink.DEFAULT_CONFIG.items():
            assert config["DEFAULT"][key] == value

    def test_fills_missing_keys(self, tmp_path, monkeypatch):
        """If config file exists but is missing keys, they should be filled in."""
        config_path = str(tmp_path / "twistnshrink.ini")
        monkeypatch.setattr(twistnshrink, "CONFIG_FILE", config_path)

        # Write a partial config
        partial = configparser.ConfigParser()
        partial["DEFAULT"] = {"MaxFrameSize": "1200"}
        with open(config_path, "w") as f:
            partial.write(f)

        config = twistnshrink.load_config()

        # Existing value preserved
        assert config["DEFAULT"]["MaxFrameSize"] == "1200"
        # Missing values filled in
        assert config["DEFAULT"]["TargetSizeKB"] == "200"
        assert config["DEFAULT"]["FileSuffix"] == "_resize"
        assert config["DEFAULT"]["RotateAngle"] == "90"

    def test_preserves_existing_values(self, tmp_path, monkeypatch):
        """Existing config values should not be overwritten."""
        config_path = str(tmp_path / "twistnshrink.ini")
        monkeypatch.setattr(twistnshrink, "CONFIG_FILE", config_path)

        # Write a complete config with custom values
        custom = configparser.ConfigParser()
        custom["DEFAULT"] = {
            "MaxFrameSize": "1500",
            "TargetSizeKB": "300",
            "FileSuffix": "_custom",
            "RotateAngle": "180",
        }
        with open(config_path, "w") as f:
            custom.write(f)

        config = twistnshrink.load_config()

        assert config["DEFAULT"]["MaxFrameSize"] == "1500"
        assert config["DEFAULT"]["TargetSizeKB"] == "300"
        assert config["DEFAULT"]["FileSuffix"] == "_custom"
        assert config["DEFAULT"]["RotateAngle"] == "180"

    def test_does_not_rewrite_when_complete(self, tmp_path, monkeypatch):
        """If all keys are present, the file should not be rewritten."""
        config_path = str(tmp_path / "twistnshrink.ini")
        monkeypatch.setattr(twistnshrink, "CONFIG_FILE", config_path)

        # Write a complete config
        complete = configparser.ConfigParser()
        complete["DEFAULT"] = dict(twistnshrink.DEFAULT_CONFIG)
        with open(config_path, "w") as f:
            complete.write(f)

        # Get the modification time
        mtime_before = os.path.getmtime(config_path)

        twistnshrink.load_config()

        # File should not have been rewritten
        mtime_after = os.path.getmtime(config_path)
        assert mtime_before == mtime_after

    def test_returns_configparser_instance(self, tmp_path, monkeypatch):
        """Return value should be a ConfigParser."""
        config_path = str(tmp_path / "twistnshrink.ini")
        monkeypatch.setattr(twistnshrink, "CONFIG_FILE", config_path)

        result = twistnshrink.load_config()
        assert isinstance(result, configparser.ConfigParser)
