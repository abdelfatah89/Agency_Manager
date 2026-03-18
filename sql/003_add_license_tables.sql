-- 003_add_license_tables.sql

CREATE TABLE IF NOT EXISTS licensed_machines (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    machine_name VARCHAR(255) NOT NULL,
    hardware_fingerprint CHAR(64) NOT NULL,
    request_code LONGTEXT NOT NULL,
    license_code LONGTEXT NOT NULL,
    license_status VARCHAR(24) NOT NULL DEFAULT 'active',
    issued_at DATETIME NOT NULL,
    expires_at DATETIME NULL,
    activated_at DATETIME NULL,
    last_seen_at DATETIME NULL,
    revoked_at DATETIME NULL,
    notes VARCHAR(1024) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_licensed_machine_fingerprint (hardware_fingerprint),
    KEY idx_licensed_machine_status (license_status),
    KEY idx_licensed_machine_last_seen (last_seen_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS app_installations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    licensed_machine_id BIGINT NOT NULL,
    app_version VARCHAR(64) NOT NULL,
    install_path VARCHAR(1024) NOT NULL,
    install_hash CHAR(64) NULL,
    machine_name VARCHAR(255) NOT NULL,
    first_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(24) NOT NULL DEFAULT 'active',
    notes VARCHAR(1024) NULL,
    CONSTRAINT fk_installation_machine
        FOREIGN KEY (licensed_machine_id) REFERENCES licensed_machines(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY uq_installation_machine_path (licensed_machine_id, install_path),
    KEY idx_installation_last_seen (last_seen_at),
    KEY idx_installation_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS license_audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    licensed_machine_id BIGINT NULL,
    app_installation_id BIGINT NULL,
    event_type VARCHAR(64) NOT NULL,
    event_result VARCHAR(24) NOT NULL,
    event_message VARCHAR(1024) NULL,
    event_details_json LONGTEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_machine
        FOREIGN KEY (licensed_machine_id) REFERENCES licensed_machines(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_audit_installation
        FOREIGN KEY (app_installation_id) REFERENCES app_installations(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    KEY idx_audit_event_time (created_at),
    KEY idx_audit_event_type (event_type),
    KEY idx_audit_event_result (event_result)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
