"""Tests for API response contracts and validation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from config.settings import Settings
from src.api.main import create_app


def test_api_endpoints_use_cleaned_data(tmp_path: Path) -> None:
    """Regions, data, analysis, and charts expose stable response shapes."""
    csv_path = tmp_path / "climate.csv"
    rows = []
    for year in range(2000, 2005):
        for month in range(1, 13):
            rows.append(
                {
                    "Region": "North_Africa",
                    "Year": year,
                    "Month": month,
                    "Temperature_Anomaly": float(year - 1999 + month / 12),
                    "Precipitation_mm": float(month),
                    "Date": f"{year}-{month:02d}",
                }
            )
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    app = create_app(Settings(csv_path, ("http://localhost:3000",)))
    with TestClient(app) as client:
        regions = client.get("/regions")
        assert regions.status_code == 200
        assert regions.json()["available_years"] == {
            "start_year": 2000,
            "end_year": 2004,
        }

        data = client.get(
            "/data",
            params={"region": "North_Africa", "start_year": 2001, "end_year": 2002},
        )
        assert data.status_code == 200
        assert data.json()["sample_size"] == 24
        assert "temperature_anomaly" in data.json()["observations"][0]

        analysis = client.get("/analysis", params={"region": "North_Africa"})
        assert analysis.status_code == 200
        assert analysis.json()["regression"]["predictor"] == "precipitation_mm"
        assert set(analysis.json()["trends"]) == {
            "temperature_anomaly",
            "precipitation_mm",
        }

        charts = client.get("/charts", params={"region": "all"})
        assert charts.status_code == 200
        assert len(charts.json()["time_series"]) == 60
        assert "yearly_averages_per_region" in charts.json()


def test_api_invalid_range_and_no_data(tmp_path: Path) -> None:
    """Invalid input is 400 and a valid empty region selection is 404."""
    csv_path = tmp_path / "climate.csv"
    pd.DataFrame(
        {
            "Region": ["North_Africa"] * 3,
            "Year": [2000, 2001, 2002],
            "Month": [1, 1, 1],
            "Temperature_Anomaly": [1.0, 2.0, 3.0],
            "Precipitation_mm": [2.0, 3.0, 4.0],
            "Date": ["2000-01", "2001-01", "2002-01"],
        }
    ).to_csv(csv_path, index=False)
    with TestClient(create_app(Settings(csv_path, ()))) as client:
        assert (
            client.get(
                "/data", params={"start_year": 2002, "end_year": 2000}
            ).status_code
            == 400
        )
        assert client.get("/data", params={"region": "Antarctica"}).status_code == 400
        assert client.get("/data", params={"region": "Southern_Africa"}).status_code == 404
