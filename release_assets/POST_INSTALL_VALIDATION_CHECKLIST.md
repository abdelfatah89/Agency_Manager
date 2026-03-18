# Post-Install Validation Checklist

## Database and Schema
- [ ] MariaDB/MySQL service is running.
- [ ] Database `konach_new` exists.
- [ ] App user `konach_app` can connect with configured password.
- [ ] `schema_migrations` exists and latest version is applied.
- [ ] Required setup tables exist (`invoices`, `invoice_number_counters`, `licensed_machines`, `app_installations`, `license_audit_log`).
- [ ] Business tables are empty on fresh install (no demo data unless explicitly approved).

## Application Runtime
- [ ] `KONACH.exe` launches successfully.
- [ ] Login screen appears without runtime import errors.
- [ ] `logs/agency_manager.log` is created after startup.

## Licensing
- [ ] Request code is generated on unlicensed first run.
- [ ] Admin tool can issue a signed license for the same machine.
- [ ] Client accepts valid license and rejects tampered or wrong-machine license.

## Admin Tool
- [ ] `LicenseAdminTool.exe` launches in separate package.
- [ ] Key generation works.
- [ ] License issue flow works end-to-end.
- [ ] No private signing material exists in client package.

## Backups and Paths
- [ ] Backup path exists and is writable.
- [ ] Manual backup command works.
- [ ] Optional cloud sync path works (if enabled).

## Installer/Upgrade
- [ ] Installer scripts run without interactive errors in target environment.
- [ ] Upgrade applies only missing SQL files and preserves existing business data.
