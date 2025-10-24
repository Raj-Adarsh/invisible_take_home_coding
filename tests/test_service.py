"""Unit tests for service layer."""

from decimal import Decimal
from uuid import uuid4

import pytest

from src.database import User
from src.repository import UserRepository
from src.security import hash_password
from src.service import (
    UserService,
    AccountService,
    TransactionService,
    TransferService,
    CardService,
)
from src.models import TransactionType, CardType


class TestUserService:
    """Tests for UserService."""

    def test_create_user(self, db_session):
        """Test creating a user."""
        service = UserService(db_session)
        user = service.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        db_session.commit()

        assert user["email"] == "test@example.com"
        assert user["first_name"] == "John"

    def test_create_duplicate_user(self, db_session):
        """Test that duplicate email raises error."""
        service = UserService(db_session)
        service.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        db_session.commit()

        with pytest.raises(ValueError, match="already exists"):
            service.create_user(
                email="test@example.com",
                password="TestPass456!",
                first_name="Jane",
                last_name="Doe",
            )

    def test_authenticate_user(self, db_session):
        """Test authenticating a user."""
        service = UserService(db_session)
        service.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        db_session.commit()

        user = service.authenticate_user(
            email="test@example.com", password="TestPass123!"
        )
        assert user is not None
        assert user["email"] == "test@example.com"

    def test_authenticate_user_wrong_password(self, db_session):
        """Test authentication with wrong password."""
        service = UserService(db_session)
        service.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        db_session.commit()

        user = service.authenticate_user(
            email="test@example.com", password="WrongPass123!"
        )
        assert user is None


class TestAccountService:
    """Tests for AccountService."""

    def test_create_account(self, db_session):
        """Test creating an account."""
        # Create user first
        user_service = UserService(db_session)
        user = user_service.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        db_session.commit()

        # Create account
        acc_service = AccountService(db_session)
        account = acc_service.create_account(
            holder_id=uuid4.UUID(hex=user["id"].hex),
            account_type="Savings",
            initial_balance=Decimal("1000.00"),
        )
        db_session.commit()

        assert account["account_type"] == "Savings"
        assert account["balance"] == Decimal("1000.00")

    def test_create_account_nonexistent_user(self, db_session):
        """Test creating account for nonexistent user."""
        service = AccountService(db_session)
        with pytest.raises(ValueError, match="not found"):
            service.create_account(
                holder_id=uuid4(),
                account_type="Savings",
                initial_balance=Decimal("1000.00"),
            )

    def test_create_account_negative_balance(self, db_session):
        """Test creating account with negative balance."""
        # Create user
        user_service = UserService(db_session)
        user = user_service.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        db_session.commit()

        service = AccountService(db_session)
        with pytest.raises(ValueError, match="cannot be negative"):
            service.create_account(
                holder_id=uuid4.UUID(hex=user["id"].hex),
                account_type="Savings",
                initial_balance=Decimal("-100.00"),
            )


class TestTransactionService:
    """Tests for TransactionService."""

    def test_deposit(self, db_session):
        """Test deposit transaction."""
        # Setup
        user_service = UserService(db_session)
        user = user_service.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        db_session.commit()

        acc_service = AccountService(db_session)
        account = acc_service.create_account(
            holder_id=uuid4.UUID(hex=user["id"].hex),
            account_type="Savings",
            initial_balance=Decimal("0.00"),
        )
        db_session.commit()

        # Test
        txn_service = TransactionService(db_session)
        transaction = txn_service.deposit(
            account_id=uuid4.UUID(hex=account["id"].hex),
            amount=Decimal("100.00"),
        )
        db_session.commit()

        assert transaction["transaction_type"] == "deposit"
        assert transaction["amount"] == Decimal("100.00")
        assert transaction["balance_after"] == Decimal("100.00")

    def test_withdrawal(self, db_session):
        """Test withdrawal transaction."""
        # Setup
        user_service = UserService(db_session)
        user = user_service.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        db_session.commit()

        acc_service = AccountService(db_session)
        account = acc_service.create_account(
            holder_id=uuid4.UUID(hex=user["id"].hex),
            account_type="Savings",
            initial_balance=Decimal("500.00"),
        )
        db_session.commit()

        # Test
        txn_service = TransactionService(db_session)
        transaction = txn_service.withdrawal(
            account_id=uuid4.UUID(hex=account["id"].hex),
            amount=Decimal("100.00"),
        )
        db_session.commit()

        assert transaction["transaction_type"] == "withdrawal"
        assert transaction["amount"] == Decimal("100.00")
        assert transaction["balance_after"] == Decimal("400.00")

    def test_withdrawal_insufficient_funds(self, db_session):
        """Test withdrawal with insufficient funds."""
        # Setup
        user_service = UserService(db_session)
        user = user_service.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        db_session.commit()

        acc_service = AccountService(db_session)
        account = acc_service.create_account(
            holder_id=uuid4.UUID(hex=user["id"].hex),
            account_type="Savings",
            initial_balance=Decimal("50.00"),
        )
        db_session.commit()

        # Test
        txn_service = TransactionService(db_session)
        with pytest.raises(ValueError, match="Insufficient funds"):
            txn_service.withdrawal(
                account_id=uuid4.UUID(hex=account["id"].hex),
                amount=Decimal("100.00"),
            )


class TestTransferService:
    """Tests for TransferService."""

    def test_transfer_money(self, db_session):
        """Test transferring money between accounts."""
        # Setup
        user_service = UserService(db_session)
        user1 = user_service.create_user(
            email="user1@example.com",
            password="TestPass123!",
            first_name="User",
            last_name="One",
        )
        user2 = user_service.create_user(
            email="user2@example.com",
            password="TestPass123!",
            first_name="User",
            last_name="Two",
        )
        db_session.commit()

        acc_service = AccountService(db_session)
        account1 = acc_service.create_account(
            holder_id=uuid4.UUID(hex=user1["id"].hex),
            account_type="Savings",
            initial_balance=Decimal("1000.00"),
        )
        account2 = acc_service.create_account(
            holder_id=uuid4.UUID(hex=user2["id"].hex),
            account_type="Savings",
            initial_balance=Decimal("0.00"),
        )
        db_session.commit()

        # Test
        transfer_service = TransferService(db_session)
        transfer = transfer_service.transfer_money(
            from_account_id=uuid4.UUID(hex=account1["id"].hex),
            to_account_id=uuid4.UUID(hex=account2["id"].hex),
            amount=Decimal("500.00"),
        )
        db_session.commit()

        assert transfer["amount"] == Decimal("500.00")
        assert transfer["status"] == "completed"

    def test_transfer_same_account(self, db_session):
        """Test transferring to same account raises error."""
        # Setup
        user_service = UserService(db_session)
        user = user_service.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        db_session.commit()

        acc_service = AccountService(db_session)
        account = acc_service.create_account(
            holder_id=uuid4.UUID(hex=user["id"].hex),
            account_type="Savings",
            initial_balance=Decimal("1000.00"),
        )
        db_session.commit()

        # Test
        transfer_service = TransferService(db_session)
        with pytest.raises(ValueError, match="same account"):
            transfer_service.transfer_money(
                from_account_id=uuid4.UUID(hex=account["id"].hex),
                to_account_id=uuid4.UUID(hex=account["id"].hex),
                amount=Decimal("500.00"),
            )


class TestCardService:
    """Tests for CardService."""

    def test_create_card(self, db_session):
        """Test creating a card."""
        # Setup
        user_service = UserService(db_session)
        user = user_service.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        db_session.commit()

        acc_service = AccountService(db_session)
        account = acc_service.create_account(
            holder_id=uuid4.UUID(hex=user["id"].hex),
            account_type="Savings",
            initial_balance=Decimal("1000.00"),
        )
        db_session.commit()

        # Test
        card_service = CardService(db_session)
        card = card_service.create_card(
            holder_id=uuid4.UUID(hex=user["id"].hex),
            account_id=uuid4.UUID(hex=account["id"].hex),
            card_type="debit",
        )
        db_session.commit()

        assert card["card_type"] == "debit"
        assert card["status"] == "active"

    def test_block_card(self, db_session):
        """Test blocking a card."""
        # Setup
        user_service = UserService(db_session)
        user = user_service.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        db_session.commit()

        acc_service = AccountService(db_session)
        account = acc_service.create_account(
            holder_id=uuid4.UUID(hex=user["id"].hex),
            account_type="Savings",
            initial_balance=Decimal("1000.00"),
        )
        db_session.commit()

        card_service = CardService(db_session)
        card = card_service.create_card(
            holder_id=uuid4.UUID(hex=user["id"].hex),
            account_id=uuid4.UUID(hex=account["id"].hex),
            card_type="debit",
        )
        db_session.commit()

        # Test
        blocked_card = card_service.block_card(uuid4.UUID(hex=card["id"].hex))
        db_session.commit()

        assert blocked_card["status"] == "blocked"
