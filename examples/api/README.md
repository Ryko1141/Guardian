# MT5 REST API Examples

This folder contains examples for using the MT5 REST API.

## Files

### `test_mt5_api.py`
Python client library and usage examples.

**Usage:**
```python
from examples.api.test_mt5_api import MT5ApiClient

client = MT5ApiClient()
client.login(account_number, password, server)
account = client.get_account_info()
print(f"Balance: ${account['balance']:,.2f}")
client.logout()
```

**Run the example:**
```bash
# Edit credentials in the file first
python examples/api/test_mt5_api.py
```

### `mt5_api_client.html`
Web-based interface for testing the API.

**Usage:**
1. Ensure API server is running: `python run_mt5_api.py`
2. Open `mt5_api_client.html` in your web browser
3. Enter your MT5 credentials
4. Click buttons to test different endpoints

## Prerequisites

1. **API Server Running:**
   ```bash
   python run_mt5_api.py
   ```

2. **MT5 Credentials:**
   - Account number
   - Password
   - Server name

## Quick Start

1. Start the API server
2. Try the web client for quick testing
3. Use the Python client for programmatic access

## Documentation

- Full API Reference: `docs/api/MT5_REST_API.md`
- Quick Start Guide: `docs/api/MT5_API_QUICKSTART.md`
- Interactive Docs: http://localhost:8000/docs
