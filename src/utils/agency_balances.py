from services import select, Agency, Transaction, CMITransaction
from .calculations import parse_float


def calculate_agency_balances(session):
    agencies = session.execute(select(Agency)).scalars().all()

    for agency in agencies:
        agency_type = (agency.agency_type or "").lower()

        if agency_type == "tpe":
            tpe_rows = session.execute(
                select(CMITransaction).where(CMITransaction.agency_name == agency.agency_name)
            ).scalars().all()

            total_transactions = sum(parse_float(row.amount) for row in tpe_rows)
            total_alimentation = sum(parse_float(row.alimentation) for row in tpe_rows)
            total_paid_amount = sum(parse_float(row.paid_amount) for row in tpe_rows)
            balance = total_alimentation - total_paid_amount
        else:
            rows = session.execute(
                select(Transaction).where(Transaction.account_name == agency.agency_name)
            ).scalars().all()

            total_transactions = sum(parse_float(row.amount) for row in rows)
            total_alimentation = sum(parse_float(row.paid_amount) for row in rows)
            balance = total_alimentation - total_transactions

        agency.total_cashplus_transaction = float(total_transactions)
        agency.alimentation = float(total_alimentation)
        agency.balance = float(balance)
