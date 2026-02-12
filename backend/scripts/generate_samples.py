"""Generate sample CAD (STL) files with various primitive shapes."""

import logging
from pathlib import Path

import numpy as np
import trimesh

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "sample_cads"


def generate_box(extents: tuple[float, float, float], name: str) -> Path:
    """Generate a box STL file."""
    mesh = trimesh.creation.box(extents=extents)
    path = OUTPUT_DIR / f"{name}.stl"
    mesh.export(str(path))
    return path


def generate_sphere(radius: float, name: str) -> Path:
    """Generate a sphere STL file."""
    mesh = trimesh.creation.icosphere(subdivisions=3, radius=radius)
    path = OUTPUT_DIR / f"{name}.stl"
    mesh.export(str(path))
    return path


def generate_cylinder(radius: float, height: float, name: str) -> Path:
    """Generate a cylinder STL file."""
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
    path = OUTPUT_DIR / f"{name}.stl"
    mesh.export(str(path))
    return path


def generate_cone(radius: float, height: float, name: str) -> Path:
    """Generate a cone STL file."""
    mesh = trimesh.creation.cone(radius=radius, height=height, sections=32)
    path = OUTPUT_DIR / f"{name}.stl"
    mesh.export(str(path))
    return path


def generate_torus(major_radius: float, minor_radius: float, name: str) -> Path:
    """Generate a torus STL file via revolution."""
    # Create a torus using trimesh's annulus/revolution
    angles = np.linspace(0, 2 * np.pi, 32, endpoint=False)
    circle_pts = np.column_stack([
        major_radius + minor_radius * np.cos(angles),
        minor_radius * np.sin(angles),
    ])
    mesh = trimesh.creation.revolve(circle_pts, sections=32)
    path = OUTPUT_DIR / f"{name}.stl"
    mesh.export(str(path))
    return path


def generate_composite_box_cylinder(
    box_size: float, cyl_radius: float, cyl_height: float, name: str
) -> Path:
    """Generate a composite shape: box + cylinder on top."""
    box = trimesh.creation.box(extents=[box_size, box_size, box_size])
    cyl = trimesh.creation.cylinder(radius=cyl_radius, height=cyl_height, sections=32)
    # Place cylinder on top of the box
    cyl.apply_translation([0, 0, box_size / 2 + cyl_height / 2])
    mesh = trimesh.util.concatenate([box, cyl])
    path = OUTPUT_DIR / f"{name}.stl"
    mesh.export(str(path))
    return path


def generate_all_samples() -> list[Path]:
    """Generate all sample STL files.

    Returns:
        List of paths to generated files.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files: list[Path] = []

    # Boxes (6 variations)
    for i, size in enumerate([1.0, 1.5, 2.0, 0.5, 0.8, 1.2]):
        scale = 1.0 + i * 0.1
        files.append(generate_box((size, size * scale, size), f"box_{i+1:02d}"))

    # Spheres (5 variations)
    for i, radius in enumerate([0.5, 0.75, 1.0, 1.25, 1.5]):
        files.append(generate_sphere(radius, f"sphere_{i+1:02d}"))

    # Cylinders (6 variations)
    for i, (r, h) in enumerate([
        (0.5, 1.0), (0.5, 2.0), (0.75, 1.5), (1.0, 1.0), (0.3, 3.0), (0.8, 0.5)
    ]):
        files.append(generate_cylinder(r, h, f"cylinder_{i+1:02d}"))

    # Cones (5 variations)
    for i, (r, h) in enumerate([
        (0.5, 1.0), (0.75, 1.5), (1.0, 2.0), (0.5, 2.5), (1.0, 0.8)
    ]):
        files.append(generate_cone(r, h, f"cone_{i+1:02d}"))

    # Tori (5 variations)
    for i, (R, r) in enumerate([
        (1.0, 0.3), (1.0, 0.5), (1.5, 0.3), (0.8, 0.4), (1.2, 0.2)
    ]):
        files.append(generate_torus(R, r, f"torus_{i+1:02d}"))

    # Composite shapes (5 variations)
    for i, (bs, cr, ch) in enumerate([
        (1.0, 0.3, 1.0), (1.5, 0.5, 0.8), (0.8, 0.4, 1.5),
        (1.2, 0.25, 1.2), (1.0, 0.6, 0.5)
    ]):
        files.append(generate_composite_box_cylinder(bs, cr, ch, f"composite_{i+1:02d}"))

    logger.info("Generated %d sample STL files in %s", len(files), OUTPUT_DIR)
    return files


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    paths = generate_all_samples()
    print(f"Generated {len(paths)} sample files:")
    for p in paths:
        print(f"  {p.name}")
