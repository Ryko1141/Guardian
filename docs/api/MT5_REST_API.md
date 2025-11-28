# MT5 REST API Documentation

A REST API that allows clients to connect to MetaTrader 5 with their credentials and perform account operations remotely.

## Features

- **Secure Authentication**: Login with MT5 credentials (account number, password, server)
- **Session Management**: Token-based authentication with 24-hour expiry
- **Account Operations**: Get balance, equity, margin, and other account details
- **Position Management**: View open positions and pending orders
- **Historical Data**: Access trading history and closed deals
- **Market Data**: Get symbol information and broker server time
- **Account Snapshots**: Complete account state with drawdown tracking

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure MetaTrader 5 is installed on your system

## Quick Start

### Starting the Server

Run the API server:
```bash
python run_mt5_api.py
```

The server will start on `http://localhost:8000`

Access the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Using the API

#### 1. Login to MT5

**Endpoint**: `POST /api/v1/login`

**Request**:
```json
{
  "account_number": 12345678,
  "password": "your_password",
  "server": "MetaQuotes-Demo",
  "path": null
}
```

**Response**:
```json
{
  "session_token": "abc123...",
  "account_number": 12345678,
  "server": "MetaQuotes-Demo",
  "expires_in": 86400
}
```

#### 2. Use Session Token

Include the session token in the `Authorization` header for all subsequent requests:
```
Authorization: Bearer abc123...
```

#### 3. Get Account Information

**Endpoint**: `GET /api/v1/account`

**Response**:
```json
{
  "login": 12345678,
  "balance": 10000.00,
  "equity": 10250.50,
  "profit": 250.50,
  "margin": 500.00,
  "margin_free": 9750.50,
  "margin_level": 2050.10,
  "leverage": 100,
  "currency": "USD",
  "server": "MetaQuotes-Demo",
  "company": "MetaQuotes Software Corp."
}
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/login` | Authenticate and create session |
| POST | `/api/v1/logout` | Logout and invalidate session |

### Account Information

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/account` | Get complete account information |
| GET | `/api/v1/balance` | Get current balance |
| GET | `/api/v1/equity` | Get current equity |
| GET | `/api/v1/snapshot` | Get comprehensive account snapshot |

### Trading Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/positions` | Get all open positions |
| GET | `/api/v1/orders` | Get all pending orders |
| GET | `/api/v1/history` | Get trading history (closed deals) |

### Market Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/symbol/{symbol}` | Get symbol information |
| GET | `/api/v1/server-time` | Get broker server time |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |

## Python Client Example

```python
from examples.test_mt5_api import MT5ApiClient

# Initialize client
client = MT5ApiClient(base_url="http://localhost:8000")

# Login
client.login(
    account_number=12345678,
    password="your_password",
    server="MetaQuotes-Demo"
)

# Get account info
account = client.get_account_info()
print(f"Balance: ${account['balance']:,.2f}")
print(f"Equity: ${account['equity']:,.2f}")

# Get positions
positions = client.get_positions()
for pos in positions:
    print(f"Position: {pos['symbol']} | Profit: ${pos['profit']:.2f}")

# Get account snapshot
snapshot = client.get_snapshot()
print(f"Total P/L: ${snapshot['total_profit_loss']:,.2f}")

# Logout
client.logout()
```

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

### Get Account Snapshot
```bash
curl -X GET "http://localhost:8000/api/v1/snapshot" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

## JavaScript/TypeScript Example

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/v1/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    account_number: 12345678,
    password: 'your_password',
    server: 'MetaQuotes-Demo'
  })
});

const { session_token } = await loginResponse.json();

// Get account info
const accountResponse = await fetch('http://localhost:8000/api/v1/account', {
  headers: {
    'Authorization': `Bearer ${session_token}`
  }
});

const account = await accountResponse.json();
console.log(`Balance: $${account.balance}`);
```

## Security Considerations

### Production Deployment

1. **Use HTTPS**: Always use HTTPS in production to encrypt credentials
2. **Environment Variables**: Store sensitive data in environment variables
3. **Session Storage**: Replace in-memory sessions with Redis or database
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **CORS**: Configure CORS properly for web clients
6. **API Keys**: Consider adding API key authentication layer
7. **Logging**: Implement secure logging (don't log passwords)

### Example HTTPS Configuration

```python
# For production with SSL
uvicorn.run(
    app,
    host="0.0.0.0",
    port=443,
    ssl_keyfile="/path/to/key.pem",
    ssl_certfile="/path/to/cert.pem"
)
```

## Error Handling

The API returns standard HTTP status codes:

- `200`: Success
- `401`: Unauthorized (invalid or expired token)
- `404`: Resource not found
- `500`: Internal server error
- `503`: Service unavailable (connection issues)

Error Response Format:
```json
{
  "detail": "Error message here",
  "error_code": "OPTIONAL_ERROR_CODE"
}
```

## Session Management

- Sessions expire after 24 hours of inactivity
- Each login creates a new session token
- Logout invalidates the session immediately
- Sessions are cleaned up on server shutdown

## Advanced Configuration

### Custom Port
```python
# In run_mt5_api.py
uvicorn.run(app, host="0.0.0.0", port=8080)  # Use port 8080
```

### Development Mode (Auto-reload)
```python
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### CORS for Web Applications
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing

Run the example client:
```bash
# Edit credentials in examples/test_mt5_api.py
python examples/test_mt5_api.py
```

## Troubleshooting

### "Failed to connect to MT5"
- Ensure MT5 terminal is installed
- Check account credentials are correct
- Verify server name is correct
- Check if MT5 terminal is not already running with different account

### "Invalid or expired session token"
- Session may have expired (24 hours)
- Login again to get a new token
- Ensure token is included in Authorization header

### Connection Refused
- Check if API server is running
- Verify port 8000 is not blocked by firewall
- Check if another application is using port 8000

## Performance Considerations

- Each session maintains a persistent MT5 connection
- Reconnection happens automatically if connection is lost
- Session cleanup occurs on logout or expiry
- Consider connection pooling for high-traffic scenarios

## Future Enhancements

Potential features for future versions:
- WebSocket support for real-time updates
- Trade execution endpoints (place/modify/close orders)
- Multi-account support
- Rate limiting and quotas
- API key management
- User roles and permissions
- Enhanced security features
- Monitoring and analytics dashboard

## License

See LICENSE file in the project root.

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review troubleshooting section
3. Check server logs for error details
4. Refer to MT5 client documentation

## Related Files

- `src/mt5_api.py` - Main API implementation
- `src/mt5_client.py` - MT5 client wrapper
- `examples/test_mt5_api.py` - Python client example
- `run_mt5_api.py` - Server launcher script
