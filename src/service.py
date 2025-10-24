"""Service layer for business logic."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from src.database import Account, Transaction, Transfer, Card, Statement
from src.models import (
    TransactionStatus,
    TransactionType,
    CardStatus,
)
from src.repository import (
    UserRepository,
    AccountRepository,
    TransactionRepository,
    TransferRepository,
    CardRepository,
    StatementRepository,
)
from src.security import hash_password, verify_password


class UserService:
    """Service for user-related operations."""

    def __init__(self, session: Session) -> None:
        """Initialize user service."""
        self.session = session
        self.user_repo = UserRepository(session)

    def create_user(
        self, email: str, password: str, first_name: str, last_name: str
    ) -> dict:
        """Create a new user."""
        # Check if user already exists
        if self.user_repo.get_by_email(email):
            raise ValueError(f"User with email {email} already exists")

        user = self.user_repo.create(
            {
                "email": email.lower(),
                "hashed_password": hash_password(password),
                "first_name": first_name,
                "last_name": last_name,
            }
        )
        return self._user_to_dict(user)

    def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Authenticate a user with email and password."""
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return self._user_to_dict(user)

    def get_user(self, user_id: UUID) -> Optional[dict]:
        """Get user by ID."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        return self._user_to_dict(user)

    @staticmethod
    def _user_to_dict(user) -> dict:
        """Convert user object to dictionary."""
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }


class AccountService:
    """Service for account-related operations."""

    def __init__(self, session: Session) -> None:
        """Initialize account service."""
        self.session = session
        self.account_repo = AccountRepository(session)
        self.user_repo = UserRepository(session)

    def create_account(
        self, holder_id: UUID, account_type: str, initial_balance: Decimal = Decimal("0.00")
    ) -> dict:
        """Create a new account."""
        # Verify holder exists
        holder = self.user_repo.get_by_id(holder_id)
        if not holder:
            raise ValueError(f"User {holder_id} not found")

        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")

        account_number = self._generate_account_number()
        account = self.account_repo.create(
            {
                "account_number": account_number,
                "holder_id": holder_id,
                "account_type": account_type,
                "balance": initial_balance.quantize(Decimal("0.01")),
            }
        )
        return self._account_to_dict(account)

    def get_account(self, account_id: UUID) -> Optional[dict]:
        """Get account by ID."""
        account = self.account_repo.get_by_id(account_id)
        if not account:
            return None
        return self._account_to_dict(account)

    def get_accounts_for_holder(self, holder_id: UUID) -> List[dict]:
        """Get all accounts for a holder."""
        accounts = self.account_repo.get_active_accounts_for_holder(holder_id)
        return [self._account_to_dict(acc) for acc in accounts]

    def get_balance(self, account_id: UUID) -> Optional[Decimal]:
        """Get account balance."""
        account = self.account_repo.get_by_id(account_id)
        if not account:
            return None
        return account.balance

    @staticmethod
    def _generate_account_number() -> str:
        """Generate a unique account number."""
        # Format: ACC-YYYYMMDDXXXXXX (16 characters after ACC-)
        return f"ACC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid4())[:8].upper()}"

    @staticmethod
    def _account_to_dict(account) -> dict:
        """Convert account object to dictionary."""
        return {
            "id": account.id,
            "account_number": account.account_number,
            "holder_id": account.holder_id,
            "account_type": account.account_type,
            "balance": account.balance,
            "is_active": account.is_active,
            "created_at": account.created_at,
            "updated_at": account.updated_at,
        }


class TransactionService:
    """Service for transaction-related operations."""

    def __init__(self, session: Session) -> None:
        """Initialize transaction service."""
        self.session = session
        self.transaction_repo = TransactionRepository(session)
        self.account_repo = AccountRepository(session)

    def deposit(self, account_id: UUID, amount: Decimal, description: Optional[str] = None) -> dict:
        """Perform a deposit transaction."""
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than 0")

        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        if not account.is_active:
            raise ValueError("Account is not active")

        # Update account balance
        new_balance = (account.balance + amount).quantize(Decimal("0.01"))
        account.balance = new_balance

        # Create transaction record
        transaction = self.transaction_repo.create(
            {
                "account_id": account_id,
                "transaction_type": TransactionType.DEPOSIT,
                "amount": amount.quantize(Decimal("0.01")),
                "status": TransactionStatus.COMPLETED,
                "balance_after": new_balance,
                "description": description,
            }
        )

        return self._transaction_to_dict(transaction)

    def withdrawal(
        self, account_id: UUID, amount: Decimal, description: Optional[str] = None
    ) -> dict:
        """Perform a withdrawal transaction."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than 0")

        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        if not account.is_active:
            raise ValueError("Account is not active")

        if account.balance < amount:
            raise ValueError("Insufficient funds")

        # Update account balance
        new_balance = (account.balance - amount).quantize(Decimal("0.01"))
        account.balance = new_balance

        # Create transaction record
        transaction = self.transaction_repo.create(
            {
                "account_id": account_id,
                "transaction_type": TransactionType.WITHDRAWAL,
                "amount": amount.quantize(Decimal("0.01")),
                "status": TransactionStatus.COMPLETED,
                "balance_after": new_balance,
                "description": description,
            }
        )

        return self._transaction_to_dict(transaction)

    def get_transactions(self, account_id: UUID, skip: int = 0, limit: int = 50) -> List[dict]:
        """Get all transactions for an account."""
        transactions = self.transaction_repo.get_by_account_id(account_id, skip, limit)
        return [self._transaction_to_dict(t) for t in transactions]

    def get_transactions_in_date_range(
        self, account_id: UUID, start_date: datetime, end_date: datetime
    ) -> List[dict]:
        """Get transactions for an account in a specific date range."""
        transactions = self.transaction_repo.get_by_account_id_and_date_range(
            account_id, start_date, end_date
        )
        return [self._transaction_to_dict(t) for t in transactions]

    @staticmethod
    def _transaction_to_dict(transaction) -> dict:
        """Convert transaction object to dictionary."""
        return {
            "id": transaction.id,
            "account_id": transaction.account_id,
            "transaction_type": transaction.transaction_type.value if hasattr(transaction.transaction_type, 'value') else transaction.transaction_type,
            "amount": transaction.amount,
            "status": transaction.status.value if hasattr(transaction.status, 'value') else transaction.status,
            "balance_after": transaction.balance_after,
            "description": transaction.description,
            "created_at": transaction.created_at,
            "updated_at": transaction.updated_at,
        }


class TransferService:
    """Service for money transfer operations."""

    def __init__(self, session: Session) -> None:
        """Initialize transfer service."""
        self.session = session
        self.transfer_repo = TransferRepository(session)
        self.account_repo = AccountRepository(session)
        self.transaction_repo = TransactionRepository(session)

    def transfer_money(
        self,
        from_account_id: UUID,
        to_account_id: UUID,
        amount: Decimal,
        description: Optional[str] = None,
    ) -> dict:
        """Transfer money between accounts."""
        if amount <= 0:
            raise ValueError("Transfer amount must be greater than 0")

        if from_account_id == to_account_id:
            raise ValueError("Cannot transfer to the same account")

        from_account = self.account_repo.get_by_id(from_account_id)
        if not from_account or not from_account.is_active:
            raise ValueError("Source account not found or inactive")

        to_account = self.account_repo.get_by_id(to_account_id)
        if not to_account or not to_account.is_active:
            raise ValueError("Destination account not found or inactive")

        if from_account.balance < amount:
            raise ValueError("Insufficient funds in source account")

        # Debit from source account
        from_account.balance = (from_account.balance - amount).quantize(Decimal("0.01"))
        from_transaction = self.transaction_repo.create(
            {
                "account_id": from_account_id,
                "transaction_type": TransactionType.TRANSFER,
                "amount": amount.quantize(Decimal("0.01")),
                "status": TransactionStatus.COMPLETED,
                "balance_after": from_account.balance,
                "description": f"Transfer to {to_account.account_number}",
            }
        )

        # Credit to destination account
        to_account.balance = (to_account.balance + amount).quantize(Decimal("0.01"))
        to_transaction = self.transaction_repo.create(
            {
                "account_id": to_account_id,
                "transaction_type": TransactionType.TRANSFER,
                "amount": amount.quantize(Decimal("0.01")),
                "status": TransactionStatus.COMPLETED,
                "balance_after": to_account.balance,
                "description": f"Transfer from {from_account.account_number}",
            }
        )

        # Create transfer record
        transfer = self.transfer_repo.create(
            {
                "from_account_id": from_account_id,
                "to_account_id": to_account_id,
                "amount": amount.quantize(Decimal("0.01")),
                "status": TransactionStatus.COMPLETED,
                "description": description,
                "from_transaction_id": from_transaction.id,
                "to_transaction_id": to_transaction.id,
            }
        )

        return self._transfer_to_dict(transfer)

    def get_outgoing_transfers(
        self, from_account_id: UUID, skip: int = 0, limit: int = 50
    ) -> List[dict]:
        """Get all outgoing transfers for an account."""
        transfers = self.transfer_repo.get_by_from_account_id(from_account_id, skip, limit)
        return [self._transfer_to_dict(t) for t in transfers]

    def get_incoming_transfers(
        self, to_account_id: UUID, skip: int = 0, limit: int = 50
    ) -> List[dict]:
        """Get all incoming transfers for an account."""
        transfers = self.transfer_repo.get_by_to_account_id(to_account_id, skip, limit)
        return [self._transfer_to_dict(t) for t in transfers]

    @staticmethod
    def _transfer_to_dict(transfer) -> dict:
        """Convert transfer object to dictionary."""
        return {
            "id": transfer.id,
            "from_account_id": transfer.from_account_id,
            "to_account_id": transfer.to_account_id,
            "amount": transfer.amount,
            "status": transfer.status.value if hasattr(transfer.status, 'value') else transfer.status,
            "description": transfer.description,
            "from_transaction_id": transfer.from_transaction_id,
            "to_transaction_id": transfer.to_transaction_id,
            "created_at": transfer.created_at,
            "updated_at": transfer.updated_at,
        }


class CardService:
    """Service for card management."""

    def __init__(self, session: Session) -> None:
        """Initialize card service."""
        self.session = session
        self.card_repo = CardRepository(session)
        self.account_repo = AccountRepository(session)

    def create_card(self, holder_id: UUID, account_id: UUID, card_type: str) -> dict:
        """Create a new card."""
        account = self.account_repo.get_by_id(account_id)
        if not account or account.holder_id != holder_id:
            raise ValueError("Account not found or does not belong to user")

        card_number = self._generate_card_number()
        expiry_date = self._generate_expiry_date()

        card = self.card_repo.create(
            {
                "card_number": card_number,
                "last_four": card_number[-4:],
                "card_type": card_type,
                "holder_id": holder_id,
                "account_id": account_id,
                "expiry_date": expiry_date,
                "cvv": self._generate_encrypted_cvv(),  # In production, use proper encryption
            }
        )

        return self._card_to_dict(card)

    def get_cards_for_holder(self, holder_id: UUID) -> List[dict]:
        """Get all cards for a holder."""
        cards = self.card_repo.get_active_cards_for_holder(holder_id)
        return [self._card_to_dict(c) for c in cards]

    def block_card(self, card_id: UUID) -> dict:
        """Block a card."""
        card = self.card_repo.get_by_id(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")

        card.status = CardStatus.BLOCKED
        self.session.flush()
        return self._card_to_dict(card)

    @staticmethod
    def _generate_card_number() -> str:
        """Generate a unique card number."""
        import random

        # Simplified card number generation (not production-ready)
        return "".join([str(random.randint(0, 9)) for _ in range(16)])

    @staticmethod
    def _generate_expiry_date() -> str:
        """Generate card expiry date (5 years from now)."""
        from datetime import timedelta

        expiry = datetime.now(timezone.utc) + timedelta(days=365 * 5)
        return expiry.strftime("%m/%Y")

    @staticmethod
    def _generate_encrypted_cvv() -> str:
        """Generate encrypted CVV (simplified)."""
        import random

        # In production, this should be properly encrypted
        return str(random.randint(100, 999))

    @staticmethod
    def _card_to_dict(card) -> dict:
        """Convert card object to dictionary."""
        return {
            "id": card.id,
            "card_number": card.card_number,
            "card_type": card.card_type.value if hasattr(card.card_type, 'value') else card.card_type,
            "status": card.status.value if hasattr(card.status, 'value') else card.status,
            "holder_id": card.holder_id,
            "account_id": card.account_id,
            "expiry_date": card.expiry_date,
            "last_four": card.last_four,
            "created_at": card.created_at,
            "updated_at": card.updated_at,
        }


class StatementService:
    """Service for generating statements."""

    def __init__(self, session: Session) -> None:
        """Initialize statement service."""
        self.session = session
        self.statement_repo = StatementRepository(session)
        self.transaction_repo = TransactionRepository(session)
        self.account_repo = AccountRepository(session)

    def generate_statement(
        self, account_id: UUID, start_date: datetime, end_date: datetime
    ) -> dict:
        """Generate a statement for an account for a period."""
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        # Get transactions in date range
        transactions = self.transaction_repo.get_by_account_id_and_date_range(
            account_id, start_date, end_date
        )

        # Calculate totals
        total_credits = Decimal("0.00")
        total_debits = Decimal("0.00")

        for txn in transactions:
            if txn.transaction_type in [TransactionType.DEPOSIT, TransactionType.TRANSFER]:
                total_credits += txn.amount
            else:
                total_debits += txn.amount

        # Get opening and closing balances
        all_transactions = self.transaction_repo.get_by_account_id_and_date_range(
            account_id,
            datetime.min.replace(tzinfo=timezone.utc),
            end_date,
        )

        opening_balance = Decimal("0.00")
        if all_transactions:
            # Get balance before the statement period
            pre_period_txns = [
                t for t in all_transactions if t.created_at < start_date
            ]
            if pre_period_txns:
                opening_balance = pre_period_txns[-1].balance_after

        closing_balance = (opening_balance + total_credits - total_debits).quantize(Decimal("0.01"))

        statement = self.statement_repo.create(
            {
                "account_id": account_id,
                "start_date": start_date,
                "end_date": end_date,
                "opening_balance": opening_balance,
                "closing_balance": closing_balance,
                "total_credits": total_credits.quantize(Decimal("0.01")),
                "total_debits": total_debits.quantize(Decimal("0.01")),
                "transaction_count": str(len(transactions)),
            }
        )

        return self._statement_to_dict(statement)

    def get_statements(self, account_id: UUID, skip: int = 0, limit: int = 50) -> List[dict]:
        """Get statements for an account."""
        statements = self.statement_repo.get_by_account_id(account_id, skip, limit)
        return [self._statement_to_dict(s) for s in statements]

    @staticmethod
    def _statement_to_dict(statement) -> dict:
        """Convert statement object to dictionary."""
        return {
            "id": statement.id,
            "account_id": statement.account_id,
            "start_date": statement.start_date,
            "end_date": statement.end_date,
            "opening_balance": statement.opening_balance,
            "closing_balance": statement.closing_balance,
            "total_credits": statement.total_credits,
            "total_debits": statement.total_debits,
            "transaction_count": statement.transaction_count,
            "created_at": statement.created_at,
            "updated_at": statement.updated_at,
        }
