"""Tests for Mann-Kendall and Sen's slope."""

from __future__ import annotations

import numpy as np
from scipy import stats

from src.statistics.trend import mann_kendall_sen


def test_mann_kendall_matches_scipy_and_sen_slope() -> None:
    """Kendall p-value agrees with SciPy and Sen slope uses year spacing."""
    years = np.array([2000, 2001, 2003, 2004, 2007], dtype=float)
    values = np.array([1.0, 2.0, 2.5, 4.0, 6.0])
    result = mann_kendall_sen(years, values)
    expected = stats.kendalltau(years, values)
    slopes = [
        (values[j] - values[i]) / (years[j] - years[i])
        for i in range(4)
        for j in range(i + 1, 5)
    ]
    assert result.p_value == expected.pvalue
    assert result.sens_slope_per_year == float(np.median(slopes))
    assert result.direction == "increasing"


def test_single_year_and_constant_series() -> None:
    """Insufficient and constant series have explicit, finite outputs."""
    assert mann_kendall_sen([2004], [1]).direction == "insufficient_data"
    constant = mann_kendall_sen([2000, 2001, 2002, 2003], [5, 5, 5, 5])
    assert constant.sens_slope_per_year == 0.0
    assert constant.p_value == 1.0
    assert (
        mann_kendall_sen([2000, 2001, 2002], [np.nan, np.nan, np.nan]).sample_size == 0
    )


def test_rejects_duplicate_years() -> None:
    """Trend points must have unique time coordinates."""
    try:
        mann_kendall_sen([2000, 2000, 2001], [1, 2, 3])
    except ValueError as error:
        assert "unique year" in str(error)
    else:
        raise AssertionError("Expected duplicate years to be rejected.")
