# SQL Migration and Update Strategy

## Folder Structure
- `sql/001_initial_schema.sql`
- `sql/002_add_invoice_tables.sql`
- `sql/003_add_license_tables.sql`
- `sql/004_add_license_indexes.sql`

## Version Tracking
- `schema_migrations` stores:
  - `version`
  - `script_name`
  - `checksum_sha256`
  - `applied_at`
  - `execution_ms`
  - `applied_by`

## Runner Behavior
- Discovers numeric SQL files in ascending order.
- Applies only missing versions.
- Verifies checksum for already-applied versions.
- Stops with error if checksum mismatch is detected.

## Safety
- Runs inside transaction scope (`engine.begin()`).
- On error, current migration transaction is rolled back.
- Partial silent drift is prevented by checksum enforcement.

## Operational Guidance
- Never edit released migration files.
- Add new migrations with new version numbers.
- Keep migrations backward-compatible and additive where possible.
