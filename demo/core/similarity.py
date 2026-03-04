"""Cosine similarity search using numpy (no pgvector dependency)."""

import numpy as np

from .database import get_all_models

# In-memory cache of model data
_cache: dict | None = None


def _load_cache() -> dict:
    """Load all models and their embeddings into memory."""
    global _cache
    models = get_all_models()
    if not models:
        _cache = {"models": [], "embeddings": np.empty((0, 256), dtype=np.float32)}
        return _cache

    embeddings = np.stack([m["embedding"] for m in models], axis=0)
    _cache = {"models": models, "embeddings": embeddings}
    return _cache


def invalidate_cache() -> None:
    """Clear the in-memory cache (e.g., after database changes)."""
    global _cache
    _cache = None


def search_similar(
    query_embedding: np.ndarray, top_k: int = 10
) -> list[dict]:
    """Find the most similar models by cosine similarity.

    Args:
        query_embedding: L2-normalized feature vector of shape (256,).
        top_k: Number of results to return.

    Returns:
        List of dicts with keys: id, filename, category, vertex_count, face_count, similarity.
    """
    global _cache
    if _cache is None:
        _load_cache()

    if len(_cache["models"]) == 0:
        return []

    # Cosine similarity = dot product (both vectors are L2-normalized)
    similarities = _cache["embeddings"] @ query_embedding
    similarities = np.clip(similarities, 0.0, 1.0)

    # Get top-k indices
    k = min(top_k, len(similarities))
    top_indices = np.argsort(similarities)[::-1][:k]

    results = []
    for idx in top_indices:
        model = _cache["models"][idx]
        results.append({
            "id": model["id"],
            "filename": model["filename"],
            "category": model["category"],
            "vertex_count": model["vertex_count"],
            "face_count": model["face_count"],
            "similarity": float(similarities[idx]),
        })

    return results
