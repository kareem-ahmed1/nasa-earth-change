"""CSV loading and schema validation for climate observations."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.cleaning import CleaningReport, clean_climate_data

LOGGER = logging.getLogger(__name__)


def load_climate_data(path: Path) -> tuple[pd.DataFrame, CleaningReport]:
    """Load, validate, and clean the configured monthly climate CSV.

    Args:
        path: Path to the merged climate CSV.

    Returns:
        Cleaned observations and a cleaning report.

    Raises:
        FileNotFoundError: If the configured CSV does not exist.
        ValueError: If the CSV cannot be parsed or does not match the schema.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Climate data CSV was not found: {path}")
    try:
        frame = pd.read_csv(path)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        raise ValueError(
            f"Could not read climate data CSV '{path}': {error}"
        ) from error
    LOGGER.info("Loaded %d raw climate rows from %s.", len(frame), path)
    return clean_climate_data(frame)
