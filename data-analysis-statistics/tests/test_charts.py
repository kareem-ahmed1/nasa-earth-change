"""Tests for frontend chart data generation."""

from __future__ import annotations

import pandas as pd

from src.charts import build_chart_data
from src.cleaning import clean_climate_data


def test_chart_data_has_all_requested_series(climate_frame: pd.DataFrame) -> None:
    """Chart output includes monthly, regression, residual, trend, and comparison data."""
    data, report = clean_climate_data(climate_frame)
    assert report.output_rows == 4
    charts = build_chart_data(data, data)
    assert len(charts["time_series"]) == 4
    assert len(charts["scatter"]) == 4
    assert len(charts["regression_line"]) == 2
    assert len(charts["residuals"]) == 4
    assert set(charts["trends"]) == {"temperature_anomaly", "precipitation_mm"}
    assert len(charts["yearly_averages_per_region"]) == 2
