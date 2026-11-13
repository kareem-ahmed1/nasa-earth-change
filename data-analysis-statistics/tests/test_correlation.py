"""Tests for Pearson correlation."""

from __future__ import annotations

import numpy as np
from scipy import stats

from src.statistics.correlation import pearson_correlation


def test_matches_scipy_and_returns_fisher_interval() -> None:
    """Correlation and p-value match SciPy on a known fixture."""
    x = np.array([1.0, 2.0, 3.0, 5.0, 7.0])
    y = np.array([2.0, 1.0, 4.0, 3.0, 8.0])
    result = pearson_correlation(x, y)
    expected = stats.pearsonr(x, y)
    assert result.coefficient == expected.statistic
    assert result.p_value == expected.pvalue
    assert result.sample_size == len(x)
    assert result.confidence_interval_95 is not None
    assert (
        result.confidence_interval_95[0]
        < result.coefficient
        < result.confidence_interval_95[1]
    )


def test_perfect_and_constant_series_edges() -> None:
    """Perfect correlation is handled and constant inputs yield undefined results."""
    perfect = pearson_correlation([1, 2, 3, 4], [2, 4, 6, 8])
    assert np.isclose(perfect.coefficient, 1.0)
    constant = pearson_correlation([1, 1, 1], [1, 2, 3])
    assert constant.coefficient is None
    assert pearson_correlation([], []).sample_size == 0


def test_pairwise_non_finite_values_are_excluded() -> None:
    """NaN pairs do not contaminate the finite-sample correlation."""
    result = pearson_correlation([1, 2, np.nan, 4], [1, 2, 3, 4])
    assert result.sample_size == 3
    assert result.confidence_interval_95 is None
    all_missing = pearson_correlation([np.nan, np.nan], [1, 2])
    assert all_missing.coefficient is None
    assert all_missing.sample_size == 0
