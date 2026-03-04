"""Generate sample STL files, compute embeddings, and populate SQLite database.

Requires ONNX model to already exist at data/pointnet.onnx.
Run export_onnx.py first.
"""

import logging
import shutil
import sys
from pathlib import Path

import numpy as np
import trimesh

# Add demo root to path
DEMO_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DEMO_DIR))

from core.cad_processor import process_cad_file
from core.config import DATABASE_PATH, ONNX_MODEL_PATH, SAMPLES_DIR
from core.database import init_database, insert_model
from core.feature_extractor import extract_features

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

TEMP_DIR = DEMO_DIR / "_temp_samples"


def generate_box(extents: tuple[float, float, float], name: str) -> Path:
    mesh = trimesh.creation.box(extents=extents)
    path = TEMP_DIR / f"{name}.stl"
    mesh.export(str(path))
    return path


def generate_sphere(radius: float, name: str) -> Path:
    mesh = trimesh.creation.icosphere(subdivisions=3, radius=radius)
    path = TEMP_DIR / f"{name}.stl"
    mesh.export(str(path))
    return path


def generate_cylinder(radius: float, height: float, name: str) -> Path:
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
    path = TEMP_DIR / f"{name}.stl"
    mesh.export(str(path))
    return path


def generate_cone(radius: float, height: float, name: str) -> Path:
    mesh = trimesh.creation.cone(radius=radius, height=height, sections=32)
    path = TEMP_DIR / f"{name}.stl"
    mesh.export(str(path))
    return path


def generate_torus(major_radius: float, minor_radius: float, name: str) -> Path:
    angles = np.linspace(0, 2 * np.pi, 32, endpoint=False)
    circle_pts = np.column_stack([
        major_radius + minor_radius * np.cos(angles),
        minor_radius * np.sin(angles),
    ])
    mesh = trimesh.creation.revolve(circle_pts, sections=32)
    path = TEMP_DIR / f"{name}.stl"
    mesh.export(str(path))
    return path


def generate_composite(box_size: float, cyl_radius: float, cyl_height: float, name: str) -> Path:
    box = trimesh.creation.box(extents=[box_size, box_size, box_size])
    cyl = trimesh.creation.cylinder(radius=cyl_radius, height=cyl_height, sections=32)
    cyl.apply_translation([0, 0, box_size / 2 + cyl_height / 2])
    mesh = trimesh.util.concatenate([box, cyl])
    path = TEMP_DIR / f"{name}.stl"
    mesh.export(str(path))
    return path


def generate_all_samples() -> list[tuple[Path, str]]:
    """Generate all 32 sample STLs. Returns list of (path, category)."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    files: list[tuple[Path, str]] = []

    for i, size in enumerate([1.0, 1.5, 2.0, 0.5, 0.8, 1.2]):
        scale = 1.0 + i * 0.1
        files.append((generate_box((size, size * scale, size), f"box_{i+1:02d}"), "box"))

    for i, radius in enumerate([0.5, 0.75, 1.0, 1.25, 1.5]):
        files.append((generate_sphere(radius, f"sphere_{i+1:02d}"), "sphere"))

    for i, (r, h) in enumerate([
        (0.5, 1.0), (0.5, 2.0), (0.75, 1.5), (1.0, 1.0), (0.3, 3.0), (0.8, 0.5)
    ]):
        files.append((generate_cylinder(r, h, f"cylinder_{i+1:02d}"), "cylinder"))

    for i, (r, h) in enumerate([
        (0.5, 1.0), (0.75, 1.5), (1.0, 2.0), (0.5, 2.5), (1.0, 0.8)
    ]):
        files.append((generate_cone(r, h, f"cone_{i+1:02d}"), "cone"))

    for i, (R, r) in enumerate([
        (1.0, 0.3), (1.0, 0.5), (1.5, 0.3), (0.8, 0.4), (1.2, 0.2)
    ]):
        files.append((generate_torus(R, r, f"torus_{i+1:02d}"), "torus"))

    for i, (bs, cr, ch) in enumerate([
        (1.0, 0.3, 1.0), (1.5, 0.5, 0.8), (0.8, 0.4, 1.5),
        (1.2, 0.25, 1.2), (1.0, 0.6, 0.5)
    ]):
        files.append((generate_composite(bs, cr, ch, f"composite_{i+1:02d}"), "composite"))

    return files


def prepare() -> None:
    """Generate samples, compute embeddings, and build the SQLite database."""
    if not ONNX_MODEL_PATH.exists():
        print(f"ERROR: ONNX model not found at {ONNX_MODEL_PATH}")
        print("Run export_onnx.py first.")
        sys.exit(1)

    # Clean previous data
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
    if SAMPLES_DIR.exists():
        shutil.rmtree(SAMPLES_DIR)
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize database
    init_database()

    # Generate samples
    print("Generating sample STL files...")
    samples = generate_all_samples()
    print(f"Generated {len(samples)} samples")

    # Process each sample
    for stl_path, category in samples:
        filename = stl_path.name
        print(f"  Processing {filename}...", end=" ")

        # Copy to samples dir
        dest = SAMPLES_DIR / filename
        shutil.copy2(stl_path, dest)

        # Extract features
        points, vertex_count, face_count = process_cad_file(dest)
        embedding = extract_features(points)

        # Insert into database
        insert_model(filename, category, vertex_count, face_count, embedding)
        print(f"OK (v={vertex_count}, f={face_count})")

    # Clean temp
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    print(f"\nDone! Database: {DATABASE_PATH}")
    print(f"Samples: {SAMPLES_DIR} ({len(samples)} files)")


if __name__ == "__main__":
    prepare()
