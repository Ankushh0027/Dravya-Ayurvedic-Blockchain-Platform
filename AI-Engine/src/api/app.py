from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.api.routes import health_router, prediction_router
from src.data.paths import load_config


def create_app() -> FastAPI:
    """
    FastAPI Application Factory for Dravya AI Engine.
    Exposes production inference endpoints, configures OpenAPI metadata,
    and installs leak-proof error handling middleware.
    """
    config = load_config()
    api_cfg = config.get("api", {})

    title = api_cfg.get(
        "title", "Dravya AI Engine - Medicinal Plant Inference API"
    )
    description = api_cfg.get(
        "description",
        "Production-grade plant classification inference API powered by Dravya AI Engine",
    )
    version = api_cfg.get("version", "0.1.0")

    app = FastAPI(
        title=title,
        description=description,
        version=version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Include routes
    app.include_router(health_router)
    app.include_router(prediction_router)

    @app.get("/", include_in_schema=False)
    async def root():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/docs")


    # Clean Exception Handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail if isinstance(exc.detail, str) else "HTTP Exception",
                "detail": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred during request processing.",
            },
        )

    return app


app = create_app()
