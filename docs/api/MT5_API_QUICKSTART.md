# MT5 REST API - Quick Start Guide

Get up and running with the MT5 REST API in 5 minutes!

## Prerequisites

1. **MetaTrader 5 Terminal** installed on your system
2. **Python 3.8+** installed
3. **MT5 Account credentials** (account number, password, server)

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI (REST API framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- MetaTrader5 (MT5 Python API)
- Other required packages

### 2. Start the API Server

```bash
python run_mt5_api.py
```

You should see:
```
MT5 REST API Server
Starting server on http://localhost:8000
API Documentation available at http://localhost:8000/docs
```

### 3. Test the API

#### Option A: Using the Web Interface

1. Open `examples/mt5_api_client.html` in your web browser
2. Enter your MT5 credentials
3. Click "Login"
4. Use the buttons to test different API endpoints

#### Option B: Using the Python Client

```python
from examples.test_mt5_api import MT5ApiClient

# Initialize client
client = MT5ApiClient()

# Login
client.login(
    account_number=12345678,
    password="your_password",
    server="MetaQuotes-Demo"
)

# Get account info
account = client.get_account_info()
print(f"Balance: ${account['balance']:,.2f}")

# Logout
client.logout()
```

#### Option C: Using cURL

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{
    "account_number": 12345678,
    "password": "your_password",
    "server": "MetaQuotes-Demo"
  }'

# Use the returned session_token for other requests
curl -X GET "http://localhost:8000/api/v1/account" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

## API Endpoints Overview

### Authentication
- `POST /api/v1/login` - Login with MT5 credentials
- `POST /api/v1/logout` - Logout and invalidate session

### Account Data
- `GET /api/v1/account` - Full account information
- `GET /api/v1/balance` - Current balance
- `GET /api/v1/equity` - Current equity
- `GET /api/v1/snapshot` - Complete account snapshot

### Trading Data
- `GET /api/v1/positions` - Open positions
- `GET /api/v1/orders` - Pending orders
- `GET /api/v1/history` - Trading history

### Market Data
- `GET /api/v1/symbol/{symbol}` - Symbol information
- `GET /api/v1/server-time` - Broker server time

## Interactive Documentation

FastAPI provides automatic interactive documentation:

1. **Swagger UI**: http://localhost:8000/docs
   - Try out API endpoints directly in the browser
   - See request/response schemas
   - Test authentication

2. **ReDoc**: http://localhost:8000/redoc
   - Alternative documentation format
   - Better for reading and sharing

## Common Use Cases

### 1. Monitor Account Balance

```python
client = MT5ApiClient()
client.login(account_number, password, server)

# Get current balance
balance = client.get_balance()
print(f"Current Balance: ${balance:,.2f}")

# Get equity
equity = client.get_equity()
print(f"Current Equity: ${equity:,.2f}")
```

### 2. Check Open Positions

```python
positions = client.get_positions()

for pos in positions:
    print(f"Symbol: {pos['symbol']}")
    print(f"Type: {'BUY' if pos['type'] == 0 else 'SELL'}")
    print(f"Volume: {pos['volume']}")
    print(f"Profit: ${pos['profit']:.2f}")
    print("-" * 40)
```

### 3. Get Account Snapshot (with Drawdown Tracking)

```python
snapshot = client.get_snapshot()

print(f"Balance: ${snapshot['balance']:,.2f}")
print(f"Equity: ${snapshot['equity']:,.2f}")
print(f"Total P/L: ${snapshot['total_profit_loss']:,.2f}")
print(f"Day Start Balance: ${snapshot['day_start_balance']:,.2f}")
print(f"Open Positions: {len(snapshot['positions'])}")
```

### 4. Monitor Trading History

```python
# Get last 7 days of history
history = client.get_history(from_days_ago=7)

print(f"Total Deals: {history['deals_count']}")

total_profit = sum(
    deal['profit'] for deal in history['deals']
)
print(f"Total Profit: ${total_profit:,.2f}")
```

## Troubleshooting

### "Failed to connect to MT5"

**Problem**: Cannot establish connection to MT5 terminal

**Solutions**:
1. Ensure MT5 terminal is installed
2. Check credentials are correct
3. Verify server name (e.g., "MetaQuotes-Demo", not "Demo")
4. Close MT5 terminal if it's running with a different account
5. Try running Python as administrator (Windows)

### "Connection refused" or "Cannot connect to localhost:8000"

**Problem**: API server is not running or port is blocked

**Solutions**:
1. Make sure you started the server with `python run_mt5_api.py`
2. Check if port 8000 is available
3. Check firewall settings
4. Try a different port (modify `run_mt5_api.py`)

### "Invalid or expired session token"

**Problem**: Session has expired or token is incorrect

**Solutions**:
1. Login again to get a new token
2. Sessions expire after 24 hours
3. Ensure token is included in Authorization header
4. Format: `Authorization: Bearer <token>`

### "Module not found" errors

**Problem**: Required packages not installed

**Solutions**:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Web client CORS errors

**Problem**: Browser blocks requests due to CORS policy

**Solutions**:
1. CORS is already enabled in the API
2. Make sure API server is running
3. Use same protocol (http/https)
4. Check browser console for specific errors

## Next Steps

1. **Read Full Documentation**: See `docs/MT5_REST_API.md`
2. **Security**: Review security considerations for production
3. **Custom Integration**: Adapt the API to your needs
4. **Monitoring**: Set up logging and monitoring
5. **Testing**: Run comprehensive tests with your MT5 account

## Example Integrations

### Trading Dashboard
Build a web dashboard to monitor multiple MT5 accounts:
- Real-time balance and equity
- Position monitoring
- P&L tracking
- Risk alerts

### Mobile App
Create a mobile app using the REST API:
- iOS/Android apps
- React Native or Flutter
- Push notifications for trades

### Automated Systems
Integrate with automated trading systems:
- Monitor account health
- Risk management checks
- Multi-account management
- Alert systems

## Support

- **Documentation**: `docs/MT5_REST_API.md`
- **API Docs**: http://localhost:8000/docs
- **Examples**: Check `examples/` directory
- **Issues**: Review troubleshooting section above

## Security Reminder

⚠️ **Important for Production**:
- Use HTTPS, not HTTP
- Store credentials securely
- Implement rate limiting
- Use proper session storage (Redis/database)
- Enable authentication logs
- Set specific CORS origins
- Never commit credentials to git

Happy Trading! 🚀
