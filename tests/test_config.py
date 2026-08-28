"""Tests for config.py — configuration loading and merging."""
import json
import os
import pytest
from unittest.mock import mock_open, patch

import config


class TestLoadConfig:
    def test_returns_default_config_when_no_file(self, monkeypatch, tmp_path):
        db_path = str(tmp_path / "nonexistent.json")
        monkeypatch.setattr(config, "CONFIG_FILE", db_path)
        monkeypatch.delenv("TON_CONTRACTS", raising=False)
        monkeypatch.delenv("TG_CHANNELS", raising=False)
        
        result = config.load_config()
        
        assert "ton_contracts" in result
        assert "tg_channels" in result
        assert result["trend_score_cap"] == 200

    def test_loads_from_file(self, monkeypatch, tmp_path):
        config_file = tmp_path / "config.json"
        test_cfg = {
            "ton_contracts": {"TestApp": "EQTest123"},
            "tg_channels": {"TestApp": "test_channel"},
            "trend_score_cap": 150,
        }
        config_file.write_text(json.dumps(test_cfg))
        monkeypatch.setattr(config, "CONFIG_FILE", str(config_file))
        monkeypatch.delenv("TON_CONTRACTS", raising=False)
        monkeypatch.delenv("TG_CHANNELS", raising=False)
        
        result = config.load_config()
        
        assert result["ton_contracts"]["TestApp"] == "EQTest123"
        assert result["trend_score_cap"] == 150

    def test_file_overrides_default(self, monkeypatch, tmp_path):
        config_file = tmp_path / "config.json"
        test_cfg = {"top_apps": ["CustomApp"]}
        config_file.write_text(json.dumps(test_cfg))
        monkeypatch.setattr(config, "CONFIG_FILE", str(config_file))
        monkeypatch.delenv("TON_CONTRACTS", raising=False)
        monkeypatch.delenv("TG_CHANNELS", raising=False)
        
        result = config.load_config()
        
        assert result["top_apps"] == ["CustomApp"]
        assert result["ton_contracts"] == config._DEFAULT_CONFIG["ton_contracts"]

    def test_invalid_json_uses_default(self, monkeypatch, tmp_path, caplog):
        config_file = tmp_path / "config.json"
        config_file.write_text("{invalid json")
        monkeypatch.setattr(config, "CONFIG_FILE", str(config_file))
        monkeypatch.delenv("TON_CONTRACTS", raising=False)
        monkeypatch.delenv("TG_CHANNELS", raising=False)
        
        result = config.load_config()
        
        assert result == config._DEFAULT_CONFIG
        assert "Ошибка чтения config.json" in caplog.text

    def test_missing_file_uses_default(self, monkeypatch, tmp_path):
        config_file = str(tmp_path / "missing.json")
        monkeypatch.setattr(config, "CONFIG_FILE", config_file)
        monkeypatch.delenv("TON_CONTRACTS", raising=False)
        monkeypatch.delenv("TG_CHANNELS", raising=False)
        
        result = config.load_config()
        
        assert result == config._DEFAULT_CONFIG


class TestLoadConfigFromEnv:
    def test_loads_contracts_from_env(self, monkeypatch):
        env_cfg = {"TestApp": "EQTest456"}
        monkeypatch.setenv("TON_CONTRACTS", json.dumps(env_cfg))
        monkeypatch.delenv("TG_CHANNELS", raising=False)
        
        result = config.load_config()
        
        assert result["ton_contracts"]["TestApp"] == "EQTest456"

    def test_loads_channels_from_env(self, monkeypatch):
        env_cfg = {"TestApp": "testenv"}
        monkeypatch.setenv("TG_CHANNELS", json.dumps(env_cfg))
        monkeypatch.delenv("TON_CONTRACTS", raising=False)
        
        result = config.load_config()
        
        assert result["tg_channels"]["TestApp"] == "testenv"

    def test_invalid_env_contracts_logs_warning(self, monkeypatch, caplog):
        monkeypatch.setenv("TON_CONTRACTS", "{invalid}")
        monkeypatch.delenv("TG_CHANNELS", raising=False)
        
        result = config.load_config()
        
        assert "Неверный формат TON_CONTRACTS" in caplog.text
        assert result["ton_contracts"] == config._DEFAULT_CONFIG["ton_contracts"]

    def test_invalid_env_channels_logs_warning(self, monkeypatch, caplog):
        monkeypatch.setenv("TG_CHANNELS", "{invalid}")
        monkeypatch.delenv("TON_CONTRACTS", raising=False)
        
        result = config.load_config()
        
        assert "Неверный формат TG_CHANNELS" in caplog.text
        assert result["tg_channels"] == config._DEFAULT_CONFIG["tg_channels"]


class TestDefaultConfig:
    def test_has_required_keys(self):
        cfg = config._DEFAULT_CONFIG
        
        assert "ton_contracts" in cfg
        assert "tg_channels" in cfg
        assert "app_categories" in cfg
        assert "top_apps" in cfg
        assert "trend_score_cap" in cfg

    def test_ton_contracts_format(self):
        contracts = config._DEFAULT_CONFIG["ton_contracts"]
        
        for app_name, address in contracts.items():
            assert address.startswith("EQ")

    def test_tg_channels_populated(self):
        channels = config._DEFAULT_CONFIG["tg_channels"]
        
        assert len(channels) > 0
        for app_name, handle in channels.items():
            assert isinstance(handle, str)
            assert len(handle) > 0

    def test_app_categories_populated(self):
        categories = config._DEFAULT_CONFIG["app_categories"]
        
        assert "Gaming" in categories
        assert "DeFi" in categories

    def test_top_apps_not_empty(self):
        top_apps = config._DEFAULT_CONFIG["top_apps"]
        
        assert len(top_apps) > 0

    def test_trend_score_cap_is_positive(self):
        cap = config._DEFAULT_CONFIG["trend_score_cap"]
        
        assert cap > 0


class TestModuleLevelConfig:
    def test_config_loaded_at_import(self):
        assert config.CONFIG is not None
        assert isinstance(config.CONFIG, dict)

    def test_config_has_all_sections(self):
        assert "ton_contracts" in config.CONFIG
        assert "tg_channels" in config.CONFIG
        assert "app_categories" in config.CONFIG
        assert "top_apps" in config.CONFIG