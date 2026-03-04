"""Configuration constants and path resolution for the demo app."""

import sys
from pathlib import Path

# PointNet settings (must match backend)
POINTNET_OUTPUT_DIM: int = 256
POINTNET_NUM_POINTS: int = 2048
POINTNET_SEED: int = 42

# Supported file extensions
ALLOWED_EXTENSIONS: set[str] = {".stl", ".obj"}


def _get_base_dir() -> Path:
    """Resolve base directory, handling PyInstaller frozen bundles."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


BASE_DIR: Path = _get_base_dir()
DATA_DIR: Path = BASE_DIR / "data"
ONNX_MODEL_PATH: Path = DATA_DIR / "pointnet.onnx"
DATABASE_PATH: Path = DATA_DIR / "demo.db"
SAMPLES_DIR: Path = DATA_DIR / "samples"
