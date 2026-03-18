# Windows Deployment (MySQL/MariaDB + Licensing)

## Recommended Installer

Use **Inno Setup** for this project.

Why Inno Setup here:
- Strong support for enterprise-style scripted install flows.
- Easy execution of PowerShell/bootstrap steps for DB install and schema updates.
- Clean upgrade/uninstall behavior and robust logging.
- Better fit than NSIS for this app's DB bootstrap + migration orchestration.

## Deployment Flow

1. Install `AgencyManager.exe` and runtime files.
2. Install MariaDB silently (`install_mariadb.ps1`).
3. Ensure DB service startup mode = Automatic and service running.
4. Create DB + least-privilege app user (`bootstrap_database.py`).
5. Write `.env` with DB credentials.
6. Run ordered SQL migrations (`run_sql_migrations.py`).
7. First app launch performs license validation.

## Upgrade Flow (DB already exists)

1. Replace app binaries.
2. Skip destructive DB operations.
3. Run `run_sql_migrations.py`.
4. Migration runner reads `schema_migrations` and applies only missing scripts.
5. If migration fails: installer exits with logs; previously applied migrations remain recorded.

## Notes

- Keep MariaDB installer file in controlled build artifacts.
- Keep admin licensing tool out of customer installer package.
- Do not package private signing keys in client deliverables.
