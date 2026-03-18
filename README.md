# KONACH - Business Management System

A comprehensive PyQt5-based ERP system for managing daily transactions, invoices, clients, and financial reports with Arabic language support.

## 📁 Project Structure

```
KONACH/
│
├── 📁 Core_Application/          # Core application components
│   ├── main_window.py            # Main dashboard controller
│   ├── main_window.ui            # Main dashboard UI
│   └── theme_manager.py          # Theme and icon management
│
├── 📁 Configuration_Database/    # Database configuration
│   ├── db_config.py              # MySQL connection settings
│   ├── konach.sql                # Database schema
│   ├── test_db_connection.py    # Connection testing utility
│   └── DATABASE_SETUP.md         # Setup instructions
│
├── 📁 Transaction_Management/    # Transaction modules
│   ├── daily_entry.py            # Daily transactions entry
│   ├── transaction_manager.ui    # Transaction UI
│   ├── rasid_jour.py             # Daily balance/journal
│   └── rasid_jour.ui             # Journal UI
│
├── 📁 Financial_Modules/         # Financial management
│   ├── factures.py               # Invoicing system
│   ├── factures.ui               # Invoice UI
│   ├── account_review.py         # Account review & reports
│   ├── account_review.ui         # Account review UI
│   ├── CMI_trans.py              # CMI payment transactions
│   └── CMI_trans.ui              # CMI transactions UI
│
├── 📁 Client_Agency_Management/  # Client/Agency management
│   ├── clients_review.py         # Client management
│   └── clients_review.ui         # Client UI
│
├── 📁 Settings_System/           # Application settings
│   ├── settings.py               # Settings controller
│   ├── settings.ui               # Settings main UI
│   ├── settings_general.ui       # General settings
│   ├── settings_clients.ui       # Client settings
│   ├── settings_accounts.ui      # Account settings
│   ├── settings_users.ui         # User management
│   └── settings_agences.ui       # Agency settings
│
├── 📁 PDF_Reports/               # PDF generation
│   └── PDFmodels.py              # PDF generation with Arabic support
│
├── 📁 Documentation/             # Project documentation
│   ├── mainwindow/               # Main window docs
│   ├── settings/                 # Settings docs
│   ├── accounts_reviw/           # Account review docs
│   ├── client_review/            # Client review docs
│   ├── CMI_transactions/         # CMI transactions docs
│   └── factures/                 # Invoices docs
│
├── 📁 Configuration_Files/       # Configuration files
│   ├── theme.json                # Application theme
│   ├── table.xml                 # Table definitions
│   └── widjets_names.md          # Widget naming conventions
│
├── 📁 assets/                    # Static resources
│   └── *.svg                     # SVG icons
│
└── README.md                     # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MySQL Server
- PyQt5
- Required Python packages (see requirements below)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd KONACH
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install PyQt5 mysql-connector-python PyMuPDF reportlab arabic-reshaper python-bidi
   ```

4. **Configure database:**
    - Canonical database name for this project is: `konach_new`
   - Edit `Configuration_Database/db_config.py` with your MySQL credentials
   - Import the database schema:
     ```bash
       mysql -u root -p < konach_new.sql
     ```
   - See `Configuration_Database/DATABASE_SETUP.md` for detailed instructions

### RBAC + Role Migration Notes

- Canonical roles are:
   - `admin`
   - `tpe_employer`
   - `cashplus_employer`
- On app startup/auth usage, legacy role values (`full_access`, `manager`, `user`, etc.) are migrated to canonical values automatically.
- The `users.role` column is migrated to `VARCHAR(32)` if needed for forward-compatible role storage.

5. **Test database connection:**
   ```bash
   python Configuration_Database/test_db_connection.py
   ```

### Running the Application

**Main Dashboard:**
```bash
python Core_Application/main_window.py
```

**Daily Transactions:**
```bash
python Transaction_Management/daily_entry.py
```

**Settings:**
```bash
python Settings_System/settings.py
```

**Other Modules:**
```bash
python Financial_Modules/factures.py
python Financial_Modules/account_review.py
python Client_Agency_Management/clients_review.py
```

## 📦 Dependencies

- **PyQt5** - GUI framework
- **mysql-connector-python** - MySQL database connector
- **PyMuPDF (fitz)** - PDF processing
- **reportlab** - PDF generation
- **arabic-reshaper** - Arabic text support
- **python-bidi** - Bidirectional text algorithm

## 🏗️ Architecture

### Module Structure

Each module follows a consistent pattern:
- **Python file (.py)** - Business logic and event handling
- **UI file (.ui)** - Qt Designer interface definition
- **Relative imports** - Uses Path objects for cross-module imports

### Database Connection

All modules use the centralized database configuration:
```python
from Configuration_Database.db_config import DB_CONFIG
```

### Theme Management

Consistent theming across all modules:
```python
from Core_Application.theme_manager import ThemeManager, get_colored_icon
```

### Path Resolution

All modules use `BASE_DIR` for resolving asset and UI file paths:
```python
from pathlib import Path
BASE_DIR = Path(__file__).parent.parent
```

## 🗄️ Database Schema

The MySQL database includes tables for:
- `daily_transactions` - Transaction records
- `clients` - Customer information
- `accounts` - Account data
- `users` - User management
- `agencies` - Agency information

See `Configuration_Database/konach.sql` for complete schema.

## 🎨 Theming

The application uses a custom theme system with:
- SVG icons located in `assets/`
- Theme configuration in `Configuration_Files/theme.json`
- Dynamic icon coloring via `theme_manager.py`

## 📝 Development Guidelines

### Adding New Modules

1. Create module folder under appropriate category
2. Add Python file with proper imports:
   ```python
   import sys
   from pathlib import Path
   BASE_DIR = Path(__file__).parent.parent
   sys.path.insert(0, str(BASE_DIR))
   ```
3. Use relative paths for UI files and assets
4. Import from existing modules using full paths

### UI File Loading

Always use Path objects for UI file loading:
```python
loadUi(str(Path(__file__).parent / "your_ui_file.ui"), self)
```

### Asset References

Reference assets using BASE_DIR:
```python
icon_path = str(BASE_DIR / "assets/icon_name.svg")
```

## 🔧 Troubleshooting

### Import Errors
- Ensure `sys.path.insert(0, str(BASE_DIR))` is at the top of each module
- Check that module paths match the actual folder structure

### UI File Not Found
- Verify UI files are in the same directory as their Python counterparts
- Use `Path(__file__).parent` for relative UI file paths

### Database Connection Issues
- Check MySQL server is running
- Verify credentials in `Configuration_Database/db_config.py`
- Run `test_db_connection.py` to diagnose

### Asset/Icon Not Found
- Ensure assets are in the `assets/` folder at project root
- Use `BASE_DIR / "assets/filename.svg"` for absolute paths

## 💾 Database Backup

The app now creates compressed MySQL dumps in:

- `backups/database/`

Backup is triggered in two ways:

- Clicking `BackupBtn` in the main window
- Automatically once when the app closes

### Backup Environment Variables

Set these in your `.env` (optional):

- `DB_BACKUP_ENABLED=1`
- `DB_BACKUP_DIR=backups/database`
- `DB_BACKUP_RETENTION_COUNT=5`
- `MYSQLDUMP_PATH=C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe` (only if `mysqldump` is not in PATH)

Optional cloud sync with `rclone` right after each successful backup:

- `DB_BACKUP_RCLONE_ENABLED=1`
- `RCLONE_PATH=C:\\rclone\\rclone.exe` (optional, only if `rclone` is not in PATH)
- `DB_BACKUP_RCLONE_SOURCE_DIR=D:\\.Code\\KONACH\\backups\\database`
- `DB_BACKUP_RCLONE_REMOTE=database_backup`
- `DB_BACKUP_RCLONE_REMOTE_PATH=databases`

With the values above, the backup service will run the equivalent of:

```powershell
rclone copy D:\.Code\KONACH\backups\database database_backup:databases
```

### Run Backup Manually

```powershell
D:/.Code/KONACH/.venv/Scripts/python.exe scripts/run_db_backup.py
```

### Optional Windows Task Scheduler (extra layer)

If you also want backups when the app is not opened, you can still add a Task Scheduler job that runs:

- `D:\.Code\KONACH\.venv\Scripts\python.exe D:\.Code\KONACH\scripts\run_db_backup.py`

## ☁️ Cloud Sync (Extra Safety)

### Option 1: Google Drive Desktop (easiest)

1. Install Google Drive for Desktop
2. Set `DB_BACKUP_DIR` to a Drive-synced folder, for example:
   - `C:\Users\<you>\My Drive\KONACH_Backups`
3. Backups will be synced automatically.

### Option 2: OneDrive Free Tier

1. Use OneDrive synced folder path for `DB_BACKUP_DIR`
2. Example:
   - `C:\Users\<you>\OneDrive\KONACH_Backups`

### Option 3: rclone (works with many free cloud providers)

1. Install `rclone`
2. Configure remote once:
   - `rclone config`
3. Add a second scheduled task:
   - `rclone copy D:\.Code\KONACH\backups\database remote:KONACH_Backups --transfers 2`

Tip: keep local backups + cloud copies together for better protection.

## 🗄️ MySQL/MariaDB Production Deployment

### Why MySQL/MariaDB for this project

- Strong transactional guarantees (InnoDB) needed for finance and invoice numbering.
- Mature Windows service operation and silent MSI installers.
- Good fit for SQLAlchemy + PyMySQL stack already used by KONACH.
- Supports online schema evolution via ordered SQL migration scripts.

### Professional Windows Install/Upgrade Workflow

Use **Inno Setup** with scripted deployment steps:

1. Install app binaries.
2. Install MariaDB silently.
3. Ensure DB service auto-start.
4. Create DB and least-privilege app user.
5. Write `.env` with runtime DB credentials.
6. Run ordered SQL migrations.
7. Start app and enforce machine-locked license validation.

Reference files:

- `deployment/windows/inno/AgencyManager.iss`
- `deployment/windows/scripts/install_mariadb.ps1`
- `deployment/windows/scripts/configure_app_database.ps1`
- `deployment/windows/scripts/apply_sql_updates.ps1`
- `scripts/bootstrap_database.py`
- `scripts/run_sql_migrations.py`
- `scripts/run_sql_migrations_with_root.py`

### Upgrade behavior (existing database)

- Do not recreate or drop the existing database.
- Run migration runner only.
- Runner checks `schema_migrations` and applies only missing scripts in order.
- If a migration fails, setup aborts and logs the exact failed script/version.

## 🧱 SQL Migration Strategy

Versioned SQL files are stored in `sql/` and applied in numeric order:

- `sql/001_initial_schema.sql`
- `sql/002_add_invoice_tables.sql`
- `sql/003_add_license_tables.sql`
- `sql/004_add_license_indexes.sql`

Migration tracking table:

- `schema_migrations`
   - `version`
   - `script_name`
   - `checksum_sha256`
   - `applied_at`
   - `execution_ms`
   - `applied_by`

Runtime component:

- `services/db_services/sql_migration_runner.py`

## 🔐 Machine-Locked Licensing

### Fingerprint design

Fingerprint is built from multiple identifiers (with fallback handling):

- BIOS/board UUID
- Primary disk serial
- Windows MachineGuid
- MAC address
- Machine name

Identifiers are normalized, composed into canonical JSON, then SHA-256 hashed.

Reference:

- `services/licensing/fingerprint.py`

### License architecture

Professional choice used here: **signed JSON license (Ed25519)**.

- Client app contains only public key (verification only).
- Admin tool holds private key (signing only, never shipped).
- License payload includes machine fingerprint, issue time, status, and optional expiry.

Client-side modules:

- `services/licensing/license_codec.py`
- `services/licensing/license_service.py`

### Startup behavior

- On first run without license:
   - generate request code
   - show request code and prompt for signed license JSON
- On every startup:
   - verify signature
   - verify machine fingerprint match
   - verify status and expiry
   - write audit event to DB when available

Handled states:

- missing license
- corrupted/invalid signature
- expired license
- revoked/inactive status
- hardware mismatch
- database unavailable (app still validates local signed license and logs DB errors)

## 🧭 Admin Tool Isolation

Admin licensing tool is intentionally separate:

- `admin_license_tool/` (private/internal)
- not packaged in customer installer
- private key ignored via `.gitignore`

Admin tool files:

- `admin_license_tool/generate_keys.py`
- `admin_license_tool/issue_license.py`
- `admin_license_tool/README.md`

Client vs Admin separation:

- **Client app contains**: fingerprint collection, request generation, signature verification, license import.
- **Admin tool contains**: private signing key and license issuance logic.
- **Never ship**: `admin_license_tool/keys/private_key.pem`.

## 🧩 Licensing Tables (DB)

- `licensed_machines`
- `app_installations`
- `license_audit_log`
- `schema_migrations`

These are separate from business/invoice tables and intended for operational security/audit concerns.

## 🧾 Invoice Numbering (Production)

Invoice numbers are now database-backed and generated by a dedicated service layer.

- Source of truth: database table `invoices`
- Number format: `FA-YYYYMM-XXXXXX` (example: `FA-202603-000123`)
- Concurrency-safe allocation: atomic counter increment in MySQL table `invoice_number_counters`
- Retry safety: idempotency key by source + payload prevents duplicate numbers for the same print action

### Schema Update

Run once per environment (or include in deploy scripts):

```powershell
D:/.Code/KONACH/.venv/Scripts/python.exe scripts/apply_invoice_schema_update.py
```

The app also attempts schema initialization at startup.

### Service Layer Entry Points

- `services/invoice_service.py`
   - `reserve_invoice_number(...)`
   - `mark_invoice_generated(...)`
   - `mark_invoice_failed(...)`
   - `ensure_invoice_schema_ready()`

## 📦 Executable Packaging (PyInstaller)

This project includes a production spec file:

- `AgencyManager.spec`

### Build Steps

1. Create and activate a clean virtual environment
2. Install runtime dependencies:

```powershell
pip install -r requirements.txt
pip install pyinstaller
```

3. Build one-file executable:

```powershell
pyinstaller --clean --noconfirm AgencyManager.spec
```

4. Output executable:

- `dist/AgencyManager.exe`

### Packaging Notes

- The spec includes app resources (`assets`, `src`, `theme`, `services`) and runtime config (`.env` when present).
- Hidden imports for SQLAlchemy, PyMySQL, dotenv, Jinja2, WeasyPrint, and `PyQt5.QtSvg` are included.
- Build on the same OS target as deployment (Windows for Windows `.exe`).

## 📄 License

[Add your license information here]

## 👥 Contributors

[Add contributor information here]

## 📧 Support

For issues and questions, please [contact information or issue tracker]

---

**Last Updated:** March 18, 2026
