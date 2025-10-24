"""Domain models for the banking service."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class TransactionType(str, Enum):
    """Types of transactions."""

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"


class TransactionStatus(str, Enum):
    """Transaction statuses."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"


class CardType(str, Enum):
    """Types of cards."""

    DEBIT = "debit"
    CREDIT = "credit"


class CardStatus(str, Enum):
    """Card statuses."""

    ACTIVE = "active"
    BLOCKED = "blocked"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class BaseResponse(BaseModel):
    """Base response model."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class UserCreate(BaseModel):
    """User creation request."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")

    @validator("email")
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v.lower()

    @validator("password")
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserResponse(BaseResponse):
    """User response model."""

    email: str
    first_name: str
    last_name: str
    is_active: bool


class LoginRequest(BaseModel):
    """Login request."""

    email: str
    password: str


class TokenResponse(BaseModel):
    """Token response."""

    access_token: str
    token_type: str = "bearer"


class AccountCreate(BaseModel):
    """Account creation request."""

    account_type: str = Field(..., description="Type of account")
    initial_balance: Decimal = Field(default=Decimal("0.00"), ge=0)

    @validator("initial_balance")
    def validate_balance(cls, v: Decimal) -> Decimal:
        """Validate initial balance."""
        if v < 0:
            raise ValueError("Initial balance cannot be negative")
        return v.quantize(Decimal("0.01"))


class AccountResponse(BaseResponse):
    """Account response model."""

    account_number: str
    account_type: str
    balance: Decimal
    is_active: bool
    holder_id: UUID


class TransactionCreate(BaseModel):
    """Transaction creation request."""

    transaction_type: TransactionType
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None

    @validator("amount")
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate transaction amount."""
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v.quantize(Decimal("0.01"))


class TransactionResponse(BaseResponse):
    """Transaction response model."""

    account_id: UUID
    transaction_type: TransactionType
    amount: Decimal
    status: TransactionStatus
    description: Optional[str]
    balance_after: Decimal


class TransferRequest(BaseModel):
    """Money transfer request."""

    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None

    @validator("amount")
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate transfer amount."""
        if v <= 0:
            raise ValueError("Transfer amount must be greater than 0")
        return v.quantize(Decimal("0.01"))


class CardCreate(BaseModel):
    """Card creation request."""

    card_type: CardType
    account_id: UUID


class CardResponse(BaseResponse):
    """Card response model."""

    card_number: str
    card_type: CardType
    status: CardStatus
    holder_id: UUID
    account_id: UUID
    expiry_date: str
    last_four: str


class StatementRequest(BaseModel):
    """Statement request."""

    account_id: UUID
    start_date: datetime
    end_date: datetime


class StatementResponse(BaseResponse):
    """Statement response model."""

    account_id: UUID
    start_date: datetime
    end_date: datetime
    opening_balance: Decimal
    closing_balance: Decimal
    total_credits: Decimal
    total_debits: Decimal
    transaction_count: int
