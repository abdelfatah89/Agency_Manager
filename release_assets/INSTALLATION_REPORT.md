# Installation and Deployment Report

## 1) Database Engine and Version
- Primary target: MariaDB 10.6+
- Compatible alternative: MySQL 8.0+
- Port: 3306 (default, configurable)

## 2) Installation Workflow
1. Install client EXE and release assets.
2. Install database engine silently (`install_mariadb.ps1`) or via approved enterprise method.
3. Create database + application user using `configure_app_database.ps1` -> `bootstrap_database.py`.
4. Apply ordered SQL migrations with migration runner.
5. Launch app and activate license.

## 3) Created Database User
- User: `konach_app` (default)
- Privileges: SELECT, INSERT, UPDATE, DELETE, EXECUTE, CREATE TEMPORARY TABLES on `konach_new`.
- Principle: least privilege in runtime; no schema-changing permissions required for normal use.

## 4) Created Schema
- Schema name: `konach_new`
- Migration tracking table: `schema_migrations`
- Invoice/licensing system tables are created by SQL migrations.

## 5) Fresh Install Data Behavior
### Intentionally Empty After Fresh Install
- Business/operational tables (transactions, clients, balances, invoices) remain empty.

### Seeded/Setup Data (Minimum Required)
- Schema metadata in `schema_migrations` after migration execution.
- DB users and privileges created by bootstrap process.
- Application login admin account is auto-created at first run when users table is empty, using `KONACH_DEFAULT_ADMIN_USER` and `KONACH_DEFAULT_ADMIN_PASS`.
- No demo/customer business data is inserted.

## 6) Upgrade Strategy
- Use incremental SQL files in numeric order.
- Migration runner applies only missing versions.
- Checksum mismatch triggers hard stop to prevent silent drift.
- Failed migration causes transaction rollback and stops process.

## 7) Success Signals and Logs
- MariaDB service running and set to Automatic.
- `schema_migrations` contains all expected versions.
- App starts and connects successfully.
- `logs/agency_manager.log` generated.

## 8) Operational Notes
- Keep signing private keys out of client package.
- Keep `.env` secrets managed per environment (not source-controlled).
- Validate backups and restore path during go-live.
