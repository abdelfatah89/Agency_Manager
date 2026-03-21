from sqlalchemy.exc import SQLAlchemyError
from services import with_session, Agency, Account, Client, select
from sqlalchemy import distinct, func as sql_func
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox


NONE_ITEM_TEXT = "-- بدون اختيار --"


def _normalize_text(value):
    return " ".join(str(value or "").strip().split())


@with_session
def _tier_name_exists(kind, name, exclude_id=None, session=None):
    normalized = _normalize_text(name)
    if not normalized:
        return False

    if kind == "agency":
        stmt = select(Agency.id).where(sql_func.lower(Agency.agency_name) == normalized.lower())
        if exclude_id is not None:
            stmt = stmt.where(Agency.id != int(exclude_id))
    elif kind == "account":
        stmt = select(Account.id).where(sql_func.lower(Account.account_name) == normalized.lower())
        if exclude_id is not None:
            stmt = stmt.where(Account.id != int(exclude_id))
    else:
        stmt = select(Client.id).where(sql_func.lower(Client.full_name) == normalized.lower())
        if exclude_id is not None:
            stmt = stmt.where(Client.id != int(exclude_id))

    return session.execute(stmt.limit(1)).scalar_one_or_none() is not None


@with_session
def _client_cin_exists(cin, exclude_id=None, session=None):
    normalized = _normalize_text(cin)
    if not normalized:
        return False

    stmt = select(Client.id).where(sql_func.lower(Client.cin) == normalized.lower())
    if exclude_id is not None:
        stmt = stmt.where(Client.id != int(exclude_id))

    return session.execute(stmt.limit(1)).scalar_one_or_none() is not None

def clear_all(self):
    self.Input_name.clear()
    self.ComboAgenceType.setCurrentIndex(0)
    self.Input_CIN.clear()
    self.Input_TelNumber.clear()
    self.Input_Adresse.clear()


def _selected_tier_kind(self):
    selected_id = self.tier_types.checkedId()
    if selected_id == 1:
        return "agency"
    if selected_id == 2:
        return "account"
    return "client"


def _set_edit_mode(self, editing):
    self.Button_Save.setText("تعديل" if editing else "حفظ")
    self.Button_Delete.setVisible(bool(editing))


def _sync_current_tier_label(self):
    kind = _selected_tier_kind(self)
    if kind == "agency":
        self.CurrentTiers.setText("وكالة حالية")
    elif kind == "account":
        self.CurrentTiers.setText("حساب حالي")
    else:
        self.CurrentTiers.setText("زبون حالي")


@with_session
def populate_current_tiers(self, session=None):
    kind = _selected_tier_kind(self)
    _sync_current_tier_label(self)

    self.ComboCurrentTiers.blockSignals(True)
    self.ComboCurrentTiers.clear()
    self.ComboCurrentTiers.addItem(NONE_ITEM_TEXT, None)

    if kind == "agency":
        rows = session.execute(select(Agency).where(Agency.is_active == True).order_by(Agency.agency_name)).scalars().all()
        for row in rows:
            self.ComboCurrentTiers.addItem(f"{row.agency_name}", int(row.id))
    elif kind == "account":
        rows = session.execute(select(Account).where(Account.is_active == True).order_by(Account.account_name)).scalars().all()
        for row in rows:
            self.ComboCurrentTiers.addItem(f"{row.account_name}", int(row.id))
    else:
        rows = session.execute(select(Client).order_by(Client.id)).scalars().all()
        for row in rows:
            self.ComboCurrentTiers.addItem(f"{row.id} - {row.full_name}", int(row.id))

    self.ComboCurrentTiers.setCurrentIndex(0)
    for i in range(self.ComboCurrentTiers.count()):
        self.ComboCurrentTiers.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)
    self.ComboCurrentTiers.blockSignals(False)

    clear_all(self)
    _set_edit_mode(self, False)


@with_session
def load_selected_tier_details(self, session=None):
    kind = _selected_tier_kind(self)
    selected_id = self.ComboCurrentTiers.currentData()

    if selected_id is None:
        clear_all(self)
        _set_edit_mode(self, False)
        return

    if kind == "agency":
        row = session.get(Agency, int(selected_id))
        if row is None:
            clear_all(self)
            _set_edit_mode(self, False)
            return
        self.Input_name.setText(row.agency_name or "")
        current_type = str(row.agency_type or "").strip()
        if current_type and self.ComboAgenceType.findText(current_type) < 0:
            self.ComboAgenceType.addItem(current_type)
        if current_type:
            self.ComboAgenceType.setCurrentText(current_type)
        else:
            self.ComboAgenceType.setCurrentIndex(0)

    elif kind == "account":
        row = session.get(Account, int(selected_id))
        if row is None:
            clear_all(self)
            _set_edit_mode(self, False)
            return
        self.Input_name.setText(row.account_name or "")

    else:
        row = session.get(Client, int(selected_id))
        if row is None:
            clear_all(self)
            _set_edit_mode(self, False)
            return
        self.Input_name.setText(row.full_name or "")
        self.Input_CIN.setText(row.cin or "")
        self.Input_TelNumber.setText(row.phone or "")
        self.Input_Adresse.setText(row.address or "")

    _set_edit_mode(self, True)

@with_session
def set_agence_types(self, session=None):
    stmt = select(distinct(Agency.agency_type)).order_by(Agency.agency_type)
    result = session.execute(stmt).scalars().all()
    types = [type_ for type_ in result if type_]  # Filter out any None values
    
    self.ComboAgenceType.clear()
    for type_ in types:
        self.ComboAgenceType.addItem(f"{type_}")

    for i in range(self.ComboAgenceType.count()):
        self.ComboAgenceType.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)

@with_session
def check_type_exists(type_name, session=None):
    """Check if a type exists in the database"""
    stmt = select(Agency).where(Agency.agency_type == type_name).limit(1)
    result = session.execute(stmt).scalar_one_or_none()
    return result is not None

@with_session
def save_info(self, session=None):
    kind = _selected_tier_kind(self)
    editing_id = self.ComboCurrentTiers.currentData()

    if kind == "agency":
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

            if _tier_name_exists("agency", name, exclude_id=editing_id):
                QMessageBox.warning(self, "تحذير", "اسم الوكالة موجود مسبقاً. لا يمكن إضافة عنصر مكرر.")
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
            
            if editing_id is None:
                row = Agency(
                    agency_name=name,
                    agency_type=agence_type,
                    total_cashplus_transaction=0,
                    alimentation=0,
                    balance=0,
                    is_active=True,
                )
                session.add(row)
            else:
                row = session.get(Agency, int(editing_id))
                if row is None:
                    QMessageBox.warning(self, "تحذير", "العنصر المحدد غير موجود")
                    populate_current_tiers(self)
                    return
                row.agency_name = name
                row.agency_type = agence_type
                row.is_active = True

            session.commit()
            
            # Refresh the combo box to include the new type
            set_agence_types(self)
            
            # Success message
            QMessageBox.information(self, "نجح", "تم تعديل الوكالة بنجاح!" if editing_id is not None else "تم حفظ الوكالة بنجاح!")
            
        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {e}")
            return
    elif kind == "account":
        try:
            name = self.Input_name.text().strip()
            
            # Validation
            if not name:
                QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم الحساب!")
                return

            if _tier_name_exists("account", name, exclude_id=editing_id):
                QMessageBox.warning(self, "تحذير", "اسم الحساب موجود مسبقاً. لا يمكن إضافة عنصر مكرر.")
                return
            
            if editing_id is None:
                row = Account(account_name=name, is_active=True)
                session.add(row)
            else:
                row = session.get(Account, int(editing_id))
                if row is None:
                    QMessageBox.warning(self, "تحذير", "العنصر المحدد غير موجود")
                    populate_current_tiers(self)
                    return
                row.account_name = name
                row.is_active = True
            session.commit()
            
            # Success message
            QMessageBox.information(self, "نجح", "تم تعديل الحساب بنجاح!" if editing_id is not None else "تم حفظ الحساب بنجاح!")
            
        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {e}")
            return
    elif kind == "client":
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

            if _tier_name_exists("client", name, exclude_id=editing_id):
                QMessageBox.warning(self, "تحذير", "اسم الزبون موجود مسبقاً. لا يمكن إضافة عنصر مكرر.")
                return

            if _client_cin_exists(cin, exclude_id=editing_id):
                QMessageBox.warning(self, "تحذير", "رقم البطاقة الوطنية موجود مسبقاً. لا يمكن إضافة عنصر مكرر.")
                return
            
            if editing_id is None:
                row = Client(
                    full_name=name,
                    cin=cin,
                    phone=tel_number,
                    address=adresse,
                    total=0,
                    total_paid=0,
                    rest=0,
                )
                session.add(row)
            else:
                row = session.get(Client, int(editing_id))
                if row is None:
                    QMessageBox.warning(self, "تحذير", "العنصر المحدد غير موجود")
                    populate_current_tiers(self)
                    return
                row.full_name = name
                row.cin = cin
                row.phone = tel_number
                row.address = adresse

            session.commit()
            
            # Success message
            QMessageBox.information(self, "نجح", "تم تعديل العميل بنجاح!" if editing_id is not None else "تم حفظ العميل بنجاح!")
            
        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {e}")
            return
    populate_current_tiers(self)


@with_session
def delete_selected_tier(self, session=None):
    kind = _selected_tier_kind(self)
    selected_id = self.ComboCurrentTiers.currentData()
    if selected_id is None:
        return

    reply = QMessageBox.question(
        self,
        "تأكيد الحذف",
        "هل أنت متأكد من حذف العنصر المحدد؟",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )
    if reply != QMessageBox.Yes:
        return

    try:
        if kind == "agency":
            row = session.get(Agency, int(selected_id))
            if row is None:
                QMessageBox.warning(self, "تحذير", "العنصر المحدد غير موجود")
                populate_current_tiers(self)
                return
            row.is_active = False
            session.commit()
            QMessageBox.information(self, "نجح", "تم حذف الوكالة بنجاح")

        elif kind == "account":
            row = session.get(Account, int(selected_id))
            if row is None:
                QMessageBox.warning(self, "تحذير", "العنصر المحدد غير موجود")
                populate_current_tiers(self)
                return
            row.is_active = False
            session.commit()
            QMessageBox.information(self, "نجح", "تم حذف الحساب بنجاح")

        else:
            row = session.get(Client, int(selected_id))
            if row is None:
                QMessageBox.warning(self, "تحذير", "العنصر المحدد غير موجود")
                populate_current_tiers(self)
                return
            session.delete(row)
            session.commit()
            QMessageBox.information(self, "نجح", "تم حذف الزبون بنجاح")

    except SQLAlchemyError as e:
        session.rollback()
        QMessageBox.critical(self, "خطأ", f"تعذر حذف العنصر: {e}")
        return

    populate_current_tiers(self)


def on_tier_mode_changed(self):
    populate_current_tiers(self)

def setup_funcs(self):
    set_agence_types(self)
    self.Button_Delete.setVisible(False)
    populate_current_tiers(self)

    self.Button_Save.clicked.connect(lambda: save_info(self))
    self.Button_Delete.clicked.connect(lambda: delete_selected_tier(self))
    self.ComboCurrentTiers.currentIndexChanged.connect(lambda _: load_selected_tier_details(self))
    self.tier_types.buttonClicked.connect(lambda _: on_tier_mode_changed(self))
    self.Button_CloseWindow.clicked.connect(self.close)