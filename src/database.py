"""Database models and ORM definitions."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    Column,
    Numeric,
    String,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

from src.models import (
    TransactionType,
    TransactionStatus,
    CardType,
    CardStatus,
)

Base = declarative_base()


class User(Base):
    """User database model."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    accounts = relationship("Account", back_populates="holder")
    cards = relationship("Card", back_populates="holder")

    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_is_active", "is_active"),
    )


class Account(Base):
    """Account database model."""

    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    account_number = Column(String(20), unique=True, nullable=False, index=True)
    holder_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_type = Column(String(50), nullable=False)
    balance = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    holder = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
    cards = relationship("Card", back_populates="account")

    __table_args__ = (
        Index("idx_accounts_holder_id", "holder_id"),
        Index("idx_accounts_is_active", "is_active"),
        UniqueConstraint("account_number", name="uq_accounts_account_number"),
    )


class Transaction(Base):
    """Transaction database model."""

    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    balance_after = Column(Numeric(15, 2), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    account = relationship("Account", back_populates="transactions")

    __table_args__ = (
        Index("idx_transactions_account_id", "account_id"),
        Index("idx_transactions_status", "status"),
        Index("idx_transactions_created_at", "created_at"),
        Index("idx_transactions_type", "transaction_type"),
    )


class Transfer(Base):
    """Transfer database model for tracking inter-account transfers."""

    __tablename__ = "transfers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    from_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    to_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    description = Column(Text, nullable=True)
    from_transaction_id = Column(UUID(as_uuid=True), nullable=True)
    to_transaction_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_transfers_from_account_id", "from_account_id"),
        Index("idx_transfers_to_account_id", "to_account_id"),
        Index("idx_transfers_status", "status"),
    )


class Card(Base):
    """Card database model."""

    __tablename__ = "cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    card_number = Column(String(19), unique=True, nullable=False, index=True)
    last_four = Column(String(4), nullable=False)
    card_type = Column(Enum(CardType), nullable=False)
    status = Column(Enum(CardStatus), default=CardStatus.ACTIVE, nullable=False)
    holder_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    expiry_date = Column(String(7), nullable=False)  # MM/YYYY format
    cvv = Column(String(255), nullable=False)  # Encrypted
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    holder = relationship("User", back_populates="cards")
    account = relationship("Account", back_populates="cards")

    __table_args__ = (
        Index("idx_cards_holder_id", "holder_id"),
        Index("idx_cards_account_id", "account_id"),
        Index("idx_cards_status", "status"),
        UniqueConstraint("card_number", name="uq_cards_card_number"),
    )


class Statement(Base):
    """Statement database model."""

    __tablename__ = "statements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    opening_balance = Column(Numeric(15, 2), nullable=False)
    closing_balance = Column(Numeric(15, 2), nullable=False)
    total_credits = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    total_debits = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    transaction_count = Column(String(10), default="0", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_statements_account_id", "account_id"),
        Index("idx_statements_period", "start_date", "end_date"),
    )
