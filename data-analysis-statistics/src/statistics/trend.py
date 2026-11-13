"""Mann-Kendall trend test and Sen's slope."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class TrendResult:
    """Non-parametric trend direction, significance, and annual slope."""

    direction: str
    p_value: float | None
    sens_slope_per_year: float | None
    sample_size: int
    kendall_tau: float | None
    significant_at_05: bool | None
    caveat: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible dictionary."""
        return asdict(self)


def mann_kendall_sen(years: Sequence[float], values: Sequence[float]) -> TrendResult:
    """Test monotonic trend and estimate Sen's slope in value units per year.

    The Mann-Kendall p-value is the two-sided Kendall rank test p-value.
    Values are expected to be annual aggregates so monthly seasonality is not
    mistaken for a long-term trend. Serial autocorrelation is not corrected.

    Args:
        years: Observation times in calendar years.
        values: One value per year.

    Returns:
        Trend test results. An insufficient or constant series is reported
        explicitly instead of raising a statistical-library error.
    """
    x = np.asarray(years, dtype=float)
    y = np.asarray(values, dtype=float)
    if x.shape != y.shape:
        raise ValueError("Years and values must have equal lengths.")
    finite = np.isfinite(x) & np.isfinite(y)
    x = x[finite]
    y = y[finite]
    order = np.argsort(x)
    x = x[order]
    y = y[order]
    n = len(y)
    if n < 3:
        return TrendResult(
            "insufficient_data",
            None,
            None,
            n,
            None,
            None,
            "Trend inference requires at least three annual observations.",
        )
    if len(np.unique(x)) != n:
        raise ValueError("Each trend observation must have a unique year.")
    differences = np.array(
        [(y[j] - y[i]) / (x[j] - x[i]) for i in range(n - 1) for j in range(i + 1, n)]
    )
    slope = float(np.median(differences))
    if np.ptp(y) == 0:
        return TrendResult(
            "no_trend",
            1.0,
            0.0,
            n,
            0.0,
            False,
            "Serial autocorrelation is not corrected; annual aggregation reduces seasonality.",
        )
    kendall = stats.kendalltau(x, y, nan_policy="omit")
    p_value = float(kendall.pvalue)
    direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "no_trend"
    return TrendResult(
        direction=direction,
        p_value=p_value,
        sens_slope_per_year=slope,
        sample_size=n,
        kendall_tau=float(kendall.statistic),
        significant_at_05=p_value < 0.05,
        caveat="Serial autocorrelation is not corrected; annual aggregation reduces seasonality.",
    )
