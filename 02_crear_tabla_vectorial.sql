-- ============================================================
-- SQL: Crear tabla vectorial para RAG
-- Ejecutar ANTES de correr el workflow de vectorización
-- ============================================================

-- Asegurar que pgvector está activo
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla principal para RAG
CREATE TABLE IF NOT EXISTS ccd.conocimiento_vectorial (
    id          SERIAL PRIMARY KEY,
    chunk_index INT UNIQUE,
    seccion     VARCHAR(100) DEFAULT 'competencias_digitales',
    contenido   TEXT NOT NULL,
    embedding   vector(1536),  -- dimensiones de text-embedding-3-small
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Índice para búsqueda vectorial rápida (cosine similarity)
CREATE INDEX IF NOT EXISTS idx_embedding_cosine
ON ccd.conocimiento_vectorial
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 10);

-- Verificar
SELECT 'Tabla vectorial lista' AS status;
