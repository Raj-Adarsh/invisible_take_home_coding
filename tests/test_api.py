"""Integration tests for API endpoints."""

from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.security import create_access_token


@pytest.fixture
def client(override_get_db):
    """Get test client."""
    return TestClient(app)


class TestAuthenticationEndpoints:
    """Tests for authentication endpoints."""

    def test_signup_valid(self, client):
        """Test user signup."""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "first_name": "John",
                "last_name": "Doe",
            },
        )
        assert response.status_code == 201
        assert response.json()["email"] == "test@example.com"

    def test_signup_duplicate_email(self, client):
        """Test signup with duplicate email."""
        # First signup
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "first_name": "John",
                "last_name": "Doe",
            },
        )

        # Second signup with same email
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPass456!",
                "first_name": "Jane",
                "last_name": "Doe",
            },
        )
        assert response.status_code == 400

    def test_login_valid(self, client):
        """Test user login."""
        # Signup
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "first_name": "John",
                "last_name": "Doe",
            },
        )

        # Login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
            },
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        # Signup
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "first_name": "John",
                "last_name": "Doe",
            },
        )

        # Login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPass123!",
            },
        )
        assert response.status_code == 401


class TestAccountEndpoints:
    """Tests for account endpoints."""

    @pytest.fixture
    def auth_token(self, client):
        """Get authentication token."""
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "first_name": "John",
                "last_name": "Doe",
            },
        )
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
            },
        )
        return response.json()["access_token"]

    def test_create_account(self, client, auth_token):
        """Test account creation."""
        response = client.post(
            "/api/v1/accounts",
            json={
                "account_type": "Savings",
                "initial_balance": "1000.00",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201
        assert response.json()["account_type"] == "Savings"
        assert response.json()["balance"] == "1000.00"

    def test_list_accounts(self, client, auth_token):
        """Test listing accounts."""
        # Create accounts
        client.post(
            "/api/v1/accounts",
            json={
                "account_type": "Savings",
                "initial_balance": "1000.00",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        client.post(
            "/api/v1/accounts",
            json={
                "account_type": "Checking",
                "initial_balance": "500.00",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # List accounts
        response = client.get(
            "/api/v1/accounts",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_account(self, client, auth_token):
        """Test getting account details."""
        # Create account
        create_response = client.post(
            "/api/v1/accounts",
            json={
                "account_type": "Savings",
                "initial_balance": "1000.00",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        account_id = create_response.json()["id"]

        # Get account
        response = client.get(
            f"/api/v1/accounts/{account_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        assert response.json()["account_type"] == "Savings"


class TestTransactionEndpoints:
    """Tests for transaction endpoints."""

    @pytest.fixture
    def account_setup(self, client):
        """Setup account for transaction tests."""
        # Signup
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "first_name": "John",
                "last_name": "Doe",
            },
        )

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
            },
        )
        token = login_response.json()["access_token"]

        # Create account
        account_response = client.post(
            "/api/v1/accounts",
            json={
                "account_type": "Savings",
                "initial_balance": "1000.00",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        account_id = account_response.json()["id"]

        return token, account_id

    def test_deposit(self, client, account_setup):
        """Test deposit transaction."""
        token, account_id = account_setup

        response = client.post(
            f"/api/v1/accounts/{account_id}/transactions/deposit",
            json={
                "transaction_type": "deposit",
                "amount": "100.00",
                "description": "Test deposit",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        assert response.json()["transaction_type"] == "deposit"
        assert response.json()["amount"] == "100.00"

    def test_withdrawal(self, client, account_setup):
        """Test withdrawal transaction."""
        token, account_id = account_setup

        response = client.post(
            f"/api/v1/accounts/{account_id}/transactions/withdrawal",
            json={
                "transaction_type": "withdrawal",
                "amount": "50.00",
                "description": "Test withdrawal",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        assert response.json()["transaction_type"] == "withdrawal"
        assert response.json()["balance_after"] == "950.00"

    def test_withdrawal_insufficient_funds(self, client, account_setup):
        """Test withdrawal with insufficient funds."""
        token, account_id = account_setup

        response = client.post(
            f"/api/v1/accounts/{account_id}/transactions/withdrawal",
            json={
                "transaction_type": "withdrawal",
                "amount": "5000.00",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400

    def test_get_transactions(self, client, account_setup):
        """Test getting transactions."""
        token, account_id = account_setup

        # Create transactions
        client.post(
            f"/api/v1/accounts/{account_id}/transactions/deposit",
            json={
                "transaction_type": "deposit",
                "amount": "100.00",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        # Get transactions
        response = client.get(
            f"/api/v1/accounts/{account_id}/transactions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) >= 1


class TestCardEndpoints:
    """Tests for card endpoints."""

    @pytest.fixture
    def account_setup(self, client):
        """Setup account for card tests."""
        # Signup
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "first_name": "John",
                "last_name": "Doe",
            },
        )

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
            },
        )
        token = login_response.json()["access_token"]

        # Create account
        account_response = client.post(
            "/api/v1/accounts",
            json={
                "account_type": "Savings",
                "initial_balance": "1000.00",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        account_id = account_response.json()["id"]

        return token, account_id

    def test_create_card(self, client, account_setup):
        """Test card creation."""
        token, account_id = account_setup

        response = client.post(
            "/api/v1/cards",
            json={
                "card_type": "debit",
                "account_id": account_id,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        assert response.json()["card_type"] == "debit"
        assert response.json()["status"] == "active"

    def test_list_cards(self, client, account_setup):
        """Test listing cards."""
        token, account_id = account_setup

        # Create cards
        client.post(
            "/api/v1/cards",
            json={
                "card_type": "debit",
                "account_id": account_id,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        # List cards
        response = client.get(
            "/api/v1/cards",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) >= 1


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
