-- 004_add_license_indexes.sql
-- Additional performance indexes for common license validation paths.

ALTER TABLE invoices
    ADD INDEX idx_invoice_status_issue_date (status, issue_date);

ALTER TABLE licensed_machines
    ADD INDEX idx_licensed_machine_customer_status (customer_name, license_status);

ALTER TABLE app_installations
    ADD INDEX idx_installation_machine_status_seen (licensed_machine_id, status, last_seen_at);

ALTER TABLE license_audit_log
    ADD INDEX idx_audit_machine_time (licensed_machine_id, created_at),
    ADD INDEX idx_audit_installation_time (app_installation_id, created_at);
