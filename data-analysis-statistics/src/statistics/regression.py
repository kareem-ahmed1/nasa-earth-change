"""Simple least-squares regression for paired climate measurements."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class RegressionResult:
    """Regression estimates and fitted residuals."""

    slope: float | None
    intercept: float | None
    r_squared: float | None
    standard_error: float | None
    p_value: float | None
    sample_size: int
    residuals: tuple[float, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible dictionary."""
        return asdict(self)


def linear_regression(
    predictor: Sequence[float], dependent: Sequence[float]
) -> RegressionResult:
    """Fit dependent = intercept + slope * predictor using SciPy.

    Non-finite pairs are dropped. With fewer than two observations or a
    constant predictor, model estimates are null and residuals are empty.

    Args:
        predictor: Independent variable values.
        dependent: Dependent variable values.

    Returns:
        Regression coefficients, model fit, p-value, and residuals.
    """
    x = np.asarray(predictor, dtype=float)
    y = np.asarray(dependent, dtype=float)
    if x.shape != y.shape:
        raise ValueError("Predictor and dependent variable must have equal lengths.")
    finite = np.isfinite(x) & np.isfinite(y)
    x = x[finite]
    y = y[finite]
    n = len(x)
    if n < 2 or np.ptp(x) == 0:
        return RegressionResult(None, None, None, None, None, n, ())

    fitted = stats.linregress(x, y)
    residuals = y - (fitted.intercept + fitted.slope * x)
    return RegressionResult(
        slope=float(fitted.slope),
        intercept=float(fitted.intercept),
        r_squared=float(fitted.rvalue**2),
        standard_error=float(fitted.stderr),
        p_value=float(fitted.pvalue),
        sample_size=n,
        residuals=tuple(float(value) for value in residuals),
    )
