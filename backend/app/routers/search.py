"""Search API router."""

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE
from app.models.database import CadModel, get_session
from app.models.schemas import SearchResponse
from app.services.cad_processor import process_cad_file, validate_file
from app.services.feature_extractor import extract_features
from app.services.similarity import search_similar

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search_cad(
    file: UploadFile,
    top_k: int = 10,
    session: AsyncSession = Depends(get_session),
) -> SearchResponse:
    """Upload a CAD file and search for similar models in the database."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Supported: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")

    if not validate_file(file.filename, content[:1024]):
        raise HTTPException(status_code=400, detail="Invalid file content")

    # Write to temp file for processing
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        points, _, _ = process_cad_file(tmp_path)
        embedding = extract_features(points)
        results = await search_similar(session, embedding, top_k=top_k)

        return SearchResponse(
            query_filename=file.filename,
            results=results,
        )
    except Exception as e:
        logger.exception("Search failed for: %s", file.filename)
        raise HTTPException(status_code=500, detail=f"Search failed: {e}") from e
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.get("/models/{model_id}/file")
async def download_model_file(
    model_id: int,
    session: AsyncSession = Depends(get_session),
) -> FileResponse:
    """Download the original CAD file for a model."""
    result = await session.execute(
        CadModel.__table__.select().where(CadModel.id == model_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Model not found")

    file_path = Path(row.original_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=str(file_path),
        filename=row.filename,
        media_type="application/octet-stream",
    )
