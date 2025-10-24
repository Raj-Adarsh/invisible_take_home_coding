"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from src.config import get_settings
from src.routes import router

settings = get_settings()

# Create FastAPI application with enhanced documentation
app = FastAPI(
    title="Banking Service API",
    description="""
# Banking REST Service

A comprehensive banking service with the following capabilities:

## Features
- **User Management**: Registration, authentication, and profile management
- **Accounts**: Create and manage multiple bank accounts
- **Transactions**: Deposit and withdrawal operations with balance tracking
- **Transfers**: Transfer money between accounts
- **Cards**: Create and manage debit/credit cards
- **Statements**: Generate account statements with transaction history

## Security
- JWT-based authentication with 30-minute token expiration
- bcrypt password hashing with salt
- Role-based access control
- HTTPS enforcement in production

## Database
- PostgreSQL (production) / SQLite (development)
- SQLAlchemy ORM with 6 entities
- Optimized with 13+ strategic indexes
- Transaction support for atomic operations

## API Standards
- RESTful API design
- Comprehensive error handling with HTTP status codes
- Request/response validation with Pydantic
- OpenAPI 3.0.0 specification with Swagger UI and ReDoc documentation
""",
    version="0.1.0",
    contact={
        "name": "Banking Service Support",
        "email": "support@bankingservice.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["localhost", "127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1", tags=["banking"])


@app.get("/")
def root() -> dict:
    """Root endpoint with service information."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "environment": settings.app_env,
        "documentation": {
            "swagger_ui": "/api/docs",
            "redoc": "/api/redoc",
            "openapi_json": "/api/openapi.json",
        },
        "status": "running",
    }


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """
    Health check endpoint.
    
    Returns the current status of the service.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "0.1.0",
    }
