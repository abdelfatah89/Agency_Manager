import sys
from pathlib import Path

from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView
from src.factures.func import setup_funcs
from src.utils import asset_url
from services.access_control import PERM_OPEN_FACTURES, require_permission


class FacturesWindow(QMainWindow):
    """Invoice list window loaded from factures.ui."""

    def __init__(self, parent=None, current_user_role=None):
        super().__init__(parent)
        self._current_user_role = require_permission(current_user_role, PERM_OPEN_FACTURES, "factures")
        loadUi(str(Path(__file__).parent / "factures.ui"), self)
        self._fix_widget_icons()
        self._setup()
        setup_funcs(self)

    def _fix_widget_icons(self):
        """Fix QComboBox and QDateEdit arrow icons with absolute asset URLs."""
        from PyQt5.QtWidgets import QComboBox, QDateEdit

        calendar_path = asset_url("calendar.svg")
        chevron_path = asset_url("chevron_down.svg")

        for widget in self.findChildren(QDateEdit):
            current_style = widget.styleSheet()
            if "::down-arrow" in current_style:
                new_style = current_style
                for pattern in ("url(../../assets/calendar.svg)", "url(/assets/calendar.svg)"):
                    new_style = new_style.replace(pattern, f"url({calendar_path})")
                widget.setStyleSheet(new_style)

        for widget in self.findChildren(QComboBox):
            current_style = widget.styleSheet()
            if "::down-arrow" in current_style:
                new_style = current_style
                for pattern in ("url(../../assets/chevron_down.svg)", "url(/assets/chevron_down.svg)"):
                    new_style = new_style.replace(pattern, f"url({chevron_path})")
                widget.setStyleSheet(new_style)

    def _setup(self):
        self.Button_CloseWindow.clicked.connect(self.close)

        # Stretch table columns to fill available width
        header = self.FacturesTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        #header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.FacturesTable.verticalHeader().setDefaultSectionSize(35)
        self.FacturesTable.verticalHeader().setVisible(False)
        self.FacturesTable.horizontalHeader().setDefaultAlignment(
            Qt.AlignCenter | Qt.AlignVCenter
        )
        self.FacturesTable.setSortingEnabled(True)
        self.FacturesTable.horizontalHeader().setSortIndicatorShown(True)
        self.FacturesTable.horizontalHeader().setSortIndicator(0, Qt.DescendingOrder)


if __name__ == "__main__":
    from services.access_control import ROLE_ADMIN

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)

    window = FacturesWindow(current_user_role=ROLE_ADMIN)
    window.show()

    sys.exit(app.exec_())

