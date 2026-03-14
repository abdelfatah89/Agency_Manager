"""
Transaction Manager — PyQt5 entry point
Loads transaction_manager.ui and wires up basic logic.

Requirements:
    pip install PyQt5

Assets (place 24×24 px SVG icons in the assets/ folder):
    assets/receipt_long.svg    — header title icon
    assets/settings.svg        — settings button
    assets/chevron_down.svg    — combo-box arrow
    assets/calendar.svg        — date-edit button
    assets/add.svg             — add-item button
    assets/delete.svg          — delete-item button
    assets/close.svg           — cancel button
    assets/arrow_forward.svg   — close/back button
    assets/print.svg           — print button
    assets/add_circle.svg      — new-document button
"""

import sys
from pathlib import Path

# Add project root to path for imports
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from theme.theme_manager import ThemeManager, get_colored_icon
from src.utils import asset_path, asset_url

# Import funcs module - must be after path setup
from src.daily_entry.funcs import setup_funcs, clear_all

# ── Icon size control ─────────────────────────────────────
# Change these two values to resize all button icons at once.
HEADER_ICON_SIZE   = 24   # px  — title icon (receipt_long) and settingsBtn
BUTTON_ICON_SIZE   = 16   # px  — all action / footer ToolButtons
ICON_TEXT_SPACING  =  0   # px  — gap between icon and label text
# ──────────────────────────────────────────────────────────

# ── Icon paths ────────────────────────────────────────────
# To swap an icon, change only its path here.
ICONS = {
    "title": asset_path("receipt_long.svg"),
    "settings": asset_path("settings.svg"),
    "add": asset_path("add.svg"),
    "delete": asset_path("delete.svg"),
    "cancel": asset_path("close.svg"),
    "close": asset_path("arrow_forward.svg"),
    "print": asset_path("print.svg"),
    "new": asset_path("add_circle.svg"),
}
# ──────────────────────────────────────────────────────────


class TransactionManager(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(str(Path(__file__).parent / "daily_entry.ui"), self)
        self._fix_widget_icons()
        # Apply theme before showing the window
        # ThemeManager.apply(QApplication.instance(), "light")
        self._setup()
        setup_funcs(self)  # Initialize backend and wire signals

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

    # ──────────────────────────────────────────────
    #  Initial UI setup
    # ──────────────────────────────────────────────
    def _setup(self):
        # Set today as the default date
        self.Input_TransactionDate.setDate(QDate.currentDate())

        # Apply icons and sizes from the ICONS dict / constants above
        self._apply_icons()

        # Stretch table columns to fill available width
        header = self.Table_TransactionsList.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.Table_TransactionsList.verticalHeader().setDefaultSectionSize(35)
        self.Table_TransactionsList.verticalHeader().setVisible(False)
        self.Table_TransactionsList.horizontalHeader().setDefaultAlignment(
            Qt.AlignCenter | Qt.AlignVCenter
        )

        # Wire close button - keep in UI since it's simple
        self.Button_CloseWindow.clicked.connect(self.close)
        # settingsBtn toggles light/dark
        self.Button_OpenSettings.clicked.connect(self._on_toggle_theme)

    # ──────────────────────────────────────────────
    #  Icons & sizes  (all sourced from ICONS dict)
    # ──────────────────────────────────────────────
    def _apply_icons(self):
        """Set icons directly from the ICONS dict without tinting."""
        h = QSize(HEADER_ICON_SIZE, HEADER_ICON_SIZE)
        b = QSize(BUTTON_ICON_SIZE, BUTTON_ICON_SIZE)

        # Title label pixmap
        self.Label_HeaderIcon.setPixmap(
            QPixmap(ICONS["title"]).scaled(h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

        from PyQt5.QtGui import QIcon

        # Header settings button
        self.Button_OpenSettings.setIcon(QIcon(ICONS["settings"]))
        self.Button_OpenSettings.setIconSize(h)

        # Item-section action buttons
        self.Button_AddItem.setIcon(QIcon(ICONS["add"]))
        self.Button_AddItem.setIconSize(b)
        self.Button_DeleteItem.setIcon(QIcon(ICONS["delete"]))
        self.Button_DeleteItem.setIconSize(b)
        self.Button_CancelItem.setIcon(QIcon(ICONS["cancel"]))
        self.Button_CancelItem.setIconSize(b)

        # Footer buttons
        self.Button_CloseWindow.setIcon(QIcon(ICONS["close"]))
        self.Button_CloseWindow.setIconSize(b)
        self.Button_PrintTransaction.setIcon(QIcon(ICONS["print"]))
        self.Button_PrintTransaction.setIconSize(b)
        self.Button_NewTransaction.setIcon(QIcon(ICONS["new"]))
        self.Button_NewTransaction.setIconSize(b)

    # ──────────────────────────────────────────────
    #  Theme toggle (No longer recolors icons)
    # ──────────────────────────────────────────────
    def _on_toggle_theme(self):
        new_mode = ThemeManager.toggle(QApplication.instance())
        print(f"[Theme] Switched to {new_mode}")

    # ──────────────────────────────────────────────
    #  Cleanup
    # ──────────────────────────────────────────────
    def closeEvent(self, event):
        """Clear form state and clean up resources on window close."""
        try:
            clear_all(self)
        except Exception as err:
            print(f"[UI] Error while clearing transaction manager: {err}")

        if hasattr(self, 'session') and self.session:
            self.session.close()
            print("[DB] Database session closed")
        event.accept()


# ──────────────────────────────────────────────────────────
def open_transaction_manager():
    app = QApplication.instance()

    if app is None:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        app = QApplication(sys.argv)
        app.setLayoutDirection(Qt.RightToLeft)

    window = TransactionManager()
    window.show()

    return window