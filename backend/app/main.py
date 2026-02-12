"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import CORS_ORIGINS
from app.models.database import async_session
from app.models.schemas import HealthResponse
from app.routers import search, upload
from app.services.feature_extractor import get_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CAD Similarity Search API",
    description="Upload CAD files (STL/OBJ) and search for similar shapes",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(search.router)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize PointNet model on startup."""
    logger.info("Loading PointNet model...")
    get_model()
    logger.info("PointNet model loaded successfully")


@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return HealthResponse(status="ok", database="connected")
    except Exception as e:
        logger.error("Health check failed: %s", e)
        return HealthResponse(status="degraded", database=f"error: {e}")
