"""Validation and cleaning for monthly Africa climate observations."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)

REGIONS = (
    "Central_Africa",
    "East_Africa",
    "North_Africa",
    "West_Africa",
    "Southern_Africa",
)
REQUIRED_COLUMNS = {
    "Region",
    "Year",
    "Month",
    "Temperature_Anomaly",
    "Precipitation_mm",
    "Date",
}
OUTPUT_COLUMNS = (
    "region",
    "date",
    "year",
    "month",
    "temperature_anomaly",
    "precipitation_mm",
)


class SchemaError(ValueError):
    """Raised when an input CSV does not match the supported schema."""


class DataValidationError(ValueError):
    """Raised when climate observations cannot be safely normalized."""


@dataclass(frozen=True)
class CleaningReport:
    """Counts of the cleaning actions applied to an input table."""

    input_rows: int
    output_rows: int
    exact_duplicates_dropped: int
    invalid_rows_dropped: int


def _normalize_region(value: object) -> str | None:
    """Normalize capitalization, spaces, and hyphens for known region labels."""
    if pd.isna(value):
        return None
    normalized = re.sub(r"[\s-]+", "_", str(value).strip()).lower()
    aliases = {
        "sahel_region": "West_Africa",
        "sahel": "West_Africa",
        "south_africa": "Southern_Africa",
    }
    if normalized in aliases:
        return aliases[normalized]
    region_map = {region.lower(): region for region in REGIONS}
    return region_map.get(normalized)


def clean_climate_data(frame: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """Validate, normalize, and clean monthly climate observations.

    Exact duplicate rows are discarded. Invalid dates, missing or non-numeric
    measurements, negative precipitation, and invalid calendar components are
    dropped with a warning. Conflicting records for the same region and month
    are rejected because choosing one would silently alter the source data.

    Args:
        frame: Raw data read from a climate CSV.

    Returns:
        A normalized frame and a count of the cleaning actions.

    Raises:
        SchemaError: If required input columns are missing.
        DataValidationError: If region labels or conflicting duplicates exist.
    """
    missing_columns = REQUIRED_COLUMNS.difference(frame.columns)
    if missing_columns:
        raise SchemaError(
            "Climate CSV is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    input_rows = len(frame)
    raw = frame.loc[:, sorted(REQUIRED_COLUMNS)].copy()
    raw["Region"] = raw["Region"].map(_normalize_region)
    unknown_regions = (
        frame.loc[raw["Region"].isna(), "Region"].dropna().astype(str).unique()
    )
    if len(unknown_regions):
        raise DataValidationError(
            "Unknown or inconsistent region label(s): "
            + ", ".join(sorted(unknown_regions))
        )
    if raw["Region"].isna().any():
        LOGGER.warning(
            "Dropping %d row(s) with missing region labels.",
            int(raw["Region"].isna().sum()),
        )

    dates = pd.to_datetime(raw["Date"], format="%Y-%m", errors="coerce")
    raw["date"] = dates
    raw["year"] = pd.to_numeric(raw["Year"], errors="coerce")
    raw["month"] = pd.to_numeric(raw["Month"], errors="coerce")
    raw["temperature_anomaly"] = pd.to_numeric(
        raw["Temperature_Anomaly"], errors="coerce"
    )
    raw["precipitation_mm"] = pd.to_numeric(raw["Precipitation_mm"], errors="coerce")

    numeric_columns = ("year", "month", "temperature_anomaly", "precipitation_mm")
    numeric_values = raw.loc[:, numeric_columns].to_numpy(dtype=float)
    valid = raw["Region"].notna() & raw["date"].notna()
    valid &= np.isfinite(numeric_values).all(axis=1)
    valid &= raw["year"].between(1, 9999) & raw["year"].eq(raw["year"].round())
    valid &= raw["month"].between(1, 12) & raw["month"].eq(raw["month"].round())
    valid &= raw["date"].dt.year.eq(raw["year"]) & raw["date"].dt.month.eq(raw["month"])
    valid &= raw["precipitation_mm"].ge(0)
    invalid_rows = int((~valid).sum())
    if invalid_rows:
        LOGGER.warning(
            "Dropping %d row(s) with missing/invalid values, inconsistent dates, "
            "invalid calendar fields, or negative precipitation.",
            invalid_rows,
        )
    raw = raw.loc[valid].copy()

    raw["year"] = raw["year"].astype(int)
    raw["month"] = raw["month"].astype(int)
    key_columns = ["Region", "date"]
    duplicate_mask = raw.duplicated(key_columns, keep=False)
    if duplicate_mask.any():
        duplicates = raw.loc[duplicate_mask]
        conflicting = (
            duplicates.groupby(key_columns, dropna=False)[
                ["temperature_anomaly", "precipitation_mm"]
            ]
            .nunique()
            .gt(1)
            .any(axis=1)
        )
        if conflicting.any():
            raise DataValidationError(
                "Conflicting observations exist for the same region and month."
            )
    before_duplicates = len(raw)
    raw = raw.drop_duplicates(subset=key_columns, keep="first")
    duplicates_dropped = before_duplicates - len(raw)
    if duplicates_dropped:
        LOGGER.warning("Dropped %d exact duplicate observation(s).", duplicates_dropped)

    cleaned = raw.rename(columns={"Region": "region"}).loc[:, OUTPUT_COLUMNS]
    cleaned = cleaned.sort_values(["region", "date"]).reset_index(drop=True)
    if cleaned.empty:
        raise DataValidationError(
            "No valid climate observations remain after cleaning."
        )

    report = CleaningReport(
        input_rows=input_rows,
        output_rows=len(cleaned),
        exact_duplicates_dropped=duplicates_dropped,
        invalid_rows_dropped=invalid_rows,
    )
    LOGGER.info(
        "Climate data cleaning complete: %d input, %d output, %d duplicate(s), "
        "%d invalid row(s) dropped.",
        report.input_rows,
        report.output_rows,
        report.exact_duplicates_dropped,
        report.invalid_rows_dropped,
    )
    return cleaned, report
