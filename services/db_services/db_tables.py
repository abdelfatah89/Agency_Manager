from typing import Optional
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="cashplus_employer")
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    cin: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ice: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_paid: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    rest: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_name: Mapped[str] = mapped_column(String(255), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())


class Agency(Base):
    __tablename__ = "agencies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agency_name: Mapped[str] = mapped_column(String(255), unique=True)
    agency_type: Mapped[str] = mapped_column(String(20), default="other")
    total_cashplus_transaction: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    alimentation: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class DailySession(Base):
    __tablename__ = "daily_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_date: Mapped[Date] = mapped_column(Date, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(10), default="open")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    opened_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    closed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="daily_session")
    daily_cash: Mapped[Optional["DailyCash"]] = relationship(back_populates="daily_session")
    daily_operation_summary: Mapped[Optional["DailyOperationSummary"]] = relationship(back_populates="daily_session")
    daily_balance: Mapped[Optional["DailyBalance"]] = relationship(back_populates="daily_session")
    general_balance: Mapped[Optional["GeneralBalance"]] = relationship(back_populates="daily_session")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    daily_id: Mapped[int] = mapped_column(ForeignKey("daily_sessions.id"), index=True)
    transaction_date: Mapped[Date] = mapped_column(Date, index=True)
    client_name: Mapped[str] = mapped_column(String(255), index=True)
    account_name: Mapped[str] = mapped_column(String(255), index=True)
    designation: Mapped[str] = mapped_column(Text)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    balance_due: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    today_in: Mapped[bool] = mapped_column(default=False)
    today_out: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    daily_session: Mapped[DailySession] = relationship(back_populates="transactions")


class CMITransaction(Base):
    __tablename__ = "cmi_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_date: Mapped[Date] = mapped_column(Date, index=True)
    agency_name: Mapped[str] = mapped_column(String(255), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    commission: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    alimentation: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    designation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())


class DailyCash(Base):
    __tablename__ = "daily_cash"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    daily_id: Mapped[int] = mapped_column(ForeignKey("daily_sessions.id"), unique=True, index=True)
    cash_10000: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    cash_200: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    cash_100: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    cash_50: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    cash_20: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    cash_10: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    cash_5: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    cash_1: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_cash: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    daily_session: Mapped[DailySession] = relationship(back_populates="daily_cash")


class DailyOperationSummary(Base):
    __tablename__ = "daily_operation_summary"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    daily_id: Mapped[int] = mapped_column(ForeignKey("daily_sessions.id"), unique=True, index=True)
    input_transactions: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    input_transaction_outin: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    output_transactions: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    output_transaction_outin: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    input_transactions_account: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    output_transactions_account: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_bills: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    vignette: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    phone_recharge: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    retailer: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    cp_merchant: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    rest_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_result: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    cmi_tamezmoute: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    daily_session: Mapped[DailySession] = relationship(back_populates="daily_operation_summary")


class DailyBalance(Base):
    __tablename__ = "daily_balance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    daily_id: Mapped[int] = mapped_column(ForeignKey("daily_sessions.id"), unique=True, index=True)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_output: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_input: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    # Keep compatibility with existing schema typo: local_agency_balane.
    local_agency_balance: Mapped[Decimal] = mapped_column("local_agency_balane", Numeric(14, 2), default=0)
    closing_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    daily_session: Mapped[DailySession] = relationship(back_populates="daily_balance")


class GeneralBalance(Base):
    __tablename__ = "general_balance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    daily_id: Mapped[int] = mapped_column(ForeignKey("daily_sessions.id"), unique=True, index=True)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    agencies_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    cashplus_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    bank_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    cmi_tamezmoute: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    closing_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    balance_variance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    daily_session: Mapped[DailySession] = relationship(back_populates="general_balance")


class InvoiceNumberCounter(Base):
    __tablename__ = "invoice_number_counters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period_key: Mapped[str] = mapped_column(String(6), unique=True, index=True)
    sequence_value: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint("source_type", "idempotency_key", name="uq_invoice_source_idempotency"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    source_type: Mapped[str] = mapped_column(String(32), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(64), index=True)
    issue_date: Mapped[Date] = mapped_column(Date, index=True)
    period_key: Mapped[str] = mapped_column(String(6), index=True)
    sequence_value: Mapped[int] = mapped_column(Integer)

    client_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    account_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date_from: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    date_to: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)

    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_paid: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_vat: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)

    status: Mapped[str] = mapped_column(String(16), default="reserved")
    pdf_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class SchemaMigration(Base):
    __tablename__ = "schema_migrations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    version: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    script_name: Mapped[str] = mapped_column(String(255))
    checksum_sha256: Mapped[str] = mapped_column(String(64))
    execution_ms: Mapped[int] = mapped_column(Integer, default=0)
    applied_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    applied_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())


class LicensedMachine(Base):
    __tablename__ = "licensed_machines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_name: Mapped[str] = mapped_column(String(255), index=True)
    machine_name: Mapped[str] = mapped_column(String(255), index=True)
    hardware_fingerprint: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    request_code: Mapped[str] = mapped_column(Text)
    license_code: Mapped[str] = mapped_column(Text)
    license_status: Mapped[str] = mapped_column(String(24), index=True, default="active")
    issued_at: Mapped[DateTime] = mapped_column(DateTime)
    expires_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    activated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    last_seen_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class AppInstallation(Base):
    __tablename__ = "app_installations"
    __table_args__ = (
        UniqueConstraint("licensed_machine_id", "install_path", name="uq_installation_machine_path"),
        Index("idx_installation_machine_status_seen", "licensed_machine_id", "status", "last_seen_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    licensed_machine_id: Mapped[int] = mapped_column(ForeignKey("licensed_machines.id", ondelete="CASCADE", onupdate="CASCADE"), index=True)
    app_version: Mapped[str] = mapped_column(String(64))
    install_path: Mapped[str] = mapped_column(String(1024))
    install_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    machine_name: Mapped[str] = mapped_column(String(255))
    first_seen_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    last_seen_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    status: Mapped[str] = mapped_column(String(24), default="active", index=True)
    notes: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)


class LicenseAuditLog(Base):
    __tablename__ = "license_audit_log"
    __table_args__ = (
        Index("idx_audit_machine_time", "licensed_machine_id", "created_at"),
        Index("idx_audit_installation_time", "app_installation_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    licensed_machine_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("licensed_machines.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    app_installation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("app_installations.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    event_result: Mapped[str] = mapped_column(String(24), index=True)
    event_message: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    event_details_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.current_timestamp())
