import logging
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc

from services import with_session, Agency, Account, Transaction, CMITransaction, select
from src.new_tiers.new_tiers import NewTiers
from src.utils import calculate_agency_balances, parse_float


logger = logging.getLogger(__name__)


def _prepare_journal_table(table):
    table.setSortingEnabled(False)
    table.setRowCount(0)


def _finalize_journal_table(table):
    table.setSortingEnabled(True)
    table.horizontalHeader().setSortIndicatorShown(True)
    table.sortItems(0, Qt.DescendingOrder)


def _is_placeholder_selection(selected_text: str) -> bool:
    return selected_text == "-- اختر الحساب/الوكالة --" or "اختر الحساب/الوكالة" in selected_text


def _is_tpe_agency(agency) -> bool:
    return bool(agency) and (agency.agency_type or "").lower() == "tpe"


def get_accounts(self, session=None):
    rows = session.execute(select(Account).order_by(Account.id)).scalars().all()
    return [row.account_name for row in rows if bool(row.is_active)]


def get_agencies(self, session=None):
    rows = session.execute(select(Agency).order_by(Agency.id)).scalars().all()
    return [row.agency_name for row in rows if bool(row.is_active)]


@with_session
def fill_account_agence_combo(self, session=None):
    try:
        accounts = get_accounts(self, session)
        agencies = get_agencies(self, session)

        self.ComboBox_AccAgenceName.clear()
        self.ComboBox_AccAgenceName.addItem("-- اختر الحساب/الوكالة --", None)
        for name in accounts:
            self.ComboBox_AccAgenceName.addItem(name)
        for name in agencies:
            self.ComboBox_AccAgenceName.addItem(name)

        self.ComboBox_AccAgenceName.view().setRowHidden(0, True)
        self.ComboBox_AccAgenceName.setCurrentIndex(0)
        for i in range(self.ComboBox_AccAgenceName.count()):
            self.ComboBox_AccAgenceName.setItemData(i, Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)
    except SQLAlchemyError as err:
        logger.exception("Error loading accounts/agencies")


def add_transaction_row(self, tx_date, costumer, designation, in_amount, out_amount):
    table = self.Table_journal
    table.blockSignals(True)
    row = table.rowCount()
    table.insertRow(row)

    def cell(text, align=Qt.AlignCenter | Qt.AlignVCenter):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(align)
        return item

    table.setItem(row, 0, cell(tx_date, Qt.AlignCenter | Qt.AlignVCenter))
    table.setItem(row, 1, cell(costumer, Qt.AlignCenter | Qt.AlignVCenter))
    table.setItem(row, 2, cell(designation, Qt.AlignCenter | Qt.AlignVCenter))
    table.setItem(row, 3, cell(f"{out_amount:,.2f}", Qt.AlignCenter | Qt.AlignVCenter))
    table.setItem(row, 4, cell(f"{in_amount:,.2f}", Qt.AlignCenter | Qt.AlignVCenter))

    table.blockSignals(False)


def calculate_balance(self, session=None):
    try:
        selected = self.ComboBox_AccAgenceName.currentText()
        if _is_placeholder_selection(selected):
            self.Label_TotalBalanceValue.setText("0.00")
            return

        agency = session.execute(select(Agency).where(Agency.agency_name == selected)).scalar_one_or_none()

        if agency:
            calculate_agency_balances(session)
            session.flush()
            self.Label_TotalBalanceValue.setText(f"{parse_float(agency.balance):,.2f}")
            return

        is_tpe_agency = _is_tpe_agency(agency)
        if is_tpe_agency:
            rows = session.execute(
                select(CMITransaction)
                .where(CMITransaction.agency_name == selected)
                ).scalars().all()
        else:
            rows = session.execute(
                select(Transaction)
                .where(Transaction.account_name == selected)
            ).scalars().all()

        total_amount = sum(parse_float(row.amount if not is_tpe_agency else row.amount_paid) for row in rows)
        total_paid = sum(parse_float(row.paid_amount if not is_tpe_agency else row.alimentation) for row in rows)
        self.Label_TotalBalanceValue.setText(f"{total_amount - total_paid:,.2f}")
    except SQLAlchemyError as err:
        logger.exception("Error calculating account review balance")


@with_session
def load_daily_transactions(self, session=None):
    try:
        selected = self.ComboBox_AccAgenceName.currentText()
        if _is_placeholder_selection(selected):
            _prepare_journal_table(self.Table_journal)
            _finalize_journal_table(self.Table_journal)
            return

        _prepare_journal_table(self.Table_journal)

        agency = session.execute(select(Agency).where(Agency.agency_name == selected)).scalar_one_or_none()
        is_tpe_agency = _is_tpe_agency(agency)

        if is_tpe_agency:
            tpe = select(CMITransaction).where(CMITransaction.agency_name == selected).order_by(desc(CMITransaction.transaction_date), desc(CMITransaction.id))
            rows = session.execute(tpe).scalars().all()
        else:
            rows = session.execute(
                select(Transaction)
                .where(Transaction.account_name == selected)
                .order_by(desc(Transaction.transaction_date), desc(Transaction.id))
            ).scalars().all()

        for row in rows:
            out_column_value = parse_float(row.paid_amount) if is_tpe_agency else parse_float(row.amount)
            add_transaction_row(
                self,
                row.transaction_date,
                row.client_name if not is_tpe_agency else row.customer_name or "",
                row.designation,
                out_column_value,
                parse_float(row.paid_amount if not is_tpe_agency else row.alimentation),
            )

        _finalize_journal_table(self.Table_journal)
        calculate_balance(self, session)
    except SQLAlchemyError as err:
        logger.exception("Error loading account review transactions")


@with_session
def filter_by_date(self, session=None):
    try:
        selected = self.ComboBox_AccAgenceName.currentText()
        if _is_placeholder_selection(selected):
            _prepare_journal_table(self.Table_journal)
            _finalize_journal_table(self.Table_journal)
            return

        _prepare_journal_table(self.Table_journal)

        agency = session.execute(select(Agency).where(Agency.agency_name == selected)).scalar_one_or_none()
        is_tpe_agency = _is_tpe_agency(agency)

        from_date = self.Input_FromDate.date().toPyDate()
        to_date = self.Input_ToDate.date().toPyDate()
        if from_date > to_date:
            from_date, to_date = to_date, from_date

        if is_tpe_agency:
            rows = session.execute(
                select(CMITransaction).where(
                    CMITransaction.agency_name == selected,
                    CMITransaction.transaction_date.between(from_date, to_date),
                )
                .order_by(desc(CMITransaction.transaction_date), desc(CMITransaction.id))
            ).scalars().all()
        else:
            rows = session.execute(
                select(Transaction).where(
                    Transaction.account_name == selected,
                    Transaction.transaction_date.between(from_date, to_date),
                )
                .order_by(desc(Transaction.transaction_date), desc(Transaction.id))
            ).scalars().all()

        for row in rows:
            out_column_value = parse_float(row.paid_amount) if is_tpe_agency else parse_float(row.amount)
            add_transaction_row(
                self,
                row.transaction_date,
                row.client_name if not is_tpe_agency else row.customer_name or "",
                row.designation,
                out_column_value,
                parse_float(row.paid_amount if not is_tpe_agency else row.alimentation),
            )

        _finalize_journal_table(self.Table_journal)
        calculate_balance(self, session)
    except SQLAlchemyError as err:
        logger.exception("Error filtering account review transactions")


def open_new_tiers_dialog(self):
    dialog = NewTiers(self)
    dialog.exec_()
    fill_account_agence_combo(self)

def fill_load(self):
    fill_account_agence_combo(self)
    load_daily_transactions(self)

def setup_funcs(self):
    fill_account_agence_combo(self)
    self.ComboBox_AccAgenceName.currentIndexChanged.connect(lambda: load_daily_transactions(self))
    self.Button_Filter.clicked.connect(lambda: filter_by_date(self))
    self.Button_Reset.clicked.connect(lambda: fill_load(self))
    self.Button_AddAccount.clicked.connect(lambda: open_new_tiers_dialog(self))
