"""Database connection and table definitions."""

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import DATABASE_URL, POINTNET_OUTPUT_DIM


engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class CadModel(Base):
    """ORM model for the cad_models table."""

    __tablename__ = "cad_models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_path = Column(String(500))
    file_hash = Column(String(64), unique=True)
    vertex_count = Column(Integer)
    face_count = Column(Integer)
    embedding = Column(Vector(POINTNET_OUTPUT_DIM))
    thumbnail_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)


async def get_session() -> AsyncSession:
    """Yield a database session."""
    async with async_session() as session:
        yield session
