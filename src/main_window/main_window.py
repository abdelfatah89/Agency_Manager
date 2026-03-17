import sys
from pathlib import Path
from typing import Optional

# Add project root to path for imports
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt

from src.account_review.account_review import AccountReviewWindow
from src.clients_review.clients_review import ClientsReviewWindow
from src.cmi_trans.CMI_trans import CMITransWindow
from src.daily_balance.daily_balance import DailyBalance
from src.daily_entry.daily_entry import TransactionManager
from src.factures.factures import FacturesWindow
from src.login.compny_info import CompanyInfoDialog
from src.login.user_manager import UserManagerDialog
from src.utils.company_info import load_company_info
from services.db_services.backup_service import run_backup_now
from services.access_control import (
    AuthenticatedUser,
    BUTTON_PERMISSIONS,
    PERM_OPEN_ACCOUNT_REVIEW,
    PERM_OPEN_CLIENTS_REVIEW,
    PERM_OPEN_CMI_TRANS,
    PERM_OPEN_COMPANY_INFO,
    PERM_OPEN_DAILY_BALANCE,
    PERM_OPEN_DAILY_ENTRY,
    PERM_OPEN_FACTURES,
    PERM_OPEN_USER_MANAGER,
    PERM_RUN_BACKUP,
    has_permission,
)

class MainWindowDashboard(QMainWindow):
    """Main dashboard window loaded from main_window.ui."""

    def __init__(self, parent=None, current_user: Optional[dict] = None):
        super().__init__(parent)
        loadUi(str(Path(__file__).parent / "dash_main.ui"), self)
        self.current_user = AuthenticatedUser.from_payload(current_user)
        self.current_role = self.current_user.role

        self.account_review = None
        self.clients_review = None
        self.cmi_trans = None
        self.daily_balance = None
        self.daily_entry = None
        self.factures = None
        self._setup_ui()
        self._setup_backgrounds()
        self._apply_role_permissions()
        self._load_company_footer()

    def _setup_ui(self):
        self.Button_AccountReview.clicked.connect(self.show_account_review)
        self.Button_ClientsReview.clicked.connect(self.show_clients_review)
        self.Button_CMITrans.clicked.connect(self.show_cmi_trans)
        self.Button_DailyBalance.clicked.connect(self.show_daily_balance)
        self.Button_DailyEntry.clicked.connect(self.show_daily_entry)
        self.Button_Factures.clicked.connect(self.show_factures)
        if hasattr(self, "BackupBtn"):
            self.BackupBtn.clicked.connect(self._on_backup_clicked)
        if hasattr(self, "InfoBtn"):
            self.InfoBtn.clicked.connect(self._open_company_info)
        if hasattr(self, "UserManagerBtn"):
            self.UserManagerBtn.clicked.connect(self._open_user_manager)
        if hasattr(self, "logoutBtn"):
            self.logoutBtn.clicked.connect(self.close)

    def _apply_role_permissions(self):
        for btn_name, permission in BUTTON_PERMISSIONS.items():
            btn = getattr(self, btn_name, None)
            if btn is not None:
                btn.setEnabled(has_permission(self.current_role, permission))

    def _ensure_permission(self, permission: str, denied_message: str = "ليس لديك صلاحية لهذا القسم") -> bool:
        if has_permission(self.current_role, permission):
            return True
        QMessageBox.warning(self, "صلاحيات", denied_message)
        return False

    @staticmethod
    def _clean_code(value: str, prefix: str) -> str:
        text = (value or "").strip()
        lowered = text.lower().replace(" ", "")
        prefix_low = prefix.lower()
        if lowered.startswith(prefix_low + ":"):
            text = text.split(":", 1)[1].strip()
        if lowered.startswith(prefix_low) and len(text) > len(prefix):
            text = text[len(prefix):].strip(" :")
        return text

    def _load_company_footer(self):
        info = load_company_info()
        ice = self._clean_code(info.get("ice", "-"), "ICE") or "-"
        if_code = self._clean_code(info.get("if_code", "-"), "IF") or "-"
        rc = self._clean_code(info.get("rc", "-"), "RC") or "-"
        if hasattr(self, "footerIceLabel"):
            self.footerIceLabel.setText(f"ICE: {ice}")
        if hasattr(self, "footerIfLabel"):
            self.footerIfLabel.setText(f"IF: {if_code}")
        if hasattr(self, "footerRcLabel"):
            self.footerRcLabel.setText(f"RC: {rc}")

    def _on_backup_clicked(self):
        if not self._ensure_permission(PERM_RUN_BACKUP):
            return
        ok, path, message = run_backup_now(reason="backup-button")
        if ok:
            QMessageBox.information(self, "Backup", f"تم إنشاء النسخة الاحتياطية بنجاح.\n{path}")
        else:
            QMessageBox.warning(self, "Backup", f"فشل إنشاء النسخة الاحتياطية.\n{message}")

    def _open_company_info(self):
        if not self._ensure_permission(PERM_OPEN_COMPANY_INFO):
            return
        dlg = CompanyInfoDialog(self)
        if dlg.exec_():
            self._load_company_footer()

    def _open_user_manager(self):
        if not self._ensure_permission(PERM_OPEN_USER_MANAGER):
            return
        dlg = UserManagerDialog(self)
        dlg.exec_()

    def _setup_backgrounds(self):
        """Set background images with absolute paths."""
        # Main window background
        bg_path = str(BASE_DIR / "assets/background.png").replace("\\", "/")
        main_style = self.styleSheet() + f"""
QMainWindow#MainWindow {{
    border-image: url({bg_path}) 0 0 0 0 stretch stretch;
}}
"""
        self.setStyleSheet(main_style)
        
        # Home frame background with gradient overlay
        hamo_bg_path = str(BASE_DIR / "assets/hamobackground.png").replace("\\", "/")
        frame_style = f"""
QFrame#homeFrame {{
    border-image: url({hamo_bg_path}) 0 0 0 0 stretch stretch;
}}

QFrame#homeFrame {{
   background-color: qlineargradient(
        spread:pad, 
        x1:0, y1:0, x2:1, y2:1, 
        stop:0 rgba(255, 150, 0, 204),
        stop:0.5 rgba(0, 0, 0, 102),
        stop:1 rgba(0, 0, 0, 204)
    );
}}
"""
        self.homeFrame.setStyleSheet(self.homeFrame.styleSheet() + frame_style)

    def show_account_review(self):
        if not self._ensure_permission(PERM_OPEN_ACCOUNT_REVIEW):
            return
        if self.account_review is None:
            try:
                self.account_review = AccountReviewWindow(self, current_user_role=self.current_role)
            except PermissionError:
                QMessageBox.warning(self, "صلاحيات", "ليس لديك صلاحية للوصول إلى مراجعة الحسابات")
                return
        self.account_review.show()

    def show_clients_review(self):
        if not self._ensure_permission(PERM_OPEN_CLIENTS_REVIEW):
            return
        if self.clients_review is None:
            try:
                self.clients_review = ClientsReviewWindow(self, current_user_role=self.current_role)
            except PermissionError:
                QMessageBox.warning(self, "صلاحيات", "ليس لديك صلاحية للوصول إلى مراجعة العملاء")
                return
        self.clients_review.show()

    def show_cmi_trans(self):
        if not self._ensure_permission(PERM_OPEN_CMI_TRANS):
            return
        if self.cmi_trans is None:
            try:
                self.cmi_trans = CMITransWindow(self, current_user_role=self.current_role)
            except PermissionError:
                QMessageBox.warning(self, "صلاحيات", "ليس لديك صلاحية للوصول إلى معاملات CMI")
                return
        self.cmi_trans.show()

    def show_daily_balance(self):
        if not self._ensure_permission(PERM_OPEN_DAILY_BALANCE):
            return
        if self.daily_balance is None:
            try:
                self.daily_balance = DailyBalance(self, current_user_role=self.current_role)
            except PermissionError:
                QMessageBox.warning(self, "صلاحيات", "ليس لديك صلاحية للوصول إلى الرصيد اليومي")
                return
        self.daily_balance.show()

    def show_daily_entry(self):
        if not self._ensure_permission(PERM_OPEN_DAILY_ENTRY):
            return
        if self.daily_entry is None:
            self.daily_entry = TransactionManager(self)
        self.daily_entry.show()

    def show_factures(self):
        if not self._ensure_permission(PERM_OPEN_FACTURES):
            return
        if self.factures is None:
            try:
                self.factures = FacturesWindow(self, current_user_role=self.current_role)
            except PermissionError:
                QMessageBox.warning(self, "صلاحيات", "ليس لديك صلاحية للوصول إلى الفواتير")
                return
        self.factures.show()



if __name__ == "__main__":
    raise SystemExit("Run main.py to start the authenticated application flow.")

