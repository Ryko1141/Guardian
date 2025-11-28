# MT5 REST API - Quick Reference Card

## 🚀 Quick Start
```bash
# 1. Install
pip install -r requirements.txt

# 2. Start Server
python run_mt5_api.py

# 3. Access Docs
# Open: http://localhost:8000/docs
```

## 📍 Base URL
```
http://localhost:8000
```

## 🔑 Authentication

### Login
```bash
POST /api/v1/login
Content-Type: application/json

{
  "account_number": 12345678,
  "password": "your_password",
  "server": "YourBroker-Demo"
}

Response: {"session_token": "abc123...", ...}
```

### Use Token
```bash
Authorization: Bearer YOUR_SESSION_TOKEN
```

### Logout
```bash
POST /api/v1/logout
Authorization: Bearer YOUR_SESSION_TOKEN
```

## 📊 API Endpoints

### Account Information
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/account` | Full account details |
| GET | `/api/v1/balance` | Current balance |
| GET | `/api/v1/equity` | Current equity |
| GET | `/api/v1/snapshot` | Complete snapshot |

### Trading Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/positions` | Open positions |
| GET | `/api/v1/orders` | Pending orders |
| GET | `/api/v1/history` | Trading history |

### Market Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/symbol/{symbol}` | Symbol info |
| GET | `/api/v1/server-time` | Server time |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |

## 💻 Python Quick Start
```python
from examples.test_mt5_api import MT5ApiClient

# Connect
client = MT5ApiClient()
client.login(12345678, "password", "Broker-Demo")

# Get Data
account = client.get_account_info()
balance = client.get_balance()
positions = client.get_positions()
snapshot = client.get_snapshot()

# Disconnect
client.logout()
```

## 🌐 cURL Examples
```bash
# Login
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"account_number":12345678,"password":"pass","server":"Demo"}'

# Get Account (replace TOKEN)
curl http://localhost:8000/api/v1/account \
  -H "Authorization: Bearer TOKEN"

# Get Positions
curl http://localhost:8000/api/v1/positions \
  -H "Authorization: Bearer TOKEN"

# Get Snapshot
curl http://localhost:8000/api/v1/snapshot \
  -H "Authorization: Bearer TOKEN"
```

## 🔧 JavaScript/TypeScript
```javascript
// Login
const response = await fetch('http://localhost:8000/api/v1/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    account_number: 12345678,
    password: 'your_password',
    server: 'Broker-Demo'
  })
});

const {session_token} = await response.json();

// Get Account
const account = await fetch('http://localhost:8000/api/v1/account', {
  headers: {'Authorization': `Bearer ${session_token}`}
}).then(r => r.json());

console.log('Balance:', account.balance);
```

## 📱 Web Client
```
Open: examples/mt5_api_client.html
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Start server: `python run_mt5_api.py` |
| MT5 connection failed | Check credentials and server name |
| Invalid token | Login again (tokens expire after 24h) |
| Module not found | Run: `pip install -r requirements.txt` |
| Port in use | Change port in `run_mt5_api.py` |

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| `GETTING_STARTED_API.md` | Beginner guide |
| `docs/MT5_API_QUICKSTART.md` | 5-minute setup |
| `docs/MT5_REST_API.md` | Complete reference |
| `http://localhost:8000/docs` | Interactive docs |

## 🔐 Security Checklist

- [ ] Never commit credentials to git
- [ ] Use HTTPS in production
- [ ] Set specific CORS origins for production
- [ ] Store tokens securely
- [ ] Logout when done
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting for production

## 📝 Response Examples

### Account Info
```json
{
  "login": 12345678,
  "balance": 10000.00,
  "equity": 10250.50,
  "profit": 250.50,
  "margin": 500.00,
  "margin_free": 9750.50,
  "leverage": 100,
  "currency": "USD",
  "server": "Broker-Demo"
}
```

### Positions
```json
[
  {
    "ticket": 123456,
    "symbol": "EURUSD",
    "volume": 0.1,
    "type": 0,
    "price_open": 1.1000,
    "price_current": 1.1050,
    "profit": 50.00,
    "sl": 1.0950,
    "tp": 1.1100
  }
]
```

### Snapshot
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "balance": 10000.00,
  "equity": 10250.50,
  "total_profit_loss": 250.50,
  "day_start_balance": 10000.00,
  "day_start_equity": 10000.00,
  "positions": [...]
}
```

## 🎯 Common Use Cases

### Check Balance
```python
client.login(account, password, server)
balance = client.get_balance()
print(f"Balance: ${balance:,.2f}")
```

### Monitor Positions
```python
positions = client.get_positions()
for pos in positions:
    print(f"{pos['symbol']}: ${pos['profit']:.2f}")
```

### Track Daily P/L
```python
snapshot = client.get_snapshot()
daily_pl = snapshot['total_profit_loss']
print(f"Today: ${daily_pl:,.2f}")
```

## 📞 Support

- **Setup Issues**: Run `python setup_mt5_api.py`
- **API Testing**: http://localhost:8000/docs
- **Examples**: Check `examples/` directory
- **Documentation**: See `docs/MT5_REST_API.md`

## ⚡ Pro Tips

1. Use the web client for quick testing
2. Check `/health` endpoint to verify server
3. Tokens last 24 hours
4. Use `/docs` for interactive API exploration
5. Run tests: `python tests/test_mt5_api.py`

---

**Server Start**: `python run_mt5_api.py`  
**Docs**: http://localhost:8000/docs  
**Web Client**: `examples/mt5_api_client.html`

---
Quick Reference v1.0
