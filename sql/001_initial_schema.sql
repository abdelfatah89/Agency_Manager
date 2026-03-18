-- 001_initial_schema.sql
-- Baseline migration bootstrap for KONACH.
-- Existing business tables are currently maintained by the project SQL dumps
-- and SQLAlchemy models. This migration introduces managed schema versioning.

CREATE TABLE IF NOT EXISTS schema_migrations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    version INT NOT NULL UNIQUE,
    script_name VARCHAR(255) NOT NULL,
    checksum_sha256 CHAR(64) NOT NULL,
    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    execution_ms INT NOT NULL DEFAULT 0,
    applied_by VARCHAR(128) NULL,
    notes VARCHAR(512) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
