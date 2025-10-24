"""Repository patterns for data access layer."""

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from src.database import User, Account, Transaction, Transfer, Card, Statement
from src.models import TransactionType, CardType, CardStatus, TransactionStatus

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base repository class for common CRUD operations."""

    def __init__(self, session: Session, model: type[T]) -> None:
        """Initialize repository with session and model."""
        self.session = session
        self.model = model

    def create(self, obj_in: dict) -> T:
        """Create a new object."""
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        self.session.flush()
        return db_obj

    def get_by_id(self, obj_id: UUID) -> Optional[T]:
        """Get object by ID."""
        return self.session.query(self.model).filter(self.model.id == obj_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all objects with pagination."""
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def update(self, obj_id: UUID, obj_in: dict) -> Optional[T]:
        """Update an object."""
        obj = self.get_by_id(obj_id)
        if not obj:
            return None
        for key, value in obj_in.items():
            setattr(obj, key, value)
        self.session.flush()
        return obj

    def delete(self, obj_id: UUID) -> bool:
        """Delete an object."""
        obj = self.get_by_id(obj_id)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.flush()
        return True


class UserRepository(BaseRepository[User]):
    """Repository for User model."""

    def __init__(self, session: Session) -> None:
        """Initialize user repository."""
        super().__init__(session, User)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.session.query(User).filter(User.email == email.lower()).first()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users."""
        return (
            self.session.query(User)
            .filter(User.is_active.is_(True))
            .offset(skip)
            .limit(limit)
            .all()
        )


class AccountRepository(BaseRepository[Account]):
    """Repository for Account model."""

    def __init__(self, session: Session) -> None:
        """Initialize account repository."""
        super().__init__(session, Account)

    def get_by_account_number(self, account_number: str) -> Optional[Account]:
        """Get account by account number."""
        return (
            self.session.query(Account)
            .filter(Account.account_number == account_number)
            .first()
        )

    def get_by_holder_id(self, holder_id: UUID) -> List[Account]:
        """Get all accounts for a specific holder."""
        return self.session.query(Account).filter(Account.holder_id == holder_id).all()

    def get_active_accounts_for_holder(self, holder_id: UUID) -> List[Account]:
        """Get all active accounts for a specific holder."""
        return (
            self.session.query(Account)
            .filter(Account.holder_id == holder_id, Account.is_active.is_(True))
            .all()
        )


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for Transaction model."""

    def __init__(self, session: Session) -> None:
        """Initialize transaction repository."""
        super().__init__(session, Transaction)

    def get_by_account_id(
        self, account_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        """Get transactions for a specific account."""
        return (
            self.session.query(Transaction)
            .filter(Transaction.account_id == account_id)
            .order_by(Transaction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_account_id_and_date_range(
        self, account_id: UUID, start_date: datetime, end_date: datetime
    ) -> List[Transaction]:
        """Get transactions for an account within a date range."""
        return (
            self.session.query(Transaction)
            .filter(
                Transaction.account_id == account_id,
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date,
            )
            .order_by(Transaction.created_at.desc())
            .all()
        )


class TransferRepository(BaseRepository[Transfer]):
    """Repository for Transfer model."""

    def __init__(self, session: Session) -> None:
        """Initialize transfer repository."""
        super().__init__(session, Transfer)

    def get_by_from_account_id(
        self, from_account_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Transfer]:
        """Get transfers from a specific account."""
        return (
            self.session.query(Transfer)
            .filter(Transfer.from_account_id == from_account_id)
            .order_by(Transfer.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_to_account_id(
        self, to_account_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Transfer]:
        """Get transfers to a specific account."""
        return (
            self.session.query(Transfer)
            .filter(Transfer.to_account_id == to_account_id)
            .order_by(Transfer.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


class CardRepository(BaseRepository[Card]):
    """Repository for Card model."""

    def __init__(self, session: Session) -> None:
        """Initialize card repository."""
        super().__init__(session, Card)

    def get_by_card_number(self, card_number: str) -> Optional[Card]:
        """Get card by card number."""
        return self.session.query(Card).filter(Card.card_number == card_number).first()

    def get_by_holder_id(self, holder_id: UUID) -> List[Card]:
        """Get all cards for a specific holder."""
        return self.session.query(Card).filter(Card.holder_id == holder_id).all()

    def get_active_cards_for_holder(self, holder_id: UUID) -> List[Card]:
        """Get all active cards for a specific holder."""
        return (
            self.session.query(Card)
            .filter(Card.holder_id == holder_id, Card.status == CardStatus.ACTIVE)
            .all()
        )


class StatementRepository(BaseRepository[Statement]):
    """Repository for Statement model."""

    def __init__(self, session: Session) -> None:
        """Initialize statement repository."""
        super().__init__(session, Statement)

    def get_by_account_id(self, account_id: UUID, skip: int = 0, limit: int = 100) -> List[
        Statement
    ]:
        """Get statements for a specific account."""
        return (
            self.session.query(Statement)
            .filter(Statement.account_id == account_id)
            .order_by(Statement.start_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_account_id_and_date_range(
        self, account_id: UUID, start_date: datetime, end_date: datetime
    ) -> List[Statement]:
        """Get statements for an account within a date range."""
        return (
            self.session.query(Statement)
            .filter(
                Statement.account_id == account_id,
                Statement.start_date >= start_date,
                Statement.end_date <= end_date,
            )
            .order_by(Statement.start_date.desc())
            .all()
        )
