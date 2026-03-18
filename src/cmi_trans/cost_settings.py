import sys
import logging
from pathlib import Path

from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog
import json
from src.utils.ui_helpers import apply_numeric_input_restrictions


logger = logging.getLogger(__name__)


class CostSettings(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(str(Path(__file__).parent / "cost_settings.ui"), self)
        self._setup()
        self.load_cost_setting()

    def _setup(self):
        #self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        apply_numeric_input_restrictions(
            self,
            force_numeric_names=[
                "Input_250cost",
                "Input_500cost",
                "Input_750cost",
                "Input_1000cost",
                "Input_PercentCost",
            ],
        )
        self.Button_Save.clicked.connect(self.save_cost_setting)
        self.Button_CloseWindow.clicked.connect(self.close)

    def load_cost_setting(self):
        try:
            with open(str(Path(__file__).parent / "cost_setting.json"), "r") as f:
                cost_setting = json.load(f)
            self.Input_250cost.setText(str(cost_setting["le250"]))
            self.Input_500cost.setText(str(cost_setting["le500"]))
            self.Input_750cost.setText(str(cost_setting["le750"]))
            self.Input_1000cost.setText(str(cost_setting["le1000"]))
            self.Input_PercentCost.setText(str(cost_setting["g1000"]))
        except FileNotFoundError:
            logger.warning("Cost setting file not found")
            return

    def save_cost_setting(self):
        try:
            cost_setting = {
                "le250": float(self.Input_250cost.text()),
                "le500": float(self.Input_500cost.text()),
                "le750": float(self.Input_750cost.text()),
                "le1000": float(self.Input_1000cost.text()),
                "g1000": float(self.Input_PercentCost.text())
            }
            with open(str(Path(__file__).parent / "cost_setting.json"), "w") as f:
                json.dump(cost_setting, f)
        except ValueError:
            logger.warning("Invalid input in cost settings")
            return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CostSettings()
    window.show()
    sys.exit(app.exec_())
