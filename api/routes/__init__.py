"""API routes module."""

from fastapi import FastAPI

# Import routers
from api.routes.auth_routes import router as auth_router
from api.routes.calculation_routes import router as calculation_router
from api.routes.heatmap_routes import router as heatmap_router

def register_routers(app: FastAPI) -> None:
    """Register all API routers with the FastAPI app."""
    app.include_router(auth_router)
    app.include_router(calculation_router)
    app.include_router(heatmap_router)
