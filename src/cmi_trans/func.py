from sqlalchemy.exc import SQLAlchemyError
from services import with_session, Agency, CMITransaction, select, extract
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from src.cmi_trans.cost_settings import CostSettings
from src.utils import parse_float
from datetime import date, datetime

def open_cost_settings(self):
    self.cost_settings_window = CostSettings(self)
    self.cost_settings_window.exec_()

def get_TpeAgences(self, session=None):
    stmt = select(Agency).order_by(Agency.id)
    agencies = session.execute(stmt).scalars().all()
    return [agency.agency_name for agency in agencies if (agency.agency_type or "").lower() == "tpe"]

@with_session
def fill_tpe_agence_combo(self, session=None):
    """Load accounts from database into the account combo box."""
    try:
        tpe_agences = get_TpeAgences(self, session)
        
        self.ComboBox_TPEagence.clear()
        self.ComboBox_TPEagence.addItem("-- اختر وكالة TPE --", None)
        for tpe_agence in tpe_agences:
            self.ComboBox_TPEagence.addItem(tpe_agence)
        
        self.ComboBox_TPEagence.view().setRowHidden(0, True)
        self.ComboBox_TPEagence.setCurrentIndex(0)
        for i in range(self.ComboBox_TPEagence.count()):
            self.ComboBox_TPEagence.setItemData(i, Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)
        
    except SQLAlchemyError as err:
        print(f"[DB] Error loading accounts: {err}")

def add_transaction_row(self, tx_date, amount, paid_amount, cost, commission, alimentation, designation):
    """Helper method to add a row to the transaction table with checkboxes."""
    
    table = self.transactionsTable
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
    table.setItem(row, 0, cell(tx_date,                Qt.AlignCenter | Qt.AlignVCenter))
    table.setItem(row, 1, cell(f"{amount:,.2f}",     Qt.AlignCenter   | Qt.AlignVCenter))
    table.setItem(row, 2, cell(f"{paid_amount:,.2f}",     Qt.AlignCenter   | Qt.AlignVCenter))
    table.setItem(row, 3, cell(f"{cost:,.2f}",     Qt.AlignCenter   | Qt.AlignVCenter))
    table.setItem(row, 4, cell(f"{commission:,.2f}",     Qt.AlignCenter   | Qt.AlignVCenter))
    table.setItem(row, 5, cell(f"{alimentation:,.2f}",  Qt.AlignCenter   | Qt.AlignVCenter))  
    table.setItem(row, 6, cell(designation,         Qt.AlignCenter | Qt.AlignVCenter))
    
    table.blockSignals(False)


def calculate_balance(self, session=None):
    try:
        stmt = select(CMITransaction).where(CMITransaction.agency_name == self.ComboBox_TPEagence.currentText())
        transactions = session.execute(stmt).scalars().all()
        total_alimentation = sum(parse_float(tran.alimentation) for tran in transactions)
        total_safe_cost = sum(parse_float(tran.cost) - (parse_float(tran.amount) * 0.02) for tran in transactions)
        total_paid_amount = sum(parse_float(tran.paid_amount) for tran in transactions)
        total_commission = sum(parse_float(tran.commission) for tran in transactions)
        bankbalance = sum(parse_float(tran.amount) - (parse_float(tran.amount) * 0.01) for tran in transactions)
        self.Label_ReccentBalanceVal.setText(f"{total_alimentation - total_paid_amount + total_safe_cost:,.2f}")
        self.bankValueLabel.setText(f"{bankbalance:,.2f}")
        self.paidClientsValueLabel.setText(f"{total_paid_amount:,.2f}")
        self.costValueLabel.setText(f"{total_commission:,.2f}")
    except SQLAlchemyError as err:
        print(f"[DB] Error calculating balance: {err}")

def calculate_filtred_balance(self, transactions):
    try:
        total_alimentation = sum(parse_float(tran.alimentation) for tran in transactions)
        total_safe_cost = sum(parse_float(tran.cost) - (parse_float(tran.amount) * 0.02) for tran in transactions)
        total_paid_amount = sum(parse_float(tran.paid_amount) for tran in transactions)
        total_commission = sum(parse_float(tran.commission) for tran in transactions)
        bankbalance = sum(parse_float(tran.amount) - (parse_float(tran.amount) * 0.01) for tran in transactions)
        self.Label_ReccentBalanceVal.setText(f"{total_alimentation - total_paid_amount + total_safe_cost:,.2f}")
        self.bankValueLabel.setText(f"{bankbalance:,.2f}")
        self.paidClientsValueLabel.setText(f"{total_paid_amount:,.2f}")
        self.costValueLabel.setText(f"{total_commission:,.2f}")
    except SQLAlchemyError as err:
        print(f"[DB] Error calculating balance: {err}")


def _parse_tx_date(value):
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()

    text = str(value).strip()
    if not text:
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _render_daily_summary_rows(self, daily_summaries):
    self.transactionsTable.setRowCount(0)
    for day in sorted(daily_summaries.keys()):
        daily = daily_summaries[day]
        add_transaction_row(
            self,
            day.strftime("%Y-%m-%d"),
            daily["amount"],
            daily["paid_amount"],
            daily["cost"],
            daily["commission"],
            daily["alimentation"],
            "ملخص يومي",
        )


def _clear_cmi_summary(self):
    self.transactionsTable.setRowCount(0)
    self.Label_ReccentBalanceVal.setText("0.00")
    self.bankValueLabel.setText("0.00")
    self.paidClientsValueLabel.setText("0.00")
    self.costValueLabel.setText("0.00")


def _month_grouped_transactions(transactions, selected_year, selected_month):
    grouped = {}
    source_rows = []

    for tx in transactions:
        tx_date = _parse_tx_date(getattr(tx, "transaction_date", None))
        if tx_date is None:
            continue
        if tx_date.year != selected_year or tx_date.month != selected_month:
            continue

        source_rows.append(tx)

        if tx_date not in grouped:
            grouped[tx_date] = {
                "amount": 0.0,
                "paid_amount": 0.0,
                "cost": 0.0,
                "commission": 0.0,
                "alimentation": 0.0,
            }

        grouped[tx_date]["amount"] += parse_float(tx.amount)
        grouped[tx_date]["paid_amount"] += parse_float(tx.paid_amount)
        grouped[tx_date]["cost"] += parse_float(tx.cost)
        grouped[tx_date]["commission"] += parse_float(tx.commission)
        grouped[tx_date]["alimentation"] += parse_float(tx.alimentation)

    return grouped, source_rows

@with_session
def load_tpe_transactions(self, session=None):
    try:
        self.transactionsTable.setRowCount(0)

        item_selected = self.ComboBox_TPEagence.currentText()
        if item_selected == "-- اختر وكالة TPE --" or "اختر وكالة TPE" in item_selected:
            return
        stmt = select(CMITransaction).where(CMITransaction.agency_name == item_selected)
        transactions = session.execute(stmt).scalars().all()
        for transaction in transactions:
            add_transaction_row(
                self,
                transaction.transaction_date,
                float(transaction.amount or 0),
                float(transaction.paid_amount or 0),
                float(transaction.cost or 0),
                float(transaction.commission or 0),
                float(transaction.alimentation or 0),
                transaction.designation,
            )
        calculate_balance(self, session)


    except SQLAlchemyError as err:
        print(f"[DB] Error loading daily transactions: {err}")

@with_session
def filter_by_month(self, session=None):
    try:
        item_selected = self.ComboBox_TPEagence.currentText()
        if item_selected == "-- اختر وكالة TPE --" or "اختر وكالة TPE" in item_selected:
            QMessageBox.warning(self, "تصفية شهرية", "اختر وكالة TPE أولاً")
            _clear_cmi_summary(self)
            return

        selected_date = self.Input_TpeMounth.date().toPyDate()
        if selected_date is None:
            QMessageBox.warning(self, "تصفية شهرية", "الشهر المحدد غير صالح")
            return

        stmt = select(CMITransaction).where(CMITransaction.agency_name == item_selected)
        transactions = session.execute(stmt).scalars().all()

        grouped, source_rows = _month_grouped_transactions(
            transactions,
            selected_date.year,
            selected_date.month,
        )

        if not grouped:
            QMessageBox.information(self, "تصفية شهرية", "لا توجد بيانات لهذا الشهر")
            _clear_cmi_summary(self)
            return

        _render_daily_summary_rows(self, grouped)
        calculate_filtred_balance(self, source_rows)

    except SQLAlchemyError as err:
        print(f"[DB] Error loading daily transactions: {err}")


@with_session
def filter_by_date(self, session=None):
    try:
        self.transactionsTable.setRowCount(0)

        item_selected = self.ComboBox_TPEagence.currentText()
        if item_selected == "-- اختر الحساب/الوكالة --" or "اختر الحساب/الوكالة" in item_selected:
            return
        stmt = select(CMITransaction).where(
            CMITransaction.agency_name == item_selected,
            CMITransaction.transaction_date == self.Input_TpeDate.date().toPyDate(),
        )
        transactions = session.execute(stmt).scalars().all()
        for transaction in transactions:
            add_transaction_row(
                self,
                transaction.transaction_date,
                float(transaction.amount or 0),
                float(transaction.paid_amount or 0),
                float(transaction.cost or 0),
                float(transaction.commission or 0),
                float(transaction.alimentation or 0),
                transaction.designation,
            )
        calculate_filtred_balance(self, transactions)

    except SQLAlchemyError as err:
        print(f"[DB] Error loading daily transactions: {err}")

def setup_funcs(self):
    fill_tpe_agence_combo(self)

    # load daily transactions when account is selected
    self.ComboBox_TPEagence.currentIndexChanged.connect(lambda: load_tpe_transactions(self))
    self.Input_TpeDate.dateChanged.connect(lambda: filter_by_date(self))
    self.Button_FilterbyTotalDays.clicked.connect(lambda: filter_by_month(self))
    self.Button_Settings.clicked.connect(lambda: open_cost_settings(self))
    self.Button_Reset.clicked.connect(lambda: load_tpe_transactions(self))
    self.Button_CloseWindow.clicked.connect(lambda: self.close())