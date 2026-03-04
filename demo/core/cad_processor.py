"""CAD file processing: loading, normalization, and point cloud sampling."""

import logging
from pathlib import Path

import numpy as np
import trimesh

logger = logging.getLogger(__name__)


def load_mesh(file_path: str | Path) -> trimesh.Trimesh:
    """Load a mesh from STL or OBJ file."""
    file_path = Path(file_path)
    ext = file_path.suffix.lower()

    mesh = trimesh.load(str(file_path), file_type=ext.lstrip("."), force="mesh")

    if not isinstance(mesh, trimesh.Trimesh):
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
    """Normalize mesh: center at origin and scale to fit unit sphere."""
    mesh = mesh.copy()
    centroid = mesh.vertices.mean(axis=0)
    mesh.vertices -= centroid
    max_dist = np.max(np.linalg.norm(mesh.vertices, axis=1))
    if max_dist > 0:
        mesh.vertices /= max_dist
    return mesh


def sample_points(mesh: trimesh.Trimesh, n_points: int = 2048) -> np.ndarray:
    """Sample points uniformly from mesh surface."""
    points, _ = trimesh.sample.sample_surface(mesh, n_points)
    return points.astype(np.float32)


def process_cad_file(file_path: str | Path, n_points: int = 2048) -> tuple[np.ndarray, int, int]:
    """Full CAD processing pipeline: load, normalize, sample.

    Returns:
        Tuple of (point_cloud, vertex_count, face_count).
    """
    logger.info("Processing CAD file: %s", file_path)
    mesh = load_mesh(file_path)
    vertex_count = len(mesh.vertices)
    face_count = len(mesh.faces)
    mesh = normalize_mesh(mesh)
    points = sample_points(mesh, n_points)
    return points, vertex_count, face_count
