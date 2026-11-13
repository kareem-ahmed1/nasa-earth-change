"""Stable Pydantic request and response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

RegionName = Literal[
    "all",
    "Central_Africa",
    "East_Africa",
    "North_Africa",
    "West_Africa",
    "Southern_Africa",
    "Sahel_Region",
    "South_Africa",
    "central-africa",
    "east-africa",
    "north-africa",
    "west-africa",
    "southern-africa",
]


class FilterRequest(BaseModel):
    """Query filters shared by climate endpoints."""

    model_config = ConfigDict(extra="forbid")

    region: RegionName = "all"
    start_year: int | None = None
    end_year: int | None = None


class YearRange(BaseModel):
    """Available or requested inclusive year bounds."""

    start_year: int
    end_year: int


class RegionsResponse(BaseModel):
    """Supported regions and available data range."""

    regions: list[str]
    available_years: YearRange


class DataPoint(BaseModel):
    """One monthly normalized observation."""

    region: str
    date: str
    year: int
    month: int
    temperature_anomaly: float
    precipitation_mm: float


class DataResponse(BaseModel):
    """Filtered observations and metadata."""

    region: str
    requested_years: YearRange
    sample_size: int
    observations: list[DataPoint]


class CorrelationResponse(BaseModel):
    """Pearson correlation result."""

    coefficient: float | None
    p_value: float | None
    confidence_interval_95: tuple[float, float] | None
    sample_size: int
    interpretation: str


class RegressionResponse(BaseModel):
    """Simple linear regression result."""

    predictor: str
    dependent_variable: str
    slope: float | None
    intercept: float | None
    r_squared: float | None
    standard_error: float | None
    p_value: float | None
    sample_size: int
    residuals: list[float]


class TrendResponse(BaseModel):
    """Mann-Kendall and Sen's slope result."""

    direction: str
    p_value: float | None
    sens_slope_per_year: float | None
    sample_size: int
    kendall_tau: float | None
    significant_at_05: bool | None
    caveat: str


class AnalysisResponse(BaseModel):
    """Complete statistical analysis response."""

    region: str
    requested_years: YearRange
    correlation: CorrelationResponse
    regression: RegressionResponse
    trends: dict[str, TrendResponse]
    assumptions: list[str]


class TimeSeriesPoint(BaseModel):
    """Monthly chart data point."""

    date: str
    temperature_anomaly: float
    precipitation_mm: float


class ScatterPoint(BaseModel):
    """Temperature anomaly and precipitation point."""

    date: str
    precipitation_mm: float
    temperature_anomaly: float


class RegressionLinePoint(BaseModel):
    """Regression line coordinate."""

    precipitation_mm: float
    temperature_anomaly: float


class ResidualPoint(BaseModel):
    """Regression residual by month."""

    date: str
    residual: float


class TrendPoint(BaseModel):
    """Annual trend observation and fitted Sen line."""

    year: int
    value: float
    sen_line: float | None = None


class RegionalYearAverage(BaseModel):
    """Annual average for a region."""

    region: str
    year: int
    temperature_anomaly: float
    precipitation_mm: float


class ChartsResponse(BaseModel):
    """Chart-ready series for all supported visualizations."""

    region: str
    requested_years: YearRange
    time_series: list[TimeSeriesPoint]
    scatter: list[ScatterPoint]
    regression_line: list[RegressionLinePoint]
    residuals: list[ResidualPoint]
    trends: dict[str, list[TrendPoint]]
    yearly_averages_per_region: list[RegionalYearAverage]
