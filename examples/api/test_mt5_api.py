"""
Example client for the MT5 REST API
Demonstrates how to authenticate and interact with the API
"""
import requests
from typing import Optional
import json


class MT5ApiClient:
    """Client for interacting with MT5 REST API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the MT5 REST API
        """
        self.base_url = base_url.rstrip("/")
        self.session_token: Optional[str] = None
        self.session = requests.Session()
    
    def login(self, account_number: int, password: str, server: str, 
              path: Optional[str] = None) -> dict:
        """
        Login to MT5 via REST API
        
        Args:
            account_number: MT5 account number
            password: MT5 password
            server: MT5 server name
            path: Optional path to MT5 terminal
        
        Returns:
            Login response with session token
        """
        url = f"{self.base_url}/api/v1/login"
        payload = {
            "account_number": account_number,
            "password": password,
            "server": server
        }
        
        if path:
            payload["path"] = path
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        self.session_token = data["session_token"]
        
        # Set authorization header for future requests
        self.session.headers.update({
            "Authorization": f"Bearer {self.session_token}"
        })
        
        print(f"✓ Logged in to account {data['account_number']} on {data['server']}")
        print(f"  Session expires in {data['expires_in']} seconds")
        
        return data
    
    def logout(self) -> dict:
        """Logout and invalidate session"""
        url = f"{self.base_url}/api/v1/logout"
        response = self.session.post(url)
        response.raise_for_status()
        
        self.session_token = None
        self.session.headers.pop("Authorization", None)
        
        return response.json()
    
    def get_account_info(self) -> dict:
        """Get account information"""
        url = f"{self.base_url}/api/v1/account"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_balance(self) -> float:
        """Get account balance"""
        url = f"{self.base_url}/api/v1/balance"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()["balance"]
    
    def get_equity(self) -> float:
        """Get account equity"""
        url = f"{self.base_url}/api/v1/equity"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()["equity"]
    
    def get_positions(self) -> list:
        """Get all open positions"""
        url = f"{self.base_url}/api/v1/positions"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_orders(self) -> dict:
        """Get all pending orders"""
        url = f"{self.base_url}/api/v1/orders"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_snapshot(self) -> dict:
        """Get complete account snapshot"""
        url = f"{self.base_url}/api/v1/snapshot"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_history(self, from_days_ago: int = 7) -> dict:
        """Get trading history"""
        url = f"{self.base_url}/api/v1/history"
        params = {"from_days_ago": from_days_ago}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_symbol_info(self, symbol: str) -> dict:
        """Get symbol information"""
        url = f"{self.base_url}/api/v1/symbol/{symbol}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_server_time(self) -> dict:
        """Get broker server time"""
        url = f"{self.base_url}/api/v1/server-time"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()


def example_usage():
    """Example usage of the MT5 API client"""
    
    # Initialize client
    client = MT5ApiClient(base_url="http://localhost:8000")
    
    # Login credentials (replace with your actual credentials)
    ACCOUNT_NUMBER = 12345678  # Your MT5 account number
    PASSWORD = "your_password"  # Your MT5 password
    SERVER = "MetaQuotes-Demo"  # Your broker server
    
    try:
        # 1. Login
        print("\n" + "="*60)
        print("1. LOGGING IN TO MT5")
        print("="*60)
        login_response = client.login(ACCOUNT_NUMBER, PASSWORD, SERVER)
        
        # 2. Get account info
        print("\n" + "="*60)
        print("2. ACCOUNT INFORMATION")
        print("="*60)
        account = client.get_account_info()
        print(f"Account: {account['login']}")
        print(f"Server: {account['server']}")
        print(f"Company: {account['company']}")
        print(f"Currency: {account['currency']}")
        print(f"Leverage: 1:{account['leverage']}")
        print(f"Balance: ${account['balance']:,.2f}")
        print(f"Equity: ${account['equity']:,.2f}")
        print(f"Margin Used: ${account['margin']:,.2f}")
        print(f"Margin Free: ${account['margin_free']:,.2f}")
        print(f"Profit: ${account['profit']:,.2f}")
        
        # 3. Get positions
        print("\n" + "="*60)
        print("3. OPEN POSITIONS")
        print("="*60)
        positions = client.get_positions()
        if positions:
            for pos in positions:
                print(f"Ticket: {pos['ticket']}")
                print(f"  Symbol: {pos['symbol']}")
                print(f"  Type: {'BUY' if pos['type'] == 0 else 'SELL'}")
                print(f"  Volume: {pos['volume']}")
                print(f"  Entry: {pos['price_open']:.5f}")
                print(f"  Current: {pos['price_current']:.5f}")
                print(f"  Profit: ${pos['profit']:.2f}")
                print()
        else:
            print("No open positions")
        
        # 4. Get account snapshot
        print("\n" + "="*60)
        print("4. ACCOUNT SNAPSHOT")
        print("="*60)
        snapshot = client.get_snapshot()
        print(f"Timestamp: {snapshot['timestamp']}")
        print(f"Balance: ${snapshot['balance']:,.2f}")
        print(f"Equity: ${snapshot['equity']:,.2f}")
        print(f"Total P/L: ${snapshot['total_profit_loss']:,.2f}")
        print(f"Day Start Balance: ${snapshot['day_start_balance']:,.2f}")
        print(f"Day Start Equity: ${snapshot['day_start_equity']:,.2f}")
        print(f"Open Positions: {len(snapshot['positions'])}")
        
        # 5. Get symbol info
        print("\n" + "="*60)
        print("5. SYMBOL INFORMATION (EURUSD)")
        print("="*60)
        try:
            symbol = client.get_symbol_info("EURUSD")
            print(f"Symbol: {symbol['name']}")
            print(f"Bid: {symbol['bid']:.5f}")
            print(f"Ask: {symbol['ask']:.5f}")
            print(f"Spread: {symbol['spread']}")
            print(f"Contract Size: {symbol['trade_contract_size']}")
        except Exception as e:
            print(f"Could not fetch symbol info: {e}")
        
        # 6. Get server time
        print("\n" + "="*60)
        print("6. SERVER TIME")
        print("="*60)
        server_time = client.get_server_time()
        print(f"Server Time: {server_time['server_time']}")
        print(f"Timezone Offset: UTC{server_time['timezone_offset']:+d}")
        
        # 7. Get history
        print("\n" + "="*60)
        print("7. TRADING HISTORY (Last 7 Days)")
        print("="*60)
        history = client.get_history(from_days_ago=7)
        print(f"Period: {history['from_date']} to {history['to_date']}")
        print(f"Total Deals: {history['deals_count']}")
        
        # 8. Logout
        print("\n" + "="*60)
        print("8. LOGGING OUT")
        print("="*60)
        logout_response = client.logout()
        print(f"✓ {logout_response['message']}")
        
    except requests.exceptions.HTTPError as e:
        print(f"\n✗ HTTP Error: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"  Detail: {error_detail.get('detail', 'Unknown error')}")
            except:
                print(f"  Response: {e.response.text}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    print("MT5 REST API Client Example")
    print("="*60)
    print("\nBefore running this example:")
    print("1. Start the MT5 API server: python -m src.mt5_api")
    print("2. Update the credentials in this file")
    print("3. Ensure MT5 terminal is installed and accessible")
    print()
    
    # Uncomment to run the example
    # example_usage()
    
    print("\nUncomment 'example_usage()' after updating credentials to run the example.")
