import sys
import logging
import os
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)
from PyQt5.QtGui import QFont, QIcon, QFontDatabase

from src.login.login import LoginWindow
from src.utils import resource_path
from services.app_logging import configure_logging
from services.auth_service import ensure_default_admin_user
from services.db_services.backup_service import run_backup_now
from services.db_services.db_config import initialize_database_connection
from services.license.license_service import (
    import_license_blob,
    validate_current_license,
)


logger = logging.getLogger(__name__)


def _configure_app_fonts(app: QApplication) -> None:
    fonts_dir = resource_path("assets/fonts")
    selected_family = ""

    if os.path.isdir(fonts_dir):
        for name in sorted(os.listdir(fonts_dir)):
            if not name.lower().endswith((".ttf", ".otf")):
                continue
            font_file = os.path.join(fonts_dir, name)
            font_id = QFontDatabase.addApplicationFont(font_file)
            if font_id < 0:
                continue
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                selected_family = families[0]
                break

    if selected_family:
        app.setFont(QFont(selected_family, 10))
        logger.info("Loaded bundled font family: %s", selected_family)
        return

    logger.warning("No bundled font file found in assets/fonts; falling back to Segoe UI")
    app.setFont(QFont("Segoe UI", 10))


class LicenseActivationDialog(QDialog):
    def __init__(self, reason: str, machine_fingerprint: str, request_code: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("KONACH License Required")
        self.setWindowIcon(QApplication.windowIcon())
        self.resize(760, 620)

        root = QVBoxLayout(self)

        reason_label = QLabel(reason)
        reason_label.setWordWrap(True)
        root.addWidget(reason_label)

        root.addWidget(QLabel("Machine Fingerprint:"))
        self.fingerprint_text = QTextEdit()
        self.fingerprint_text.setReadOnly(True)
        self.fingerprint_text.setPlainText(machine_fingerprint)
        self.fingerprint_text.setMaximumHeight(90)
        root.addWidget(self.fingerprint_text)

        request_header = QHBoxLayout()
        request_header.addWidget(QLabel("Request Code:"))
        copy_btn = QPushButton("Copy Request Code")
        copy_btn.clicked.connect(self._copy_request_code)
        request_header.addWidget(copy_btn)
        request_header.addStretch(1)
        root.addLayout(request_header)

        self.request_code_text = QTextEdit()
        self.request_code_text.setReadOnly(True)
        self.request_code_text.setPlainText(request_code)
        self.request_code_text.setMinimumHeight(120)
        root.addWidget(self.request_code_text)

        root.addWidget(QLabel("Paste signed license JSON from administrator:"))
        self.license_input = QTextEdit()
        self.license_input.setPlaceholderText("Paste signed license JSON here...")
        self.license_input.setMinimumHeight(220)
        root.addWidget(self.license_input)

        actions = QHBoxLayout()
        actions.addStretch(1)
        self.activate_btn = QPushButton("Activate")
        self.activate_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        actions.addWidget(self.activate_btn)
        actions.addWidget(cancel_btn)
        root.addLayout(actions)

    def _copy_request_code(self) -> None:
        text = self.request_code_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Copy Failed", "Request code is empty.")
            return
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copied", "Request code copied to clipboard.")

    def license_blob(self) -> str:
        return self.license_input.toPlainText().strip()


def _enforce_license() -> bool:
    result = validate_current_license()
    if result.is_valid:
        return True

    request_code = ""
    if result.payload:
        request_code = str(result.payload.get("request_code") or "")

    while True:
        dialog = LicenseActivationDialog(
            reason=result.reason,
            machine_fingerprint=result.machine_fingerprint,
            request_code=request_code,
        )
        if dialog.exec_() != QDialog.Accepted:
            QMessageBox.critical(None, "License Required", "Application is locked until a valid license is provided.")
            return False

        license_blob = dialog.license_blob()
        if not license_blob:
            QMessageBox.warning(None, "License Required", "License text is empty.")
            continue

        try:
            import_license_blob(license_blob)
            recheck = validate_current_license()
            if recheck.is_valid:
                return True
            QMessageBox.warning(None, "License Invalid", recheck.reason)
        except Exception as exc:
            logger.exception("License import failed")
            QMessageBox.warning(None, "License Invalid", str(exc))

def main() -> None:
    configure_logging()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("assets/icons/window_icon.ico")))
    _configure_app_fonts(app)
    
    # Set application metadata
    app.setApplicationName("KONACH")
    app.setOrganizationName("KONACH")

    if not initialize_database_connection():
        QMessageBox.critical(
            None,
            "Database Error",
            "Unable to connect to database and automatic setup failed. Check .env MySQL credentials.",
        )
        sys.exit(3)

    created_admin = ensure_default_admin_user()
    if created_admin:
        username, _ = created_admin
        logger.info("Default admin user created: %s", username)
    else:
        logger.info("Default admin user already exists or users table is populated")

    #if not _enforce_license():
    #    sys.exit(2)

    # Start with login screen.
    window = LoginWindow()
    window.setWindowIcon(app.windowIcon())
    window.show()

    # Execute application
    exit_code = app.exec_()

    # Safety backup on app shutdown.
    ok, path, message = run_backup_now(reason="app-close")
    if ok:
        logger.info("Backup created on close: %s", path)
    else:
        logger.warning("Backup on close did not complete: %s", message)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
