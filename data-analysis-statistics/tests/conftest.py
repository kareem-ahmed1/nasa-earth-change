"""Shared climate test fixtures."""

from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def climate_frame() -> pd.DataFrame:
    """Return a small, well-formed monthly fixture."""
    return pd.DataFrame(
        {
            "Region": ["north africa"] * 4,
            "Year": [2004, 2004, 2005, 2005],
            "Month": [1, 2, 1, 2],
            "Temperature_Anomaly": [1.0, 2.0, 3.0, 4.0],
            "Precipitation_mm": [2.0, 1.0, 4.0, 3.0],
            "Date": ["2004-01", "2004-02", "2005-01", "2005-02"],
        }
    )
