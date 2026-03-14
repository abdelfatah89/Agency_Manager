import sys
from pathlib import Path

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
from services.db_services.backup_service import run_backup_now

class MainWindowDashboard(QMainWindow):
    """Main dashboard window loaded from main_window.ui."""

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(str(Path(__file__).parent / "dash_main.ui"), self)

        self.account_review = None
        self.clients_review = None
        self.cmi_trans = None
        self.daily_balance = None
        self.daily_entry = None
        self.factures = None
        self._setup_ui()
        self._setup_backgrounds()

    def _setup_ui(self):
        self.Button_AccountReview.clicked.connect(self.show_account_review)
        self.Button_ClientsReview.clicked.connect(self.show_clients_review)
        self.Button_CMITrans.clicked.connect(self.show_cmi_trans)
        self.Button_DailyBalance.clicked.connect(self.show_daily_balance)
        self.Button_DailyEntry.clicked.connect(self.show_daily_entry)
        self.Button_Factures.clicked.connect(self.show_factures)
        if hasattr(self, "BackupBtn"):
            self.BackupBtn.clicked.connect(self._on_backup_clicked)
        if hasattr(self, "logoutBtn"):
            self.logoutBtn.clicked.connect(self.close)

    def _on_backup_clicked(self):
        ok, path, message = run_backup_now(reason="backup-button")
        if ok:
            QMessageBox.information(self, "Backup", f"تم إنشاء النسخة الاحتياطية بنجاح.\n{path}")
        else:
            QMessageBox.warning(self, "Backup", f"فشل إنشاء النسخة الاحتياطية.\n{message}")

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
        if self.account_review is None:
            self.account_review = AccountReviewWindow(self)
        self.account_review.show()

    def show_clients_review(self):
        if self.clients_review is None:
            self.clients_review = ClientsReviewWindow(self)
        self.clients_review.show()

    def show_cmi_trans(self):
        if self.cmi_trans is None:
            self.cmi_trans = CMITransWindow(self)
        self.cmi_trans.show()

    def show_daily_balance(self):
        if self.daily_balance is None:
            self.daily_balance = DailyBalance(self)
        self.daily_balance.show()

    def show_daily_entry(self):
        if self.daily_entry is None:
            self.daily_entry = TransactionManager(self)
        self.daily_entry.show()

    def show_factures(self):
        if self.factures is None:
            self.factures = FacturesWindow(self)
        self.factures.show()



if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)

    window = MainWindowDashboard()
    window.show()

    sys.exit(app.exec_())

