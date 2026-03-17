import sys
from pathlib import Path

# Add project root to path for imports
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView

from theme.theme_manager import get_colored_icon
from src.cmi_trans.func import setup_funcs
from src.utils import asset_path, asset_url
from services.access_control import PERM_OPEN_CMI_TRANS, has_permission

ICON_SIZE_SM = 18
ICON_SIZE_MD = 22

# Expected icons you will provide in assets/:
#   - cmi_header.svg, settings.svg, notifications.svg, dark_mode.svg, light_mode.svg
ICONS = {
    "reset": asset_path("refreach.svg"),
    "settings": asset_path("settings.svg"),
}


class CMITransWindow(QMainWindow):
    """CMI transactions window loaded from CMI_trans.ui."""

    def __init__(self, parent=None, current_user_role=None):
        super().__init__(parent)
        if current_user_role and not has_permission(current_user_role, PERM_OPEN_CMI_TRANS):
            raise PermissionError("User is not allowed to access CMI transactions")
        loadUi(str(Path(__file__).parent / "CMI_trans.ui"), self)
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

    def _setup(self):
        # Set today as the default date
        self.Input_TpeDate.setDate(QDate.currentDate())

        # Stretch table columns to fill available width
        header = self.transactionsTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        self.transactionsTable.verticalHeader().setDefaultSectionSize(35)
        self.transactionsTable.verticalHeader().setVisible(False)
        self.transactionsTable.horizontalHeader().setDefaultAlignment(
            Qt.AlignCenter | Qt.AlignVCenter
        )


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)

    window = CMITransWindow()
    window.show()

    sys.exit(app.exec_())

