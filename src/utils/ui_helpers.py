from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QRegularExpressionValidator
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QLineEdit, QWidget


def create_readonly_checkbox_cell(checked: bool) -> QWidget:
    checkbox = QCheckBox()
    checkbox.setChecked(bool(checked))
    checkbox.setEnabled(False)
    checkbox.setFocusPolicy(Qt.NoFocus)

    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.addWidget(checkbox)
    layout.setAlignment(Qt.AlignCenter)
    layout.setContentsMargins(0, 0, 0, 0)
    return widget


def apply_numeric_input_restrictions(container, force_numeric_names=None):
    """Apply numeric-only validation on line edits.

    - Accepts digits with optional decimal part (dot or comma), up to 2 decimals.
    - Skips non-editable/read-only fields.
    - When force_numeric_names is provided, only those object names are targeted.
    """
    force_names = set(force_numeric_names or [])
    numeric_pattern = QRegularExpression(r"^\d*(?:[\.,]\d{0,2})?$")

    for line_edit in container.findChildren(QLineEdit):
        if not line_edit.isEnabled() or line_edit.isReadOnly():
            continue

        object_name = line_edit.objectName() or ""
        if force_names and object_name not in force_names:
            continue

        validator = QRegularExpressionValidator(numeric_pattern, line_edit)
        line_edit.setValidator(validator)
