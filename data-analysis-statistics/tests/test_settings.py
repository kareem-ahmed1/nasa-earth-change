"""Tests for environment-backed configuration."""

from __future__ import annotations

from pathlib import Path

import pytest

from config.settings import Settings


def test_settings_read_paths_and_cors_origins(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings expose configured data paths and split CORS origins."""
    monkeypatch.setenv("CLIMATE_DATA_FILE", "data\\custom.csv")
    monkeypatch.setenv("CORS_ORIGINS", "https://one.example, https://two.example ")
    settings = Settings.from_env()
    assert settings.climate_data_file == Path("data\\custom.csv")
    assert settings.cors_origins == ("https://one.example", "https://two.example")
