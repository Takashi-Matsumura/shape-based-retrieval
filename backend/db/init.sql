CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS cad_models (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_path VARCHAR(500),
    file_hash VARCHAR(64) UNIQUE,
    vertex_count INTEGER,
    face_count INTEGER,
    embedding vector(256),
    thumbnail_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vector search index (IVFFlat with cosine distance)
-- Note: IVFFlat index requires at least some rows to build.
-- For small datasets, exact search is used automatically.
CREATE INDEX IF NOT EXISTS idx_cad_embedding
  ON cad_models
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 10);
