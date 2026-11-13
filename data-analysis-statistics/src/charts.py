"""Chart-ready data transformations."""

from __future__ import annotations

import pandas as pd

from src.statistics.regression import linear_regression
from src.statistics.trend import mann_kendall_sen


def build_chart_data(data: pd.DataFrame, all_data: pd.DataFrame) -> dict[str, object]:
    """Build chart series for time series, regression, residuals, and trends.

    Args:
        data: Data filtered by the requested region and year range.
        all_data: All cleaned observations, used for regional comparisons.

    Returns:
        JSON-compatible collections for frontend chart rendering.
    """
    monthly = (
        data.groupby("date", as_index=False)
        .agg(
            temperature_anomaly=("temperature_anomaly", "mean"),
            precipitation_mm=("precipitation_mm", "mean"),
        )
        .sort_values("date")
    )
    scatter = data.loc[:, ["date", "temperature_anomaly", "precipitation_mm"]].copy()
    model = linear_regression(
        scatter["precipitation_mm"].to_numpy(),
        scatter["temperature_anomaly"].to_numpy(),
    )
    regression_line: list[dict[str, float]] = []
    residual_points: list[dict[str, object]] = []
    if model.slope is not None and model.intercept is not None:
        minimum = float(scatter["precipitation_mm"].min())
        maximum = float(scatter["precipitation_mm"].max())
        regression_line = [
            {
                "precipitation_mm": minimum,
                "temperature_anomaly": model.intercept + model.slope * minimum,
            },
            {
                "precipitation_mm": maximum,
                "temperature_anomaly": model.intercept + model.slope * maximum,
            },
        ]
        residual_points = [
            {
                "date": date.strftime("%Y-%m"),
                "residual": residual,
            }
            for date, residual in zip(scatter["date"], model.residuals, strict=True)
        ]

    annual = monthly.copy()
    annual["year"] = annual["date"].dt.year
    annual = annual.groupby("year", as_index=False).agg(
        temperature_anomaly=("temperature_anomaly", "mean"),
        precipitation_mm=("precipitation_mm", "mean"),
    )
    trend_series: dict[str, list[dict[str, float | int]]] = {}
    for variable in ("temperature_anomaly", "precipitation_mm"):
        trend = mann_kendall_sen(annual["year"], annual[variable])
        points = [
            {"year": int(year), "value": float(value)}
            for year, value in zip(annual["year"], annual[variable], strict=True)
        ]
        if trend.sens_slope_per_year is not None and len(points):
            intercept = float(
                (annual[variable] - trend.sens_slope_per_year * annual["year"]).median()
            )
            points = [
                {
                    **point,
                    "sen_line": intercept + trend.sens_slope_per_year * point["year"],
                }
                for point in points
            ]
        trend_series[variable] = points

    comparison = (
        all_data.loc[
            all_data["year"].between(int(data["year"].min()), int(data["year"].max()))
        ]
        .groupby(["region", "year"], as_index=False)
        .agg(
            temperature_anomaly=("temperature_anomaly", "mean"),
            precipitation_mm=("precipitation_mm", "mean"),
        )
        .to_dict(orient="records")
    )
    return {
        "time_series": [
            {
                "date": row.date.strftime("%Y-%m"),
                "temperature_anomaly": float(row.temperature_anomaly),
                "precipitation_mm": float(row.precipitation_mm),
            }
            for row in monthly.itertuples(index=False)
        ],
        "scatter": [
            {
                "date": row.date.strftime("%Y-%m"),
                "precipitation_mm": float(row.precipitation_mm),
                "temperature_anomaly": float(row.temperature_anomaly),
            }
            for row in scatter.itertuples(index=False)
        ],
        "regression_line": regression_line,
        "residuals": residual_points,
        "trends": trend_series,
        "yearly_averages_per_region": comparison,
    }
