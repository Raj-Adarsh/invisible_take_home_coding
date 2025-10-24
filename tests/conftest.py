"""Test configuration and fixtures."""

import os
import sys
from decimal import Decimal
from uuid import uuid4

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.config import Settings, get_settings
from src.database import Base
from src.db import get_db
from src.main import app


# Override settings for testing
class TestSettings(Settings):
    """Test settings using in-memory SQLite database."""

    database_url: str = "sqlite:///:memory:"
    database_echo: bool = False
    debug: bool = True
    secret_key: str = "test-secret-key-32-characters!!!"
    app_env: str = "testing"

    class Config:
        """Pydantic configuration."""
        env_file = None  # Don't load from .env


# Create test settings instance
test_settings = TestSettings()


def get_test_settings() -> TestSettings:
    """Get test settings."""
    return test_settings


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="session")
def test_session_maker(test_engine):
    """Create a test session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session(test_session_maker):
    """Get a test database session."""
    session = test_session_maker()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def override_get_db(db_session):
    """Override the get_db dependency."""
    def _get_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def override_settings():
    """Override get_settings for all tests."""
    from src import config as config_module
    original_get_settings = config_module.get_settings
    config_module.get_settings = get_test_settings
    yield
    config_module.get_settings = original_get_settings


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def test_account_data():
    """Test account data."""
    return {
        "account_type": "Savings",
        "initial_balance": Decimal("1000.00"),
    }


@pytest.fixture
def test_transaction_data():
    """Test transaction data."""
    return {
        "amount": Decimal("100.00"),
        "description": "Test transaction",
    }
