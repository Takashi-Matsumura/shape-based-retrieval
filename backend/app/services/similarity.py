"""Similarity search using pgvector."""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import SearchResult

logger = logging.getLogger(__name__)


async def search_similar(
    session: AsyncSession,
    query_vector: list[float],
    top_k: int = 10,
    exclude_id: int | None = None,
) -> list[SearchResult]:
    """Search for similar CAD models using cosine similarity.

    Args:
        session: Database session.
        query_vector: Query feature vector.
        top_k: Number of results to return.
        exclude_id: Optional model ID to exclude from results.

    Returns:
        List of SearchResult sorted by similarity (descending).
    """
    vector_str = "[" + ",".join(str(v) for v in query_vector) + "]"

    exclude_clause = "WHERE id != :exclude_id" if exclude_id else ""

    query = text(f"""
        SELECT id, filename, vertex_count, face_count, created_at,
               1 - (embedding <=> CAST(:query_vector AS vector)) AS similarity
        FROM cad_models
        {exclude_clause}
        ORDER BY embedding <=> CAST(:query_vector AS vector)
        LIMIT :top_k
    """)

    params: dict = {"query_vector": vector_str, "top_k": top_k}
    if exclude_id:
        params["exclude_id"] = exclude_id

    result = await session.execute(query, params)
    rows = result.fetchall()

    return [
        SearchResult(
            id=row.id,
            filename=row.filename,
            vertex_count=row.vertex_count,
            face_count=row.face_count,
            similarity=max(0.0, min(1.0, float(row.similarity))),
            created_at=row.created_at,
        )
        for row in rows
    ]
