import sys
import os
from pathlib import Path
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont, QPainterPath
from PyQt5.QtCore import Qt, QEvent, QObject, QSize, QRectF, QSettings
from PyQt5.QtSvg import QSvgRenderer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.auth_service import authenticate_user, ensure_default_admin_user
from src.main_window.main_window import MainWindowDashboard
from src.utils import resource_path


# ── Base directory (works both frozen and as script) ─────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGIN_ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PROJECT_ASSETS_DIR = os.path.join(str(PROJECT_ROOT), "assets")


def _find_asset(*candidates: str) -> str:
    """Return first existing asset path from login-local or project-level assets."""
    for filename in candidates:
        for folder in (LOGIN_ASSETS_DIR, PROJECT_ASSETS_DIR):
            path = os.path.join(folder, filename)
            if os.path.exists(path):
                return path
    return ""

# ── Logo card settings (edit here to customise) ───────────────────────────────
LOGO_CARD = {
    "card_w":      116,   # outer QLabel width  (px)
    "card_h":      98,   # outer QLabel height (px)
    "icon_w":       155,   # composite pixmap width  (px)
    "icon_h":       200,   # composite pixmap height (px)
    "fg_scale":   0.60,   # foreground logo size relative to icon canvas (0–1)
    "radius":       20,   # border-radius of the glass card (px)
    "padding":      15,   # inner padding of the glass card (px)
    "opacity":    0.85,   # glass opacity effect (0.0 = invisible, 1.0 = solid)
    "bg_color":  "rgba(255, 255, 255, 0.15)",
    "border":    "1px solid rgba(255, 255, 255, 0.25)",
}


def _svg_pixmap(path: str, width: int, height: int = None) -> QPixmap:
    """Render an SVG file into a transparent QPixmap at exact width×height.
    If height is omitted, height == width (square).
    """
    if height is None:
        height = width
    px = QPixmap(width, height)
    px.fill(Qt.transparent)
    renderer = QSvgRenderer(path)
    painter = QPainter(px)
    renderer.render(painter, QRectF(0, 0, width, height))
    painter.end()
    return px


def _composite_svg_pixmap(
    bg_path: str, fg_path: str,
    width: int, height: int,
    fg_scale: float = 0.55,
) -> QPixmap:
    """Paint bg_path (PNG or SVG) as full-size background, then fg_path (SVG)
    centered on top. fg_scale controls foreground size relative to canvas.
    """
    px = QPixmap(width, height)
    px.fill(Qt.transparent)
    painter = QPainter(px)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    # ── Background – PNG via QPixmap, SVG via QSvgRenderer ───────────────
    if os.path.exists(bg_path):
        if bg_path.lower().endswith(".png"):
            bg_pix = QPixmap(bg_path).scaled(
                width, height,
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation,
            )
            painter.drawPixmap(0, 0, bg_pix)
        else:
            QSvgRenderer(bg_path).render(painter, QRectF(0, 0, width, height))
    # ── Foreground logo – centered, scaled down ─────────────────────────────
    if os.path.exists(fg_path):
        fw = width  * fg_scale
        fh = height * fg_scale
        fx = (width  - fw) / 2
        fy = (height - fh) / 2
        if fg_path.lower().endswith(".png"):
            fg_pix = QPixmap(fg_path).scaled(
                int(fw),
                int(fh),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            px_x = int((width - fg_pix.width()) / 2)
            px_y = int((height - fg_pix.height()) / 2)
            painter.drawPixmap(px_x, px_y, fg_pix)
        else:
            QSvgRenderer(fg_path).render(painter, QRectF(fx, fy, fw, fh))
    painter.end()
    return px


def _load_almarai_font():
    """Register Almarai font (system-installed) as the app-wide default."""
    QtWidgets.QApplication.setFont(QFont("Almarai-ExtraBold", 10))


class CoverImageFilter(QObject):
    """Event filter that paints a pixmap as cover (fill height, clip width) on the target widget."""

    def __init__(self, widget: QtWidgets.QWidget, pixmap: QPixmap):
        super().__init__(widget)
        self._pixmap = pixmap
        widget.installEventFilter(self)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Paint:
            painter = QPainter(obj)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.setRenderHint(QPainter.Antialiasing)
            w, h = obj.width(), obj.height()

            # Build clip path matching CSS radii:
            #   top-left: 25px, bottom-left: 100px, others: square
            tl_r = 25
            bl_r = 100
            clip = QPainterPath()
            clip.moveTo(tl_r, 0)
            clip.lineTo(w, 0)
            clip.lineTo(w, h)
            clip.lineTo(bl_r, h)
            clip.arcTo(0, h - 2 * bl_r, 2 * bl_r, 2 * bl_r, 270, -90)
            clip.lineTo(0, tl_r)
            clip.arcTo(0, 0, 2 * tl_r, 2 * tl_r, 180, -90)
            clip.closeSubpath()

            # Fill with solid black first so no transparency bleeds through
            painter.setClipPath(clip)
            painter.fillPath(clip, Qt.black)

            # Draw cover image
            scaled = self._pixmap.scaled(
                w, h,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
            x = (w - scaled.width()) // 2
            y = (h - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.end()
            return True  # we handled painting; children paint themselves on top
        return False


class _CenteredToolButton(QtWidgets.QToolButton):
    """QToolButton that draws its icon + text as a centered pair."""

    def paintEvent(self, _event):
        from PyQt5.QtWidgets import QStyle, QStyleOptionToolButton, QStylePainter
        sp = QStylePainter(self)
        opt = QStyleOptionToolButton()
        self.initStyleOption(opt)
        # Draw the button background / border via the stylesheet
        opt.text = ""
        opt.icon = QIcon()
        sp.drawComplexControl(QStyle.CC_ToolButton, opt)
        # Measure icon + gap + text
        icon_pix = self.icon().pixmap(self.iconSize())
        text     = self.text()
        fm       = sp.fontMetrics()
        gap      = 8
        total_w  = icon_pix.width() + gap + fm.horizontalAdvance(text)
        x = (self.width()  - total_w)        // 2
        y_icon = (self.height() - icon_pix.height()) // 2
        y_text = (self.height() + fm.ascent() - fm.descent()) // 2
        sp.drawPixmap(x, y_icon, icon_pix)
        sp.setPen(Qt.white)
        sp.drawText(x + icon_pix.width() + gap, y_text, text)


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self, on_login_success=None):
        super().__init__()
        self._on_login_success = on_login_success
        self._settings = QSettings("KONACH", "KONACH-App")

        # Load the .ui file
        ui_path = os.path.join(BASE_DIR, "login.ui")
        uic.loadUi(ui_path, self)

        # Frameless + translucent window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Apply centered icon+text paint to the login button
        self.loginBtn.__class__ = _CenteredToolButton

        # Window icon
        icon_path = resource_path("assets/icons/window_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Center the window on screen
        self._center_window()

        # Connect signals
        self._connect_signals()

        # Password visibility state
        self._password_visible = False

        # Eye icon paths (default: hidden)
        self._eye_open_path = _find_asset("eye-open.svg", "search.svg", "settings.svg")
        self._eye_closed_path = _find_asset("eye-closed.svg", "lock.svg")

        # Load all SVG icons (uic cannot render SVGs via <pixmap> property)
        self._load_svg_icons()

        # Restore remember-me state.
        self._restore_remembered_user()

        # Bootstrap first admin user on fresh database.
        created_admin = ensure_default_admin_user()
        if created_admin is not None:
            username, password = created_admin
            QtWidgets.QMessageBox.information(
                self,
                "تهيئة أولية",
                f"تم إنشاء مستخدم افتراضي:\nاسم المستخدم: {username}\nكلمة المرور: {password}",
            )

        # Cover image on the right panel (scale-to-height, clip width)
        img_path = _find_asset("login_image.png", "login_background.png")
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                # Remove border-image from stylesheet so Qt doesn't double-draw
                current_style = self.rightFrame.styleSheet() or ""
                self.rightFrame.setStyleSheet(
                    current_style
                    + "\nQFrame#rightFrame { border: none; border-bottom-left-radius: 100px;"
                    + "border-top-left-radius: 25px; }"
                )
                CoverImageFilter(self.rightFrame, pixmap)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _load_svg_icons(self):
        """Render all SVG assets into their target labels/buttons.
        Each entry: (widget, filename, width, height)
        """
        # ── Composite logo (Overlay_logo behind logo) ──────────────────────────
        overlay_path = _find_asset("Overlay_logo.png")
        logo_path = _find_asset("logo.svg", "logo.png")

        if hasattr(self, "logoLabel"):
            # Apply card size from config (overrides .ui fixed size)
            self.logoLabel.setFixedSize(LOGO_CARD["card_w"], LOGO_CARD["card_h"])

            # Apply glass stylesheet from config
            current_logo_style = self.logoLabel.styleSheet() or ""
            self.logoLabel.setStyleSheet(
                current_logo_style
                + f"\nQLabel#logoLabel {{"
                + f"  background-color: {LOGO_CARD['bg_color']};"
                + f"  border: {LOGO_CARD['border']};"
                + f"  border-radius: {LOGO_CARD['radius']}px;"
                + f"  padding: {LOGO_CARD['padding']}px;"
                + f"}}"
            )

            self.logoLabel.setPixmap(
                _composite_svg_pixmap(
                    overlay_path, logo_path,
                    LOGO_CARD["icon_w"], LOGO_CARD["icon_h"],
                    fg_scale=LOGO_CARD["fg_scale"],
                )
            )

            # Frosted-glass opacity on the logo card
            from PyQt5.QtWidgets import QGraphicsOpacityEffect
            _op = QGraphicsOpacityEffect(self.logoLabel)
            _op.setOpacity(LOGO_CARD["opacity"])
            self.logoLabel.setGraphicsEffect(_op)
        icons = [
            # (objectName in .ui, filename, width, height)
            ("shieldIconLabel", "shieldIcon.svg", 14, 17),
            ("cloudIconLabel", "cloudIcon.svg", 19, 14),
            ("verifiedIconLabel", "verifiedIcon.svg", 14, 17),
            ("lockIconLabel", "lock.svg", 18, 18),
        ]
        for widget_name, filename, w, h in icons:
            label = getattr(self, widget_name, None)
            path = _find_asset(filename)
            if label is not None and os.path.exists(path):
                label.setPixmap(_svg_pixmap(path, w, h))

        if hasattr(self, "emailIconBtn"):
            arobas_path = _find_asset("arobass.svg")
            if arobas_path:
                self.emailIconBtn.setIcon(QIcon(_svg_pixmap(arobas_path, 18, 18)))
                self.emailIconBtn.setIconSize(QSize(18, 18))
                self.emailIconBtn.setEnabled(False)

        # Login button icon (left of text)
        entry_path = _find_asset("entry.svg", "arrow_forward.svg", "logout.svg")
        if os.path.exists(entry_path):
            self.loginBtn.setIcon(QIcon(_svg_pixmap(entry_path, 22, 22)))
            self.loginBtn.setIconSize(QSize(22, 22))

        # Eye button default icon
        if hasattr(self, "eyeBtn") and os.path.exists(self._eye_closed_path):
            self.eyeBtn.setIcon(QIcon(_svg_pixmap(self._eye_closed_path, 18, 18)))
            self.eyeBtn.setIconSize(QSize(18, 18))

    def _restore_remembered_user(self):
        remember = self._settings.value("login/remember", False, type=bool)
        username = self._settings.value("login/username", "", type=str)

        if hasattr(self, "rememberCheckBox"):
            self.rememberCheckBox.setChecked(bool(remember))

        if remember and username:
            self.emailInput.setText(username)
            self.passwordInput.setFocus()

    def _center_window(self):
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

    def _connect_signals(self):
        # Login button
        self.loginBtn.clicked.connect(self._on_login)

        # Exit button
        self.exitBtn.clicked.connect(self.close)

        # Eye toggle (show/hide password)
        self.eyeBtn.clicked.connect(self._toggle_password)

        # Forgot password
        self.forgotBtn.clicked.connect(self._on_forgot_password)

        # Allow pressing Enter in either field to submit
        self.emailInput.returnPressed.connect(self._on_login)
        self.passwordInput.returnPressed.connect(self._on_login)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_login(self):
        email = self.emailInput.text().strip()
        password = self.passwordInput.text()

        if not email:
            self._shake(self.emailInputFrame)
            self.emailInput.setFocus()
            return
        if not password:
            self._shake(self.passwordInputFrame)
            self.passwordInput.setFocus()
            return

        user, error_message = authenticate_user(email, password)
        if error_message:
            self._shake(self.passwordInputFrame)
            self.passwordInput.setFocus()
            QtWidgets.QMessageBox.warning(self, "فشل تسجيل الدخول", error_message)
            return

        self._save_remember_preference(email)

        if callable(self._on_login_success):
            self._on_login_success(user, self)
            return

        self._open_dashboard(user)

    def _save_remember_preference(self, username: str):
        remember = hasattr(self, "rememberCheckBox") and self.rememberCheckBox.isChecked()
        self._settings.setValue("login/remember", remember)
        self._settings.setValue("login/username", username if remember else "")

    def _open_dashboard(self, user):
        self._dashboard = MainWindowDashboard(current_user=user)
        self._dashboard.show()
        self.close()

    def _toggle_password(self):
        self._password_visible = not self._password_visible
        if self._password_visible:
            self.passwordInput.setEchoMode(QtWidgets.QLineEdit.Normal)
            if os.path.exists(self._eye_open_path):
                self.eyeBtn.setIcon(QIcon(_svg_pixmap(self._eye_open_path, 18, 18)))
            self.eyeBtn.setToolTip("إخفاء كلمة المرور")
        else:
            self.passwordInput.setEchoMode(QtWidgets.QLineEdit.Password)
            if os.path.exists(self._eye_closed_path):
                self.eyeBtn.setIcon(QIcon(_svg_pixmap(self._eye_closed_path, 18, 18)))
            self.eyeBtn.setToolTip("إظهار كلمة المرور")

    def _on_forgot_password(self):
        QtWidgets.QMessageBox.information(
            self,
            "نسيت كلمة المرور",
            "سيتم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.",
        )

    # ── Animation helper ──────────────────────────────────────────────────────

    def _shake(self, widget):
        """Briefly highlight the border of a frame to indicate an error."""
        original = widget.styleSheet()
        # Add red border
        widget.setStyleSheet(original + "border-color: #EF4444;")
        # Restore after 600 ms
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(600, lambda: widget.setStyleSheet(original))


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)

    _load_almarai_font()

    window = LoginWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
