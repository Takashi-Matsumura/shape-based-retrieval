"""Upload API router."""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE, UPLOAD_DIR
from app.models.database import CadModel, get_session
from app.models.schemas import CadModelDetail, CadModelResponse, UploadResponse
from app.services.cad_processor import compute_file_hash, process_cad_file, validate_file
from app.services.feature_extractor import extract_features

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_cad_file(
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
) -> UploadResponse:
    """Upload a CAD file, extract features, and store in database."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Supported: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read file content
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")

    # Validate file header
    if not validate_file(file.filename, content[:1024]):
        raise HTTPException(status_code=400, detail="Invalid file content")

    # Save with UUID filename
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / unique_name
    file_path.write_bytes(content)

    try:
        # Compute hash and check for duplicates
        file_hash = compute_file_hash(file_path)
        existing = await session.execute(
            CadModel.__table__.select().where(CadModel.file_hash == file_hash)
        )
        if existing.first():
            file_path.unlink(missing_ok=True)
            raise HTTPException(status_code=409, detail="This file has already been uploaded")

        # Process CAD file
        points, vertex_count, face_count = process_cad_file(str(file_path))

        # Extract features
        embedding = extract_features(points)

        # Store in database
        cad_model = CadModel(
            filename=file.filename,
            original_path=str(file_path),
            file_hash=file_hash,
            vertex_count=vertex_count,
            face_count=face_count,
            embedding=embedding,
        )
        session.add(cad_model)
        await session.commit()
        await session.refresh(cad_model)

        logger.info("Uploaded and processed: %s (id=%d)", file.filename, cad_model.id)

        return UploadResponse(
            id=cad_model.id,
            filename=cad_model.filename,
            vertex_count=cad_model.vertex_count,
            face_count=cad_model.face_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        file_path.unlink(missing_ok=True)
        logger.exception("Failed to process file: %s", file.filename)
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}") from e


@router.get("/models", response_model=list[CadModelResponse])
async def list_models(
    session: AsyncSession = Depends(get_session),
) -> list[CadModelResponse]:
    """List all registered CAD models."""
    result = await session.execute(
        CadModel.__table__.select().order_by(CadModel.created_at.desc())
    )
    rows = result.fetchall()
    return [
        CadModelResponse(
            id=row.id,
            filename=row.filename,
            vertex_count=row.vertex_count,
            face_count=row.face_count,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.get("/models/{model_id}", response_model=CadModelDetail)
async def get_model(
    model_id: int,
    session: AsyncSession = Depends(get_session),
) -> CadModelDetail:
    """Get details of a specific CAD model."""
    result = await session.execute(
        CadModel.__table__.select().where(CadModel.id == model_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Model not found")

    return CadModelDetail(
        id=row.id,
        filename=row.filename,
        vertex_count=row.vertex_count,
        face_count=row.face_count,
        original_path=row.original_path,
        file_hash=row.file_hash,
        created_at=row.created_at,
    )


@router.delete("/models/{model_id}")
async def delete_model(
    model_id: int,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """Delete a CAD model and its file."""
    result = await session.execute(
        CadModel.__table__.select().where(CadModel.id == model_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Model not found")

    # Delete file
    if row.original_path:
        Path(row.original_path).unlink(missing_ok=True)

    # Delete from database
    await session.execute(
        CadModel.__table__.delete().where(CadModel.id == model_id)
    )
    await session.commit()

    logger.info("Deleted model: id=%d, filename=%s", model_id, row.filename)
    return {"message": f"Model {model_id} deleted successfully"}
