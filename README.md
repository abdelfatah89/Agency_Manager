# KONACH

نظام مكتبي لإدارة العمليات اليومية والفواتير والمراجعة المالية.

## 1) المتطلبات

- Windows 10/11
- Python 3.10 أو أحدث
- MySQL عبر AppServ (تثبيت يدوي)

## 2) إعداد قاعدة البيانات (AppServ)

1. ثبّت AppServ وتأكد أن خدمة MySQL تعمل.
2. حدّث ملف .env بقيم MySQL الصحيحة:
   - DB_HOST
   - DB_PORT
   - DB_USER
   - DB_PASSWORD
   - DB_NAME

ملاحظة: التطبيق يطبّق التهيئة تلقائيًا عند أول تشغيل إذا كانت بيانات .env صحيحة.

- يتم تطبيق `sql/001_initial_schema.sql` لتجهيز سجل الهجرات.
- إذا كانت الجداول الأساسية غير موجودة، يتم تطبيق المخطط الكامل من `sql/002_business_schema.sql` تلقائيًا.
- بعد ذلك يتم تطبيق الهجرات الإضافية من مجلد `sql` تلقائيًا.
- يتم إنشاء المستخدم الإداري الافتراضي تلقائيًا عند أول تشغيل فقط عندما يكون جدول `users` فارغًا، عبر:
  - `KONACH_DEFAULT_ADMIN_USER`
  - `KONACH_DEFAULT_ADMIN_PASS`

## 3) إعداد بيئة بايثون

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 4) تشغيل التطبيق من المصدر

```powershell
python main.py
```

## 5) البناء (PyInstaller onedir)

```powershell
.\scripts\build_release.ps1
```

الناتج الأساسي يكون داخل dist\KONACH بعد البناء.

## 6) الأيقونات والخطوط

- أيقونة النافذة: assets/icons/window_icon.ico
- أيقونة الملف التنفيذي: assets/icons/exe_icon.ico
- الخطوط المدمجة: assets/fonts

إذا كان مجلد fonts فارغًا، سيستخدم التطبيق خطًا احتياطيًا تلقائيًا.

## 7) النسخ الاحتياطي عبر rclone

الملفات المتعلقة بـ rclone موجودة في مجلد rclone.

### إعداد سريع

1. ثبّت rclone على الجهاز.
2. نفّذ الأمر التالي مرة واحدة للإعداد:

```powershell
rclone config
```

3. أنشئ remote (مثال: gdrive).
4. جرّب الاتصال:

```powershell
rclone lsd gdrive:
```

5. مثال رفع نسخة احتياطية:

```powershell
rclone copy .\backups\database gdrive:KONACH-Backups\database
```

## 8) ملاحظات سريعة

- عند فشل الاتصال بقاعدة البيانات، راجع قيم .env وتأكد أن MySQL يعمل.
- عند تشغيل نسخة exe، تأكد وجود مجلد _internal وملفات assets ضمن توزيع onedir.
- لا تحذف مجلد keys إذا كنت تستخدم نظام التراخيص.
