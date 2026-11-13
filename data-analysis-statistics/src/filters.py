"""Year and region filtering."""

from __future__ import annotations

import pandas as pd

from src.cleaning import REGIONS, _normalize_region


class FilterError(ValueError):
    """Raised when a requested region or year range is invalid."""


def filter_data(
    data: pd.DataFrame,
    region: str = "all",
    start_year: int | None = None,
    end_year: int | None = None,
) -> pd.DataFrame:
    """Return observations in the requested region and inclusive year range.

    Args:
        data: Cleaned climate data.
        region: One known region label or ``all``.
        start_year: First included year, defaulting to the available minimum.
        end_year: Last included year, defaulting to the available maximum.

    Returns:
        A sorted filtered copy, which may be empty.

    Raises:
        FilterError: If the region, order, or available year bounds are invalid.
    """
    normalized_input = region.strip()
    if normalized_input.lower() == "all":
        normalized_region = "all"
    else:
        canonical = _normalize_region(normalized_input)
        if canonical is None or canonical not in REGIONS:
            raise FilterError(
                f"Unknown region '{region}'. Choose one of {', '.join(REGIONS)} or 'all'."
            )
        normalized_region = canonical
    if data.empty:
        raise FilterError("No climate data is available to filter.")

    available_start = int(data["year"].min())
    available_end = int(data["year"].max())
    selected_start = available_start if start_year is None else start_year
    selected_end = available_end if end_year is None else end_year
    if selected_start > selected_end:
        raise FilterError("start_year must be less than or equal to end_year.")
    if selected_start < available_start or selected_end > available_end:
        raise FilterError(
            f"Requested years must be within the available range "
            f"{available_start}-{available_end}."
        )

    selected = data.loc[
        data["year"].between(selected_start, selected_end)
        & (
            (data["region"] == normalized_region)
            if normalized_region != "all"
            else True
        )
    ]
    return selected.sort_values(["region", "date"]).reset_index(drop=True)
