"""Unit tests for domain models."""

from decimal import Decimal
from uuid import uuid4

import pytest

from src.models import (
    UserCreate,
    AccountCreate,
    TransactionCreate,
    TransactionType,
    CardType,
    TransferRequest,
)


class TestUserCreate:
    """Tests for UserCreate model."""

    def test_user_create_valid(self):
        """Test creating a valid user."""
        user = UserCreate(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        assert user.email == "test@example.com"
        assert user.first_name == "John"

    def test_user_create_email_lowercase(self):
        """Test that email is converted to lowercase."""
        user = UserCreate(
            email="TEST@EXAMPLE.COM",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        assert user.email == "test@example.com"

    def test_user_create_invalid_email(self):
        """Test that invalid email raises error."""
        with pytest.raises(ValueError, match="Invalid email format"):
            UserCreate(
                email="invalid-email",
                password="TestPass123!",
                first_name="John",
                last_name="Doe",
            )

    def test_user_create_weak_password_no_uppercase(self):
        """Test that password without uppercase raises error."""
        with pytest.raises(ValueError, match="uppercase letter"):
            UserCreate(
                email="test@example.com",
                password="testpass123!",
                first_name="John",
                last_name="Doe",
            )

    def test_user_create_weak_password_no_digit(self):
        """Test that password without digit raises error."""
        with pytest.raises(ValueError, match="digit"):
            UserCreate(
                email="test@example.com",
                password="TestPass!",
                first_name="John",
                last_name="Doe",
            )

    def test_user_create_weak_password_no_special_char(self):
        """Test that password without special character raises error."""
        with pytest.raises(ValueError, match="special character"):
            UserCreate(
                email="test@example.com",
                password="TestPass123",
                first_name="John",
                last_name="Doe",
            )

    def test_user_create_password_too_short(self):
        """Test that short password raises error."""
        with pytest.raises(ValueError):
            UserCreate(
                email="test@example.com",
                password="TPass1!",
                first_name="John",
                last_name="Doe",
            )


class TestAccountCreate:
    """Tests for AccountCreate model."""

    def test_account_create_valid(self):
        """Test creating a valid account."""
        account = AccountCreate(
            account_type="Savings",
            initial_balance=Decimal("1000.00"),
        )
        assert account.account_type == "Savings"
        assert account.initial_balance == Decimal("1000.00")

    def test_account_create_default_balance(self):
        """Test account creation with default balance."""
        account = AccountCreate(account_type="Checking")
        assert account.initial_balance == Decimal("0.00")

    def test_account_create_negative_balance(self):
        """Test that negative balance raises error."""
        with pytest.raises(ValueError):
            AccountCreate(
                account_type="Savings",
                initial_balance=Decimal("-100.00"),
            )

    def test_account_create_balance_decimal_places(self):
        """Test that balance is quantized to 2 decimal places."""
        account = AccountCreate(
            account_type="Savings",
            initial_balance=Decimal("100.1"),
        )
        assert account.initial_balance == Decimal("100.10")


class TestTransactionCreate:
    """Tests for TransactionCreate model."""

    def test_transaction_create_valid(self):
        """Test creating a valid transaction."""
        transaction = TransactionCreate(
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("100.00"),
            description="Test deposit",
        )
        assert transaction.transaction_type == TransactionType.DEPOSIT
        assert transaction.amount == Decimal("100.00")

    def test_transaction_create_zero_amount(self):
        """Test that zero amount raises error."""
        with pytest.raises(ValueError, match="greater than 0"):
            TransactionCreate(
                transaction_type=TransactionType.DEPOSIT,
                amount=Decimal("0.00"),
            )

    def test_transaction_create_negative_amount(self):
        """Test that negative amount raises error."""
        with pytest.raises(ValueError, match="greater than 0"):
            TransactionCreate(
                transaction_type=TransactionType.WITHDRAWAL,
                amount=Decimal("-50.00"),
            )

    def test_transaction_create_amount_quantization(self):
        """Test that amount is quantized to 2 decimal places."""
        transaction = TransactionCreate(
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("100.1"),
        )
        assert transaction.amount == Decimal("100.10")


class TestTransferRequest:
    """Tests for TransferRequest model."""

    def test_transfer_request_valid(self):
        """Test creating a valid transfer request."""
        from_id = uuid4()
        to_id = uuid4()
        transfer = TransferRequest(
            from_account_id=from_id,
            to_account_id=to_id,
            amount=Decimal("500.00"),
        )
        assert transfer.from_account_id == from_id
        assert transfer.to_account_id == to_id
        assert transfer.amount == Decimal("500.00")

    def test_transfer_request_zero_amount(self):
        """Test that zero amount raises error."""
        with pytest.raises(ValueError, match="greater than 0"):
            TransferRequest(
                from_account_id=uuid4(),
                to_account_id=uuid4(),
                amount=Decimal("0.00"),
            )

    def test_transfer_request_negative_amount(self):
        """Test that negative amount raises error."""
        with pytest.raises(ValueError, match="greater than 0"):
            TransferRequest(
                from_account_id=uuid4(),
                to_account_id=uuid4(),
                amount=Decimal("-100.00"),
            )
