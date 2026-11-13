"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    climate_data_file: Path
    cors_origins: tuple[str, ...]

    @classmethod
    def from_env(cls) -> Settings:
        """Create settings from environment variables and project defaults."""
        default_data_file = PROJECT_ROOT / "data" / "africa_climate_merged_2004_2024.csv"
        if not default_data_file.exists():
            default_data_file = PROJECT_ROOT / "africa_climate_merged_2004_2024.csv"
        data_file = os.getenv(
            "CLIMATE_DATA_FILE",
            str(default_data_file),
        )
        origins = os.getenv("CORS_ORIGINS", "*")
        return cls(
            climate_data_file=Path(data_file).expanduser(),
            cors_origins=tuple(
                origin.strip() for origin in origins.split(",") if origin.strip()
            ),
        )
