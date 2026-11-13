"""FastAPI routes and request handling."""

from __future__ import annotations

import logging
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Request

from src.charts import build_chart_data
from src.cleaning import REGIONS
from src.filters import FilterError, filter_data
from src.statistics.correlation import pearson_correlation
from src.statistics.regression import linear_regression
from src.statistics.trend import mann_kendall_sen

from .schemas import (
    AnalysisResponse,
    ChartsResponse,
    CorrelationResponse,
    DataPoint,
    DataResponse,
    FilterRequest,
    RegressionResponse,
    RegionsResponse,
    TrendResponse,
    YearRange,
)

LOGGER = logging.getLogger(__name__)
router = APIRouter()


def _dataset(request: Request) -> pd.DataFrame:
    """Get startup-loaded data from this app's state."""
    return request.app.state.climate_data


def _selected_data(
    request: Request, filters: FilterRequest
) -> tuple[pd.DataFrame, int, int]:
    """Apply validated request filters and return selected inclusive bounds."""
    data = _dataset(request)
    minimum = int(data["year"].min())
    maximum = int(data["year"].max())
    start_year = minimum if filters.start_year is None else filters.start_year
    end_year = maximum if filters.end_year is None else filters.end_year
    try:
        selected = filter_data(data, filters.region, start_year, end_year)
    except FilterError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if selected.empty:
        raise HTTPException(
            status_code=404, detail="No data is available for the requested filters."
        )
    return selected, start_year, end_year


@router.get("/regions", response_model=RegionsResponse)
def get_regions(request: Request) -> RegionsResponse:
    """List supported regions and observed year coverage."""
    data = _dataset(request)
    return RegionsResponse(
        regions=list(REGIONS),
        available_years=YearRange(
            start_year=int(data["year"].min()),
            end_year=int(data["year"].max()),
        ),
    )


@router.get("/data", response_model=DataResponse)
def get_data(
    request: Request,
    filters: Annotated[FilterRequest, Depends()],
) -> DataResponse:
    """Return filtered monthly observations."""
    data, start_year, end_year = _selected_data(request, filters)
    observations = [
        DataPoint(
            region=row.region,
            date=row.date.strftime("%Y-%m"),
            year=int(row.year),
            month=int(row.month),
            temperature_anomaly=float(row.temperature_anomaly),
            precipitation_mm=float(row.precipitation_mm),
        )
        for row in data.itertuples(index=False)
    ]
    return DataResponse(
        region=filters.region,
        requested_years=YearRange(start_year=start_year, end_year=end_year),
        sample_size=len(observations),
        observations=observations,
    )


@router.get("/analysis", response_model=AnalysisResponse)
def get_analysis(
    request: Request,
    filters: Annotated[FilterRequest, Depends()],
) -> AnalysisResponse:
    """Return all statistical analyses for the filtered observations."""
    data, start_year, end_year = _selected_data(request, filters)
    correlation = pearson_correlation(
        data["temperature_anomaly"].to_numpy(),
        data["precipitation_mm"].to_numpy(),
    )
    regression = linear_regression(
        data["precipitation_mm"].to_numpy(),
        data["temperature_anomaly"].to_numpy(),
    )

    monthly = data.groupby("date", as_index=False).agg(
        temperature_anomaly=("temperature_anomaly", "mean"),
        precipitation_mm=("precipitation_mm", "mean"),
    )
    monthly["year"] = monthly["date"].dt.year
    annual = monthly.groupby("year", as_index=False).agg(
        temperature_anomaly=("temperature_anomaly", "mean"),
        precipitation_mm=("precipitation_mm", "mean"),
    )
    trends = {
        variable: TrendResponse(
            **mann_kendall_sen(annual["year"], annual[variable]).to_dict()
        )
        for variable in ("temperature_anomaly", "precipitation_mm")
    }
    return AnalysisResponse(
        region=filters.region,
        requested_years=YearRange(start_year=start_year, end_year=end_year),
        correlation=CorrelationResponse(**correlation.to_dict()),
        regression=RegressionResponse(
            predictor="precipitation_mm",
            dependent_variable="temperature_anomaly",
            **{
                key: value
                for key, value in regression.to_dict().items()
                if key != "residuals"
            },
            residuals=list(regression.residuals),
        ),
        trends=trends,
        assumptions=[
            "Pearson and linear regression use paired monthly observations with finite values.",
            "Correlation/regression p-values assume independent observations; monthly autocorrelation may make them optimistic.",
            "Trend tests use annual means to reduce seasonality and require at least three years.",
            "Mann-Kendall p-values do not correct for serial autocorrelation.",
        ],
    )


@router.get("/charts", response_model=ChartsResponse)
def get_charts(
    request: Request,
    filters: Annotated[FilterRequest, Depends()],
) -> ChartsResponse:
    """Return chart series for the frontend."""
    data, start_year, end_year = _selected_data(request, filters)
    charts = build_chart_data(data, _dataset(request))
    return ChartsResponse(
        region=filters.region,
        requested_years=YearRange(start_year=start_year, end_year=end_year),
        **charts,
    )
