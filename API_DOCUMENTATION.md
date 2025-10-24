# Banking Service API Documentation

## Overview

The Banking Service API provides a comprehensive REST interface for managing banking operations including user authentication, account management, transactions, transfers, cards, and statements.

**Base URL:** `http://localhost:8000/api/v1`

**API Version:** 0.1.0

## Documentation

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc
- **OpenAPI JSON:** http://localhost:8000/api/openapi.json

## Authentication

All endpoints (except `/auth/signup` and `/auth/login`) require JWT authentication via the `Authorization` header.

### Authentication Header Format
```
Authorization: Bearer <access_token>
```

### Token Details
- **Algorithm:** HS256
- **Expiration:** 30 minutes
- **Secret Key:** Configured via `SECRET_KEY` environment variable

## Error Handling

The API uses standard HTTP status codes and returns error details in the response body.

### Common Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists or conflict |
| 422 | Unprocessable Entity | Validation error |
| 500 | Server Error | Internal server error |

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Authentication Endpoints

### 1. User Signup

**Endpoint:** `POST /auth/signup`

**Description:** Register a new user account

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one digit
- At least one special character (!@#$%^&*)

**Success Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Response (409):**
```json
{
  "detail": "Email already registered"
}
```

### 2. User Login

**Endpoint:** `POST /auth/login`

**Description:** Authenticate user and receive access token

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Response (401):**
```json
{
  "detail": "Invalid credentials"
}
```

### 3. Get Current User

**Endpoint:** `GET /auth/me`

**Description:** Retrieve current authenticated user information

**Authentication:** Required ✓

**Success Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Account Endpoints

### 1. Create Account

**Endpoint:** `POST /accounts`

**Description:** Create a new bank account for the authenticated user

**Authentication:** Required ✓

**Request Body:**
```json
{
  "account_type": "SAVINGS",
  "initial_balance": 1000.00
}
```

**Account Types:**
- `SAVINGS` - Savings account
- `CHECKING` - Checking account
- `CREDIT` - Credit account
- `INVESTMENT` - Investment account

**Success Response (200):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "account_number": "ACC00123456789",
  "account_type": "SAVINGS",
  "holder_id": "550e8400-e29b-41d4-a716-446655440000",
  "balance": 1000.00,
  "status": "ACTIVE",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2. List All Accounts

**Endpoint:** `GET /accounts`

**Description:** Retrieve all accounts for the authenticated user

**Authentication:** Required ✓

**Success Response (200):**
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "account_number": "ACC00123456789",
    "account_type": "SAVINGS",
    "balance": 1500.00,
    "status": "ACTIVE",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### 3. Get Account Details

**Endpoint:** `GET /accounts/{account_id}`

**Description:** Retrieve detailed information about a specific account

**Authentication:** Required ✓

**URL Parameters:**
- `account_id` (string, UUID): The account ID

**Success Response (200):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "account_number": "ACC00123456789",
  "account_type": "SAVINGS",
  "holder_id": "550e8400-e29b-41d4-a716-446655440000",
  "balance": 1500.00,
  "status": "ACTIVE",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:22:00Z"
}
```

## Transaction Endpoints

### 1. Deposit Money

**Endpoint:** `POST /transactions/deposit`

**Description:** Deposit money into an account

**Authentication:** Required ✓

**Request Body:**
```json
{
  "account_id": "660e8400-e29b-41d4-a716-446655440001",
  "amount": 500.00,
  "description": "Monthly salary deposit"
}
```

**Amount Validation:**
- Must be positive (> 0)
- Maximum 2 decimal places

**Success Response (200):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "account_id": "660e8400-e29b-41d4-a716-446655440001",
  "transaction_type": "DEPOSIT",
  "amount": 500.00,
  "status": "COMPLETED",
  "description": "Monthly salary deposit",
  "balance_after": 2000.00,
  "created_at": "2024-01-15T14:22:00Z"
}
```

### 2. Withdraw Money

**Endpoint:** `POST /transactions/withdrawal`

**Description:** Withdraw money from an account

**Authentication:** Required ✓

**Request Body:**
```json
{
  "account_id": "660e8400-e29b-41d4-a716-446655440001",
  "amount": 100.00,
  "description": "ATM withdrawal"
}
```

**Error Response - Insufficient Funds (400):**
```json
{
  "detail": "Insufficient funds for withdrawal"
}
```

**Success Response (200):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "account_id": "660e8400-e29b-41d4-a716-446655440001",
  "transaction_type": "WITHDRAWAL",
  "amount": 100.00,
  "status": "COMPLETED",
  "description": "ATM withdrawal",
  "balance_after": 1900.00,
  "created_at": "2024-01-15T14:25:00Z"
}
```

### 3. Get Transaction History

**Endpoint:** `GET /accounts/{account_id}/transactions`

**Description:** Retrieve transaction history for an account

**Authentication:** Required ✓

**URL Parameters:**
- `account_id` (string, UUID): The account ID

**Query Parameters (Optional):**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Number of records to return (default: 10, max: 100)

**Success Response (200):**
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "account_id": "660e8400-e29b-41d4-a716-446655440001",
    "transaction_type": "DEPOSIT",
    "amount": 500.00,
    "status": "COMPLETED",
    "description": "Monthly salary deposit",
    "balance_after": 2000.00,
    "created_at": "2024-01-15T14:22:00Z"
  },
  {
    "id": "770e8400-e29b-41d4-a716-446655440003",
    "account_id": "660e8400-e29b-41d4-a716-446655440001",
    "transaction_type": "WITHDRAWAL",
    "amount": 100.00,
    "status": "COMPLETED",
    "description": "ATM withdrawal",
    "balance_after": 1900.00,
    "created_at": "2024-01-15T14:25:00Z"
  }
]
```

## Transfer Endpoints

### 1. Transfer Money

**Endpoint:** `POST /transfers`

**Description:** Transfer money between two accounts

**Authentication:** Required ✓

**Request Body:**
```json
{
  "from_account_id": "660e8400-e29b-41d4-a716-446655440001",
  "to_account_id": "660e8400-e29b-41d4-a716-446655440004",
  "amount": 250.00,
  "description": "Payment to friend"
}
```

**Transfer Rules:**
- Cannot transfer to the same account
- Must have sufficient funds
- Amount must be positive

**Success Response (200):**
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440005",
  "from_account_id": "660e8400-e29b-41d4-a716-446655440001",
  "to_account_id": "660e8400-e29b-41d4-a716-446655440004",
  "amount": 250.00,
  "status": "COMPLETED",
  "description": "Payment to friend",
  "created_at": "2024-01-15T14:30:00Z"
}
```

### 2. Get Outgoing Transfers

**Endpoint:** `GET /transfers/outgoing`

**Description:** Retrieve outgoing transfers from your accounts

**Authentication:** Required ✓

**Success Response (200):**
```json
[
  {
    "id": "880e8400-e29b-41d4-a716-446655440005",
    "from_account_id": "660e8400-e29b-41d4-a716-446655440001",
    "to_account_id": "660e8400-e29b-41d4-a716-446655440004",
    "amount": 250.00,
    "status": "COMPLETED",
    "description": "Payment to friend",
    "created_at": "2024-01-15T14:30:00Z"
  }
]
```

### 3. Get Incoming Transfers

**Endpoint:** `GET /transfers/incoming`

**Description:** Retrieve incoming transfers to your accounts

**Authentication:** Required ✓

**Success Response (200):**
```json
[
  {
    "id": "880e8400-e29b-41d4-a716-446655440006",
    "from_account_id": "660e8400-e29b-41d4-a716-446655440010",
    "to_account_id": "660e8400-e29b-41d4-a716-446655440001",
    "amount": 100.00,
    "status": "COMPLETED",
    "description": "Refund",
    "created_at": "2024-01-15T14:35:00Z"
  }
]
```

## Card Endpoints

### 1. Create Card

**Endpoint:** `POST /cards`

**Description:** Create a new card for an account

**Authentication:** Required ✓

**Request Body:**
```json
{
  "account_id": "660e8400-e29b-41d4-a716-446655440001",
  "card_type": "DEBIT"
}
```

**Card Types:**
- `DEBIT` - Debit card
- `CREDIT` - Credit card

**Success Response (200):**
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440007",
  "account_id": "660e8400-e29b-41d4-a716-446655440001",
  "card_number": "4532123456789012",
  "card_type": "DEBIT",
  "cvv": "123",
  "expiry_date": "12/26",
  "holder_name": "John Doe",
  "status": "ACTIVE",
  "created_at": "2024-01-15T14:40:00Z"
}
```

### 2. List All Cards

**Endpoint:** `GET /cards`

**Description:** Retrieve all cards for the authenticated user

**Authentication:** Required ✓

**Success Response (200):**
```json
[
  {
    "id": "990e8400-e29b-41d4-a716-446655440007",
    "account_id": "660e8400-e29b-41d4-a716-446655440001",
    "card_number": "****9012",
    "card_type": "DEBIT",
    "expiry_date": "12/26",
    "holder_name": "John Doe",
    "status": "ACTIVE",
    "created_at": "2024-01-15T14:40:00Z"
  }
]
```

### 3. Block Card

**Endpoint:** `POST /cards/{card_id}/block`

**Description:** Block/disable a card

**Authentication:** Required ✓

**URL Parameters:**
- `card_id` (string, UUID): The card ID

**Success Response (200):**
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440007",
  "status": "BLOCKED",
  "blocked_at": "2024-01-15T14:45:00Z"
}
```

## Statement Endpoints

### 1. Generate Statement

**Endpoint:** `POST /statements`

**Description:** Generate an account statement for a date range

**Authentication:** Required ✓

**Request Body:**
```json
{
  "account_id": "660e8400-e29b-41d4-a716-446655440001",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**Date Format:** `YYYY-MM-DD`

**Success Response (200):**
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440008",
  "account_id": "660e8400-e29b-41d4-a716-446655440001",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "opening_balance": 1500.00,
  "closing_balance": 1900.00,
  "total_debit": 100.00,
  "total_credit": 500.00,
  "transaction_count": 2,
  "generated_at": "2024-01-15T14:50:00Z"
}
```

### 2. Get Statements

**Endpoint:** `GET /accounts/{account_id}/statements`

**Description:** Retrieve all statements for an account

**Authentication:** Required ✓

**URL Parameters:**
- `account_id` (string, UUID): The account ID

**Query Parameters (Optional):**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Number of records to return (default: 10, max: 100)

**Success Response (200):**
```json
[
  {
    "id": "aa0e8400-e29b-41d4-a716-446655440008",
    "account_id": "660e8400-e29b-41d4-a716-446655440001",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "opening_balance": 1500.00,
    "closing_balance": 1900.00,
    "total_debit": 100.00,
    "total_credit": 500.00,
    "transaction_count": 2,
    "generated_at": "2024-01-15T14:50:00Z"
  }
]
```

## Health Check Endpoint

### Health Status

**Endpoint:** `GET /health`

**Description:** Check the health status of the API

**Success Response (200):**
```json
{
  "status": "healthy",
  "service": "banking-service",
  "version": "0.1.0"
}
```

## Code Examples

### Python with Requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Signup
signup_response = requests.post(
    f"{BASE_URL}/auth/signup",
    json={
        "email": "user@example.com",
        "password": "SecurePass123!",
        "full_name": "John Doe"
    }
)

# Login
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "user@example.com",
        "password": "SecurePass123!"
    }
)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create Account
account_response = requests.post(
    f"{BASE_URL}/accounts",
    json={
        "account_type": "SAVINGS",
        "initial_balance": 1000.00
    },
    headers=headers
)

print(account_response.json())
```

### JavaScript with Fetch

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// Signup
const signupResponse = await fetch(`${BASE_URL}/auth/signup`, {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    email: "user@example.com",
    password: "SecurePass123!",
    full_name: "John Doe"
  })
});

// Login
const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    email: "user@example.com",
    password: "SecurePass123!"
  })
});

const loginData = await loginResponse.json();
const token = loginData.access_token;

// Create Account
const accountResponse = await fetch(`${BASE_URL}/accounts`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  },
  body: JSON.stringify({
    account_type: "SAVINGS",
    initial_balance: 1000.00
  })
});

const account = await accountResponse.json();
console.log(account);
```

### cURL

```bash
# Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'

# Create Account (with token)
curl -X POST http://localhost:8000/api/v1/accounts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "account_type": "SAVINGS",
    "initial_balance": 1000.00
  }'
```

## Best Practices

1. **Token Management**
   - Store tokens securely (never expose in URLs or logs)
   - Refresh tokens before expiration (30 minutes)
   - Use HTTPS in production

2. **Error Handling**
   - Always check HTTP status codes
   - Parse error messages for debugging
   - Implement exponential backoff for retries

3. **Data Validation**
   - Validate input before sending requests
   - Handle validation errors from API responses
   - Use provided examples as templates

4. **Security**
   - Never hardcode credentials
   - Use environment variables for secrets
   - Implement request signing in production
   - Add rate limiting on client side

## Support

For issues or questions, please refer to:
- API Documentation: http://localhost:8000/api/docs
- GitHub Issues: [Your Repository URL]
- Email: support@bankingservice.com
