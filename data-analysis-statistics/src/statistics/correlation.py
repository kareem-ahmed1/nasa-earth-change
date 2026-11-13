"""Pearson correlation with Fisher-transformed confidence intervals."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class CorrelationResult:
    """Pearson correlation estimates and interpretation."""

    coefficient: float | None
    p_value: float | None
    confidence_interval_95: tuple[float, float] | None
    sample_size: int
    interpretation: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible dictionary."""
        return asdict(self)


def pearson_correlation(
    temperature: Sequence[float], precipitation: Sequence[float]
) -> CorrelationResult:
    """Calculate Pearson r, its p-value, Fisher 95% CI, and interpretation.

    Missing or non-finite pairs are excluded. Fewer than three pairs or a
    constant input makes the correlation undefined; fewer than four pairs
    cannot support the Fisher-transformed interval.

    Args:
        temperature: Temperature anomaly observations.
        precipitation: Paired precipitation observations.

    Returns:
        A result with null estimates where the sample is insufficient.
    """
    temp = np.asarray(temperature, dtype=float)
    precip = np.asarray(precipitation, dtype=float)
    if temp.shape != precip.shape:
        raise ValueError("Temperature and precipitation must have equal lengths.")
    finite = np.isfinite(temp) & np.isfinite(precip)
    temp = temp[finite]
    precip = precip[finite]
    n = len(temp)
    if n < 3 or np.ptp(temp) == 0 or np.ptp(precip) == 0:
        return CorrelationResult(
            None, None, None, n, "Correlation is undefined for this sample."
        )

    coefficient, p_value = stats.pearsonr(temp, precip)
    if abs(coefficient) < 0.2:
        strength = "very weak"
    elif abs(coefficient) < 0.4:
        strength = "weak"
    elif abs(coefficient) < 0.6:
        strength = "moderate"
    elif abs(coefficient) < 0.8:
        strength = "strong"
    else:
        strength = "very strong"
    if abs(coefficient) < 0.2:
        interpretation = "There is little to no linear association."
    else:
        direction = "positive" if coefficient > 0 else "negative"
        interpretation = f"A {strength} {direction} linear association."

    interval: tuple[float, float] | None = None
    if n > 3:
        fisher_z = np.arctanh(np.clip(coefficient, -0.999999999, 0.999999999))
        margin = stats.norm.ppf(0.975) / np.sqrt(n - 3)
        interval = (
            float(np.tanh(fisher_z - margin)),
            float(np.tanh(fisher_z + margin)),
        )
    return CorrelationResult(
        float(coefficient),
        float(p_value),
        interval,
        n,
        interpretation,
    )
