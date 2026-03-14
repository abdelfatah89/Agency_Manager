"""
Script to create styled UI file with renamed widgets and inline QSS
"""
import json
import re

# Read the original UI file
with open(r'd:\.Code\KONACH\src\daily_entry\daily_entry.ui', 'r', encoding='utf-8') as f:
    ui_content = f.read()

# Read theme.json for styling values
with open(r'd:\.Code\KONACH\theme\theme.json', 'r', encoding='utf-8') as f:
    theme = json.load(f)

lighttheme = theme['light']

# Widget rename mapping
widget_renames = {
    'titleIconLabel': 'headerTitleIcon',
    'titleLabel': 'headerTitleLabel',
    'subtitleLabel': 'headerSubtitleLabel',
    'statusBadge': 'systemStatusBadge',
    'settingsBtn': 'settingsIconButton',
    'customerIdCombo': 'clientIdComboBox',
    'customerInput': 'clientNameInput',
    'dateEdit': 'transactionDateEdit',
    'accountCombo': 'accountComboBox',
    'verifyBtn': 'saveTransactionButton',
    'descInput': 'designationInput',
    'qtySpinBox': 'quantitySpinBox',
    'lineTotalInput_2': 'remainingInput',
    'lineTotalInput': 'paymentInput',
    'In_checkBox': 'inboxCheckBox',
    'Out_checkBox': 'outboxCheckBox',
    'addBtn': 'addTransactionButton',
    'deleteBtn': 'deleteTransactionButton',
    'cancelBtn': 'clearFormButton',
    'newBtn': 'newDocumentButton',
    'closeBtn': 'closeWindowButton',
    'printBtn': 'printDocumentButton',
}

# Apply widget renames
for old_name, new_name in widget_renames.items():
    # Rename in widget name attributes
    ui_content = re.sub(
        f'name="{old_name}"',
        f'name="{new_name}"',
        ui_content
    )

# Function to create QSS string properly formatted
def qss(styles_dict):
    """Convert dict of CSS properties toQSS string"""
    return '; '.join(f'{k}: {v}' for k, v in styles_dict.items())

# Function to add or replace styleSheet property
def add_stylesheet(widget_name, qss_string):
    """Add styleSheet property to a widget"""
    global ui_content
    
    # Pattern to find the widget and check if it has styleSheet
    widget_pattern = rf'(<widget [^>]*name="{widget_name}"[^>]*>)(.*?)(</widget>)'
    
    match = re.search(widget_pattern, ui_content, re.DOTALL)
    if not match:
        print(f"Warning: Widget {widget_name} not found")
        return
    
    widget_start = match.group(1)
    widget_content = match.group(2)
    widget_end = match.group(3)
    
    # Check if styleSheet already exists
    stylesheet_pattern = r'<property name="styleSheet">.*?</property>'
    if re.search(stylesheet_pattern, widget_content, re.DOTALL):
        # Replace existing styleSheet
        new_stylesheet = f'''<property name="styleSheet">
    <string notr="true">{qss_string}</string>
   </property>'''
        widget_content = re.sub(stylesheet_pattern, new_stylesheet, widget_content, flags=re.DOTALL)
    else:
        # Add new styleSheet after widget opening tag
        new_stylesheet = f'''
   <property name="styleSheet">
    <string notr="true">{qss_string}</string>
   </property>'''
        # Find first property and insert before it
        first_prop_match = re.search(r'(<property )', widget_content)
        if first_prop_match:
            insert_pos = first_prop_match.start()
            widget_content = widget_content[:insert_pos] + new_stylesheet + '\n   ' + widget_content[insert_pos:]
        else:
            widget_content = new_stylesheet + widget_content
    
    # Replace in ui_content
    ui_content = ui_content.replace(match.group(0), widget_start + widget_content + widget_end)

# Function to add stylesheet property to QFrame widgets by name
def add_frame_stylesheet(frame_name, qss_string):
    """Add styleSheet property to a QFrame widget"""
    add_stylesheet(frame_name, qss_string)

# Add styleSheet to QMainWindow (window gradient)
main_window_qss = qss({
    'background': f'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {lighttheme["window"]["gradient_start"]}, stop:1 {lighttheme["window"]["gradient_end"]})'
})
# Find QMainWindow and add stylesheet
ui_content = re.sub(
    r'(<widget class="QMainWindow" name="TransactionManager">)',
    r'\1\n  <property name="styleSheet">\n   <string notr="true">' + main_window_qss + r'</string>\n  </property>',
    ui_content
)

# Add glass panel styles to QFrame sections
glass_frames = {
    'headerFrame': qss({
        'background-color': lighttheme['glass']['header_bg'],
        'border': f'1px solid {lighttheme["glass"]["header_border"]}',
        'border-radius': '12px'
    }),
    'customerSection': qss({
        'background-color': lighttheme['glass']['section_bg'],
        'border': f'1px solid {lighttheme["glass"]["section_border"]}',
        'border-radius': '12px'
    }),
    'itemSection': qss({
        'background-color': lighttheme['glass']['section_bg'],
        'border': f'1px solid {lighttheme["glass"]["section_border"]}',
        'border-radius': '12px'
    }),
    'tableFrame': qss({
        'background-color': lighttheme['glass']['table_frame_bg'],
        'border': f'1px solid {lighttheme["glass"]["section_border"]}',
        'border-radius': '12px'
    }),
    'footerFrame': qss({
        'background-color': lighttheme['glass']['footer_bg'],
        'border': f'1px solid {lighttheme["glass"]["footer_border"]}',
        'border-radius': '12px'
    }),
    'totalsFrame': qss({
        'background-color': lighttheme['totals']['frame_bg'],
        'border': f'1px solid {lighttheme["totals"]["frame_border"]}',
        'border-radius': '8px',
        'padding': '8px'
    }),
    'totalsFrame_2': qss({
        'background-color': lighttheme['totals']['frame_bg'],
        'border': f'1px solid {lighttheme["totals"]["frame_border"]}',
        'border-radius': '8px',
        'padding': '8px'
    }),
}

for frame_name, style in glass_frames.items():
    add_frame_stylesheet(frame_name, style)

# Add styles to field labels (QLabel widgets that are field labels)
label_qss = qss({
    'color': lighttheme['text']['secondary'],
    'font-weight': 'bold'
})

field_labels = [
    'lbl_date', 'lbl_customerId', 'lbl_customer', 'lbl_account',
    'lbl_desc', 'lbl_qty', 'lbl_unitPrice', 'lbl_lineTotal', 'lbl_tax',
    'lbl_subtotalHeader', 'lbl_grandTotalHeader', 'lbl_subtotalHeader_2', 
    'lbl_grandTotalHeader_2', 'prevtotallbl'
]

for label in field_labels:
    add_stylesheet(label, label_qss)

# Add systemStatusBadge styling (success badge)
status_badge_qss = qss({
    'background-color': lighttheme['status']['success_bg'],
    'color': lighttheme['status']['success_text'],
    'border': f'1px solid {lighttheme["status"]["success_border"]}',
    'border-radius': '12px',
    'padding': '4px 12px',
    'font-weight': 'bold'
})
add_stylesheet('systemStatusBadge', status_badge_qss)

# Add input widget styling (QLineEdit, QComboBox, QDateEdit, QSpinBox)
input_qss = qss({
    'background-color': lighttheme['input']['bg'],
    'color': lighttheme['input']['text'],
    'border': f'1px solid {lighttheme["input"]["border"]}',
    'border-radius': '8px',
    'padding': '8px 12px',
    'selection-background-color': lighttheme['input']['selection_bg'],
    'selection-color': lighttheme['input']['selection_text']
})
input_qss_hover = f"{input_qss}; border: 1px solid {lighttheme['input']['hover_border']}"
input_qss_focus = f"{input_qss}; border: 2px solid {lighttheme['input']['focus_border']}"

# Combine with pseudo-states
full_input_qss = f"QLineEdit, QComboBox, QDateEdit, QSpinBox {{ {input_qss} }} QLineEdit:hover, QComboBox:hover, QDateEdit:hover, QSpinBox:hover {{ border: 1px solid {lighttheme['input']['hover_border']}; }} QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {{ border: 2px solid {lighttheme['input']['focus_border']}; }}"

input_widgets = [
    'clientNameInput', 'designationInput', 'unitPriceInput', 
    'paymentInput', 'remainingInput', 'clientIdComboBox', 
    'accountComboBox', 'transactionDateEdit', 'quantitySpinBox'
]

for widget in input_widgets:
    add_stylesheet(widget, full_input_qss)

# Add primary button styling
primary_btn_qss = f"QPushButton, QToolButton {{ background-color: {lighttheme['buttons']['primary']['bg']}; color: {lighttheme['buttons']['primary']['text']}; border: none; border-radius: 8px; padding: 10px 20px; font-weight: bold; }} QPushButton:hover, QToolButton:hover {{ background-color: {lighttheme['buttons']['primary']['bg_hover']}; }} QPushButton:pressed, QToolButton:pressed {{ background-color: {lighttheme['buttons']['primary']['bg_pressed']}; }}"

primary_buttons = ['saveTransactionButton', 'addTransactionButton', 'newDocumentButton']
for btn in primary_buttons:
    add_stylesheet(btn, primary_btn_qss)

# Add ghost-danger button styling  
ghost_danger_qss = f"QToolButton {{ background-color: {lighttheme['buttons']['ghost_danger']['bg']}; color: {lighttheme['buttons']['ghost_danger']['text']}; border: none; border-radius: 8px; padding: 8px 16px; font-weight: bold; }} QToolButton:hover {{ color: {lighttheme['buttons']['ghost_danger']['text_hover']}; background-color: rgba(239, 68, 68, 0.05); }}"
add_stylesheet('deleteTransactionButton', ghost_danger_qss)

# Add ghost-normal button styling
ghost_normal_qss = f"QToolButton {{ background-color: {lighttheme['buttons']['ghost_normal']['bg']}; color: {lighttheme['buttons']['ghost_normal']['text']}; border: none; border-radius: 8px; padding: 8px 16px; font-weight: bold; }} QToolButton:hover {{ color: {lighttheme['buttons']['ghost_normal']['text_hover']}; background-color: rgba(209, 213, 219, 0.15); }}"
add_stylesheet('clearFormButton', ghost_normal_qss)

# Add secondary button styling
secondary_btn_qss = f"QToolButton {{ background-color: {lighttheme['buttons']['secondary']['bg']}; color: {lighttheme['buttons']['secondary']['text']}; border: 1px solid {lighttheme['buttons']['secondary']['border']}; border-radius: 8px; padding: 8px 16px; font-weight: bold; }} QToolButton:hover {{ background-color: {lighttheme['buttons']['secondary']['bg_hover']}; border: 1px solid {lighttheme['buttons']['secondary']['border_hover']}; }} QToolButton:pressed {{ background-color: {lighttheme['buttons']['secondary']['bg_pressed']}; }}"

secondary_buttons = ['closeWindowButton', 'printDocumentButton']
for btn in secondary_buttons:
    add_stylesheet(btn, secondary_btn_qss)

# Add icon-only button styling
icon_btn_qss = f"QToolButton {{ background-color: {lighttheme['buttons']['icon_only']['bg']}; border: none; border-radius: 6px; padding: 8px; }} QToolButton:hover {{ background-color: {lighttheme['buttons']['icon_only']['bg_hover']}; }}"
add_stylesheet('settingsIconButton', icon_btn_qss)

# Add table styling
table_qss = f"""QTableWidget {{
    background-color: {lighttheme['table']['bg']};
    border: none;
    gridline-color: {lighttheme['table']['grid']};
    color: {lighttheme['table']['row_text']};
}}
QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {lighttheme['table']['row_border']};
}}
QTableWidget::item:selected {{
    background-color: {lighttheme['table']['row_selected_bg']};
    color: {lighttheme['table']['row_selected_text']};
}}
QTableWidget::item:hover {{
    background-color: {lighttheme['table']['row_hover']};
}}
QHeaderView::section {{
    background-color: {lighttheme['table']['header_bg']};
    color: {lighttheme['table']['header_text']};
    padding: 8px;
    border: none;
    border-bottom: 1px solid {lighttheme['table']['row_border']};
    font-weight: bold;
}}"""
add_stylesheet('transactionTable', table_qss)

# Write the modified content to the new file
output_path = r'd:\.Code\KONACH\src\daily_entry\daily_entry_styled.ui'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(ui_content)

print(f"✓ Created styled UI file: {output_path}")
print(f"✓ Renamed {len(widget_renames)} widgets")
print(f"✓ Applied styles to {len(glass_frames)} frames")
print(f"✓ Styled {len(field_labels)} labels")
print(f"✓ Styled {len(input_widgets)} input widgets")
print(f"✓ Styled {len(primary_buttons) + len(secondary_buttons) + 3} buttons")
print(f"✓ Applied table styling")
