"""Generate demo query STL/OBJ files for similarity search testing.

These shapes are intentionally similar-but-not-identical to the seeded samples,
so the search results will show ranked similarity rather than exact matches.
"""

import logging
from pathlib import Path

import numpy as np
import trimesh

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "demo_queries"


def generate_all_queries() -> list[tuple[Path, str]]:
    """Generate demo query STL files.

    Returns:
        List of (path, description) tuples.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    queries: list[tuple[Path, str]] = []

    # 1. Slightly flattened sphere — should match sphere samples
    mesh = trimesh.creation.icosphere(subdivisions=3, radius=0.9)
    mesh.apply_scale([1.0, 1.0, 0.7])  # squash Z axis
    p = OUTPUT_DIR / "query_flat_sphere.stl"
    mesh.export(str(p))
    queries.append((p, "扁平な球体 → sphere群に類似ヒットするはず"))

    # 2. Tall thin cylinder — should match cylinder samples
    mesh = trimesh.creation.cylinder(radius=0.35, height=2.5, sections=32)
    p = OUTPUT_DIR / "query_thin_cylinder.stl"
    mesh.export(str(p))
    queries.append((p, "細長い円柱 → cylinder群に類似ヒットするはず"))

    # 3. Small torus — should match torus samples
    angles = np.linspace(0, 2 * np.pi, 32, endpoint=False)
    circle_pts = np.column_stack([
        0.9 + 0.25 * np.cos(angles),
        0.25 * np.sin(angles),
    ])
    mesh = trimesh.creation.revolve(circle_pts, sections=32)
    p = OUTPUT_DIR / "query_small_torus.stl"
    mesh.export(str(p))
    queries.append((p, "小さめトーラス → torus群に類似ヒットするはず"))

    # 4. Slightly elongated box — should match box samples
    mesh = trimesh.creation.box(extents=[1.1, 1.3, 0.9])
    p = OUTPUT_DIR / "query_elongated_box.stl"
    mesh.export(str(p))
    queries.append((p, "やや長めの直方体 → box群に類似ヒットするはず"))

    # 5. Wide cone — should match cone samples
    mesh = trimesh.creation.cone(radius=0.9, height=1.2, sections=32)
    p = OUTPUT_DIR / "query_wide_cone.stl"
    mesh.export(str(p))
    queries.append((p, "幅広コーン → cone群に類似ヒットするはず"))

    # 6. Composite variant (box + sphere on top) — novel shape, mixed results expected
    box = trimesh.creation.box(extents=[1.0, 1.0, 1.0])
    sphere = trimesh.creation.icosphere(subdivisions=2, radius=0.4)
    sphere.apply_translation([0, 0, 0.9])
    mesh = trimesh.util.concatenate([box, sphere])
    p = OUTPUT_DIR / "query_box_sphere.stl"
    mesh.export(str(p))
    queries.append((p, "箱+球の複合形状 → composite/box群に部分的にヒットするはず"))

    logger.info("Generated %d demo query files in %s", len(queries), OUTPUT_DIR)
    return queries


def generate_obj_queries() -> list[tuple[Path, str]]:
    """Generate demo query OBJ files.

    Returns:
        List of (path, description) tuples.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    queries: list[tuple[Path, str]] = []

    # 1. Slightly squashed sphere (OBJ) — should match sphere samples
    mesh = trimesh.creation.icosphere(subdivisions=3, radius=1.1)
    mesh.apply_scale([1.0, 0.8, 1.0])  # squash Y axis
    p = OUTPUT_DIR / "query_squashed_sphere.obj"
    mesh.export(str(p), file_type="obj")
    queries.append((p, "やや潰れた球体(OBJ) → sphere群に類似ヒットするはず"))

    # 2. Short fat cylinder (OBJ) — should match cylinder samples
    mesh = trimesh.creation.cylinder(radius=0.9, height=0.6, sections=32)
    p = OUTPUT_DIR / "query_fat_cylinder.obj"
    mesh.export(str(p), file_type="obj")
    queries.append((p, "太く短い円柱(OBJ) → cylinder群に類似ヒットするはず"))

    # 3. Tall narrow cone (OBJ) — should match cone samples
    mesh = trimesh.creation.cone(radius=0.4, height=2.2, sections=32)
    p = OUTPUT_DIR / "query_tall_cone.obj"
    mesh.export(str(p), file_type="obj")
    queries.append((p, "細長いコーン(OBJ) → cone群に類似ヒットするはず"))

    # 4. Large torus (OBJ) — should match torus samples
    angles = np.linspace(0, 2 * np.pi, 32, endpoint=False)
    circle_pts = np.column_stack([
        1.3 + 0.35 * np.cos(angles),
        0.35 * np.sin(angles),
    ])
    mesh = trimesh.creation.revolve(circle_pts, sections=32)
    p = OUTPUT_DIR / "query_large_torus.obj"
    mesh.export(str(p), file_type="obj")
    queries.append((p, "大きめトーラス(OBJ) → torus群に類似ヒットするはず"))

    logger.info("Generated %d OBJ demo query files in %s", len(queries), OUTPUT_DIR)
    return queries


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = generate_all_queries()
    obj_results = generate_obj_queries()
    all_results = results + obj_results
    print(f"Generated {len(all_results)} demo query files:")
    for path, desc in all_results:
        print(f"  {path.name:30s} — {desc}")
