"""Application configuration management."""

import os
from pathlib import Path

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://caduser:cadpass@db:5432/cadsearch",
)

UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB

ALLOWED_EXTENSIONS: set[str] = {".stl", ".obj"}

# PointNet settings
POINTNET_OUTPUT_DIM: int = 256
POINTNET_NUM_POINTS: int = 2048
POINTNET_SEED: int = 42
POINTNET_WEIGHTS_PATH: Path = Path(os.getenv("POINTNET_WEIGHTS", "/app/data/pointnet_weights.pt"))

# CORS
CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]
