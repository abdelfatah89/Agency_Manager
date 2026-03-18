import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy import text, select
from sqlalchemy.exc import IntegrityError

from .db_services.db_config import SessionLocal
from .db_services.db_config import with_session
from .db_services.sql_migration_runner import run_sql_migrations
from .db_services.db_tables import Invoice


logger = logging.getLogger(__name__)

_SOURCE_DAILY_ENTRY = "daily_entry"
_SOURCE_FACTURES = "factures"
_SCHEMA_READY = False


@dataclass(frozen=True)
class InvoiceReservation:
    id: int
    invoice_number: str
    source_type: str
    reused: bool


def _as_date(value: Any) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if hasattr(value, "toPyDate"):
        return value.toPyDate()
    return None


def _as_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value or 0))
    except Exception:
        return Decimal("0")


def _normalize_payload(payload: Dict[str, Any]) -> str:
    # Canonical JSON for deterministic idempotency hashing.
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _compute_idempotency_key(source_type: str, payload: Dict[str, Any]) -> str:
    raw = f"{source_type}|{_normalize_payload(payload)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _period_key(issue_date: date) -> str:
    return issue_date.strftime("%Y%m")


def _build_invoice_number(period_key: str, sequence: int) -> str:
    return f"FA-{period_key}-{sequence:06d}"


def ensure_invoice_schema(session) -> None:
    global _SCHEMA_READY
    if _SCHEMA_READY:
        return

    invoices_exists = session.execute(text("SHOW TABLES LIKE 'invoices'"))
    counters_exists = session.execute(text("SHOW TABLES LIKE 'invoice_number_counters'"))
    if invoices_exists.scalar_one_or_none() is None or counters_exists.scalar_one_or_none() is None:
        raise RuntimeError(
            "Invoice schema is missing. Run SQL migrations via installer or scripts/run_sql_migrations.py"
        )

    _SCHEMA_READY = True


def _next_sequence_value(session, period_key: str) -> int:
    # Atomic counter allocation in MySQL; safe under concurrency.
    session.execute(
        text(
            """
            INSERT INTO invoice_number_counters (period_key, sequence_value)
            VALUES (:period_key, 1)
            ON DUPLICATE KEY UPDATE sequence_value = LAST_INSERT_ID(sequence_value + 1)
            """
        ),
        {"period_key": period_key},
    )
    seq = session.execute(text("SELECT LAST_INSERT_ID()"))
    return int(seq.scalar_one())


@with_session
def reserve_invoice_number(
    source_type: str,
    payload: Dict[str, Any],
    issue_date: date,
    *,
    client_name: Optional[str] = None,
    account_name: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    session=None,
) -> InvoiceReservation:
    if source_type not in {_SOURCE_DAILY_ENTRY, _SOURCE_FACTURES}:
        raise ValueError(f"Unsupported source_type: {source_type}")

    canonical_issue_date = _as_date(issue_date)
    if canonical_issue_date is None:
        raise ValueError("issue_date is required")

    ensure_invoice_schema(session)

    payload_text = _normalize_payload(payload)
    idempotency_key = _compute_idempotency_key(source_type, payload)

    existing = session.execute(
        select(Invoice).where(
            Invoice.source_type == source_type,
            Invoice.idempotency_key == idempotency_key,
        )
    ).scalar_one_or_none()

    if existing:
        return InvoiceReservation(
            id=existing.id,
            invoice_number=existing.invoice_number,
            source_type=existing.source_type,
            reused=True,
        )

    period = _period_key(canonical_issue_date)
    sequence = _next_sequence_value(session, period)
    number = _build_invoice_number(period, sequence)

    invoice = Invoice(
        invoice_number=number,
        source_type=source_type,
        idempotency_key=idempotency_key,
        issue_date=canonical_issue_date,
        period_key=period,
        sequence_value=sequence,
        client_name=(client_name or "").strip() or None,
        account_name=(account_name or "").strip() or None,
        date_from=_as_date(date_from),
        date_to=_as_date(date_to),
        total_amount=_as_decimal(payload.get("total_amount")),
        total_paid=_as_decimal(payload.get("total_paid")),
        total_vat=_as_decimal(payload.get("total_vat")),
        balance=_as_decimal(payload.get("balance")),
        status="reserved",
        payload_json=payload_text,
    )

    try:
        session.add(invoice)
        session.flush()
    except IntegrityError:
        # Concurrency race: another transaction inserted same source/idempotency first.
        session.rollback()
        ensure_invoice_schema(session)
        existing = session.execute(
            select(Invoice).where(
                Invoice.source_type == source_type,
                Invoice.idempotency_key == idempotency_key,
            )
        ).scalar_one_or_none()
        if existing:
            return InvoiceReservation(
                id=existing.id,
                invoice_number=existing.invoice_number,
                source_type=existing.source_type,
                reused=True,
            )
        raise

    return InvoiceReservation(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        source_type=invoice.source_type,
        reused=False,
    )


@with_session
def mark_invoice_generated(invoice_id: int, pdf_path: str, session=None) -> None:
    ensure_invoice_schema(session)
    invoice = session.get(Invoice, int(invoice_id))
    if invoice is None:
        raise ValueError(f"Invoice id={invoice_id} not found")
    invoice.status = "generated"
    invoice.pdf_path = pdf_path
    invoice.error_message = None


@with_session
def mark_invoice_failed(invoice_id: int, error_message: str, session=None) -> None:
    ensure_invoice_schema(session)
    invoice = session.get(Invoice, int(invoice_id))
    if invoice is None:
        raise ValueError(f"Invoice id={invoice_id} not found")
    invoice.status = "failed"
    invoice.error_message = (error_message or "").strip()[:2000]


def ensure_invoice_schema_ready() -> None:
    """Public entry point to initialize SQL migrations needed by invoice subsystem."""
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = int(os.getenv("DB_PORT") or 3306)
    db_name = os.getenv("DB_NAME")
    if not all([db_user, db_host, db_name]):
        raise RuntimeError("Missing DB env vars for SQL migration bootstrap")

    database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    run_sql_migrations(database_url=database_url, applied_by="invoice_service")
