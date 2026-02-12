"""Pydantic schemas for API request/response models."""

from datetime import datetime

from pydantic import BaseModel, Field


class CadModelResponse(BaseModel):
    """Response schema for a CAD model."""

    id: int
    filename: str
    vertex_count: int | None = None
    face_count: int | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class CadModelDetail(CadModelResponse):
    """Detailed response schema for a single CAD model."""

    original_path: str | None = None
    file_hash: str | None = None


class SearchResult(BaseModel):
    """A single search result with similarity score."""

    id: int
    filename: str
    vertex_count: int | None = None
    face_count: int | None = None
    similarity: float = Field(ge=0.0, le=1.0)
    created_at: datetime | None = None


class SearchResponse(BaseModel):
    """Response schema for similarity search."""

    query_filename: str
    results: list[SearchResult]


class UploadResponse(BaseModel):
    """Response schema for file upload."""

    id: int
    filename: str
    vertex_count: int | None = None
    face_count: int | None = None
    message: str = "File uploaded and processed successfully"


class HealthResponse(BaseModel):
    """Response schema for health check."""

    status: str = "ok"
    database: str = "connected"
