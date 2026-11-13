"""Application factory and ASGI entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from config.settings import PROJECT_ROOT, Settings
from src.data_loader import load_climate_data

from .routes import router


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create an API application and load its dataset once at startup.

    Args:
        settings: Explicit configuration, or environment-backed defaults.

    Returns:
        A configured FastAPI application.
    """
    configured = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Load the configured dataset once for the lifetime of the app."""
        data, report = load_climate_data(configured.climate_data_file)
        app.state.climate_data = data
        logging.getLogger(__name__).info(
            "Loaded %d climate rows (%d duplicates and %d invalid rows dropped).",
            report.output_rows,
            report.exact_duplicates_dropped,
            report.invalid_rows_dropped,
        )
        yield

    app = FastAPI(
        title="NASA Africa Climate Analysis API",
        version="1.0.0",
        description=(
            "Monthly regional temperature-anomaly and precipitation data with "
            "correlation, regression, and annual trend analysis."
        ),
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(configured.cors_origins),
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.get("/", include_in_schema=False)
    async def serve_index() -> FileResponse:
        """Serve the frontend index page at the root URL."""
        return FileResponse(PROJECT_ROOT / "frontend" / "index.html")

    app.include_router(router)

    @app.exception_handler(RequestValidationError)
    async def invalid_request_handler(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        """Return query and path validation failures as HTTP 400."""
        logging.getLogger(__name__).debug(
            "Rejected invalid request to %s.", request.url.path
        )
        details = [
            {
                "location": list(item["loc"]),
                "message": item["msg"],
                "type": item["type"],
            }
            for item in error.errors()
        ]
        return JSONResponse(status_code=400, content={"detail": details})

    @app.exception_handler(Exception)
    async def unexpected_error_handler(
        request: Request, error: Exception
    ) -> JSONResponse:
        """Log unexpected failures and return a generic 500 response."""
        logging.getLogger(__name__).exception(
            "Unexpected API error for %s %s",
            request.method,
            request.url.path,
            exc_info=error,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected server error occurred."},
        )

    return app


app = create_app()
