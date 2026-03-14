from sqlalchemy.exc import SQLAlchemyError
from services import with_session, Agency, Account, Client, select
from sqlalchemy import distinct
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

def clear_all(self):
    self.Input_name.clear()
    self.ComboAgenceType.setCurrentIndex(0)
    self.Input_CIN.clear()
    self.Input_TelNumber.clear()
    self.Input_Adresse.clear()

@with_session
def set_agence_types(self, session=None):
    stmt = select(distinct(Agency.agency_type)).order_by(Agency.agency_type)
    result = session.execute(stmt).scalars().all()
    types = [type_ for type_ in result if type_]  # Filter out any None values
    
    self.ComboAgenceType.clear()
    for type_ in types:
        self.ComboAgenceType.addItem(f"{type_}")

    for i in range(self.ComboAgenceType.count()):
        self.ComboAgenceType.setItemData(i, Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)

@with_session
def check_type_exists(type_name, session=None):
    """Check if a type exists in the database"""
    stmt = select(Agency).where(Agency.agency_type == type_name).limit(1)
    result = session.execute(stmt).scalar_one_or_none()
    return result is not None

@with_session
def save_info(self, session=None):
    selected_id = self.tier_types.checkedId()
    if selected_id == 1:
        try:
            name = self.Input_name.text().strip()
            type_selected = self.ComboAgenceType.currentText().strip()
            
            # Validation
            if not name:
                QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم الوكالة!")
                return
            if not type_selected:
                QMessageBox.warning(self, "تحذير", "يرجى اختيار أو إدخال نوع الوكالة!")
                return
            
            agence_type = type_selected
            
            # Check if the type is new
            if not check_type_exists(agence_type):
                reply = QMessageBox.question(
                    self, 
                    "تأكيد النوع الجديد", 
                    f"النوع '{agence_type}' غير موجود في قاعدة البيانات.\nهل تريد إضافة هذا النوع الجديد؟",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            new_agence = Agency(
                agency_name=name,
                agency_type=agence_type,
                total_cashplus_transaction=0,
                alimentation=0,
                balance=0,
                is_active=True,
            )
            session.add(new_agence)
            session.commit()
            
            # Refresh the combo box to include the new type
            set_agence_types(self)
            
            # Success message
            QMessageBox.information(self, "نجح", "تم حفظ الوكالة بنجاح!")
            
        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {e}")
            return
    elif selected_id == 2:
        try:
            name = self.Input_name.text().strip()
            
            # Validation
            if not name:
                QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم الحساب!")
                return
            
            new_account = Account(account_name=name, is_active=True)
            session.add(new_account)
            session.commit()
            
            # Success message
            QMessageBox.information(self, "نجح", "تم حفظ الحساب بنجاح!")
            
        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {e}")
            return
    elif selected_id == 3:
        try:
            name = self.Input_name.text().strip()
            cin = self.Input_CIN.text().strip()
            tel_number = self.Input_TelNumber.text().strip()
            adresse = self.Input_Adresse.text().strip()
            
            # Validation with specific messages
            if not name:
                QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم العميل!")
                return
            if not cin:
                QMessageBox.warning(self, "تحذير", "يرجى إدخال رقم البطاقة الوطنية!")
                return
            if not tel_number:
                QMessageBox.warning(self, "تحذير", "يرجى إدخال رقم الهاتف!")
                return
            if not adresse:
                QMessageBox.warning(self, "تحذير", "يرجى إدخال العنوان!")
                return
            
            new_client = Client(
                full_name=name,
                cin=cin,
                phone=tel_number,
                address=adresse,
                total=0,
                total_paid=0,
                rest=0,
            )
            session.add(new_client)
            session.commit()
            
            # Success message
            QMessageBox.information(self, "نجح", "تم حفظ العميل بنجاح!")
            
        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {e}")
            return
    clear_all(self)

def setup_funcs(self):
    set_agence_types(self)
    self.Button_Save.clicked.connect(lambda: save_info(self))
    self.Button_CloseWindow.clicked.connect(self.close)