"""CAD file processing: loading, normalization, and point cloud sampling."""

import hashlib
import logging
from pathlib import Path

import numpy as np
import trimesh

logger = logging.getLogger(__name__)


def compute_file_hash(file_path: str | Path) -> str:
    """Compute SHA-256 hash of a file.

    Args:
        file_path: Path to the file.

    Returns:
        Hex string of the file's SHA-256 hash.
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def validate_file(filename: str, content_start: bytes) -> bool:
    """Validate file extension and basic header check.

    Args:
        filename: Original filename.
        content_start: First bytes of file content for header validation.

    Returns:
        True if the file appears valid.
    """
    ext = Path(filename).suffix.lower()
    if ext not in {".stl", ".obj"}:
        return False

    if ext == ".stl":
        # STL files are either ASCII (starts with "solid") or binary (80-byte header)
        # Both are valid
        return len(content_start) >= 80 or content_start.strip().startswith(b"solid")

    if ext == ".obj":
        # OBJ files are text-based, should contain recognizable tokens
        try:
            text = content_start.decode("utf-8", errors="ignore")
            return any(token in text for token in ("v ", "f ", "#", "o ", "g "))
        except Exception:
            return False

    return False


def load_mesh(file_path: str | Path) -> trimesh.Trimesh:
    """Load a mesh from STL or OBJ file.

    Args:
        file_path: Path to the CAD file.

    Returns:
        A trimesh.Trimesh object.

    Raises:
        ValueError: If the file cannot be loaded as a valid mesh.
    """
    file_path = Path(file_path)
    ext = file_path.suffix.lower()

    mesh = trimesh.load(str(file_path), file_type=ext.lstrip("."), force="mesh")

    if not isinstance(mesh, trimesh.Trimesh):
        # If it loaded as a Scene, try to concatenate all meshes
        if isinstance(mesh, trimesh.Scene):
            meshes = [g for g in mesh.geometry.values() if isinstance(g, trimesh.Trimesh)]
            if not meshes:
                raise ValueError(f"No valid mesh geometry found in {file_path}")
            mesh = trimesh.util.concatenate(meshes)
        else:
            raise ValueError(f"Could not load {file_path} as a valid mesh")

    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        raise ValueError(f"Mesh from {file_path} has no vertices or faces")

    return mesh


def normalize_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Normalize mesh: center at origin and scale to fit unit sphere.

    Args:
        mesh: Input mesh.

    Returns:
        Normalized mesh (copy of the input).
    """
    mesh = mesh.copy()

    # Center at origin
    centroid = mesh.vertices.mean(axis=0)
    mesh.vertices -= centroid

    # Scale to unit sphere
    max_dist = np.max(np.linalg.norm(mesh.vertices, axis=1))
    if max_dist > 0:
        mesh.vertices /= max_dist

    return mesh


def sample_points(mesh: trimesh.Trimesh, n_points: int = 2048) -> np.ndarray:
    """Sample points uniformly from mesh surface.

    Args:
        mesh: Input mesh.
        n_points: Number of points to sample.

    Returns:
        Point cloud array of shape (n_points, 3).
    """
    points, _ = trimesh.sample.sample_surface(mesh, n_points)
    return points.astype(np.float32)


def process_cad_file(file_path: str | Path, n_points: int = 2048) -> tuple[np.ndarray, int, int]:
    """Full CAD processing pipeline: load, normalize, sample.

    Args:
        file_path: Path to the CAD file.
        n_points: Number of points to sample.

    Returns:
        Tuple of (point_cloud, vertex_count, face_count).
        point_cloud has shape (n_points, 3).
    """
    logger.info("Processing CAD file: %s", file_path)

    mesh = load_mesh(file_path)
    vertex_count = len(mesh.vertices)
    face_count = len(mesh.faces)

    logger.info("Loaded mesh: %d vertices, %d faces", vertex_count, face_count)

    mesh = normalize_mesh(mesh)
    points = sample_points(mesh, n_points)

    logger.info("Sampled %d points from mesh surface", n_points)

    return points, vertex_count, face_count
