"""
theme_manager.py — Centralised QSS theme for the Transaction Manager.

Usage:
    from theme_manager import ThemeManager

    # Apply on startup (default: light)
    ThemeManager.apply(app)

    # Toggle from a button click
    new_mode = ThemeManager.toggle(app)

    # Current mode
    mode = ThemeManager.current()   # "light" or "dark"

Button variants
───────────────
  PRIMARY   — addBtn, newBtn, verifyBtn     (filled blue)
  SECONDARY — closeBtn, printBtn            (outlined neutral)
  GHOST-N   — cancelBtn                     (text-only, gray)
  GHOST-D   — deleteBtn                     (text-only, red/danger)
  ICON-ONLY — settingsBtn                   (circle icon button)
"""

import json
import os
from pathlib import Path
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor

_BASE_DIR = Path(__file__).parent.parent
_THEME_FILE = _BASE_DIR / "theme" / "theme.json"

# ── Load token file once ──────────────────────────────────────────────────────
with open(_THEME_FILE, encoding="utf-8-sig") as _f:
    _TOKENS: dict = json.load(_f)


# ── QSS builder ──────────────────────────────────────────────────────────────

def _qss(t: dict) -> str:
    """Build the complete application QSS from a theme token dict."""
    g    = t["glass"]
    tx   = t["text"]
    bd   = t["border"]
    pr   = t["primary"]
    st   = t["status"]
    bp   = t["buttons"]["primary"]
    bs   = t["buttons"]["secondary"]
    bgn  = t["buttons"]["ghost_normal"]
    bgd  = t["buttons"]["ghost_danger"]
    bio  = t["buttons"]["icon_only"]
    inp  = t["input"]
    tbl  = t["table"]
    tot  = t["totals"]
    sb   = t["scrollbar"]
    win  = t["window"]

    return f"""
/* ═══════════════════════════════════════════════════════
   TRANSACTION MANAGER — QSS Theme  (auto-generated)
   Edit theme.json to change colors; do NOT edit here.
   ═══════════════════════════════════════════════════════ */

/* ── Window & root ─────────────────────────────────── */
QMainWindow {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #EFF6FF,
        stop:1 "#E0E7FF"
    );
    font-family: 'Tajawal', 'Segoe UI', 'Arial', sans-serif;
}}

QWidget#centralWidget {{
    background: transparent;
}}

/* Prevent unnamed container QFrames from showing system background */
QFrame {{
    background: transparent;
    border: none;
}}

/* ── Outer glass card ───────────────────────────────── */
QFrame#outerFrame {{
    background-color: {g["card_bg"]};
    border: 1px solid {g["card_border"]};
    border-radius: 20px;
}}

/* ── Header ─────────────────────────────────────────── */
QFrame#headerFrame {{
    background-color: {g["header_bg"]};
    border-bottom: 1px solid {g["header_border"]};
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
    min-height: 72px;
}}

QLabel#titleLabel {{
    color: {tx["primary"]};
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.3px;
}}

QLabel#subtitleLabel {{
    color: {tx["secondary"]};
    font-size: 15px;
    font-weight: 400;
    margin-top: 2px;
}}

QLabel#titleIconLabel {{
    color: {pr["base"]};
    font-size: 20px;
}}

/* ── Status badge ───────────────────────────────────── */
QLabel#statusBadge {{
    color: {st["success_text"]};
    background-color: {st["success_bg"]};
    border: 1px solid {st["success_border"]};
    border-radius: 12px;
    padding: 3px 12px;
    font-size: 15px;
    font-weight: 600;
}}

/* ── BUTTON: icon-only  (settingsBtn) ──────────────── */
QToolButton#settingsBtn {{
    background: {bio["bg"]};
    border: none;
    border-radius: 18px;
    padding: 6px;
    color: {bio["text"]};
    min-width: 36px;
    min-height: 36px;
}}
QToolButton#settingsBtn:hover {{
    background-color: {bio["bg_hover"]};
}}

QToolButton::menu-indicator {{ image: none; }}

/* ── Section frames ─────────────────────────────────── */
QFrame#customerSection,
QFrame#itemSection {{
    background-color: {g["section_bg"]};
    border: 1px solid {g["section_border"]};
    border-radius: 12px;
}}

/* ── Field labels ───────────────────────────────────── */
QLabel#lbl_customerId, QLabel#lbl_customer, QLabel#lbl_date,
QLabel#lbl_account,    QLabel#lbl_itemRef,  QLabel#lbl_desc,
QLabel#lbl_unitPrice,  QLabel#lbl_lineTotal,QLabel#lbl_qty,
QLabel#lbl_tax,        QLabel#lbl_totalWithTax {{
    color: {tx["secondary"]};
    font-size: 13px;
    font-weight: 600;
}}

/* ── Inputs (all types) ─────────────────────────────── */
QLineEdit,
QComboBox,
QDateEdit,
QSpinBox,
QDoubleSpinBox {{
    background-color: {inp["bg"]};
    border: 1px solid {inp["border"]};
    border-radius: 8px;
    color: {inp["text"]};
    font-size: 15px;
    padding: 6px 10px;
    min-height: 32px;
    selection-background-color: {inp["selection_bg"]};
    selection-color: {inp["selection_text"]};
}}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {{
    border: 2px solid {inp["focus_border"]};
    background-color: {inp["bg"]};
}}
QLineEdit:hover, QComboBox:hover, QDateEdit:hover, QSpinBox:hover {{
    border-color: {inp["hover_border"]};
}}
QLineEdit:disabled, QComboBox:disabled, QDateEdit:disabled, QSpinBox:disabled {{
    background-color: {inp["disabled_bg"]};
    color: {inp["disabled_text"]};
}}

QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox::down-arrow {{
    image: url({Path(__file__).parent.parent / "assets/chevron_down.svg"});
    width: 14px; height: 14px;
}}
QDateEdit::drop-down {{ border: none; width: 24px; }}
QDateEdit::down-arrow {{
    image: url({Path(__file__).parent.parent / "assets/calendar.svg"});
    width: 14px; height: 14px;
}}

/* ── BUTTON: primary  (addBtn, newBtn, verifyBtn) ───── */
QPushButton#verifyBtn,
QToolButton#addBtn,
QToolButton#newBtn {{
    background-color: {bp["bg"]};
    color: {bp["text"]};
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    padding: 7px 18px;
    min-height: 34px;
    spacing: 6px;
}}
QPushButton#verifyBtn:hover,
QToolButton#addBtn:hover,
QToolButton#newBtn:hover {{
    background-color: {bp["bg_hover"]};
}}
QPushButton#verifyBtn:pressed,
QToolButton#addBtn:pressed,
QToolButton#newBtn:pressed {{
    background-color: {bp["bg_pressed"]};
}}

/* ── BUTTON: ghost-normal  (cancelBtn) ──────────────── */
QToolButton#cancelBtn {{
    background: {bgn["bg"]};
    color: {bgn["text"]};
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    padding: 7px 14px;
    min-height: 34px;
    spacing: 6px;
}}
QToolButton#cancelBtn:hover {{
    background: {bgn["bg_hover"]};
    color: {bgn["text_hover"]};
}}

/* ── BUTTON: ghost-danger  (deleteBtn) ──────────────── */
QToolButton#deleteBtn {{
    background: {bgd["bg"]};
    color: {bgd["text"]};
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    padding: 7px 14px;
    min-height: 34px;
    spacing: 6px;
}}
QToolButton#deleteBtn:hover {{
    background: {bgd["bg_hover"]};
    color: {bgd["text_hover"]};
}}

/* ── Divider above action buttons ───────────────────── */
QFrame#actionDivider {{
    color: {bd["default"]};
}}

/* ── Table frame ────────────────────────────────────── */
QFrame#tableFrame {{
    background-color: {g["table_frame_bg"]};
    border: 1px solid {g["card_border"]};
    border-radius: 12px;
}}

/* ── Table widget ───────────────────────────────────── */
QTableWidget {{
    background-color: {tbl["bg"]};
    border: none;
    gridline-color: {tbl["grid"]};
    font-size: 14px;
    alternate-background-color: {tbl["alternate_row"]};
    outline: none;
}}
QTableWidget::item {{
    padding: 10px 20px;
    color: {tbl["row_text"]};
    border-bottom: 1px solid {tbl["row_border"]};
}}
QTableWidget::item:hover {{
    background-color: {tbl["row_hover"]};
}}
QTableWidget::item:selected {{
    background-color: {tbl["row_selected_bg"]};
    color: {tbl["row_selected_text"]};
}}

QHeaderView::section {{
    background-color: {tbl["header_bg"]};
    color: {tbl["header_text"]};
    font-size: 10px;
    font-weight: 700;
    padding: 12px 20px;
    border: none;
    border-bottom: 1px solid {bd["default"]};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ── Scrollbar ──────────────────────────────────────── */
QScrollBar:vertical {{
    background: {sb["track"]};
    width: 8px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {sb["thumb"]};
    border-radius: 4px; min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {sb["thumb_hover"]}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0; background: none;
}}
QScrollBar:horizontal {{
    background: {sb["track"]};
    height: 8px;
}}
QScrollBar::handle:horizontal {{
    background: {sb["thumb"]};
    border-radius: 4px; min-width: 20px;
}}
QScrollBar::handle:horizontal:hover {{ background: {sb["thumb_hover"]}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0; background: none;
}}

/* ── Footer ─────────────────────────────────────────── */
QFrame#footerFrame {{
    background-color: {g["footer_bg"]};
    border-top: 1px solid {g["footer_border"]};
    border-bottom-left-radius: 20px;
    border-bottom-right-radius: 20px;
    min-height: 76px;
}}

/* ── BUTTON: secondary  (closeBtn, printBtn) ─────────── */
QToolButton#closeBtn,
QToolButton#printBtn {{
    background-color: {bs["bg"]};
    border: 1px solid {bs["border"]};
    border-radius: 8px;
    color: {bs["text"]};
    font-size: 14px;
    font-weight: 500;
    padding: 7px 20px;
    min-height: 36px;
    spacing: 6px;
}}
QToolButton#closeBtn:hover,
QToolButton#printBtn:hover {{
    background-color: {bs["bg_hover"]};
    border-color: {bs["border_hover"]};
}}
QToolButton#closeBtn:pressed,
QToolButton#printBtn:pressed {{
    background-color: {bs["bg_pressed"]};
}}

/* ── Totals box ──────────────────────────────────────── */
QFrame#totalsFrame {{
    background-color: {tot["frame_bg"]};
    border: 1px solid {tot["frame_border"]};
    border-radius: 12px;
    padding: 0 8px;
}}

QLabel#lbl_subtotalHeader {{
    color: {tot["label_text"]};
    font-size: 15px;
    font-weight: 700;
}}
QLabel#lbl_grandTotalHeader {{
    color: {tot["grand_label_text"]};
    font-size: 17px;
    font-weight: 700;
}}
QLabel#subtotalValue {{
    color: {tot["value_text"]};
    font-family: 'Courier New', monospace;
    font-size: 20px;
    font-weight: 600;
}}
QLabel#grandTotalValue {{
    color: {tot["grand_value_text"]};
    font-family: 'Courier New', monospace;
    font-size: 20px;
    font-weight: 700;
}}

/* ── Vertical separators ─────────────────────────────── */
QFrame#vSep1, QFrame#vSep2 {{
    background-color: {tot["separator"]};
    max-width: 1px;
    min-width: 1px;
}}
"""


# ── Colored-icon helper ───────────────────────────────────────────────────────

def get_colored_icon(icon_path: str, color_name: str) -> QIcon:
    """Return a QIcon with all opaque pixels recolored to *color_name*."""
    pixmap = QPixmap(icon_path)
    if pixmap.isNull():
        return QIcon()
    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color_name))
    painter.end()
    return QIcon(pixmap)


# ── Public API ────────────────────────────────────────────────────────────────

class ThemeManager:
    """
    Static class — manages light/dark mode for the whole application.

    Quick-start:
        ThemeManager.apply(app)                # light (default)
        ThemeManager.apply(app, "dark")        # dark
        mode = ThemeManager.toggle(app)        # switches and returns new mode
        print(ThemeManager.current())          # "light" | "dark"
    """

    _mode: str = "light"

    @classmethod
    def apply(cls, app, mode: str = "light") -> None:
        """Apply the named theme to *app* (a QApplication instance)."""
        mode = mode.lower()
        if mode not in ("light", "dark"):
            raise ValueError(f"mode must be 'light' or 'dark', got {mode!r}")
        cls._mode = mode
        tokens = _TOKENS[mode]
        app.setStyleSheet(_qss(tokens))

    @classmethod
    def toggle(cls, app) -> str:
        """Switch between light and dark; returns the new mode string."""
        new_mode = "dark" if cls._mode == "light" else "light"
        cls.apply(app, new_mode)
        return new_mode

    @classmethod
    def current(cls) -> str:
        """Return the active mode: 'light' or 'dark'."""
        return cls._mode

    @classmethod
    def icon_color(cls, key: str) -> str:
        """Return the hex color string for *key* in the active theme.

        Keys: title | settings | btn_primary | btn_secondary |
              btn_ghost | btn_danger
        """
        return _TOKENS[cls._mode]["icon_colors"][key]
