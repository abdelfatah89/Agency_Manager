import sys
import time
from datetime import date as dt_date, timedelta
from pathlib import Path

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QTableWidgetItem
from sqlalchemy import text, true
from sqlalchemy.exc import IntegrityError, OperationalError

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from services import (
    with_session,
    select,
    desc,
    DailyBalance,
    DailyCash,
    DailyOperationSummary,
    DailySession,
    GeneralBalance,
    Transaction,
    Agency
)
from src.daily_entry.daily_entry import open_transaction_manager
from src.utils import calculate_agency_balances, compute_diff_percent, parse_float
from src.utils.ui_helpers import create_readonly_checkbox_cell, apply_numeric_input_restrictions
from services.access_control import ROLE_ADMIN

def get_agencies(self, session=None):
    rows = session.execute(select(Agency).order_by(Agency.id)).scalars().all()
    return [row.agency_name for row in rows if bool(row.is_active)]

def _ensure_local_agency_column(session):
    """Ensure daily_balance has local agency column, preserving existing typo-based schema."""
    try:
        session.execute(
            text(
                "ALTER TABLE daily_balance "
                "ADD COLUMN IF NOT EXISTS local_agency_balane DECIMAL(14,2) NOT NULL DEFAULT 0.00"
            )
        )
        session.commit()
    except Exception:
        # Best effort only; app should continue with existing schema.
        session.rollback()


def _get_or_create_session_by_date(session, target_date):
    row = session.execute(select(DailySession).where(DailySession.session_date == target_date)).scalar_one_or_none()
    if row:
        return row

    # If the table is empty, force first created row to start with ID = 1.
    has_any_row = session.execute(select(DailySession.id).limit(1)).scalar_one_or_none()
    if has_any_row is None:
        try:
            session.execute(text("ALTER TABLE daily_sessions AUTO_INCREMENT = 1"))
        except Exception:
            # Non-fatal: if DB user lacks privilege, insertion will still proceed.
            pass

    for attempt in range(3):
        existing = session.execute(
            select(DailySession).where(DailySession.session_date == target_date)
        ).scalar_one_or_none()
        if existing:
            return existing

        try:
            new_row = DailySession(session_date=target_date, status="open")
            session.add(new_row)
            session.flush()
            return new_row
        except (OperationalError, IntegrityError) as exc:
            session.rollback()

            existing = session.execute(
                select(DailySession).where(DailySession.session_date == target_date)
            ).scalar_one_or_none()
            if existing:
                return existing

            db_code = None
            if getattr(exc, "orig", None) is not None and getattr(exc.orig, "args", None):
                db_code = exc.orig.args[0]

            # 1205: lock wait timeout, 1213: deadlock. Retry briefly.
            if db_code in (1205, 1213) and attempt < 2:
                time.sleep(0.15 * (attempt + 1))
                continue

            # 1062 duplicate key (another request inserted same session date).
            if db_code == 1062:
                existing = session.execute(
                    select(DailySession).where(DailySession.session_date == target_date)
                ).scalar_one_or_none()
                if existing:
                    return existing

            raise


def _session_by_id(session, daily_id):
    if not daily_id:
        return None
    return session.get(DailySession, int(daily_id))


def _get_all_session_ids(session):
    ids = session.execute(select(DailySession.id).order_by(DailySession.id)).scalars().all()
    return [int(i) for i in ids]


def _set_current_session(self, daily_session):
    self.counterLabel.setText(str(daily_session.id))
    sd = daily_session.session_date
    # Avoid triggering dateChanged while we are programmatically navigating sessions.
    self.day_date.blockSignals(True)
    try:
        self.day_date.setDate(QDate(sd.year, sd.month, sd.day))
    finally:
        self.day_date.blockSignals(False)


def _set_date_without_signal(self, target_date):
    self.day_date.blockSignals(True)
    try:
        self.day_date.setDate(QDate(target_date.year, target_date.month, target_date.day))
    finally:
        self.day_date.blockSignals(False)


def _load_virtual_session_data(self, session, target_date):
    # Virtual page: show next date without creating/saving DB rows yet.
    self.counterLabel.setText("")
    _set_date_without_signal(self, target_date)

    virtual_daily_id = -1
    load_caisse_data(self, virtual_daily_id, session)
    load_operations_data(self, virtual_daily_id, session)
    load_balance_data(self, virtual_daily_id, session)
    load_general_balance_data(self, virtual_daily_id, session)
    load_transactions_table(self, virtual_daily_id, session)

    if hasattr(self, "otherTransactionVal"):
        self.otherTransactionVal.setText("0.00")
    if hasattr(self, "genTotalDiffVal"):
        self.genTotalDiffVal.setText("0.00")
    if hasattr(self, "genDiffPercent"):
        self.genDiffPercent.setText("0.00%")
    elif hasattr(self, "genBadge"):
        self.genBadge.setText("0.00%")


def _resolve_current_session(session, self):
    daily_id = int(self.counterLabel.text()) if self.counterLabel.text().isdigit() else 0
    row = _session_by_id(session, daily_id)
    if row:
        return row
    return _get_or_create_session_by_date(session, self.day_date.date().toPyDate())


def _save_current_page_before_navigation(self, session):
    """Persist edits before changing pages, but only for real persisted sessions."""
    daily_id = int(self.counterLabel.text()) if self.counterLabel.text().isdigit() else 0
    current_row = _session_by_id(session, daily_id) if daily_id else None
    if not current_row:
        # If a virtual page was already created/saved, recover its real session by date.
        selected_date = self.day_date.date().toPyDate()
        current_row = session.execute(
            select(DailySession).where(DailySession.session_date == selected_date)
        ).scalar_one_or_none()

    if not current_row:
        return

    # Keep navigation state consistent after saving a page that started as virtual.
    self.counterLabel.setText(str(current_row.id))

    _persist_all_in_session(self, session)


def _is_manager_role(self):
    return getattr(self, "_current_user_role", "") == ROLE_ADMIN


def _get_opening_balance(session, selected_date, manager_mode=False):
    """Opening balance is derived from previous day's persisted data."""
    prev_session = session.execute(
        select(DailySession)
        .where(DailySession.session_date < selected_date)
        .order_by(desc(DailySession.session_date))
        .limit(1)
    ).scalar_one_or_none()

    if not prev_session:
        return 0.0

    prev_balance = session.execute(select(DailyBalance).where(DailyBalance.daily_id == prev_session.id)).scalar_one_or_none()
    prev_cash = session.execute(select(DailyCash).where(DailyCash.daily_id == prev_session.id)).scalar_one_or_none()

    if manager_mode and prev_cash and prev_cash.total_cash is not None:
        return parse_float(prev_cash.total_cash)

    if prev_balance and prev_balance.closing_balance is not None:
        return parse_float(prev_balance.closing_balance)

    if prev_cash and prev_cash.total_cash is not None:
        return parse_float(prev_cash.total_cash)

    return 0.0


def _load_current_session_data(self, session, daily_session):
    _set_current_session(self, daily_session)
    load_caisse_data(self, daily_session.id, session)
    load_operations_data(self, daily_session.id, session)
    load_balance_data(self, daily_session.id, session)
    load_general_balance_data(self, daily_session.id, session)
    load_transactions_table(self, daily_session.id, session)
    _calculate_all_in_session(self, session)


def _add_transactions_row(self, transaction, row_index):
    """Backward-compatible wrapper for legacy call sites."""
    add_transaction_row(self, transaction, row_index=row_index, insert_row=True)


def add_transaction_row(self, transaction, row_index=None, insert_row=False):
    table = self.transactionsTable

    if row_index is None:
        row_index = table.rowCount()

    if insert_row:
        table.insertRow(row_index)
    elif row_index >= table.rowCount():
        table.setRowCount(row_index + 1)

    tx_date = transaction.transaction_date.strftime("%d/%m/%Y") if transaction.transaction_date else ""
    account_name = transaction.account_name or ""
    client_name = transaction.client_name or ""
    amount = parse_float(transaction.amount)
    paid_amount = parse_float(transaction.paid_amount)
    balance_due = parse_float(transaction.balance_due)

    values = [
        tx_date,
        str(row_index + 1),
        account_name,
        client_name,
        f"{amount:,.2f}",
        f"{paid_amount:,.2f}",
        f"{balance_due:,.2f}",
    ]

    for col, text in enumerate(values):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        table.setItem(row_index, col, item)

    # Month column was removed from the UI, so OUT/IN are now columns 7 and 8.
    table.setCellWidget(row_index, 7, create_readonly_checkbox_cell(transaction.today_out))
    table.setCellWidget(row_index, 8, create_readonly_checkbox_cell(transaction.today_in))


@with_session
def get_date(self, session=None):
    row = _resolve_current_session(session, self)
    _set_current_session(self, row)


@with_session
def to_nextPage(self, session=None):
    _save_current_page_before_navigation(self, session)
    current_row = _session_by_id(session, int(self.counterLabel.text())) if self.counterLabel.text().isdigit() else None
    if not current_row:
        selected_date = self.day_date.date().toPyDate()
        current_row = session.execute(
            select(DailySession).where(DailySession.session_date == selected_date)
        ).scalar_one_or_none()
        if current_row:
            self.counterLabel.setText(str(current_row.id))

    ids = _get_all_session_ids(session)

    if current_row:
        if current_row.id not in ids:
            ids.append(current_row.id)
            ids.sort()

        idx = ids.index(current_row.id)
        has_next_existing = idx < len(ids) - 1

        if has_next_existing:
            next_row = _session_by_id(session, ids[idx + 1])
            if next_row:
                _load_current_session_data(self, session, next_row)
            return

        # At last real session: move to virtual tomorrow page without DB insert.
        _load_virtual_session_data(self, session, current_row.session_date + timedelta(days=1))
        return

    ## Already on a virtual page: keep moving forward virtually.
    virtual_date = self.day_date.date().toPyDate() + timedelta(days=1)
    _load_virtual_session_data(self, session, virtual_date)


@with_session
def to_previousPage(self, session=None):
    _save_current_page_before_navigation(self, session)
    ids = _get_all_session_ids(session)
    if not ids:
        return

    current_id = int(self.counterLabel.text()) if self.counterLabel.text().isdigit() else None
    if current_id is None:
        prev_id = ids[-1]
    elif current_id not in ids:
        prev_id = ids[0]
    else:
        idx = ids.index(current_id)
        prev_id = ids[max(idx - 1, 0)]

    row = _session_by_id(session, prev_id)
    if row:
        _load_current_session_data(self, session, row)


@with_session
def to_firstPage(self, session=None):
    _save_current_page_before_navigation(self, session)
    ids = _get_all_session_ids(session)
    if not ids:
        return

    row = _session_by_id(session, ids[0])
    if row:
        _load_current_session_data(self, session, row)


@with_session
def to_lastPage(self, session=None):
    _save_current_page_before_navigation(self, session)
    last = session.execute(select(DailySession).order_by(desc(DailySession.id)).limit(1)).scalar_one_or_none()
    if not last:
        last = _get_or_create_session_by_date(session, self.day_date.date().toPyDate())

    _load_current_session_data(self, session, last)


@with_session
def get_daily_id(self, session=None):
    last = session.execute(
        select(DailySession)
        .order_by(desc(DailySession.id), desc(DailySession.session_date))
        .limit(1)
    ).scalar_one_or_none()
    if not last:
        last = _get_or_create_session_by_date(session, dt_date.today())

    _load_current_session_data(self, session, last)


def load_caisse_data(self, daily_id, session=None):
    cashbox_widgets = [
        self.le_cb10000,
        self.le_cb200,
        self.le_cb100,
        self.le_cb50,
        self.le_cb20,
        self.le_cb10,
        self.le_cb5,
        self.le_cb1,
    ]

    record = session.execute(select(DailyCash).where(DailyCash.daily_id == daily_id)).scalar_one_or_none()
    if record:
        values = [
            record.cash_10000,
            record.cash_200,
            record.cash_100,
            record.cash_50,
            record.cash_20,
            record.cash_10,
            record.cash_5,
            record.cash_1,
        ]
        for i, value in enumerate(values):
            cashbox_widgets[i].setText(f"{parse_float(value):,.2f}")
        self.cbTotalVal.setText(f"{parse_float(record.total_cash):,.2f}")
        return

    for widget in cashbox_widgets:
        widget.setText("")
    self.cbTotalVal.setText("0.00")


def load_operations_data(self, daily_id, session=None):
    widgets = [
        self.le_cpNatTransIn,
        self.le_cpIntTransIn,
        self.le_cpNatTransOut,
        self.le_cpIntTransOut,
        self.le_cpClientIn,
        self.le_cpClientOut,
        self.le_cpInvoices,
        self.le_cpMarchant,
        self.le_cpVehicleTax,
        self.le_cpDetailant,
        self.le_cpPhoneTopup,
        self.lbl_totalval,
        self.cpRemaining1Val,
    ]

    record = session.execute(
        select(DailyOperationSummary).where(DailyOperationSummary.daily_id == daily_id)
    ).scalar_one_or_none()

    if record:
        values = [
            record.input_transactions,
            record.input_transaction_outin,
            record.output_transactions,
            record.output_transaction_outin,
            record.input_transactions_account,
            record.output_transactions_account,
            record.total_bills,
            record.cp_merchant,
            record.vignette,
            record.retailer,
            record.phone_recharge,
            record.total_result,
            record.rest_amount,
        ]
        for i, value in enumerate(values):
            widgets[i].setText(f"{parse_float(value):.2f}")
        return

    # Keep input fields empty for easier typing on new sessions.
    for widget in widgets[:11]:
        widget.setText("")

    # Computed/output fields remain explicit.
    for widget in widgets[11:]:
        widget.setText("0.00")


def load_balance_data(self, daily_id, session=None):
    bal = session.execute(select(DailyBalance).where(DailyBalance.daily_id == daily_id)).scalar_one_or_none()
    op = session.execute(
        select(DailyOperationSummary).where(DailyOperationSummary.daily_id == daily_id)
    ).scalar_one_or_none()

    if bal:
        self.cpBalanceFirstBadge.setText(f"{parse_float(bal.opening_balance):.2f}")
        # Canonical semantics: IN=receipts, OUT=payments.
        self.cpTotalInVal.setText(f"{parse_float(bal.total_input):.2f}")
        self.cpTotalOutVal.setText(f"{parse_float(bal.total_output):.2f}")

        cmi_tam = parse_float(op.cmi_tamezmoute if op else 0)
        self.le_cbCmiTam.setText(f"{cmi_tam:.2f}")

        self.cpLastDayVal.setText(f"{parse_float(bal.closing_balance):.2f}")
        self.cbCmiBankBadge.setText(f"{cmi_tam - cmi_tam * 0.01:.2f}" if cmi_tam > 0 else "0.00")
        mizan_value = parse_float(bal.closing_balance) - parse_float(self.cbTotalVal.text())
        self.cbMizanVal.setText(f"{mizan_value:,.2f}")
        _apply_mizan_negative_style(self, mizan_value)
        if hasattr(self, "le_LocalAgency"):
            self.le_LocalAgency.setText(f"{parse_float(bal.local_agency_balance):.2f}")
        return

    self.cpBalanceFirstBadge.setText("0.00")
    self.cpTotalInVal.setText("0.00")
    self.cpTotalOutVal.setText("0.00")
    self.le_cbCmiTam.setText("")
    self.cpLastDayVal.setText("0.00")
    self.cbCmiBankBadge.setText("0.00")
    self.cbMizanVal.setText("0.00")
    _apply_mizan_negative_style(self, 0.0)
    if hasattr(self, "le_LocalAgency"):
        self.le_LocalAgency.setText("")


def load_general_balance_data(self, daily_id, session=None):
    row = session.execute(
        select(GeneralBalance).where(GeneralBalance.daily_id == daily_id)
    ).scalar_one_or_none()

    if row:
        self.genCashPlusVal.setText(f"{parse_float(row.cashplus_balance):.2f}")
        self.genBankVal.setText(f"{parse_float(row.bank_balance):.2f}")
        self.genFirstBalVal.setText(f"{parse_float(row.opening_balance):,.2f}")
        self.genBranchVal.setText(f"{parse_float(row.agencies_balance):,.2f}")
        self.genFinalBalVal.setText(f"{parse_float(row.closing_balance):,.2f}")
        self.genTotalDiffVal.setText(f"{parse_float(row.balance_variance):,.2f}")
        cmi_tam = parse_float(row.cmi_tamezmoute)
        cmi_bank_badge = cmi_tam - (cmi_tam * 0.02) if cmi_tam > 0 else 0.0
        self.genCmiTpeVal.setText(f"{cmi_bank_badge:,.2f}")
        if hasattr(self, "genDiffPercent"):
            diff_percent = compute_diff_percent(parse_float(row.opening_balance), parse_float(row.closing_balance))
            self.genDiffPercent.setText(f"{diff_percent:,.2f}%")
        return

    # New/virtual page: start editable fields at zero so old page values are not reused.
    self.genCashPlusVal.setText("0.00")
    self.genBankVal.setText("0.00")
    self.genFirstBalVal.setText("0.00")
    self.genCmiTpeVal.setText("0.00")
    self.genBranchVal.setText("0.00")
    self.genFinalBalVal.setText("0.00")
    self.genTotalDiffVal.setText("0.00")
    if hasattr(self, "genDiffPercent"):
        self.genDiffPercent.setText("0.00%")


def load_transactions_table(self, daily_id, session=None):
    table = self.transactionsTable
    table.setRowCount(0)

    if session is None:
        return

    rows = session.execute(
        select(Transaction)
        .where(
            Transaction.daily_id == daily_id,
            (Transaction.today_in.is_(True)) | (Transaction.today_out.is_(True)),
        )
        .order_by(Transaction.id)
    ).scalars().all()

    table.setSortingEnabled(False)
    table.setRowCount(len(rows))

    try:
        for row_idx, transaction in enumerate(rows):
            add_transaction_row(self, transaction, row_index=row_idx)
    finally:
        table.setSortingEnabled(True)


@with_session
def load_data(self, session=None):
    row = _resolve_current_session(session, self)
    _load_current_session_data(self, session, row)


@with_session
def search_using_date(self, session=None):
    current_date = self.day_date.date().toPyDate()
    row = session.execute(select(DailySession).where(DailySession.session_date == current_date)).scalar_one_or_none()
    if not row:
        row = _get_or_create_session_by_date(session, current_date)

    _load_current_session_data(self, session, row)


def get_value(widget):
    return parse_float(widget.text() if hasattr(widget, "text") else widget)


def _apply_mizan_negative_style(self, mizan_value):
    is_negative = parse_float(mizan_value) < 0
    self.cbMizanVal.setProperty("negative", is_negative)
    self.cbMizanVal.style().unpolish(self.cbMizanVal)
    self.cbMizanVal.style().polish(self.cbMizanVal)
    self.cbMizanVal.update()


def calculate_operations(self, session=None):
    selected_date = self.day_date.date().toPyDate()
    daily_session = _get_or_create_session_by_date(session, selected_date)
    daily_id = daily_session.id

    values = [
        get_value(self.le_cpNatTransIn),
        get_value(self.le_cpIntTransIn),
        get_value(self.le_cpNatTransOut),
        get_value(self.le_cpIntTransOut),
        get_value(self.le_cpClientIn),
        get_value(self.le_cpClientOut),
        get_value(self.le_cpInvoices),
        get_value(self.le_cpMarchant),
        get_value(self.le_cpVehicleTax),
        get_value(self.le_cpDetailant),
        get_value(self.le_cpPhoneTopup),
        get_value(self.le_cbCmiTam),
    ]
    local_agency = get_value(self.le_LocalAgency) if hasattr(self, "le_LocalAgency") else 0.0

    total_in = values[0] + values[1] + values[4]
    total_out = values[2] + values[3] + values[5]
    expenses = values[6] + values[7] + values[8] + values[9] + (values[10] * 0.98)  # CMI has 2% fee

    total_result = total_in - total_out + expenses - local_agency
    opening = _get_opening_balance(session, selected_date, manager_mode=_is_manager_role(self))
    self.cpBalanceFirstBadge.setText(f"{opening:,.2f}")
    rest_amount = opening + total_result

    self.lbl_totalval.setText(f"{total_result:.2f}")
    self.cpRemaining1Val.setText(f"{rest_amount:.2f}")

    row = session.execute(
        select(DailyOperationSummary).where(DailyOperationSummary.daily_id == daily_id)
    ).scalar_one_or_none()

    payload = {
        "input_transactions": float(values[0]),
        "input_transaction_outin": float(values[1]),
        "output_transactions": float(values[2]),
        "output_transaction_outin": float(values[3]),
        "input_transactions_account": float(values[4]),
        "output_transactions_account": float(values[5]),
        "total_bills": float(values[6]),
        "cp_merchant": float(values[7]),
        "vignette": float(values[8]),
        "retailer": float(values[9]),
        "phone_recharge": float(values[10]),
        "cmi_tamezmoute": float(values[11]),
        "total_result": float(total_result),
        "rest_amount": float(rest_amount),
    }

    if not row:
        row = DailyOperationSummary(daily_id=daily_id, **payload)
        session.add(row)
    else:
        for key, value in payload.items():
            setattr(row, key, value)



def calculate_caisse(self, session=None):
    selected_date = self.day_date.date().toPyDate()
    daily_session = _get_or_create_session_by_date(session, selected_date)
    daily_id = daily_session.id

    cash_values = [
        get_value(self.le_cb10000),
        get_value(self.le_cb200),
        get_value(self.le_cb100),
        get_value(self.le_cb50),
        get_value(self.le_cb20),
        get_value(self.le_cb10),
        get_value(self.le_cb5),
        get_value(self.le_cb1),
    ]
    denominations = [10000, 200, 100, 50, 20, 10, 5, 1]
    total_cash = float(sum(v * d for v, d in zip(cash_values, denominations)))

    row = session.execute(select(DailyCash).where(DailyCash.daily_id == daily_id)).scalar_one_or_none()
    payload = {
        "cash_10000": float(cash_values[0]),
        "cash_200": float(cash_values[1]),
        "cash_100": float(cash_values[2]),
        "cash_50": float(cash_values[3]),
        "cash_20": float(cash_values[4]),
        "cash_10": float(cash_values[5]),
        "cash_5": float(cash_values[6]),
        "cash_1": float(cash_values[7]),
        "total_cash": float(total_cash),
    }

    if not row:
        row = DailyCash(daily_id=daily_id, **payload)
        session.add(row)
    else:
        for key, value in payload.items():
            setattr(row, key, value)

    self.cbTotalVal.setText(f"{total_cash:.2f}")



def calculate_balance(self, session=None):
    selected_date = self.day_date.date().toPyDate()
    daily_session = _get_or_create_session_by_date(session, selected_date)
    daily_id = daily_session.id

    opening_balance = _get_opening_balance(session, selected_date, manager_mode=_is_manager_role(self))

    # CMI amount and operations total from DailyOperationSummary
    self.cpBalanceFirstBadge.setText(f"{opening_balance:,.2f}")
    op_summary = session.execute(select(DailyOperationSummary).where(DailyOperationSummary.daily_id == daily_id)).scalar_one_or_none()
    cmi_tam_amount = parse_float(op_summary.cmi_tamezmoute) if op_summary else 0.0
    cmi_bank_net = cmi_tam_amount - (cmi_tam_amount * 0.01) if cmi_tam_amount > 0 else 0.0
    cmi_paid_amount = cmi_tam_amount - (cmi_tam_amount * 0.02) if cmi_tam_amount > 0 else 0.0
    operations_total = parse_float(op_summary.total_result) if op_summary else 0.0

    # Sum transactions marked today_in/today_out directly from Transaction table
    rows = session.execute(
        select(Transaction).where(Transaction.daily_id == daily_id)
    ).scalars().all()
    def effective_value(tx):
        amt, paid = parse_float(tx.amount), parse_float(tx.paid_amount)
        return paid + amt

    total_in = sum(effective_value(tx) for tx in rows if tx.today_in)
    total_out = sum(effective_value(tx) for tx in rows if tx.today_out)

    # Canonical formula: closing = opening + operations + total_in - total_out - cmi
    closing = opening_balance + operations_total + total_in - total_out - cmi_paid_amount

    self.cpTotalInVal.setText(f"{total_in:,.2f}")
    self.cpTotalOutVal.setText(f"{total_out:,.2f}")
    self.cbCmiBankBadge.setText(f"{cmi_bank_net:,.2f}" if cmi_tam_amount > 0 else "0.00")

    self.cpLastDayVal.setText(f"{closing:,.2f}")
    cash_row = session.execute(select(DailyCash).where(DailyCash.daily_id == daily_id)).scalar_one_or_none()
    current_cash_total = parse_float(cash_row.total_cash) if cash_row else 0.0
    mizan = current_cash_total - closing
    self.cbMizanVal.setText(f"{mizan:,.2f}")
    _apply_mizan_negative_style(self, mizan)

    local_agency = get_value(self.le_LocalAgency) if hasattr(self, "le_LocalAgency") else 0.0
    row = session.execute(select(DailyBalance).where(DailyBalance.daily_id == daily_id)).scalar_one_or_none()
    payload = {
        "opening_balance": float(opening_balance),
        "total_output": float(total_out),
        "total_input": float(total_in),
        "local_agency_balance": float(local_agency),
        "closing_balance": float(closing),
    }

    if not row:
        row = DailyBalance(daily_id=daily_id, **payload)
        session.add(row)
    else:
        for key, value in payload.items():
            setattr(row, key, value)



def calculate_trans_in_out(self, session=None):
    selected_date = self.day_date.date().toPyDate()
    daily_session = _get_or_create_session_by_date(session, selected_date)
    agencies = get_agencies(self, session)

    name_filter = ~Transaction.account_name.in_(agencies) if agencies else true()
    rows = session.execute(
        select(Transaction).where((Transaction.daily_id == daily_session.id) & name_filter)
    ).scalars().all()

    def effective_value(tx):
        amount = parse_float(tx.amount)
        paid = parse_float(tx.paid_amount)
        # For movement rows, paid_amount is often the real cash flow value.
        return paid + amount

    total_in = sum(effective_value(t) for t in rows if bool(t.today_in))
    total_out = sum(effective_value(t) for t in rows if bool(t.today_out))
    net_other_transactions = total_in - total_out

    # Canonical semantics: IN=receipts, OUT=payments.
    self.cpTotalInVal.setText(f"{total_in:,.2f}")
    self.cpTotalOutVal.setText(f"{total_out:,.2f}")

    if hasattr(self, "otherTransactionVal"):
        self.otherTransactionVal.setText(f"{net_other_transactions:,.2f}")

def get_daily_branches_balance(self, session=None, target_date=None):
    calculate_agency_balances(session)
    selected_date = target_date or self.day_date.date().toPyDate()
    agency_transactions = session.execute(
        select(Transaction)
        .where(
            Transaction.transaction_date == selected_date,
            Transaction.account_name.in_(get_agencies(self, session)),
        )
    ).scalars().all()

    # Re-read from agencies to ensure accuracy regardless of general balance rows.
    aliementation = sum(parse_float(t.paid_amount) for t in agency_transactions)
    decaissement = sum(parse_float(t.amount) for t in agency_transactions)
    total = aliementation - decaissement
    self.genBranchVal.setText(f"{total:,.2f}")
    return total

def get_branches_balance(self, session=None):
    calculate_agency_balances(session)
    # Re-read from agencies to ensure accuracy regardless of general balance rows.
    from services import Agency

    agencies = session.execute(select(Agency)).scalars().all()
    total = sum(parse_float(a.balance) for a in agencies)
    self.genBranchVal.setText(f"{total:,.2f}")
    return total



def calculate_genBalance(self, session=None):
    daily_id = int(self.counterLabel.text()) if self.counterLabel.text().isdigit() else 0
    if not daily_id:
        return

    current_session = _session_by_id(session, daily_id)
    if not current_session:
        return

    current_gen = session.execute(
        select(GeneralBalance).where(GeneralBalance.daily_id == daily_id)
    ).scalar_one_or_none()

    prev_gen = session.execute(
        select(GeneralBalance)
        .join(DailySession, DailySession.id == GeneralBalance.daily_id)
        .where(DailySession.session_date < current_session.session_date)
        .order_by(desc(DailySession.session_date))
        .limit(1)
    ).scalar_one_or_none()

    if prev_gen:
        opening = parse_float(prev_gen.closing_balance)
    elif current_gen and current_gen.opening_balance is not None:
        opening = parse_float(current_gen.opening_balance)
    else:
        opening = _get_opening_balance(
            session,
            current_session.session_date,
            manager_mode=_is_manager_role(self),
        )

    cash_row = session.execute(select(DailyCash).where(DailyCash.daily_id == daily_id)).scalar_one_or_none()
    daily_cash_total = parse_float(cash_row.total_cash) if cash_row else 0.0

    agencies_balance = get_daily_branches_balance(self, session, target_date=current_session.session_date)

    op_row = session.execute(
        select(DailyOperationSummary).where(DailyOperationSummary.daily_id == daily_id)
    ).scalar_one_or_none()
    cmi_tam = parse_float(op_row.cmi_tamezmoute if op_row else 0)
    cmi_fee_rate = 0.01
    cmi_bank_badge = cmi_tam * (1 - cmi_fee_rate) if cmi_tam > 0 else 0.0

    cashplus_balance = get_value(self.genCashPlusVal)
    bank_balance = get_value(self.genBankVal)
    other_transactions = get_value(self.otherTransactionVal) if hasattr(self, "otherTransactionVal") else 0.0
    closing = (
        agencies_balance
        + cashplus_balance
        + bank_balance
        + cmi_bank_badge
        + other_transactions
    )
    variance = closing - opening


    self.genFirstBalVal.setText(f"{opening:,.2f}")
    self.genCmiTpeVal.setText(f"{cmi_bank_badge:,.2f}")
    self.genBranchVal.setText(f"{agencies_balance:,.2f}")
    self.genFinalBalVal.setText(f"{closing:,.2f}")
    self.genTotalDiffVal.setText(f"{variance:,.2f}")

    diff_percent = compute_diff_percent(opening, closing)
    if hasattr(self, "genDiffPercent"):
        self.genDiffPercent.setText(f"{diff_percent:,.2f}%")

    row = current_gen
    if not row:
        row = GeneralBalance(daily_id=daily_id)
        session.add(row)

    payload = {
        "opening_balance": float(opening),
        "agencies_balance": float(agencies_balance),
        "cashplus_balance": float(cashplus_balance),
        "bank_balance": float(bank_balance),
        "cmi_tamezmoute": float(cmi_tam),
        "closing_balance": float(closing),
        "balance_variance": float(variance),
    }

    for key, value in payload.items():
        setattr(row, key, value)


def _persist_all_in_session(self, session):
    calculate_agency_balances(session)
    calculate_trans_in_out(self, session)
    calculate_operations(self, session)
    calculate_caisse(self, session)
    calculate_balance(self, session)
    calculate_genBalance(self, session)
    session.commit()


def _calculate_all_in_session(self, session):
    _persist_all_in_session(self, session)

    row = _resolve_current_session(session, self)
    _set_current_session(self, row)
    load_transactions_table(self, row.id, session)


@with_session
def calculate_all(self, session=None):
    _calculate_all_in_session(self, session)

def setup_funcs(self):
    cashbox_widgets = [
        self.le_cb10000,
        self.le_cb200,
        self.le_cb100,
        self.le_cb50,
        self.le_cb20,
        self.le_cb10,
        self.le_cb5,
        self.le_cb1,
    ]

    cashplus_widgets = [
        self.le_cpNatTransIn,
        self.le_cpIntTransIn,
        self.le_cpNatTransOut,
        self.le_cpIntTransOut,
        self.le_cpClientIn,
        self.le_cpClientOut,
        self.le_cpInvoices,
        self.le_cpMarchant,
        self.le_cpVehicleTax,
        self.le_cpDetailant,
        self.le_cpPhoneTopup,
        self.le_LocalAgency,
        self.le_cbCmiTam,
    ]

    genbalance_widgets = [
        self.genCashPlusVal,
        self.genBankVal,
    ]

    numeric_names = [w.objectName() for w in (cashbox_widgets + cashplus_widgets + genbalance_widgets) if w]
    apply_numeric_input_restrictions(self, force_numeric_names=numeric_names)

    # Editable numeric fields start empty, with a visible numeric hint.
    for widget in (cashbox_widgets + cashplus_widgets):
        if widget:
            widget.setPlaceholderText("0.00")

    # Startup should always point to the latest existing session ID.
    with_session(lambda _self, session=None: _ensure_local_agency_column(session))(self)
    get_daily_id(self)
    calculate_all(self)

    def _connect_recalc(widget):
        try:
            widget.editingFinished.disconnect()
        except Exception:
            pass
        widget.editingFinished.connect(lambda _w=widget: calculate_all(self))

    for le in cashbox_widgets:
        _connect_recalc(le)

    for le in cashplus_widgets:
        _connect_recalc(le)

    for le in genbalance_widgets:
        _connect_recalc(le)

    def _open_transactions_and_recalculate(_checked=False):
        manager_window = open_transaction_manager(current_user_role=getattr(self, "_current_user_role", None), parent=self)
        if manager_window is None:
            calculate_all(self)
            return

        # Keep a reference so the window is not garbage-collected.
        self._transaction_manager_window = manager_window

        # Recalculate after transactions window is closed so labels/DB reflect latest edits.
        def _safe_recalculate_after_close(*_):
            try:
                calculate_all(self)
            except RuntimeError:
                # Daily balance window/widgets may already be destroyed.
                pass

        manager_window.destroyed.connect(_safe_recalculate_after_close)

    try:
        self.cpSubPanelToggleBtn.clicked.disconnect()
    except Exception:
        pass
    self.cpSubPanelToggleBtn.clicked.connect(_open_transactions_and_recalculate)

    if hasattr(self, "Button_refresh"):
        try:
            self.Button_refresh.clicked.disconnect()
        except Exception:
            pass
        self.Button_refresh.clicked.connect(lambda: calculate_all(self))

    self.navNextBtn.clicked.connect(lambda: to_nextPage(self))
    self.navPrevBtn.clicked.connect(lambda: to_previousPage(self))
    self.navFirstBtn.clicked.connect(lambda: to_firstPage(self))
    self.navLastBtn.clicked.connect(lambda: to_lastPage(self))
    self.day_date.dateChanged.connect(lambda _d: search_using_date(self))
