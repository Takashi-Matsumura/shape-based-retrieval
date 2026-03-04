"""SQLite database access for the demo app."""

import sqlite3
import struct
from pathlib import Path

import numpy as np

from .config import DATABASE_PATH, POINTNET_OUTPUT_DIM

SCHEMA = """
CREATE TABLE IF NOT EXISTS cad_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    category TEXT,
    vertex_count INTEGER,
    face_count INTEGER,
    embedding BLOB NOT NULL
);
"""


def pack_embedding(embedding: np.ndarray) -> bytes:
    """Pack a float32 embedding array into a binary blob."""
    return struct.pack(f"{POINTNET_OUTPUT_DIM}f", *embedding.tolist())


def unpack_embedding(blob: bytes) -> np.ndarray:
    """Unpack a binary blob into a float32 embedding array."""
    return np.array(struct.unpack(f"{POINTNET_OUTPUT_DIM}f", blob), dtype=np.float32)


def init_database(db_path: Path | None = None) -> None:
    """Create the database schema if it doesn't exist."""
    db_path = db_path or DATABASE_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(SCHEMA)
        conn.commit()


def insert_model(
    filename: str,
    category: str,
    vertex_count: int,
    face_count: int,
    embedding: np.ndarray,
    db_path: Path | None = None,
) -> int:
    """Insert a model into the database and return its ID."""
    db_path = db_path or DATABASE_PATH
    blob = pack_embedding(embedding)
    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.execute(
            "INSERT INTO cad_models (filename, category, vertex_count, face_count, embedding) "
            "VALUES (?, ?, ?, ?, ?)",
            (filename, category, vertex_count, face_count, blob),
        )
        conn.commit()
        return cursor.lastrowid


def get_all_models(db_path: Path | None = None) -> list[dict]:
    """Load all models from the database.

    Returns:
        List of dicts with keys: id, filename, category, vertex_count, face_count, embedding.
    """
    db_path = db_path or DATABASE_PATH
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, filename, category, vertex_count, face_count, embedding FROM cad_models"
        ).fetchall()

    return [
        {
            "id": row["id"],
            "filename": row["filename"],
            "category": row["category"],
            "vertex_count": row["vertex_count"],
            "face_count": row["face_count"],
            "embedding": unpack_embedding(row["embedding"]),
        }
        for row in rows
    ]
