from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox

from services.auth_service import (
    ROLE_CASHPLUS_EMPLOYER,
    ROLE_FULL_ACCESS,
    ROLE_TPE_EMPLOYER,
    ensure_default_admin_user,
    list_users,
    upsert_user,
)


ROLE_ITEMS = [
    ("صلاحية كاملة", ROLE_FULL_ACCESS),
    ("موظف كاش بلوس", ROLE_CASHPLUS_EMPLOYER),
    ("موظف TPE", ROLE_TPE_EMPLOYER),
]


class UserManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(str(Path(__file__).parent / "user_manager.ui"), self)
        ensure_default_admin_user()
        self._users = {}
        self._setup_ui()
        self._load_users()

    def _setup_ui(self) -> None:
        self.Button_CloseWindow.clicked.connect(self.reject)
        self.Button_Save.clicked.connect(self._save)

        self.ComboUserName.setInsertPolicy(self.ComboUserName.NoInsert)
        self.ComboUserName.currentTextChanged.connect(self._on_username_changed)

        self.ComboUserRole.clear()
        self.ComboUserRole.setEditable(False)
        for label, value in ROLE_ITEMS:
            self.ComboUserRole.addItem(label, value)

    def _load_users(self) -> None:
        rows = list_users()
        self._users = {row["username"]: row for row in rows}
        visible_usernames = [
            row["username"]
            for row in rows
            if row.get("role") != ROLE_FULL_ACCESS
        ]

        current = self.ComboUserName.currentText().strip()
        self.ComboUserName.blockSignals(True)
        self.ComboUserName.clear()
        for username in sorted(visible_usernames):
            self.ComboUserName.addItem(username)
        self.ComboUserName.setCurrentText(current)
        self.ComboUserName.blockSignals(False)

        self._on_username_changed(self.ComboUserName.currentText())

    def _set_role_combo(self, role: str) -> None:
        for idx in range(self.ComboUserRole.count()):
            if self.ComboUserRole.itemData(idx) == role:
                self.ComboUserRole.setCurrentIndex(idx)
                return
        self.ComboUserRole.setCurrentIndex(0)

    def _on_username_changed(self, username: str) -> None:
        uname = (username or "").strip()
        user = self._users.get(uname)
        if user:
            self._set_role_combo(user.get("role", ROLE_CASHPLUS_EMPLOYER))
            self.Password_Input.clear()
            self.Password_Input.setPlaceholderText("اتركها فارغة للإبقاء على كلمة المرور الحالية")
        else:
            self._set_role_combo(ROLE_CASHPLUS_EMPLOYER)
            self.Password_Input.clear()
            self.Password_Input.setPlaceholderText("كلمة مرور للمستخدم الجديد")

    def _save(self) -> None:
        username = self.ComboUserName.currentText().strip()
        password = self.Password_Input.text()
        role = self.ComboUserRole.currentData() or ROLE_CASHPLUS_EMPLOYER

        ok, message = upsert_user(username=username, role=role, password=password)
        if not ok:
            QMessageBox.warning(self, "إدارة المستخدمين", message)
            return

        QMessageBox.information(self, "إدارة المستخدمين", message)
        self._load_users()
        self.Password_Input.clear()