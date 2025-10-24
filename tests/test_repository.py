"""Unit tests for repository layer."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from src.database import User, Account, Transaction, Card
from src.models import TransactionType, TransactionStatus, CardType, CardStatus
from src.repository import (
    UserRepository,
    AccountRepository,
    TransactionRepository,
    CardRepository,
)
from src.security import hash_password


class TestUserRepository:
    """Tests for UserRepository."""

    def test_create_user(self, db_session):
        """Test creating a user."""
        repo = UserRepository(db_session)
        user_data = {
            "email": "test@example.com",
            "hashed_password": hash_password("TestPass123!"),
            "first_name": "John",
            "last_name": "Doe",
        }
        user = repo.create(user_data)
        db_session.commit()

        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.is_active is True

    def test_get_user_by_id(self, db_session):
        """Test getting user by ID."""
        repo = UserRepository(db_session)
        user_data = {
            "email": "test@example.com",
            "hashed_password": hash_password("TestPass123!"),
            "first_name": "John",
            "last_name": "Doe",
        }
        created_user = repo.create(user_data)
        db_session.commit()

        retrieved_user = repo.get_by_id(created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"

    def test_get_user_by_email(self, db_session):
        """Test getting user by email."""
        repo = UserRepository(db_session)
        user_data = {
            "email": "test@example.com",
            "hashed_password": hash_password("TestPass123!"),
            "first_name": "John",
            "last_name": "Doe",
        }
        repo.create(user_data)
        db_session.commit()

        user = repo.get_by_email("test@example.com")
        assert user is not None
        assert user.email == "test@example.com"

    def test_get_active_users(self, db_session):
        """Test getting active users."""
        repo = UserRepository(db_session)
        user_data_1 = {
            "email": "user1@example.com",
            "hashed_password": hash_password("TestPass123!"),
            "first_name": "User",
            "last_name": "One",
        }
        user_data_2 = {
            "email": "user2@example.com",
            "hashed_password": hash_password("TestPass123!"),
            "first_name": "User",
            "last_name": "Two",
            "is_active": False,
        }
        repo.create(user_data_1)
        repo.create(user_data_2)
        db_session.commit()

        active_users = repo.get_active_users()
        assert len(active_users) == 1
        assert active_users[0].email == "user1@example.com"


class TestAccountRepository:
    """Tests for AccountRepository."""

    def test_create_account(self, db_session):
        """Test creating an account."""
        # Create user first
        user_repo = UserRepository(db_session)
        user = user_repo.create(
            {
                "email": "test@example.com",
                "hashed_password": hash_password("TestPass123!"),
                "first_name": "John",
                "last_name": "Doe",
            }
        )
        db_session.commit()

        # Create account
        acc_repo = AccountRepository(db_session)
        account_data = {
            "account_number": "ACC-20251024-ABC123",
            "holder_id": user.id,
            "account_type": "Savings",
            "balance": Decimal("1000.00"),
        }
        account = acc_repo.create(account_data)
        db_session.commit()

        assert account.account_type == "Savings"
        assert account.balance == Decimal("1000.00")

    def test_get_account_by_number(self, db_session):
        """Test getting account by account number."""
        # Setup
        user_repo = UserRepository(db_session)
        user = user_repo.create(
            {
                "email": "test@example.com",
                "hashed_password": hash_password("TestPass123!"),
                "first_name": "John",
                "last_name": "Doe",
            }
        )
        db_session.commit()

        acc_repo = AccountRepository(db_session)
        account = acc_repo.create(
            {
                "account_number": "ACC-20251024-ABC123",
                "holder_id": user.id,
                "account_type": "Savings",
                "balance": Decimal("1000.00"),
            }
        )
        db_session.commit()

        # Test
        retrieved = acc_repo.get_by_account_number("ACC-20251024-ABC123")
        assert retrieved is not None
        assert retrieved.account_type == "Savings"

    def test_get_accounts_by_holder_id(self, db_session):
        """Test getting accounts by holder ID."""
        # Setup
        user_repo = UserRepository(db_session)
        user = user_repo.create(
            {
                "email": "test@example.com",
                "hashed_password": hash_password("TestPass123!"),
                "first_name": "John",
                "last_name": "Doe",
            }
        )
        db_session.commit()

        acc_repo = AccountRepository(db_session)
        acc_repo.create(
            {
                "account_number": "ACC-001",
                "holder_id": user.id,
                "account_type": "Savings",
                "balance": Decimal("1000.00"),
            }
        )
        acc_repo.create(
            {
                "account_number": "ACC-002",
                "holder_id": user.id,
                "account_type": "Checking",
                "balance": Decimal("500.00"),
            }
        )
        db_session.commit()

        # Test
        accounts = acc_repo.get_by_holder_id(user.id)
        assert len(accounts) == 2


class TestTransactionRepository:
    """Tests for TransactionRepository."""

    def test_get_transactions_by_account_id(self, db_session):
        """Test getting transactions by account ID."""
        # Setup user and account
        user_repo = UserRepository(db_session)
        user = user_repo.create(
            {
                "email": "test@example.com",
                "hashed_password": hash_password("TestPass123!"),
                "first_name": "John",
                "last_name": "Doe",
            }
        )
        db_session.commit()

        acc_repo = AccountRepository(db_session)
        account = acc_repo.create(
            {
                "account_number": "ACC-001",
                "holder_id": user.id,
                "account_type": "Savings",
                "balance": Decimal("1000.00"),
            }
        )
        db_session.commit()

        # Create transactions
        txn_repo = TransactionRepository(db_session)
        txn_repo.create(
            {
                "account_id": account.id,
                "transaction_type": TransactionType.DEPOSIT,
                "amount": Decimal("100.00"),
                "status": TransactionStatus.COMPLETED,
                "balance_after": Decimal("1100.00"),
            }
        )
        txn_repo.create(
            {
                "account_id": account.id,
                "transaction_type": TransactionType.WITHDRAWAL,
                "amount": Decimal("50.00"),
                "status": TransactionStatus.COMPLETED,
                "balance_after": Decimal("1050.00"),
            }
        )
        db_session.commit()

        # Test
        transactions = txn_repo.get_by_account_id(account.id)
        assert len(transactions) == 2
        assert transactions[0].transaction_type == TransactionType.WITHDRAWAL
        assert transactions[1].transaction_type == TransactionType.DEPOSIT


class TestCardRepository:
    """Tests for CardRepository."""

    def test_get_active_cards_for_holder(self, db_session):
        """Test getting active cards for a holder."""
        # Setup user and account
        user_repo = UserRepository(db_session)
        user = user_repo.create(
            {
                "email": "test@example.com",
                "hashed_password": hash_password("TestPass123!"),
                "first_name": "John",
                "last_name": "Doe",
            }
        )
        db_session.commit()

        acc_repo = AccountRepository(db_session)
        account = acc_repo.create(
            {
                "account_number": "ACC-001",
                "holder_id": user.id,
                "account_type": "Savings",
                "balance": Decimal("1000.00"),
            }
        )
        db_session.commit()

        # Create cards
        card_repo = CardRepository(db_session)
        card_repo.create(
            {
                "card_number": "1234567890123456",
                "last_four": "3456",
                "card_type": CardType.DEBIT,
                "holder_id": user.id,
                "account_id": account.id,
                "expiry_date": "12/2028",
                "cvv": "encrypted_cvv",
                "status": CardStatus.ACTIVE,
            }
        )
        card_repo.create(
            {
                "card_number": "6543210987654321",
                "last_four": "4321",
                "card_type": CardType.CREDIT,
                "holder_id": user.id,
                "account_id": account.id,
                "expiry_date": "06/2027",
                "cvv": "encrypted_cvv",
                "status": CardStatus.BLOCKED,
            }
        )
        db_session.commit()

        # Test
        active_cards = card_repo.get_active_cards_for_holder(user.id)
        assert len(active_cards) == 1
        assert active_cards[0].status == CardStatus.ACTIVE
