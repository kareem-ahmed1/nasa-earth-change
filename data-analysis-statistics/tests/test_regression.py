"""Tests for simple linear regression."""

from __future__ import annotations

import numpy as np
from scipy import stats

from src.statistics.regression import linear_regression


def test_matches_scipy_linregress() -> None:
    """Model coefficients, fit, p-value, and standard error match SciPy."""
    x = np.array([1.0, 2.0, 4.0, 5.0, 8.0])
    y = np.array([2.0, 2.5, 5.1, 5.8, 8.7])
    result = linear_regression(x, y)
    expected = stats.linregress(x, y)
    assert result.slope == expected.slope
    assert result.intercept == expected.intercept
    assert result.r_squared == expected.rvalue**2
    assert result.standard_error == expected.stderr
    assert np.allclose(result.residuals, y - (expected.intercept + expected.slope * x))


def test_perfect_fit_and_degenerate_inputs() -> None:
    """Perfect fits have zero residuals; constant predictors are undefined."""
    perfect = linear_regression([1, 2, 3], [3, 5, 7])
    assert perfect.r_squared == 1.0
    assert np.allclose(perfect.residuals, 0.0)
    assert linear_regression([1, 1], [2, 3]).slope is None
    assert linear_regression([float("nan")], [1]).sample_size == 0
    assert linear_regression([1, 2], [float("nan"), float("nan")]).sample_size == 0
