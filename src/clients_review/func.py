from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem
from sqlalchemy.exc import SQLAlchemyError

from services import with_session, Client, Transaction, select


def add_transaction_row(self, name, total, total_paid, rest):
    table = self.Table_clients
    table.blockSignals(True)
    row = table.rowCount()
    table.insertRow(row)

    def cell(text, align=Qt.AlignCenter | Qt.AlignVCenter):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(align)
        return item

    table.setItem(row, 0, cell(name, Qt.AlignCenter | Qt.AlignVCenter))
    table.setItem(row, 1, cell(f"{total:,.2f}", Qt.AlignCenter | Qt.AlignVCenter))
    table.setItem(row, 2, cell(f"{total_paid:,.2f}", Qt.AlignCenter | Qt.AlignVCenter))
    table.setItem(row, 3, cell(f"{rest:,.2f}", Qt.AlignCenter | Qt.AlignVCenter))

    table.blockSignals(False)


def calculate_total_rest(self, session=None):
    try:
        clients = session.execute(select(Client)).scalars().all()
        total_rest = sum(float(client.rest or 0) for client in clients)
        self.Label_TotalBalanceValue.setText(f"{total_rest:,.2f}")
    except SQLAlchemyError as err:
        print(f"[DB] Error calculating balance: {err}")


@with_session
def calculate_and_load_balance(self, session=None):
    try:
        self.Table_clients.setRowCount(0)
        clients = session.execute(select(Client)).scalars().all()

        for client in clients:
            tx_rows = session.execute(
                select(Transaction).where(Transaction.client_name == client.full_name)
            ).scalars().all()

            total = sum(float(tx.amount or 0) for tx in tx_rows)
            total_paid = sum(float(tx.paid_amount or 0) for tx in tx_rows)
            rest = total - total_paid

            client.total = total
            client.total_paid = total_paid
            client.rest = rest

            add_transaction_row(self, client.full_name, total, total_paid, rest)

        calculate_total_rest(self, session)
    except SQLAlchemyError as err:
        print(f"[DB] Error calculating balance: {err}")


@with_session
def filter_by_date(self, session=None):
    try:
        self.Table_clients.setRowCount(0)

        clients = session.execute(select(Client)).scalars().all()
        total_rest = 0.0

        from_date = self.Input_FromDate.date().toPyDate()
        to_date = self.Input_ToDate.date().toPyDate()

        for client in clients:
            tx_rows = session.execute(
                select(Transaction).where(
                    Transaction.client_name == client.full_name,
                    Transaction.transaction_date.between(from_date, to_date),
                )
            ).scalars().all()

            total = sum(float(tx.amount or 0) for tx in tx_rows)
            total_paid = sum(float(tx.paid_amount or 0) for tx in tx_rows)
            rest = total - total_paid

            add_transaction_row(self, client.full_name, total, total_paid, rest)
            total_rest += rest

        self.Label_TotalBalanceValue.setText(f"{total_rest:,.2f}")
    except SQLAlchemyError as err:
        print(f"[DB] Error loading transactions: {err}")


def setup_funcs(self):
    calculate_and_load_balance(self)
    self.Button_Filter.clicked.connect(lambda: filter_by_date(self))
    self.Button_Reset.clicked.connect(lambda: calculate_and_load_balance(self))
