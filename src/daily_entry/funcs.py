"""
Backend functions for daily_entry module.
Refactored to the new schema centered on daily_sessions.
"""

import json
import logging
import sys
from datetime import date as dt_date
from pathlib import Path

from PyQt5.QtCore import QDate, Qt, QStringListModel
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from sqlalchemy import func as sql_func
from sqlalchemy.exc import SQLAlchemyError

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from services import (
    with_session,
    select,
    desc,
    Account,
    Agency,
    Client,
    CMITransaction,
    DailySession,
    Transaction,
)
from services.access_control import PERM_OPEN_FACTURES, has_permission
from services.invoice_service import (
    reserve_invoice_number,
    mark_invoice_generated,
    mark_invoice_failed,
)
from src.utils import calculate_agency_balances, parse_float
from src.utils.ui_helpers import apply_numeric_input_restrictions
from src.new_tiers.new_tiers import NewTiers
from src.factures.factures import FacturesWindow
from src.factures_generator.facture_generator import (
    extract_daily_invoice_data,
    generate_daily_invoice,
)


logger = logging.getLogger(__name__)


def _selected_client_id(self):
    cid = self.ComboBox_CustomerID.currentData()
    if cid is not None:
        return int(cid)

    raw = (self.ComboBox_CustomerID.currentText() or "").strip()
    if not raw or "اختر الزبون" in raw:
        return None

    prefix = raw.split("-")[0].strip()
    return int(prefix) if prefix.isdigit() else None


@with_session
def set_clientname(self, session=None):
    client_id = _selected_client_id(self)
    if not client_id:
        self.Input_CustomerName.clear()
        return

    client = session.get(Client, client_id)
    self.Input_CustomerName.setText(client.full_name if client else "")


def _get_or_create_daily_session(session, target_date):
    stmt = select(DailySession).where(DailySession.session_date == target_date)
    row = session.execute(stmt).scalar_one_or_none()
    if row:
        return row

    row = DailySession(session_date=target_date, status="open")
    session.add(row)
    session.flush()
    return row


def _normalize_designation(text):
    raw = str(text or "").strip()
    return " ".join(raw.split())


def _validate_required_transaction_fields(customer_name, account, client_id, designation):
    if not customer_name:
        return False, "الرجاء إدخال اسم الزبون!"
    if not account or account == "-- اختر الحساب --":
        return False, "الرجاء إدخال الحساب!"
    if not client_id:
        return False, "الرجاء إدخال الزبون!"
    if not _normalize_designation(designation):
        return False, "الرجاء إدخال وصف المعاملة!"
    return True, ""


def _collect_designation_suggestions(session, recent_limit=40, frequent_limit=40):
    suggestions = []
    seen = set()

    recent_rows = session.execute(
        select(Transaction.designation)
        .where(
            Transaction.designation.isnot(None),
            Transaction.designation != "",
        )
        .order_by(desc(Transaction.id))
        .limit(recent_limit)
    ).all()

    frequent_rows = session.execute(
        select(Transaction.designation)
        .where(
            Transaction.designation.isnot(None),
            Transaction.designation != "",
        )
        .group_by(Transaction.designation)
        .order_by(sql_func.count(Transaction.id).desc(), desc(sql_func.max(Transaction.id)))
        .limit(frequent_limit)
    ).all()

    for row in recent_rows + frequent_rows:
        value = _normalize_designation(row[0] if row else "")
        key = value.casefold()
        if not value or key in seen:
            continue
        seen.add(key)
        suggestions.append(value)

    return suggestions


def _apply_description_completer(self, suggestions):
    completer = getattr(self, "_item_description_completer", None)
    if completer is None:
        completer = QCompleter(self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.Input_ItemDescription.setCompleter(completer)
        self._item_description_completer = completer

    model = QStringListModel(suggestions, completer)
    completer.setModel(model)


@with_session
def refresh_description_suggestions(self, session=None):
    suggestions = _collect_designation_suggestions(session)
    _apply_description_completer(self, suggestions)


@with_session
def load_clients(self, session=None):
    try:
        stmt = select(Client).order_by(Client.id)
        clients = session.execute(stmt).scalars().all()

        self.ComboBox_CustomerID.clear()
        self.ComboBox_CustomerID.addItem("-- اختر الزبون --", None)
        for client in clients:
            self.ComboBox_CustomerID.addItem(f"{client.id} - {client.full_name}", client.id)

        self.ComboBox_CustomerID.view().setRowHidden(0, True)
        self.ComboBox_CustomerID.setCurrentIndex(0)
        for i in range(self.ComboBox_CustomerID.count()):
            self.ComboBox_CustomerID.setItemData(i, Qt.AlignmentFlag.AlignLeft, Qt.ItemDataRole.TextAlignmentRole)
    except SQLAlchemyError as err:
        logger.exception("Error loading clients")


@with_session
def load_accounts(self, session=None):
    try:
        accounts = session.execute(select(Account).order_by(Account.id)).scalars().all()
        agencies = session.execute(select(Agency).order_by(Agency.id)).scalars().all()

        self.ComboBox_CustomerAccount.clear()
        self.ComboBox_CustomerAccount.addItem("-- اختر الحساب --", None)

        for account in accounts:
            if bool(account.is_active):
                self.ComboBox_CustomerAccount.addItem(account.account_name)

        for agency in agencies:
            if bool(agency.is_active):
                self.ComboBox_CustomerAccount.addItem(agency.agency_name)

        self.ComboBox_CustomerAccount.view().setRowHidden(0, True)
        self.ComboBox_CustomerAccount.setCurrentIndex(0)
        for i in range(self.ComboBox_CustomerAccount.count()):
            self.ComboBox_CustomerAccount.setItemData(i, Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)
    except SQLAlchemyError as err:
        logger.exception("Error loading accounts")


@with_session
def calculate_overall_total(self, session=None):
    client_id = _selected_client_id(self)
    if not client_id:
        self.Label_PreviousTotalValue.setText("0.00")
        self.Label_TotalAmountValue.setText("0.00")
        return

    client = session.get(Client, client_id)
    if not client:
        self.Label_PreviousTotalValue.setText("0.00")
        self.Label_TotalAmountValue.setText("0.00")
        return

    client_name = client.full_name
    selected_date = self.Input_TransactionDate.date().toPyDate()

    all_rows = session.execute(select(Transaction).where(Transaction.client_name == client_name)).scalars().all()
    total_rest = sum(float(t.balance_due or 0) for t in all_rows)

    prev_rows = session.execute(
        select(Transaction).where(
            Transaction.client_name == client_name,
            Transaction.transaction_date < selected_date,
        )
    ).scalars().all()
    prev_total = sum(float(t.balance_due or 0) for t in prev_rows)

    total_amount = sum(float(t.amount or 0) for t in all_rows)
    total_paid = sum(float(t.paid_amount or 0) for t in all_rows)

    client.total = total_amount
    client.total_paid = total_paid
    client.rest = total_rest

    self.Label_PreviousTotalValue.setText(f"{prev_total:,.2f}")
    self.Label_TotalAmountValue.setText(f"{total_rest:,.2f}")


def get_commission_and_cost(amount):
    try:
        with open(str(Path(__file__).parent.parent / "cmi_trans" / "cost_setting.json"), "r", encoding="utf-8") as f:
            cost_setting = json.load(f)

        amount = float(amount)
        if amount <= 0:
            return 0.0, 0.0
        if amount <= 250:
            cost = float(cost_setting["le250"])
        elif amount <= 500:
            cost = float(cost_setting["le500"])
        elif amount <= 750:
            cost = float(cost_setting["le750"])
        elif amount <= 1000:
            cost = float(cost_setting["le1000"])
        else:
            cost = amount * float(cost_setting["g1000"])

        commission = cost - amount * 0.01
        return commission, cost
    except Exception as err:
        logger.exception("Error getting CMI commission/cost")
        return 0.0, 0.0


def _is_tpe_agency(session, account_name):
    agency_type = session.execute(
        select(Agency.agency_type).where(Agency.agency_name == account_name)
    ).scalar_one_or_none()
    return agency_type == "TPE"


def _upsert_cmi_row(session, transaction_date, agency_name, designation, amount, alimentation):
    commission, cost = get_commission_and_cost(amount)
    paid_amount = amount - cost

    existing = session.execute(
        select(CMITransaction)
        .where(
            CMITransaction.transaction_date == transaction_date,
            CMITransaction.agency_name == agency_name,
            CMITransaction.designation == designation,
        )
        .order_by(desc(CMITransaction.id))
    ).scalars().first()

    if existing:
        existing.amount = float(amount)
        existing.paid_amount = float(paid_amount)
        existing.cost = float(cost)
        existing.commission = float(commission)
        existing.alimentation = float(alimentation)
        return

    session.add(
        CMITransaction(
            transaction_date=transaction_date,
            agency_name=agency_name,
            amount=float(amount),
            paid_amount=float(paid_amount),
            cost=float(cost),
            commission=float(commission),
            alimentation=float(alimentation),
            designation=designation,
        )
    )


@with_session
def save_transaction_to_db(self, session=None):
    table = self.Table_TransactionsList
    if table.rowCount() == 0:
        QMessageBox.warning(self, "تحذير", "لا توجد معاملات للحفظ!")
        return False

    try:
        transaction_date = self.Input_TransactionDate.date().toPyDate()
        daily_session = _get_or_create_daily_session(session, transaction_date)

        client_id = _selected_client_id(self)
        customer_name = self.Input_CustomerName.text().strip()
        account = self.ComboBox_CustomerAccount.currentText().strip()

        if not customer_name:
            QMessageBox.warning(self, "تحذير", "الرجاء إدخال اسم الزبون!")
            return False
        if not account or account == "-- اختر الحساب --":
            QMessageBox.warning(self, "تحذير", "الرجاء إدخال الحساب!")
            return False
        if not client_id:
            QMessageBox.warning(self, "تحذير", "الرجاء إدخال الزبون!")
            return False

        for row in range(table.rowCount()):
            designation_item = table.item(row, 0)
            designation = designation_item.text() if designation_item else ""
            is_valid, message = _validate_required_transaction_fields(customer_name, account, client_id, designation)
            if not is_valid:
                QMessageBox.warning(self, "تحذير", message)
                return False
            trans_id = designation_item.data(Qt.UserRole) if designation_item else None

            qty = float(table.item(row, 1).text() if table.item(row, 1) else "1")
            unit_price = float(table.item(row, 2).text().replace(",", "") if table.item(row, 2) else "0")
            payment = float(table.item(row, 3).text().replace(",", "") if table.item(row, 3) else "0")
            remaining = float(table.item(row, 4).text().replace(",", "") if table.item(row, 4) else "0")

            inbox_checked = get_checkbox_state(table, row, 5)
            outbox_checked = get_checkbox_state(table, row, 6)
            total_amount = float(unit_price * qty)

            if trans_id is not None:
                transaction = session.get(Transaction, int(trans_id))
                if transaction:
                    transaction.daily_id = daily_session.id
                    transaction.transaction_date = transaction_date
                    transaction.client_name = customer_name
                    transaction.account_name = account
                    transaction.designation = designation
                    transaction.amount = total_amount
                    transaction.paid_amount = float(payment)
                    transaction.balance_due = float(remaining)
                    transaction.today_in = bool(inbox_checked)
                    transaction.today_out = bool(outbox_checked)
            else:
                session.add(
                    Transaction(
                        daily_id=daily_session.id,
                        transaction_date=transaction_date,
                        client_name=customer_name,
                        account_name=account,
                        designation=designation,
                        amount=total_amount,
                        paid_amount=float(payment),
                        balance_due=float(remaining),
                        today_in=bool(inbox_checked),
                        today_out=bool(outbox_checked),
                    )
                )

            if _is_tpe_agency(session, account):
                _upsert_cmi_row(session, transaction_date, account, designation, total_amount, float(payment))

        calculate_agency_balances(session)

        QMessageBox.information(self, "نجح", f"تم حفظ {table.rowCount()} معاملة بنجاح!")
        return True
    except SQLAlchemyError as err:
        session.rollback()
        QMessageBox.critical(self, "Database Error", f"Failed to save transactions:\n{err}")
        logger.exception("Error saving transactions")
        return False
    except ValueError as err:
        session.rollback()
        QMessageBox.warning(self, "خطأ في البيانات", f"تحقق من صحة الأرقام المدخلة:\n{err}")
        return False


@with_session
def load_transactions_for_date(self, session=None):
    try:
        self.Table_TransactionsList.setRowCount(0)

        client_name = self.Input_CustomerName.text().strip()
        client_id = _selected_client_id(self)
        if not client_name and client_id:
            client = session.get(Client, client_id)
            client_name = client.full_name if client else ""

        if not client_name:
            update_totals(self)
            return

        account = self.ComboBox_CustomerAccount.currentText().strip()
        py_date = self.Input_TransactionDate.date().toPyDate()

        daily_session = session.execute(
            select(DailySession).where(DailySession.session_date == py_date)
        ).scalar_one_or_none()

        if not daily_session:
            update_totals(self)
            return

        stmt = (
            select(Transaction)
            .where(
                Transaction.daily_id == daily_session.id,
                Transaction.transaction_date == py_date,
                Transaction.client_name == client_name,
                Transaction.account_name == account,
            )
            .order_by(Transaction.id)
        )
        transactions = session.execute(stmt).scalars().all()

        for trans in transactions:
            add_transaction_row(
                self,
                designation=trans.designation,
                qty=1,
                unit_price=float(trans.amount or 0),
                payment=float(trans.paid_amount or 0),
                remaining=float(trans.balance_due or 0),
                inbox=bool(trans.today_in),
                outbox=bool(trans.today_out),
                trans_id=trans.id,
            )

        update_totals(self)
    except SQLAlchemyError as err:
        logger.exception("Error loading transactions for date")


@with_session
def save_single_transaction(
    self,
    designation,
    qty,
    unit_price,
    payment,
    remaining,
    inbox=False,
    outbox=False,
    trans_id=None,
    session=None,
):
    try:
        transaction_date = self.Input_TransactionDate.date().toPyDate()
        daily_session = _get_or_create_daily_session(session, transaction_date)

        customer_name = self.Input_CustomerName.text().strip()
        account = self.ComboBox_CustomerAccount.currentText().strip()
        client_id = _selected_client_id(self)

        is_valid, message = _validate_required_transaction_fields(customer_name, account, client_id, designation)
        if not is_valid:
            QMessageBox.warning(self, "تحذير", message)
            return False

        amount = float(unit_price) * float(qty)

        if trans_id is not None:
            transaction = session.get(Transaction, int(trans_id))
            if transaction:
                transaction.daily_id = daily_session.id
                transaction.transaction_date = transaction_date
                transaction.client_name = customer_name
                transaction.account_name = account
                transaction.designation = designation
                transaction.amount = float(amount)
                transaction.paid_amount = float(payment)
                transaction.balance_due = float(remaining)
                transaction.today_in = bool(inbox)
                transaction.today_out = bool(outbox)
        else:
            session.add(
                Transaction(
                    daily_id=daily_session.id,
                    transaction_date=transaction_date,
                    client_name=customer_name,
                    account_name=account,
                    designation=designation,
                    amount=float(amount),
                    paid_amount=float(payment),
                    balance_due=float(remaining),
                    today_in=bool(inbox),
                    today_out=bool(outbox),
                )
            )

        if _is_tpe_agency(session, account):
            _upsert_cmi_row(session, transaction_date, account, designation, amount, float(payment))

        calculate_agency_balances(session)

        return True
    except SQLAlchemyError as err:
        session.rollback()
        QMessageBox.critical(self, "Database Error", f"فشل حفظ المعاملة:\n{err}")
        logger.exception("Error saving single transaction")
        return False
    except ValueError as err:
        session.rollback()
        QMessageBox.warning(self, "خطأ في البيانات", f"تحقق من صحة الأرقام المدخلة:\n{err}")
        return False


def add_transaction_row(self, designation, qty, unit_price, payment, remaining, inbox=False, outbox=False, trans_id=None):
    from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QWidget

    table = self.Table_TransactionsList
    table.blockSignals(True)
    row = table.rowCount()
    table.insertRow(row)

    def cell(text, align=Qt.AlignCenter | Qt.AlignVCenter, item_data=None):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(align)
        if item_data is not None:
            item.setData(Qt.UserRole, item_data)
        return item

    def create_checkbox_cell(checked=False):
        checkbox = QCheckBox()
        checkbox.setChecked(checked)
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return widget

    table.setItem(row, 0, cell(designation, Qt.AlignCenter | Qt.AlignVCenter, trans_id))
    table.setItem(row, 1, cell(str(qty), Qt.AlignHCenter | Qt.AlignVCenter))
    table.setItem(row, 2, cell(f"{unit_price:,.2f}", Qt.AlignCenter | Qt.AlignVCenter))
    table.setItem(row, 3, cell(f"{payment:,.2f}", Qt.AlignCenter | Qt.AlignVCenter))
    table.setItem(row, 4, cell(f"{remaining:,.2f}", Qt.AlignCenter | Qt.AlignVCenter))

    table.setCellWidget(row, 5, create_checkbox_cell(inbox))
    table.setCellWidget(row, 6, create_checkbox_cell(outbox))
    table.blockSignals(False)


def get_checkbox_state(table, row, col):
    from PyQt5.QtWidgets import QCheckBox

    widget = table.cellWidget(row, col)
    if widget:
        checkbox = widget.findChild(QCheckBox)
        if checkbox:
            return checkbox.isChecked()
    return False


def recalculate(self):
    try:
        unit = float(self.Input_ItemUnitPrice.text().replace(",", "") or 0)
        qty = self.Input_ItemQuantity.value()
        payment = float(self.Input_PaymentAmount.text().replace(",", "") or 0)
        total = unit * qty
        remaining = total - payment
        self.Input_RemainingAmount.setText(f"{remaining:,.2f}")
    except ValueError:
        self.Input_RemainingAmount.clear()


def update_totals(self):
    table = self.Table_TransactionsList
    total = 0.0
    total_paid = 0.0
    total_remaining = 0.0

    if table.rowCount() == 0:
        self.Label_GrandTotalValue.setText("0.00")
        self.Label_PayValue.setText("0.00")
        self.Label_OverallRemainingValue.setText("0.00")
        calculate_overall_total(self)
        return

    for row in range(table.rowCount()):
        def _val(col, r=row):
            item = table.item(r, col)
            if not item:
                return 0.0
            try:
                return float(item.text().replace(",", ""))
            except ValueError:
                return 0.0

        total += _val(2)
        total_paid += _val(3)
        total_remaining += _val(4)

    self.Label_GrandTotalValue.setText(f"{total:,.2f}")
    self.Label_PayValue.setText(f"{total_paid:,.2f}")
    self.Label_OverallRemainingValue.setText(f"{total_remaining:,.2f}")
    calculate_overall_total(self)


def on_date_changed(self):
    load_transactions_for_date(self)
    update_totals(self)
    on_cancel(self)


def on_customer_selected(self, index):
    if index > 0:
        set_clientname(self)
    else:
        self.Input_CustomerName.clear()
    load_transactions_for_date(self)
    update_totals(self)


def on_verify(self):
    if save_transaction_to_db(self):
        logger.info("All transactions saved successfully")
        load_transactions_for_date(self)
        refresh_description_suggestions(self)


def on_table_row_clicked(self, row, column):
    table = self.Table_TransactionsList
    designation_item = table.item(row, 0)
    trans_id = designation_item.data(Qt.UserRole) if designation_item else None

    self.Input_ItemDescription.setText(table.item(row, 0).text() if table.item(row, 0) else "")
    self.Input_ItemQuantity.setValue(int(float(table.item(row, 1).text() if table.item(row, 1) else "1")))
    self.Input_ItemUnitPrice.setText(table.item(row, 2).text().replace(",", "") if table.item(row, 2) else "0")
    self.Input_PaymentAmount.setText(table.item(row, 3).text().replace(",", "") if table.item(row, 3) else "0")
    self.Input_RemainingAmount.setText(table.item(row, 4).text().replace(",", "") if table.item(row, 4) else "0")

    if hasattr(self, "CheckBox_TransactionIn"):
        self.CheckBox_TransactionIn.setChecked(get_checkbox_state(table, row, 5))
    if hasattr(self, "CheckBox_TransactionOut"):
        self.CheckBox_TransactionOut.setChecked(get_checkbox_state(table, row, 6))

    self.current_edit_row = row
    self.current_trans_id = trans_id
    self.Button_AddItem.setText("حفظ التعديلات")


def on_add_item(self):
    inbox_checked = self.CheckBox_TransactionIn.isChecked() if hasattr(self, "CheckBox_TransactionIn") else False
    outbox_checked = self.CheckBox_TransactionOut.isChecked() if hasattr(self, "CheckBox_TransactionOut") else False

    try:
        unit_price = float(self.Input_ItemUnitPrice.text().replace(",", "") or 0)
        qty = self.Input_ItemQuantity.value()
        payment = float(self.Input_PaymentAmount.text().replace(",", "") or 0)
        remaining = float(self.Input_RemainingAmount.text().replace(",", "") or 0)
    except ValueError:
        QMessageBox.warning(self, "خطأ", "يرجى التحقق من الأرقام المدخلة")
        return

    trans_id = None
    if getattr(self, "current_edit_row", None) is not None:
        row = self.current_edit_row
        designation_item = self.Table_TransactionsList.item(row, 0)
        if designation_item:
            trans_id = designation_item.data(Qt.UserRole)

    success = save_single_transaction(
        self,
        designation=self.Input_ItemDescription.text(),
        qty=qty,
        unit_price=unit_price,
        payment=payment,
        remaining=remaining,
        inbox=inbox_checked,
        outbox=outbox_checked,
        trans_id=trans_id,
    )

    if success:
        load_transactions_for_date(self)
        refresh_description_suggestions(self)
        on_cancel(self)


@with_session
def delete_transaction_from_db(self, trans_id, session=None):
    try:
        if trans_id is None:
            return False

        transaction = session.get(Transaction, int(trans_id))
        if not transaction:
            QMessageBox.warning(self, "تحذير", "لم يتم العثور على المعاملة")
            return False

        if _is_tpe_agency(session, transaction.account_name):
            cmi_match = session.execute(
                select(CMITransaction)
                .where(
                    CMITransaction.transaction_date == transaction.transaction_date,
                    CMITransaction.agency_name == transaction.account_name,
                    CMITransaction.designation == transaction.designation,
                )
                .order_by(desc(CMITransaction.id))
            ).scalars().first()
            if cmi_match:
                session.delete(cmi_match)

        session.delete(transaction)
        calculate_agency_balances(session)
        return True
    except SQLAlchemyError as err:
        session.rollback()
        QMessageBox.critical(self, "Database Error", f"فشل حذف المعاملة:\n{err}")
        logger.exception("Error deleting transaction")
        return False


def on_delete_item(self):
    rows = self.Table_TransactionsList.selectedItems()
    if not rows:
        return

    row = rows[0].row()
    designation_item = self.Table_TransactionsList.item(row, 0)
    trans_id = designation_item.data(Qt.UserRole) if designation_item else None

    if trans_id is not None:
        reply = QMessageBox.question(
            self,
            "تأكيد الحذف",
            "هل أنت متأكد من حذف هذه المعاملة؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes and delete_transaction_from_db(self, trans_id):
            load_transactions_for_date(self)
            on_cancel(self)
            calculate_overall_total(self)
        return

    self.Table_TransactionsList.removeRow(row)
    update_totals(self)
    calculate_overall_total(self)


def clear_all(self):
    self.ComboBox_CustomerID.setCurrentIndex(0)
    self.ComboBox_CustomerAccount.setCurrentIndex(0)
    self.Input_TransactionDate.setDate(QDate.currentDate())
    self.Table_TransactionsList.setRowCount(0)
    self.Input_ItemDescription.clear()
    self.Input_ItemUnitPrice.clear()
    self.Input_PaymentAmount.clear()
    self.Input_RemainingAmount.clear()
    self.Input_ItemQuantity.setValue(1)
    self.CheckBox_TransactionIn.setChecked(False)
    self.CheckBox_TransactionOut.setChecked(False)
    self.current_edit_row = None
    self.current_trans_id = None
    self.Button_AddItem.setText("إضافة")
    update_totals(self)


def on_cancel(self):
    self.Input_ItemDescription.clear()
    self.Input_ItemUnitPrice.clear()
    self.Input_PaymentAmount.clear()
    self.Input_RemainingAmount.clear()
    self.Input_ItemQuantity.setValue(1)

    if hasattr(self, "CheckBox_TransactionIn"):
        self.CheckBox_TransactionIn.setChecked(False)
    if hasattr(self, "CheckBox_TransactionOut"):
        self.CheckBox_TransactionOut.setChecked(False)

    self.current_edit_row = None
    self.current_trans_id = None
    self.Button_AddItem.setText("إضافة")


def on_new_document(self):
    clear_all(self)


def on_print(self):
    try:
        vat_label = (
            getattr(self, "Label_TVAValue", None)
            or getattr(self, "Label_VATValue", None)
            or getattr(self, "Label_TotalVatValue", None)
            or getattr(self, "Label_TotalTVAValue", None)
        )

        data = extract_daily_invoice_data(
            self.Table_TransactionsList,
            self.ComboBox_CustomerID,
            self.Input_CustomerName,
            self.ComboBox_CustomerAccount,
            self.Input_TransactionDate,
            self.Label_GrandTotalValue,
            self.Label_PayValue,
            self.Label_OverallRemainingValue,
            vat_label,
        )

        table_snapshot = []
        for row in range(self.Table_TransactionsList.rowCount()):
            row_data = []
            for col in range(5):
                item = self.Table_TransactionsList.item(row, col)
                row_data.append(item.text().strip() if item and item.text() else "")
            table_snapshot.append(row_data)

        data["source_rows"] = table_snapshot

        reservation = reserve_invoice_number(
            source_type="daily_entry",
            payload=data,
            issue_date=self.Input_TransactionDate.date().toPyDate(),
            client_name=data.get("client_name"),
            account_name=data.get("account_name"),
            date_from=self.Input_TransactionDate.date().toPyDate(),
            date_to=self.Input_TransactionDate.date().toPyDate(),
        )

        data["invoice_no"] = reservation.invoice_number
        pdf_path = generate_daily_invoice(data, invoice_number=reservation.invoice_number)

        if pdf_path:
            mark_invoice_generated(reservation.id, pdf_path)
            QMessageBox.information(self, "نجاح", f"تم إنشاء ملف PDF وفتحه بنجاح!\nالملف: {pdf_path}")
        else:
            mark_invoice_failed(reservation.id, "PDF generation returned no file path")
            QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء إنشاء ملف PDF.")
    except Exception as err:
        logger.exception("Daily entry invoice generation failed")
        try:
            if "reservation" in locals():
                mark_invoice_failed(reservation.id, str(err))
        except Exception:
            logger.exception("Failed to persist invoice failure status")
        QMessageBox.critical(self, "خطأ", f"تعذر طباعة الفاتورة:\n{err}")


def on_checkbox(self, box):
    checkbox = getattr(self, box)
    unit_price = parse_float(self.Input_ItemUnitPrice.text())
    payment = parse_float(self.Input_PaymentAmount.text())

    # Treat 0 / 0.00 as empty for this validation.
    if unit_price > 0 and payment > 0 and checkbox.checkState():
        QMessageBox.warning(self, "تحذير", "لا يمكن ملأ خانتا الدفع والمبلغ\nفي حالة تحديد IN او OUT في سجل واحد")
        checkbox.setCheckState(False)


def open_new_tiers_dialog(self):
    dialog = NewTiers(self)
    dialog.exec_()
    load_clients(self)
    load_accounts(self)


def open_list_transactions(self):
    try:
        current_role = getattr(self, "_current_user_role", None)
        if not has_permission(current_role, PERM_OPEN_FACTURES):
            raise PermissionError("ليس لديك صلاحية للوصول إلى الفواتير")

        window = getattr(self, "_factures_window", None)
        if window is None:
            window = FacturesWindow(parent=self, current_user_role=current_role)
            self._factures_window = window

        window.show()
        window.raise_()
        window.activateWindow()
    except PermissionError as err:
        QMessageBox.warning(self, "صلاحيات غير كافية", str(err))
    except Exception as err:
        logger.exception("Error while opening factures window from daily entry")
        QMessageBox.critical(self, "خطأ", f"تعذر فتح نافذة الفواتير:\n{err}")


def setup_funcs(self):
    apply_numeric_input_restrictions(
        self,
        force_numeric_names=[
            "Input_ItemUnitPrice",
            "Input_PaymentAmount",
            "Input_RemainingAmount",
        ],
    )

    load_clients(self)
    load_accounts(self)
    refresh_description_suggestions(self)

    self.ComboBox_CustomerAccount.currentIndexChanged.connect(lambda: load_transactions_for_date(self))

    self.Button_VerifyCustomer.clicked.connect(lambda: on_verify(self))
    self.Button_AddItem.clicked.connect(lambda: on_add_item(self))
    self.Button_DeleteItem.clicked.connect(lambda: on_delete_item(self))
    self.Button_CancelItem.clicked.connect(lambda: on_cancel(self))
    self.Button_NewTransaction.clicked.connect(lambda: on_new_document(self))
    self.Button_PrintTransaction.clicked.connect(lambda: on_print(self))

    self.Table_TransactionsList.cellClicked.connect(lambda row, col: on_table_row_clicked(self, row, col))
    self.Input_TransactionDate.dateChanged.connect(lambda date: on_date_changed(self))
    self.ComboBox_CustomerID.currentIndexChanged.connect(lambda index: on_customer_selected(self, index))

    self.Input_ItemUnitPrice.textChanged.connect(lambda: recalculate(self))
    self.Input_PaymentAmount.textChanged.connect(lambda: recalculate(self))
    self.Input_ItemQuantity.valueChanged.connect(lambda: recalculate(self))
    self.Table_TransactionsList.itemChanged.connect(lambda: update_totals(self))

    self.Button_AddTier.clicked.connect(lambda: open_new_tiers_dialog(self))
    self.Button_ListTransactions.clicked.connect(lambda: open_list_transactions(self))

    self.CheckBox_TransactionIn.stateChanged.connect(lambda: on_checkbox(self, "CheckBox_TransactionIn"))
    self.CheckBox_TransactionOut.stateChanged.connect(lambda: on_checkbox(self, "CheckBox_TransactionOut"))
