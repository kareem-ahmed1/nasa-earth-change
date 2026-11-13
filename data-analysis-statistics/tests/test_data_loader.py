"""Tests for CSV loading."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import load_climate_data


def test_loads_configured_csv(tmp_path: Path) -> None:
    """Loader parses the source CSV through the shared cleaner."""
    csv_path = tmp_path / "climate.csv"
    pd.DataFrame(
        {
            "Region": ["Sahel_Region"],
            "Year": [2004],
            "Month": [1],
            "Temperature_Anomaly": [0.5],
            "Precipitation_mm": [3.0],
            "Date": ["2004-01"],
        }
    ).to_csv(csv_path, index=False)
    data, report = load_climate_data(csv_path)
    assert data.loc[0, "temperature_anomaly"] == 0.5
    assert report.output_rows == 1


def test_missing_file_is_explicit(tmp_path: Path) -> None:
    """A missing file reports its configured path."""
    with pytest.raises(FileNotFoundError, match="missing.csv"):
        load_climate_data(tmp_path / "missing.csv")
