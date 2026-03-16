from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox

from src.utils.company_info import load_company_info, save_company_info


class CompanyInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(str(Path(__file__).parent / "compny_info.ui"), self)
        self._bind_events()
        self._load_data()

    def _bind_events(self) -> None:
        self.Button_CloseWindow.clicked.connect(self.reject)
        self.Button_Save.clicked.connect(self._save)

    def _load_data(self) -> None:
        data = load_company_info()
        self.CompnyNameInput.setText(data.get("company_name", ""))
        self.PhoneNumberInput.setText(data.get("phone", ""))
        self.AdresseInput.setText(data.get("address", ""))
        self.ICE_Input.setText(data.get("ice", ""))
        self.IF_Input.setText(data.get("if_code", ""))
        self.RC_Input.setText(data.get("rc", ""))

    def _save(self) -> None:
        payload = {
            "company_name": self.CompnyNameInput.text().strip(),
            "phone": self.PhoneNumberInput.text().strip(),
            "address": self.AdresseInput.text().strip(),
            "ice": self.ICE_Input.text().strip(),
            "if_code": self.IF_Input.text().strip(),
            "rc": self.RC_Input.text().strip(),
        }
        save_company_info(payload)
        QMessageBox.information(self, "معلومات الشركة", "تم حفظ معلومات الشركة بنجاح")
        self.accept()