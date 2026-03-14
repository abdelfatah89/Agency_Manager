import sys
from pathlib import Path

from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView

from src.account_review.func import setup_funcs
from src.utils import asset_url

class AccountReviewWindow(QMainWindow):
    """Account review window loaded from account_review.ui."""

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(str(Path(__file__).parent / "account_review.ui"), self)
        self._fix_widget_icons()
        self._setup()
        setup_funcs(self)

    def _fix_widget_icons(self):
        """Fix QComboBox and QDateEdit arrow icons with absolute paths."""
        from PyQt5.QtWidgets import QComboBox, QDateEdit
        
        calendar_path = asset_url("calendar.svg")
        chevron_path = asset_url("chevron_down.svg")
        
        # Fix all QDateEdit widgets
        for widget in self.findChildren(QDateEdit):
            current_style = widget.styleSheet()
            if "::down-arrow" in current_style:
                new_style = current_style
                for pattern in ("url(../../assets/calendar.svg)", "url(/assets/calendar.svg)"):
                    new_style = new_style.replace(pattern, f"url({calendar_path})")
                widget.setStyleSheet(new_style)
        
        # Fix all QComboBox widgets
        for widget in self.findChildren(QComboBox):
            current_style = widget.styleSheet()
            if "::down-arrow" in current_style:
                new_style = current_style
                for pattern in ("url(../../assets/chevron_down.svg)", "url(/assets/chevron_down.svg)"):
                    new_style = new_style.replace(pattern, f"url({chevron_path})")
                widget.setStyleSheet(new_style)

    def _setup(self):
        # Later you can:
        # - populate journalTable with account movements
        # - hook up search/filter/print/export and pagination buttons
        self.Input_FromDate.setDate(QDate.currentDate())
        self.Input_ToDate.setDate(QDate.currentDate())
        
        # Stretch table columns to fill available width
        header = self.Table_journal.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        #header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.Table_journal.verticalHeader().setDefaultSectionSize(35)
        self.Table_journal.verticalHeader().setVisible(False)
        self.Table_journal.horizontalHeader().setDefaultAlignment(
            Qt.AlignCenter | Qt.AlignVCenter
        )

        self.Button_CloseWindow.clicked.connect(self.close)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)

    window = AccountReviewWindow()
    window.show()

    sys.exit(app.exec_())

