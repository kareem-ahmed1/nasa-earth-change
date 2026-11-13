# NASA Africa Climate Analysis

A typed Python 3.11+ service for monthly African regional climate data. It
provides a JSON API for filtered observations, Pearson correlation, linear
regression, Mann-Kendall trend tests with Sen's slope, and chart-ready series.

## Data inspection and assumptions

The CSVs available in the workspace at implementation time were
`temperature.csv`, `land_data.csv`, and `africa_climate_merged_2004_2024.csv`.
The specifically requested `data/2004-2025.csv` and separate precipitation
file were not present. Per the source selection, the application uses the
merged CSV. Its schema is:

| Column | Meaning |
| --- | --- |
| `Region` | `Central_Africa`, `East_Africa`, `North_Africa`, `Sahel_Region`, or `South_Africa` |
| `Year`, `Month`, `Date` | Monthly observations; `Date` is `YYYY-MM` |
| `Temperature_Anomaly` | The temperature measure in the merged source (not absolute temperature) |
| `Precipitation_mm` | Precipitation in millimetres, per the source column label |

The inspected merged file contains monthly data from 2004 through 2024. The
CSV schema does not specify the precipitation period aggregation or the
temperature-anomaly unit, so the API preserves the source measure and label
without claiming a more precise unit. The separate `temperature.csv` contains
absolute `Temperature` and a `Temperature_Anomaly` column, but `land_data.csv`
contains desertification/NDVI rather than precipitation. Thus the merged
anomaly is used instead of substituting an unrelated land measure or silently
mixing sources.

The inspected merged CSV has 1,260 rows (5 regions × 21 years × 12 months),
with no exact duplicates or missing/invalid values under the loader's
validation rules. Observed values range from -1.366 to 2.993 for
`Temperature_Anomaly` and from 0.0 to 30.95 for `Precipitation_mm`.

At startup the loader validates required columns, date/year/month agreement,
known region labels, and numeric measurements. Region case, spaces, and
hyphens are normalized to the five known labels. Invalid or incomplete rows
and identical duplicate observations are dropped with warning logs; conflicting
values for the same region/month and unknown region names raise explicit
errors. No missing-value imputation or outlier trimming is performed. This
preserves source measurements and avoids inventing climate observations.

The data file is external and is not committed. Configure the path with
`CLIMATE_DATA_FILE`; by default it looks for
`africa_climate_merged_2004_2024.csv` in the project root. Put an alternate
merged CSV in `data/` and set `CLIMATE_DATA_FILE=data/your-file.csv`.
`CORS_ORIGINS` is a comma-separated allowlist (default:
`http://localhost:3000`).

## Setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:CLIMATE_DATA_FILE = "data\africa_climate_merged_2004_2024.csv"
```

The configured CSV must use the schema above. The default local workspace file
is ignored by git along with CSVs under `data/`.

## Run the API

```powershell
uvicorn src.api.main:app --reload
```

Interactive OpenAPI documentation is available at `http://localhost:8000/docs`.
The optional Plotly reference page is `frontend/index.html`; it expects the API
on `http://localhost:8000`.

All data endpoints accept `region` (`all` or one of the five exact labels),
`start_year`, and `end_year` query parameters. Years are inclusive, default to
the available full data range, and must be ordered and within that range.

### Example requests

```text
GET http://localhost:8000/regions
GET http://localhost:8000/data?region=North_Africa&start_year=2010&end_year=2020
GET http://localhost:8000/analysis?region=all&start_year=2004&end_year=2024
GET http://localhost:8000/charts?region=Sahel_Region&start_year=2004&end_year=2024
```

### Response examples

`GET /regions`:

```json
{
  "regions": ["Central_Africa", "East_Africa", "North_Africa", "Sahel_Region", "South_Africa"],
  "available_years": {"start_year": 2004, "end_year": 2024}
}
```

`GET /data?...` includes:

```json
{
  "region": "North_Africa",
  "requested_years": {"start_year": 2010, "end_year": 2020},
  "sample_size": 132,
  "observations": [{
    "region": "North_Africa",
    "date": "2010-01",
    "year": 2010,
    "month": 1,
    "temperature_anomaly": 0.7,
    "precipitation_mm": 0.4
  }]
}
```

`GET /analysis?...` includes `correlation` (coefficient, two-sided p-value,
95% Fisher-z confidence interval, sample size, interpretation), `regression`
(predictor `precipitation_mm`, dependent variable `temperature_anomaly`,
slope, intercept, R², standard error, p-value, and paired residuals), `trends`
(annual results for each variable), and assumption/caveat strings.

`GET /charts?...` returns `time_series` (monthly values suitable for a dual-axis
chart), `scatter`, `regression_line`, `residuals`, annual `trends` with the Sen
line, and `yearly_averages_per_region`. Regional comparison data covers all
five regions over the selected year window, even when other chart series are
filtered to one region.

Invalid region/year parameters return HTTP 400, an empty valid selection
returns 404, and unexpected server failures return HTTP 500. API errors use a
JSON `detail` field.

## Statistical methods

- **Pearson correlation:** Measures linear association (r ranges from -1 to 1).
  The p-value tests zero correlation; the confidence interval uses Fisher's
  z-transform and is omitted when fewer than four paired observations remain.
  Undefined cases, including constant series, return null estimates.
- **Linear regression:** Fits temperature anomaly as the dependent variable and
  precipitation as the predictor. Slope is the estimated anomaly change for a
  one-unit precipitation change; R² is the fraction of sample variation
  explained by the linear model. The reported standard error is the slope's
  standard error. Residuals are observed minus fitted values.
- **Mann-Kendall and Sen's slope:** Trend inference uses annual averages to
  avoid treating the monthly seasonal cycle as a long-term trend. The direction
  follows Sen's slope; p < 0.05 indicates statistical significance. Sen's slope
  is the median pairwise change per year. At least three annual points are
  required. Serial autocorrelation is not corrected and may affect the p-value.

Correlation/regression significance assumes independent paired observations;
monthly climate observations can be autocorrelated, so p-values may be
optimistic. These methods describe associations and trends, not causal effects.

## Tests and quality checks

```powershell
pytest
black --check config src tests
ruff check config src tests
mypy config src
```

Tests compare estimates against SciPy on small fixtures and cover invalid and
missing data, duplicate rows, region/year filtering, constant series,
perfect-fit data, and insufficient trend samples.
