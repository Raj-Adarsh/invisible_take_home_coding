#!/usr/bin/env python3
"""
Banking Service Test Client
Demonstrates the complete flow of the Banking REST Service API
"""

import requests
import json
from typing import Dict, Any
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class BankingServiceTestClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.api_prefix = API_PREFIX
        self.token = None
        self.user_id = None
        self.account_id = None
        self.session = requests.Session()
    
    def get_url(self, path: str, include_prefix: bool = True) -> str:
        """Build full URL with optional API prefix"""
        if include_prefix:
            return f"{self.base_url}{self.api_prefix}{path}"
        return f"{self.base_url}{path}"

    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
        print(f"{text.center(60)}")
        print(f"{'='*60}{Colors.ENDC}\n")

    def print_step(self, step: int, text: str):
        """Print a formatted step"""
        print(f"{Colors.CYAN}[Step {step}] {Colors.BOLD}{text}{Colors.ENDC}")

    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

    def print_request(self, method: str, endpoint: str, data: Dict = None):
        """Print request details"""
        print(f"{Colors.BLUE}→ {method} {self.base_url}{endpoint}{Colors.ENDC}")
        if data:
            print(f"  Payload: {Colors.YELLOW}{json.dumps(data, indent=2)}{Colors.ENDC}")

    def print_response(self, response: requests.Response):
        """Print response details"""
        try:
            data = response.json()
            status = Colors.GREEN if response.status_code < 400 else Colors.RED
            print(f"{status}← Status {response.status_code}{Colors.ENDC}")
            print(f"  Response: {Colors.YELLOW}{json.dumps(data, indent=2)}{Colors.ENDC}")
            return data
        except json.JSONDecodeError:
            print(f"{Colors.RED}← Status {response.status_code}{Colors.ENDC}")
            print(f"  Response: {response.text}")
            return None

    def check_health(self):
        """Check API health"""
        self.print_step(0, "Checking API Health")
        self.print_request("GET", "/health")
        
        try:
            response = self.session.get(self.get_url("/health", include_prefix=False), timeout=5)
            self.print_response(response)
            
            if response.status_code == 200:
                self.print_success("API is healthy and running")
                return True
            else:
                self.print_error("API health check failed")
                return False
        except requests.exceptions.ConnectionError:
            self.print_error(f"Cannot connect to API at {self.base_url}")
            return False

    def signup_user(self, email: str, password: str, full_name: str) -> bool:
        """Register a new user"""
        self.print_step(1, "User Signup")
        
        # Split full_name into first and last name
        name_parts = full_name.split() if full_name else ["Test", "User"]
        first_name = name_parts[0]
        last_name = name_parts[-1] if len(name_parts) > 1 else name_parts[0]
        
        payload = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name
        }
        
        self.print_request("POST", "/auth/signup", payload)
        response = self.session.post(self.get_url("/auth/signup"), json=payload)
        data = self.print_response(response)
        
        if response.status_code in [200, 201] and data:
            self.user_id = data.get("id")
            self.print_success(f"User registered: {email} (ID: {self.user_id})")
            return True
        else:
            self.print_error("Signup failed")
            return False

    def login_user(self, email: str, password: str) -> bool:
        """Login user and get authentication token"""
        self.print_step(2, "User Login")
        
        payload = {
            "email": email,
            "password": password
        }
        
        self.print_request("POST", "/auth/login", payload)
        response = self.session.post(self.get_url("/auth/login"), json=payload)
        data = self.print_response(response)
        
        if response.status_code == 200 and data:
            self.token = data.get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            self.print_success(f"Login successful - Token obtained")
            return True
        else:
            self.print_error("Login failed")
            return False

    def get_current_user(self) -> bool:
        """Retrieve current user information"""
        self.print_step(3, "Get Current User Info")
        
        self.print_request("GET", "/auth/me")
        response = self.session.get(self.get_url("/auth/me"))
        data = self.print_response(response)
        
        if response.status_code == 200 and data:
            self.print_success(f"Retrieved user: {data.get('full_name')}")
            return True
        else:
            self.print_error("Failed to get user info")
            return False

    def create_account(self, account_type: str = "SAVINGS", initial_balance: float = 1000.00) -> bool:
        """Create a new bank account"""
        self.print_step(4, "Create Bank Account")
        
        payload = {
            "account_type": account_type,
            "initial_balance": initial_balance
        }
        
        self.print_request("POST", "/accounts", payload)
        response = self.session.post(self.get_url("/accounts"), json=payload)
        data = self.print_response(response)
        
        if response.status_code == 200 and data:
            self.account_id = data.get("id")
            account_number = data.get("account_number")
            self.print_success(f"Account created: {account_number} (ID: {self.account_id})")
            return True
        else:
            self.print_error("Account creation failed")
            return False

    def get_accounts(self) -> bool:
        """List all user accounts"""
        self.print_step(5, "List All Accounts")
        
        self.print_request("GET", "/accounts")
        response = self.session.get(self.get_url("/accounts"))
        data = self.print_response(response)
        
        if response.status_code == 200 and data:
            accounts = data if isinstance(data, list) else [data]
            self.print_success(f"Retrieved {len(accounts)} account(s)")
            return True
        else:
            self.print_error("Failed to retrieve accounts")
            return False

    def get_account_details(self, account_id: str = None) -> bool:
        """Get details of a specific account"""
        self.print_step(6, "Get Account Details")
        
        account_id = account_id or self.account_id
        self.print_request("GET", f"/accounts/{account_id}")
        response = self.session.get(self.get_url("/accounts/{account_id}"))
        data = self.print_response(response)
        
        if response.status_code == 200 and data:
            balance = data.get("balance")
            self.print_success(f"Account Balance: ${balance}")
            return True
        else:
            self.print_error("Failed to get account details")
            return False

    def deposit_money(self, amount: float = 500.00, account_id: str = None) -> bool:
        """Deposit money to account"""
        self.print_step(7, "Deposit Money")
        
        account_id = account_id or self.account_id
        payload = {
            "account_id": account_id,
            "amount": amount,
            "description": "Test deposit"
        }
        
        self.print_request("POST", "/transactions/deposit", payload)
        response = self.session.post(self.get_url(f"/accounts/{self.account_id}/transactions/deposit"), json=payload)
        data = self.print_response(response)
        
        if response.status_code == 200 and data:
            self.print_success(f"Deposit successful: ${amount}")
            return True
        else:
            self.print_error("Deposit failed")
            return False

    def withdraw_money(self, amount: float = 100.00, account_id: str = None) -> bool:
        """Withdraw money from account"""
        self.print_step(8, "Withdraw Money")
        
        account_id = account_id or self.account_id
        payload = {
            "account_id": account_id,
            "amount": amount,
            "description": "Test withdrawal"
        }
        
        self.print_request("POST", "/transactions/withdrawal", payload)
        response = self.session.post(self.get_url(f"/accounts/{self.account_id}/transactions/withdrawal"), json=payload)
        data = self.print_response(response)
        
        if response.status_code == 200 and data:
            self.print_success(f"Withdrawal successful: ${amount}")
            return True
        else:
            self.print_error("Withdrawal failed")
            return False

    def get_transactions(self, account_id: str = None) -> bool:
        """Get transaction history"""
        self.print_step(9, "Get Transaction History")
        
        account_id = account_id or self.account_id
        self.print_request("GET", f"/accounts/{account_id}/transactions")
        response = self.session.get(self.get_url("/accounts/{account_id}/transactions"))
        data = self.print_response(response)
        
        if response.status_code == 200 and data:
            transactions = data if isinstance(data, list) else [data]
            self.print_success(f"Retrieved {len(transactions)} transaction(s)")
            return True
        else:
            self.print_error("Failed to retrieve transactions")
            return False

    def create_card(self, account_id: str = None, card_type: str = "debit") -> bool:
        """Create a new card"""
        self.print_step(10, "Create Card")
        
        account_id = account_id or self.account_id
        payload = {
            "account_id": account_id,
            "card_type": card_type
        }
        
        self.print_request("POST", "/cards", payload)
        response = self.session.post(self.get_url("/cards"), json=payload)
        data = self.print_response(response)
        
        if response.status_code == 200 and data:
            card_number = data.get("card_number", "****")
            self.print_success(f"Card created: {card_number[-4:]}")
            return True
        else:
            self.print_error("Card creation failed")
            return False

    def get_cards(self) -> bool:
        """Get all user cards"""
        self.print_step(11, "Get User Cards")
        
        self.print_request("GET", "/cards")
        response = self.session.get(self.get_url("/cards"))
        data = self.print_response(response)
        
        if response.status_code == 200 and data:
            cards = data if isinstance(data, list) else [data]
            self.print_success(f"Retrieved {len(cards)} card(s)")
            return True
        else:
            self.print_error("Failed to retrieve cards")
            return False

    def generate_statement(self, account_id: str = None) -> bool:
        """Generate account statement"""
        self.print_step(12, "Generate Statement")
        
        account_id = account_id or self.account_id
        payload = {
            "account_id": account_id,
            "start_date": "2024-01-01",
            "end_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        self.print_request("POST", "/statements", payload)
        response = self.session.post(self.get_url(f"/accounts/{self.account_id}/statements"), json=payload)
        data = self.print_response(response)
        
        if response.status_code == 200 and data:
            self.print_success("Statement generated successfully")
            return True
        else:
            self.print_error("Statement generation failed")
            return False

    def run_full_flow(self):
        """Run complete test flow"""
        self.print_header("Banking Service Test Client - Complete Flow")
        
        # Test data
        test_email = f"testuser_{datetime.now().timestamp():.0f}@example.com"
        test_password = "TestPassword123!"
        test_name = "Test User"
        
        steps = [
            ("Health Check", self.check_health),
            ("Signup", lambda: self.signup_user(test_email, test_password, test_name)),
            ("Login", lambda: self.login_user(test_email, test_password)),
            ("Get Current User", self.get_current_user),
            ("Create Account", self.create_account),
            ("Get Accounts", self.get_accounts),
            ("Get Account Details", self.get_account_details),
            ("Deposit Money", self.deposit_money),
            ("Withdraw Money", self.withdraw_money),
            ("Get Transactions", self.get_transactions),
            ("Create Card", self.create_card),
            ("Get Cards", self.get_cards),
            ("Generate Statement", self.generate_statement),
        ]
        
        results = []
        for step_name, step_func in steps:
            try:
                result = step_func()
                results.append((step_name, result))
            except Exception as e:
                self.print_error(f"Exception in {step_name}: {str(e)}")
                results.append((step_name, False))
        
        # Print summary
        self.print_header("Test Summary")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"{Colors.BOLD}Results:{Colors.ENDC}")
        for step_name, result in results:
            status = f"{Colors.GREEN}✓ PASS{Colors.ENDC}" if result else f"{Colors.RED}✗ FAIL{Colors.ENDC}"
            print(f"  {step_name:<30} {status}")
        
        print(f"\n{Colors.BOLD}Overall: {Colors.GREEN}{passed}/{total} tests passed{Colors.ENDC}")
        
        if passed == total:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed!{Colors.ENDC}")
        else:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  {total - passed} test(s) failed{Colors.ENDC}")

    def run_api_explorer(self):
        """Interactive API explorer mode"""
        self.print_header("Banking Service - Interactive API Explorer")
        
        menu_options = {
            "1": ("Health Check", self.check_health),
            "2": ("Signup", lambda: self.signup_user(
                input("Email: "),
                input("Password: "),
                input("Full Name: ")
            )),
            "3": ("Login", lambda: self.login_user(
                input("Email: "),
                input("Password: ")
            )),
            "4": ("Get Current User", self.get_current_user),
            "5": ("Create Account", lambda: self.create_account(
                input("Account Type (SAVINGS/CHECKING): ") or "SAVINGS",
                float(input("Initial Balance: ") or 1000)
            )),
            "6": ("Get Accounts", self.get_accounts),
            "7": ("Get Account Details", self.get_account_details),
            "8": ("Deposit", lambda: self.deposit_money(
                float(input("Amount: "))
            )),
            "9": ("Withdraw", lambda: self.withdraw_money(
                float(input("Amount: "))
            )),
            "10": ("Transactions", self.get_transactions),
            "11": ("Create Card", self.create_card),
            "12": ("Get Cards", self.get_cards),
            "13": ("Generate Statement", self.generate_statement),
            "14": ("Run Full Test Flow", self.run_full_flow),
            "0": ("Exit", None),
        }
        
        while True:
            print(f"\n{Colors.BOLD}Available Options:{Colors.ENDC}")
            for key, (name, _) in menu_options.items():
                print(f"  {key}. {name}")
            
            choice = input(f"\n{Colors.CYAN}Select option: {Colors.ENDC}")
            
            if choice not in menu_options:
                self.print_error("Invalid option")
                continue
            
            name, func = menu_options[choice]
            
            if choice == "0":
                print(f"\n{Colors.GREEN}Goodbye!{Colors.ENDC}\n")
                break
            
            try:
                func()
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Cancelled{Colors.ENDC}")
            except Exception as e:
                self.print_error(f"Error: {str(e)}")


def main():
    """Main entry point"""
    import sys
    
    client = BankingServiceTestClient()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--flow":
            client.run_full_flow()
        elif sys.argv[1] == "--interactive":
            client.run_api_explorer()
        else:
            print(f"Usage: {sys.argv[0]} [--flow|--interactive]")
            print(f"  --flow:        Run complete test flow")
            print(f"  --interactive: Interactive API explorer")
    else:
        # Default: run full flow
        client.run_full_flow()


if __name__ == "__main__":
    main()
