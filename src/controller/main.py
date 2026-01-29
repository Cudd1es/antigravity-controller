"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controller.api import commands, health, status
from controller.config import get_settings
from controller.db.database import init_db
from controller.websocket.router import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    settings = get_settings()
    if settings.debug:
        print(f"Starting Antigravity Controller on {settings.host}:{settings.port}")
    await init_db()
    yield
    # Shutdown
    print("Shutting down Antigravity Controller")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Antigravity Controller",
        description="Controller service for Antigravity Agent and Mobile App communication",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # CORS middleware for mobile app access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(commands.router, prefix="/api/v1", tags=["Commands"])
    app.include_router(status.router, prefix="/api/v1", tags=["Status"])
    app.include_router(ws_router, prefix="/ws/v1", tags=["WebSocket"])

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "controller.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
