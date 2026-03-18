-- 002_add_invoice_tables.sql

CREATE TABLE IF NOT EXISTS invoice_number_counters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    period_key VARCHAR(6) NOT NULL,
    sequence_value INT NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_invoice_counter_period (period_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS invoices (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    invoice_number VARCHAR(32) NOT NULL,
    source_type VARCHAR(32) NOT NULL,
    idempotency_key VARCHAR(64) NOT NULL,
    issue_date DATE NOT NULL,
    period_key VARCHAR(6) NOT NULL,
    sequence_value INT NOT NULL,
    client_name VARCHAR(255) NULL,
    account_name VARCHAR(255) NULL,
    date_from DATE NULL,
    date_to DATE NULL,
    total_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    total_paid NUMERIC(14,2) NOT NULL DEFAULT 0,
    total_vat NUMERIC(14,2) NOT NULL DEFAULT 0,
    balance NUMERIC(14,2) NOT NULL DEFAULT 0,
    status VARCHAR(16) NOT NULL DEFAULT 'reserved',
    pdf_path VARCHAR(512) NULL,
    payload_json LONGTEXT NULL,
    error_message LONGTEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_invoice_number (invoice_number),
    UNIQUE KEY uq_invoice_source_idempotency (source_type, idempotency_key),
    KEY idx_invoice_issue_date (issue_date),
    KEY idx_invoice_period (period_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
