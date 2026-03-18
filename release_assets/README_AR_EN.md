# KONACH Agency Manager - Client Deployment Guide (EN + AR)

## English

### 1) Product Overview
KONACH Agency Manager is a desktop financial operations system for transaction entry, balance tracking, invoicing, and reporting. The application is licensed per machine and uses MySQL/MariaDB as the required backend.

### 2) System Requirements
- Windows 10/11 (64-bit)
- Minimum 8 GB RAM (recommended 16 GB)
- MariaDB 10.6+ or MySQL 8.0+
- Network access to database host/port
- Write permission to application folder, logs folder, and ProgramData license folder

### 3) Installation Steps
1. Install the client package into `C:\Program Files\KONACH`.
2. Install MariaDB using the provided installer scripts or your enterprise database method.
3. Configure database and create app user using `install/configure_app_database.ps1`.
4. Apply schema updates using `install/apply_sql_updates.ps1`.
5. Create `config/.env` from `config/.env.example` and set secure values.
6. Launch `KONACH.exe`.

### 4) MySQL/MariaDB Installation Summary
- Engine: MariaDB 10.6+ (recommended) or MySQL 8.0+
- Service: `MariaDB` (startup type = Automatic)
- Required schema: `konach_new`
- Required app DB user: `konach_app` (least privilege, no DDL in normal runtime)

### 5) First Run Steps
1. Start `KONACH.exe`.
2. If no license is installed, copy generated request code.
3. Send request code to admin licensing team.
4. Paste signed license JSON in activation dialog.
5. Login with app credentials.

### 6) Configuration Steps
Set values in `.env` (do not store real values in source control):
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `KONACH_LICENSE_PUBLIC_KEY_PEM` (optional when `config/license_public_key.pem` exists)
- Optional backup settings (`DB_BACKUP_*`, `RCLONE_*`)

### 7) License Activation and Usage
- License is machine-bound through hardware fingerprint.
- Client validates signed license using Ed25519 public key.
- Public key can be provided as:
  - PEM text
  - Base64 raw Ed25519 public key
  - Base64 DER/SPKI public key
- Fallback file path supported: `config/license_public_key.pem`

### 8) Running the Program
- Double-click `KONACH.exe`
- Logs are written to `logs/agency_manager.log`
- License file is stored under `%ProgramData%\KONACH\license\license.json` unless overridden

### 9) Logs and Basic Troubleshooting
- App logs: `logs/agency_manager.log`
- Migration failures: check console/installer logs and `schema_migrations` table
- License errors:
  - `MalformedFraming`: invalid key format in env
  - `License signature is invalid`: wrong public key vs signing private key
  - `Hardware fingerprint mismatch`: license issued for another machine

### 10) Backup and Restore Basics
- Backup script: `scripts/run_db_backup.py`
- Backup location: `backups/database` (or configured path)
- Restore by importing dump into target database and re-running migrations if required

### 11) Upgrade Notes
1. Replace binaries.
2. Keep existing `.env` and license files.
3. Run SQL migrations (only missing versions are applied).
4. Validate startup, login, and critical modules.

### 12) Support and Maintenance
- Keep SQL migrations immutable once released.
- Rotate DB and app credentials according to policy.
- Keep signing private key outside client environment.
- Review logs weekly and backup restore monthly.

---

## العربية

### 1) نظرة عامة على المنتج
KONACH Agency Manager هو نظام مكتبي لإدارة العمليات المالية اليومية، وإدخال المعاملات، ومتابعة الأرصدة، وإصدار الفواتير، وإعداد التقارير. التطبيق مرتبط بترخيص لكل جهاز ويعتمد على MySQL/MariaDB كقاعدة بيانات أساسية.

### 2) متطلبات النظام
- Windows 10/11 (64-bit)
- ذاكرة 8 جيجابايت كحد أدنى (يفضل 16 جيجابايت)
- MariaDB 10.6+ أو MySQL 8.0+
- اتصال شبكي بخادم قاعدة البيانات
- صلاحية كتابة لمجلد التطبيق والسجلات ومجلد الترخيص في ProgramData

### 3) خطوات التثبيت
1. تثبيت حزمة العميل في `C:\Program Files\KONACH`.
2. تثبيت MariaDB عبر سكربتات التثبيت المرفقة أو عبر آلية المؤسسة.
3. إعداد قاعدة البيانات وإنشاء مستخدم التطبيق عبر `install/configure_app_database.ps1`.
4. تطبيق تحديثات المخطط عبر `install/apply_sql_updates.ps1`.
5. إنشاء ملف `config/.env` انطلاقا من `config/.env.example` مع القيم الآمنة.
6. تشغيل `KONACH.exe`.

### 4) ملخص تثبيت MySQL/MariaDB
- المحرك: MariaDB 10.6+ (موصى به) أو MySQL 8.0+
- الخدمة: `MariaDB` مع تشغيل تلقائي
- مخطط قاعدة البيانات المطلوب: `konach_new`
- مستخدم قاعدة البيانات المطلوب للتطبيق: `konach_app` بصلاحيات محدودة

### 5) خطوات التشغيل الأول
1. تشغيل `KONACH.exe`.
2. عند عدم وجود ترخيص، انسخ كود الطلب.
3. أرسل كود الطلب لمسؤول التراخيص.
4. الصق ملف ترخيص JSON الموقّع في نافذة التفعيل.
5. سجّل الدخول بحساب التطبيق.

### 6) خطوات الإعداد
اضبط القيم في ملف `.env` (ولا تضع القيم الحقيقية في المستودع):
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `KONACH_LICENSE_PUBLIC_KEY_PEM` (اختياري عند توفر `config/license_public_key.pem`)
- إعدادات النسخ الاحتياطي الاختيارية (`DB_BACKUP_*`, `RCLONE_*`)

### 7) تفعيل الترخيص واستخدامه
- الترخيص مرتبط ببصمة الجهاز.
- التطبيق يتحقق من التوقيع باستخدام المفتاح العام Ed25519.
- يمكن إدخال المفتاح العام بصيغة:
  - PEM
  - Base64 لمفتاح Ed25519 خام
  - Base64 لمفتاح DER/SPKI
- يوجد مسار بديل افتراضي: `config/license_public_key.pem`

### 8) تشغيل البرنامج
- تشغيل `KONACH.exe`
- السجلات في `logs/agency_manager.log`
- ملف الترخيص في `%ProgramData%\KONACH\license\license.json` (افتراضيا)

### 9) السجلات وحل المشاكل الأساسية
- سجل التطبيق: `logs/agency_manager.log`
- فشل الترحيلات: راجع سجلات التثبيت وجدول `schema_migrations`
- أخطاء الترخيص:
  - `MalformedFraming`: صيغة مفتاح عامة غير صحيحة
  - `License signature is invalid`: عدم تطابق المفتاح العام مع الخاص
  - `Hardware fingerprint mismatch`: الترخيص صادر لجهاز آخر

### 10) النسخ الاحتياطي والاستعادة
- سكربت النسخ: `scripts/run_db_backup.py`
- موقع النسخ: `backups/database` أو المسار المخصص
- الاستعادة تتم عبر استيراد نسخة SQL ثم تشغيل الترحيلات عند الحاجة

### 11) ملاحظات الترقية
1. استبدل ملفات التطبيق التنفيذية.
2. احتفظ بملف `.env` وملف الترخيص الحالي.
3. شغّل ترحيلات SQL (يتم تطبيق الناقص فقط).
4. تحقق من التشغيل وتسجيل الدخول والوظائف الأساسية.

### 12) الدعم والصيانة
- لا تعدّل ملفات ترحيل SQL بعد إصدارها.
- بدّل كلمات المرور دوريا.
- احفظ المفتاح الخاص بالتوقيع خارج بيئة العميل.
- راجع السجلات أسبوعيا ونفذ اختبار استعادة شهريا.
