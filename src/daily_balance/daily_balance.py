"""
rasid_jour.py  Daily Balance Dashboard (الرصيد اليومي)
Loads rasid_jour.ui and wires up the UI with QSS styling and sample data.
Styling is embedded per-widget inside rasid_jour.ui — no global QSS here.

Requirements:
    pip install PyQt5

Assets (SVG icons in assets/ folder):
    assets/nightlight.svg       -> dark mode toggle
    assets/tag.svg              -> transaction counter
    assets/calendar_today.svg   -> date display
    assets/bar_chart.svg        -> card icon (general)
    assets/payments.svg         -> card icon (cash box)
    assets/trending_up.svg      -> card icon (cash plus)
    assets/history.svg          -> transactions title icon / last-day button
    assets/search.svg           -> search box icon
    assets/swap_horiz.svg       -> sub-panel icon
    assets/first_page.svg       -> nav: first
    assets/chevron_left.svg     -> nav: prev
    assets/chevron_right.svg    -> nav: next
    assets/last_page.svg        -> nav: last
"""

import sys
from pathlib import Path

# Add project root to path for imports
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor
from PyQt5 import uic
from theme.theme_manager import get_colored_icon
from src.utils import asset_path
from services.access_control import (
    PERM_OPEN_DAILY_BALANCE,
    ROLE_ADMIN,
    ROLE_CASHPLUS_EMPLOYER,
    require_permission,
)

# Import funcs module - must be after path setup
from src.daily_balance.funcs import setup_funcs

# ── Icon size constants ────────────────────────────────────────────────────────
ICON_SM = 16   # small icons  (labels, search)
ICON_MD = 20   # medium icons (header chips, nav, cards)

# ── Icon paths ─────────────────────────────────────────────────────────────────
ICONS = {
    "darkMode": asset_path("nightlight.svg"),
    "counter": asset_path("tag.svg"),
    "date": asset_path("calendar_today.svg"),
    "general": asset_path("bar_chart.svg"),
    "cashBox": asset_path("payments.svg"),
    "cashPlus": asset_path("trending_up.svg"),
    "transactions": asset_path("history.svg"),
    "search": asset_path("search.svg"),
    "swapHoriz": asset_path("swap_horiz.svg"),
    "navFirst": asset_path("first_page.svg"),
    "navPrev": asset_path("chevron_left.svg"),
    "navNext": asset_path("chevron_right.svg"),
    "navLast": asset_path("last_page.svg"),
}


class DailyBalance(QMainWindow):
    def __init__(self, parent=None, current_user_role=None):
        super().__init__(parent)
        uic.loadUi(str(Path(__file__).parent / "daily_balance.ui"), self)
        self._current_page = 1
        self._current_user_role = require_permission(current_user_role, PERM_OPEN_DAILY_BALANCE, "daily balance")
        self._setup()
        setup_funcs(self)
        self._apply_role_restrictions()

    # ──────────────────────────────────────────────────────────────────────────
    def _setup(self):
        header = self.transactionsTable.horizontalHeader()
        # PyQt5 expects a concrete resize mode value, not the enum type.
        #header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.transactionsTable.verticalHeader().setVisible(False)

        self._apply_icons()

    def _apply_role_restrictions(self):
        if not self._current_user_role:
            return

        if self._current_user_role != ROLE_ADMIN and hasattr(self, "localagence_frame"):
            self.localagence_frame.hide()
            self.localagence_frame.setParent(None)

        if self._current_user_role == ROLE_CASHPLUS_EMPLOYER:
            if hasattr(self, "generalCard"):
                self.generalCard.hide()
                self.generalCard.setParent(None)

    # ──────────────────────────────────────────────────────────────────────────
    #  Icons
    # ──────────────────────────────────────────────────────────────────────────
    def _apply_icons(self):
        sm    = QSize(ICON_SM, ICON_SM)
        md    = QSize(ICON_MD, ICON_MD)
        muted = "#9CA3AF"
        dark  = "#374151"
        blue  = "#3B82F6"
        white = "#FFFFFF"

        # Header chips
        self.counterIconLabel.setPixmap(
            get_colored_icon(ICONS["counter"], muted).pixmap(sm))
        self.dateIconLabel.setPixmap(
            get_colored_icon(ICONS["date"], muted).pixmap(sm))

        # General card
        self.genIconBtn.setIcon(get_colored_icon(ICONS["general"], white))
        self.genIconBtn.setIconSize(md)

        # Cash Box card
        self.cbTitleIconLabel.setPixmap(
            get_colored_icon(ICONS["cashBox"], "#059669").pixmap(md))

        # Cash Plus card
        self.cpTitleIconLabel.setPixmap(
            get_colored_icon(ICONS["cashPlus"], "#F97316").pixmap(md))
        self.cpSubPanelIconLabel.setPixmap(
            get_colored_icon(ICONS["swapHoriz"], muted).pixmap(sm))

        # "آخر اليوم" button inside the sub-panel
        self.cpSubPanelToggleBtn.setIcon(get_colored_icon(ICONS["transactions"], "#3B82F6"))
        self.cpSubPanelToggleBtn.setIconSize(sm)

        # Transactions section
        self.transTitleIconLabel.setPixmap(
            get_colored_icon(ICONS["transactions"], blue).pixmap(md))

        # Navigation buttons
        self.navFirstBtn.setIcon(get_colored_icon(ICONS["navFirst"], dark))
        self.navFirstBtn.setIconSize(md)
        self.navPrevBtn.setIcon(get_colored_icon(ICONS["navPrev"], dark))
        self.navPrevBtn.setIconSize(md)
        self.navNextBtn.setIcon(get_colored_icon(ICONS["navNext"], dark))
        self.navNextBtn.setIconSize(md)
        self.navLastBtn.setIcon(get_colored_icon(ICONS["navLast"], dark))
        self.navLastBtn.setIconSize(md)



# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps,    True)

    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)

    window = DailyBalance(current_user_role=ROLE_ADMIN)
    window.show()
    sys.exit(app.exec_())
