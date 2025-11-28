# MT5 REST API - Getting Started

Welcome to the MT5 REST API! This guide will help you get started in just a few minutes.

## What is this?

The MT5 REST API allows you to connect to MetaTrader 5 accounts remotely using standard HTTP requests. You can:
- Login with your MT5 credentials (account, password, server)
- Get account information (balance, equity, margin)
- View open positions and orders
- Access trading history
- Monitor multiple accounts simultaneously

## Prerequisites

- **Python 3.8+** installed
- **MetaTrader 5** terminal installed
- **MT5 Account** credentials (account number, password, server)

## Quick Setup (3 Steps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi` - Web framework
- `uvicorn` - Web server
- `pydantic` - Data validation
- `MetaTrader5` - MT5 Python API
- `python-multipart` - Form data support

### Step 2: Start the Server

```bash
python run_mt5_api.py
```

You should see:
```
MT5 REST API Server
Starting server on http://localhost:8000
API Documentation available at http://localhost:8000/docs
```

### Step 3: Test It Out

#### Option A: Web Interface (Easiest)

1. Open `examples/mt5_api_client.html` in your browser
2. Enter your MT5 account number, password, and server
3. Click "Login"
4. Click any button to test different API features

#### Option B: Interactive API Docs

1. Open http://localhost:8000/docs in your browser
2. Click on the `POST /api/v1/login` endpoint
3. Click "Try it out"
4. Enter your credentials
5. Click "Execute"
6. Copy the `session_token` from the response
7. Click "Authorize" at the top and paste your token
8. Now you can test all other endpoints!

#### Option C: Python Client

```python
from examples.test_mt5_api import MT5ApiClient

# Create client
client = MT5ApiClient()

# Login
client.login(
    account_number=12345678,      # Your account number
    password="your_password",      # Your password
    server="YourBroker-Demo"       # Your server
)

# Get account info
account = client.get_account_info()
print(f"Balance: ${account['balance']:,.2f}")
print(f"Equity: ${account['equity']:,.2f}")

# Get positions
positions = client.get_positions()
for pos in positions:
    print(f"Position: {pos['symbol']} | Profit: ${pos['profit']:.2f}")

# Logout
client.logout()
```

## Common Server Names

Your MT5 server name might look like:
- `MetaQuotes-Demo` (demo account)
- `YourBroker-Live` (live account)
- `YourBroker-Server` (varies by broker)

To find your server:
1. Open MT5 terminal
2. File → Login to Trade Account
3. The server is shown in the server dropdown

## API Endpoints

Once logged in, you can use these endpoints:

### Account Information
- `GET /api/v1/account` - Full account details
- `GET /api/v1/balance` - Current balance
- `GET /api/v1/equity` - Current equity

### Trading Data
- `GET /api/v1/positions` - Open positions
- `GET /api/v1/orders` - Pending orders
- `GET /api/v1/snapshot` - Complete snapshot

### Historical Data
- `GET /api/v1/history?from_days_ago=7` - Last 7 days of trades

### Market Data
- `GET /api/v1/symbol/EURUSD` - Get symbol info
- `GET /api/v1/server-time` - Broker server time

### Session Management
- `POST /api/v1/login` - Login
- `POST /api/v1/logout` - Logout

## cURL Examples

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{
    "account_number": 12345678,
    "password": "your_password",
    "server": "MetaQuotes-Demo"
  }'
```

Response:
```json
{
  "session_token": "abc123xyz...",
  "account_number": 12345678,
  "server": "MetaQuotes-Demo",
  "expires_in": 86400
}
```

### Get Account Info
```bash
curl -X GET "http://localhost:8000/api/v1/account" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

### Get Positions
```bash
curl -X GET "http://localhost:8000/api/v1/positions" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

## JavaScript Example

```javascript
// Login
const response = await fetch('http://localhost:8000/api/v1/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    account_number: 12345678,
    password: 'your_password',
    server: 'MetaQuotes-Demo'
  })
});

const { session_token } = await response.json();

// Get account
const accountResponse = await fetch('http://localhost:8000/api/v1/account', {
  headers: {'Authorization': `Bearer ${session_token}`}
});

const account = await accountResponse.json();
console.log('Balance:', account.balance);
```

## Troubleshooting

### "Connection refused"
→ Start the server: `python run_mt5_api.py`

### "Failed to connect to MT5"
→ Check your credentials and server name
→ Make sure MT5 terminal is installed
→ Close MT5 if it's running with a different account

### "Invalid or expired session token"
→ Login again (tokens expire after 24 hours)

### "Module not found"
→ Install dependencies: `pip install -r requirements.txt`

### Port already in use
→ Another application is using port 8000
→ Modify `run_mt5_api.py` to use a different port

## Security Notes

- **Never share your session token** - it gives full access to your account data
- **Use HTTPS in production** - credentials are sent over the network
- **Tokens expire after 24 hours** - login again after expiry
- **Logout when done** - explicitly logout to invalidate the token

## Next Steps

1. **Read the full documentation**: `docs/MT5_REST_API.md`
2. **Try the web client**: Open `examples/mt5_api_client.html`
3. **Test all endpoints**: Use http://localhost:8000/docs
4. **Build your integration**: Use the Python client as a reference
5. **Review security**: See production security recommendations

## Use Cases

### Personal Trading Dashboard
Monitor your trading account from anywhere:
```python
client = MT5ApiClient()
client.login(account, password, server)

# Check daily
snapshot = client.get_snapshot()
daily_pl = snapshot['total_profit_loss']
print(f"Today's P/L: ${daily_pl:,.2f}")
```

### Multi-Account Monitoring
Monitor multiple accounts:
```python
accounts = [
    {'account': 123, 'password': 'pass1', 'server': 'Broker1'},
    {'account': 456, 'password': 'pass2', 'server': 'Broker2'}
]

for acc in accounts:
    client = MT5ApiClient()
    client.login(acc['account'], acc['password'], acc['server'])
    balance = client.get_balance()
    print(f"Account {acc['account']}: ${balance:,.2f}")
    client.logout()
```

### Trading Alerts
Set up alerts for position changes:
```python
import time

client = MT5ApiClient()
client.login(account, password, server)

while True:
    positions = client.get_positions()
    
    for pos in positions:
        if pos['profit'] < -100:
            print(f"⚠️ Large loss on {pos['symbol']}: ${pos['profit']:.2f}")
    
    time.sleep(60)  # Check every minute
```

## Support

- **Quick Start**: This file
- **Full Documentation**: `docs/MT5_REST_API.md`
- **API Reference**: http://localhost:8000/docs
- **Examples**: `examples/` directory

## What's Next?

Once you're comfortable with the basics:
1. Explore all API endpoints in the documentation
2. Build custom integrations for your needs
3. Consider security hardening for production use
4. Set up monitoring and alerts
5. Create custom dashboards or mobile apps

Happy trading! 🚀
