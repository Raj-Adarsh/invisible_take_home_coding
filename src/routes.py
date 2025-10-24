"""API route handlers for the banking service."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from src.db import get_db
from src.models import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    AccountCreate,
    AccountResponse,
    TransactionCreate,
    TransactionResponse,
    TransferRequest,
    CardCreate,
    CardResponse,
    StatementRequest,
    StatementResponse,
)
from src.security import create_access_token, decode_access_token
from src.service import (
    UserService,
    AccountService,
    TransactionService,
    TransferService,
    CardService,
    StatementService,
)

router = APIRouter()


# Dependency to get current user from token
def get_current_user_id(authorization: str = Header(default="")) -> UUID:
    """Extract and validate user ID from Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    token = authorization[7:]  # Remove "Bearer " prefix
    try:
        payload = decode_access_token(token)
        user_id = UUID(payload.get("sub"))
        return user_id
    except (ValueError, KeyError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e


# Authentication Endpoints
@router.post("/auth/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)) -> dict:
    """Sign up a new user."""
    try:
        service = UserService(db)
        user = service.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        db.commit()
        return user
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/auth/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)) -> dict:
    """Authenticate user and return access token."""
    service = UserService(db)
    user = service.authenticate_user(email=credentials.email, password=credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(data={"sub": str(user["id"])})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/auth/me", response_model=UserResponse)
def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict:
    """Get current user profile."""
    user_id = get_current_user_id(authorization)
    service = UserService(db)
    user = service.get_user(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


# Account Endpoints
@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account_data: AccountCreate,
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict:
    """Create a new account for the current user."""
    user_id = get_current_user_id(authorization)

    try:
        service = AccountService(db)
        account = service.create_account(
            holder_id=user_id,
            account_type=account_data.account_type,
            initial_balance=account_data.initial_balance,
        )
        db.commit()
        return account
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/accounts", response_model=List[AccountResponse])
def list_accounts(authorization: str = Header(default=""), db: Session = Depends(get_db)) -> List[dict]:
    """List all accounts for the current user."""
    user_id = get_current_user_id(authorization)
    service = AccountService(db)
    return service.get_accounts_for_holder(user_id)


@router.get("/accounts/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: UUID,
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict:
    """Get account details."""
    user_id = get_current_user_id(authorization)
    service = AccountService(db)
    account = service.get_account(account_id)

    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    if account["holder_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return account


# Transaction Endpoints
@router.post(
    "/accounts/{account_id}/transactions/deposit",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def deposit(
    account_id: UUID,
    transaction_data: TransactionCreate,
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict:
    """Deposit money into an account."""
    user_id = get_current_user_id(authorization)
    service = AccountService(db)
    account = service.get_account(account_id)

    if not account or account["holder_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        txn_service = TransactionService(db)
        transaction = txn_service.deposit(
            account_id=account_id,
            amount=transaction_data.amount,
            description=transaction_data.description,
        )
        db.commit()
        return transaction
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post(
    "/accounts/{account_id}/transactions/withdrawal",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def withdrawal(
    account_id: UUID,
    transaction_data: TransactionCreate,
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict:
    """Withdraw money from an account."""
    user_id = get_current_user_id(authorization)
    service = AccountService(db)
    account = service.get_account(account_id)

    if not account or account["holder_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        txn_service = TransactionService(db)
        transaction = txn_service.withdrawal(
            account_id=account_id,
            amount=transaction_data.amount,
            description=transaction_data.description,
        )
        db.commit()
        return transaction
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/accounts/{account_id}/transactions", response_model=List[TransactionResponse])
def get_transactions(
    account_id: UUID,
    skip: int = 0,
    limit: int = 50,
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> List[dict]:
    """Get transactions for an account."""
    user_id = get_current_user_id(authorization)
    service = AccountService(db)
    account = service.get_account(account_id)

    if not account or account["holder_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    txn_service = TransactionService(db)
    return txn_service.get_transactions(account_id, skip, limit)


# Transfer Endpoints
@router.post(
    "/transfers",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
def transfer_money(
    transfer_data: TransferRequest,
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict:
    """Transfer money between accounts."""
    user_id = get_current_user_id(authorization)
    acc_service = AccountService(db)
    from_account = acc_service.get_account(transfer_data.from_account_id)

    if not from_account or from_account["holder_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        transfer_service = TransferService(db)
        transfer = transfer_service.transfer_money(
            from_account_id=transfer_data.from_account_id,
            to_account_id=transfer_data.to_account_id,
            amount=transfer_data.amount,
            description=transfer_data.description,
        )
        db.commit()
        return transfer
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/accounts/{account_id}/transfers/outgoing", response_model=List[dict])
def get_outgoing_transfers(
    account_id: UUID,
    skip: int = 0,
    limit: int = 50,
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> List[dict]:
    """Get outgoing transfers for an account."""
    user_id = get_current_user_id(authorization)
    acc_service = AccountService(db)
    account = acc_service.get_account(account_id)

    if not account or account["holder_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    transfer_service = TransferService(db)
    return transfer_service.get_outgoing_transfers(account_id, skip, limit)


@router.get("/accounts/{account_id}/transfers/incoming", response_model=List[dict])
def get_incoming_transfers(
    account_id: UUID,
    skip: int = 0,
    limit: int = 50,
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> List[dict]:
    """Get incoming transfers for an account."""
    user_id = get_current_user_id(authorization)
    acc_service = AccountService(db)
    account = acc_service.get_account(account_id)

    if not account or account["holder_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    transfer_service = TransferService(db)
    return transfer_service.get_incoming_transfers(account_id, skip, limit)


# Card Endpoints
@router.post(
    "/cards",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_card(
    card_data: CardCreate,
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict:
    """Create a new card."""
    user_id = get_current_user_id(authorization)

    try:
        service = CardService(db)
        card = service.create_card(
            holder_id=user_id,
            account_id=card_data.account_id,
            card_type=card_data.card_type.value,
        )
        db.commit()
        return card
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/cards", response_model=List[CardResponse])
def list_cards(authorization: str = Header(default=""), db: Session = Depends(get_db)) -> List[dict]:
    """List all cards for the current user."""
    user_id = get_current_user_id(authorization)
    service = CardService(db)
    return service.get_cards_for_holder(user_id)


@router.post("/cards/{card_id}/block", status_code=status.HTTP_200_OK)
def block_card(
    card_id: UUID,
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict:
    """Block a card."""
    user_id = get_current_user_id(authorization)

    try:
        service = CardService(db)
        card_service_instance = CardService(db)
        card = card_service_instance.block_card(card_id)

        if card["holder_id"] != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        db.commit()
        return card
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


# Statement Endpoints
@router.post(
    "/accounts/{account_id}/statements",
    response_model=StatementResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_statement(
    account_id: UUID,
    statement_request: StatementRequest,
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict:
    """Generate a statement for an account."""
    user_id = get_current_user_id(authorization)
    acc_service = AccountService(db)
    account = acc_service.get_account(account_id)

    if not account or account["holder_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        service = StatementService(db)
        statement = service.generate_statement(
            account_id=account_id,
            start_date=statement_request.start_date,
            end_date=statement_request.end_date,
        )
        db.commit()
        return statement
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/accounts/{account_id}/statements", response_model=List[StatementResponse])
def get_statements(
    account_id: UUID,
    skip: int = 0,
    limit: int = 50,
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> List[dict]:
    """Get statements for an account."""
    user_id = get_current_user_id(authorization)
    acc_service = AccountService(db)
    account = acc_service.get_account(account_id)

    if not account or account["holder_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    service = StatementService(db)
    return service.get_statements(account_id, skip, limit)


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}
