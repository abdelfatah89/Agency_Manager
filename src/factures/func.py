import logging
from sqlalchemy.exc import SQLAlchemyError
from services import with_session, Client, Transaction, select
from sqlalchemy import asc
from services.invoice_service import (
    reserve_invoice_number,
    mark_invoice_generated,
    mark_invoice_failed,
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from src.factures_generator.facture_generator import (
    extract_invoice_data,
    generate_invoice,
)


logger = logging.getLogger(__name__)

def add_transaction_row(self, date, designation, amount, paid_amount, transaction_id=None):
    """Helper method to add a row to the transaction table with checkboxes."""
    
    table = self.FacturesTable
    table.blockSignals(True)
    row = table.rowCount()
    table.insertRow(row)

    def cell(text, align=Qt.AlignCenter | Qt.AlignVCenter, item_data=None):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(align)
        if item_data is not None:
            item.setData(Qt.UserRole, item_data)
        return item

    # Add text cells
    table.setItem(row, 0, cell(date,                        Qt.AlignCenter   | Qt.AlignVCenter, transaction_id))
    table.setItem(row, 1, cell(designation,                 Qt.AlignCenter   | Qt.AlignVCenter))
    table.setItem(row, 2, cell(f"{amount:,.2f}",       Qt.AlignCenter   | Qt.AlignVCenter))
    table.setItem(row, 3, cell(f"{paid_amount:,.2f}",    Qt.AlignCenter   | Qt.AlignVCenter))  
    
    table.blockSignals(False)

def get_clients(self, session=None):
    """Get clients from database."""
    try:
        stmt = select(Client).order_by(Client.id)
        clients = session.execute(stmt).scalars()
        return clients
    except SQLAlchemyError as err:
        logger.exception("Error getting clients")
        return []

@with_session
def fill_client_combo(self, session=None):
    """Load accounts from database into the account combo box."""
    try:
        clients = get_clients(self, session)
        
        self.ComboBox_CustomerAccount.clear()
        self.ComboBox_CustomerAccount.addItem("-- اختر العميل --", None)
        for client in clients:
            self.ComboBox_CustomerAccount.addItem(client.full_name)
        
        self.ComboBox_CustomerAccount.view().setRowHidden(0, True)
        self.ComboBox_CustomerAccount.setCurrentIndex(0)
        for i in range(self.ComboBox_CustomerAccount.count()):
            self.ComboBox_CustomerAccount.setItemData(i, Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)
        
    except SQLAlchemyError as err:
        logger.exception("Error loading clients into combo")

def calculate_balance(self, transactions):
    try:
        if not transactions:
            self.Label_GrandTotalValue.setText("0.00")
            self.Label_PayValue.setText("0.00")
            self.Label_OverallRemainingValue.setText("0.00")
            return 0.0, 0.0, 0.0
            
        total_amount = sum(float(tran.amount or 0) for tran in transactions)
        total_paid = sum(float(tran.paid_amount or 0) for tran in transactions)
        rest = total_amount - total_paid
        self.Label_GrandTotalValue.setText(f"{total_amount:,.2f}")
        self.Label_PayValue.setText(f"{total_paid:,.2f}")
        self.Label_OverallRemainingValue.setText(f"{rest:,.2f}")
        return total_amount, total_paid, rest
    except SQLAlchemyError as err:
        logger.exception("Error calculating invoice balance")

@with_session
def load_daily_transactions(self, session=None):
    try:
        self.FacturesTable.setRowCount(0)

        item_selected = self.ComboBox_CustomerAccount.currentText()
        if not item_selected or item_selected == "-- اختر العميل --" or "اختر العميل" in item_selected:
            self._current_factures_transactions = []
            calculate_balance(self, [])
            return
        stmt = (
            select(Transaction)
            .where(Transaction.client_name == item_selected)
            .order_by(asc(Transaction.transaction_date), asc(Transaction.id))
        )
        transactions = session.execute(stmt).scalars().all()
        self._current_factures_transactions = [
            {
                "id": int(transaction.id),
                "transaction_date": str(transaction.transaction_date),
                "designation": transaction.designation,
                "amount": float(transaction.amount or 0),
                "paid_amount": float(transaction.paid_amount or 0),
            }
            for transaction in transactions
        ]
        for transaction in transactions:
            add_transaction_row(
                self,
                transaction.transaction_date,
                transaction.designation,
                float(transaction.amount or 0),
                float(transaction.paid_amount or 0),
                int(transaction.id),
            )
        calculate_balance(self, transactions)


    except SQLAlchemyError as err:
        logger.exception("Error loading invoice transactions")

@with_session
def filter_by_date(self, session=None):
    try:
        self.FacturesTable.setRowCount(0)

        item_selected = self.ComboBox_CustomerAccount.currentText()
        if not item_selected or item_selected == "-- اختر العميل --" or "اختر العميل" in item_selected:
            self._current_factures_transactions = []
            calculate_balance(self, [])
            return
        stmt = select(Transaction).where(
            Transaction.client_name == item_selected,
            Transaction.transaction_date.between(self.Input_FromDate.date().toPyDate(), self.Input_ToDate.date().toPyDate()),
        ).order_by(asc(Transaction.transaction_date), asc(Transaction.id))
        transactions = session.execute(stmt).scalars().all()
        self._current_factures_transactions = [
            {
                "id": int(transaction.id),
                "transaction_date": str(transaction.transaction_date),
                "designation": transaction.designation,
                "amount": float(transaction.amount or 0),
                "paid_amount": float(transaction.paid_amount or 0),
            }
            for transaction in transactions
        ]
        for transaction in transactions:
            add_transaction_row(
                self,
                transaction.transaction_date,
                transaction.designation,
                float(transaction.amount or 0),
                float(transaction.paid_amount or 0),
                int(transaction.id),
            )
        calculate_balance(self, transactions)

    except SQLAlchemyError as err:
        logger.exception("Error filtering invoice transactions")

def prepare_invoice(self):
    try:
        data = extract_invoice_data(self.FacturesTable, self.ComboBox_CustomerAccount, self.Input_FromDate, self.Input_ToDate, self.Label_GrandTotalValue, self.Label_PayValue, self.Label_OverallRemainingValue)
        tx_snapshot = getattr(self, "_current_factures_transactions", [])
        data["source_transactions"] = tx_snapshot

        reservation = reserve_invoice_number(
            source_type="factures",
            payload=data,
            issue_date=self.Input_ToDate.date().toPyDate(),
            client_name=data.get("client_name"),
            date_from=self.Input_FromDate.date().toPyDate(),
            date_to=self.Input_ToDate.date().toPyDate(),
        )

        data["invoice_no"] = reservation.invoice_number
        pdf_path = generate_invoice(data, invoice_number=reservation.invoice_number)

        if pdf_path:
            mark_invoice_generated(reservation.id, pdf_path)
            QMessageBox.information(self, "نجاح", f"تم إنشاء ملف PDF وفتحه بنجاح!\nالملف: {pdf_path}")
        else:
            mark_invoice_failed(reservation.id, "PDF generation returned no file path")
            QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء إنشاء ملف PDF.")
    except Exception as err:
        logger.exception("Error generating invoice")
        try:
            if "reservation" in locals():
                mark_invoice_failed(reservation.id, str(err))
        except Exception:
            logger.exception("Failed to persist facture invoice failure status")
        QMessageBox.critical(self, "خطأ", f"تعذر إنشاء الفاتورة:\n{err}")

def setup_funcs(self):
    from PyQt5.QtCore import QDate
    self.Input_FromDate.setDate(QDate.currentDate())
    self.Input_ToDate.setDate(QDate.currentDate())
    calculate_balance(self, [])
    
    fill_client_combo(self)

    self.ComboBox_CustomerAccount.currentIndexChanged.connect(lambda: load_daily_transactions(self))
    self.Button_Filter.clicked.connect(lambda: filter_by_date(self))
    self.Button_Reset.clicked.connect(lambda: load_daily_transactions(self))
    self.printBtn.clicked.connect(lambda: prepare_invoice(self))
