"""Tests for climate data cleaning."""

from __future__ import annotations

import pandas as pd
import pytest

from src.cleaning import DataValidationError, SchemaError, clean_climate_data


def test_normalizes_regions_and_drops_invalid_rows(climate_frame: pd.DataFrame) -> None:
    """Known region spelling variants normalize; invalid observations are reported."""
    climate_frame.loc[0, "Region"] = "North-Africa"
    climate_frame["Temperature_Anomaly"] = climate_frame["Temperature_Anomaly"].astype(
        object
    )
    climate_frame.loc[1, "Temperature_Anomaly"] = "not-a-number"
    cleaned, report = clean_climate_data(climate_frame)
    assert cleaned["region"].unique().tolist() == ["North_Africa"]
    assert report.invalid_rows_dropped == 1
    assert len(cleaned) == 3


def test_drops_exact_duplicates(climate_frame: pd.DataFrame) -> None:
    """An identical duplicate key is dropped and counted."""
    frame = pd.concat([climate_frame, climate_frame.iloc[[0]]], ignore_index=True)
    cleaned, report = clean_climate_data(frame)
    assert len(cleaned) == 4
    assert report.exact_duplicates_dropped == 1


def test_rejects_conflicting_duplicates(climate_frame: pd.DataFrame) -> None:
    """Conflicting records for the same month are rejected."""
    duplicate = climate_frame.iloc[[0]].copy()
    duplicate.loc[:, "Temperature_Anomaly"] = 9.0
    with pytest.raises(DataValidationError, match="Conflicting observations"):
        clean_climate_data(pd.concat([climate_frame, duplicate], ignore_index=True))


def test_rejects_unknown_region(climate_frame: pd.DataFrame) -> None:
    """Unrecognized region names are not silently discarded."""
    climate_frame.loc[0, "Region"] = "Unknown"
    with pytest.raises(DataValidationError, match="Unknown"):
        clean_climate_data(climate_frame)


def test_rejects_missing_schema_column(climate_frame: pd.DataFrame) -> None:
    """Missing required source columns produce a clear schema error."""
    with pytest.raises(SchemaError, match="Precipitation_mm"):
        clean_climate_data(climate_frame.drop(columns=["Precipitation_mm"]))
