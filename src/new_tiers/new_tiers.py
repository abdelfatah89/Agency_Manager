import sys
from pathlib import Path

# Add project root to path for imports
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QDialog, QHeaderView, QButtonGroup
from src.utils import asset_url

from src.new_tiers.func import setup_funcs, clear_all, set_agence_types


class NewTiers(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(str(Path(__file__).parent / "new_tiers.ui"), self)
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
        self.tier_types = QButtonGroup(self)
        self.tier_types.addButton(self.radioAgence,     1)  # id = 1
        self.tier_types.addButton(self.radioAccount,    2)  # id = 2
        self.tier_types.addButton(self.radioClient,     3)  # id = 3
        self.tier_types.buttonClicked.connect(self.on_tier_selected)
        self.radioAgence.setChecked(True)
        self.on_tier_selected()

    def on_tier_selected(self):
        selected_id = self.tier_types.checkedId()
        if selected_id == 1:
            self.Input_name.setEnabled(True)
            self.ComboAgenceType.setEnabled(True)
            self.Input_CIN.setEnabled(False)
            self.Input_TelNumber.setEnabled(False)
            self.Input_Adresse.setEnabled(False)
        elif selected_id == 2:
            self.Input_name.setEnabled(True)
            self.ComboAgenceType.setEnabled(False)
            self.Input_CIN.setEnabled(False)
            self.Input_TelNumber.setEnabled(False)
            self.Input_Adresse.setEnabled(False)
        elif selected_id == 3:
            self.Input_name.setEnabled(True)
            self.ComboAgenceType.setEnabled(False)
            self.Input_CIN.setEnabled(True)
            self.Input_TelNumber.setEnabled(True)
            self.Input_Adresse.setEnabled(True)
        clear_all(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewTiers()
    window.show()
    sys.exit(app.exec_())
