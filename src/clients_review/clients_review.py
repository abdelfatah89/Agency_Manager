import sys
from pathlib import Path

from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView

from src.clients_review.func import setup_funcs
from src.utils import asset_url
from services.access_control import PERM_OPEN_CLIENTS_REVIEW, has_permission


class ClientsReviewWindow(QMainWindow):
    """Customers review window loaded from clients_review.ui."""

    def __init__(self, parent=None, current_user_role=None):
        super().__init__(parent)
        if current_user_role and not has_permission(current_user_role, PERM_OPEN_CLIENTS_REVIEW):
            raise PermissionError("User is not allowed to access clients review")
        loadUi(str(Path(__file__).parent / "clients_review.ui"), self)
        self._fix_widget_icons()

        # Here you can later:
        # - populate clientsTable with rows
        # - wire pagination buttons and refresh/export/print actions
        self.Input_FromDate.setDate(QDate.currentDate())
        self.Input_ToDate.setDate(QDate.currentDate())
        header = self.Table_clients.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.Button_CloseWindow.clicked.connect(self.close)

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
                for pattern in (r"url(../../assets/calendar.svg)", r"url(/assets/calendar.svg)"):
                    new_style = new_style.replace(pattern, f"url({calendar_path})")
                widget.setStyleSheet(new_style)
        
        # Fix all QComboBox widgets
        for widget in self.findChildren(QComboBox):
            current_style = widget.styleSheet()
            if "::down-arrow" in current_style:
                new_style = current_style
                for pattern in (r"url(../../assets/chevron_down.svg)", r"url(/assets/chevron_down.svg)"):
                    new_style = new_style.replace(pattern, f"url({chevron_path})")
                widget.setStyleSheet(new_style)
        setup_funcs(self)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)

    window = ClientsReviewWindow()
    window.show()

    sys.exit(app.exec_())

