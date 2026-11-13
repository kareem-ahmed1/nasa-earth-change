"""Tests for region and year filters."""

from __future__ import annotations

import pandas as pd
import pytest

from src.cleaning import clean_climate_data
from src.filters import FilterError, filter_data


def test_filters_region_and_inclusive_years(climate_frame: pd.DataFrame) -> None:
    """Filters include both requested boundary years."""
    data, _ = clean_climate_data(climate_frame)
    selected = filter_data(data, "North_Africa", 2004, 2004)
    assert len(selected) == 2
    assert selected["year"].eq(2004).all()


def test_rejects_reversed_and_out_of_range_years(climate_frame: pd.DataFrame) -> None:
    """Invalid ranges are rejected instead of returning accidental results."""
    data, _ = clean_climate_data(climate_frame)
    with pytest.raises(FilterError, match="less than or equal"):
        filter_data(data, "all", 2005, 2004)
    with pytest.raises(FilterError, match="available range"):
        filter_data(data, "all", 2003, 2004)


def test_valid_range_can_have_no_rows(climate_frame: pd.DataFrame) -> None:
    """A valid but absent region/year combination returns an empty frame."""
    data, _ = clean_climate_data(climate_frame)
    selected = filter_data(data, "South_Africa", 2004, 2005)
    assert selected.empty


def test_rejects_unknown_region(climate_frame: pd.DataFrame) -> None:
    """Region selection is limited to the supported five regions."""
    data, _ = clean_climate_data(climate_frame)
    with pytest.raises(FilterError, match="Unknown region"):
        filter_data(data, "West_Africa")
