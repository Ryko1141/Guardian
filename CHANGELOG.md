# Changelog

All notable changes to the Guardian project will be documented in this file.

## [Unreleased]

### Added - MT5 REST API (v1.0.0) - 2025-11-28

#### New Features
- **REST API Server** (`src/mt5_api.py`)
  - FastAPI-based REST API for remote MT5 account access
  - Session-based authentication with Bearer tokens
  - 15+ endpoints for account management, positions, orders, history
  - CORS support for web applications
  - Interactive Swagger UI documentation
  - Automatic session cleanup and expiration (24 hours)

#### API Endpoints
- `POST /api/v1/login` - Authenticate with MT5 credentials
- `POST /api/v1/logout` - Logout and disconnect
- `GET /api/v1/account` - Get full account information
- `GET /api/v1/balance` - Get current balance
- `GET /api/v1/equity` - Get current equity
- `GET /api/v1/positions` - Get open positions
- `GET /api/v1/orders` - Get pending orders
- `GET /api/v1/snapshot` - Get complete account snapshot
- `GET /api/v1/history` - Get trading history
- `GET /api/v1/symbol/{symbol}` - Get symbol information
- `GET /api/v1/server-time` - Get broker server time
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive documentation
- `GET /redoc` - Alternative documentation

#### Client Libraries & Examples
- **Python Client** (`examples/api/test_mt5_api.py`)
  - Easy-to-use MT5ApiClient wrapper class
  - Complete usage examples
  - Error handling and session management
  
- **Web Client** (`examples/api/mt5_api_client.html`)
  - Beautiful responsive web interface
  - Interactive API testing
  - Real-time response display
  - No backend required

- **Automated Tests** (`tests/test_mt5_api.py`)
  - Health checks
  - Endpoint accessibility tests
  - Authentication verification
  - Security tests

#### Scripts & Tools
- **Server Launcher** (`run_mt5_api.py`)
  - Simple server startup script
  - Production-ready configuration
  
- **Setup Script** (`setup_mt5_api.py`)
  - Automated dependency checking
  - Installation helper
  - MT5 availability verification

#### Documentation
- **Complete API Reference** (`docs/api/MT5_REST_API.md`)
  - All endpoints documented
  - Multiple language examples (Python, cURL, JavaScript)
  - Security best practices
  - Production deployment guide
  
- **Quick Start Guide** (`docs/api/MT5_API_QUICKSTART.md`)
  - 5-minute setup
  - Common use cases
  - Troubleshooting guide
  
- **Getting Started** (`docs/api/MT5_API_GETTING_STARTED.md`)
  - Beginner-friendly guide
  - Step-by-step instructions
  - Multiple client examples
  
- **Implementation Details** (`docs/api/MT5_API_IMPLEMENTATION.md`)
  - Technical overview
  - Architecture details
  - Testing results
  
- **Quick Reference** (`docs/api/MT5_API_QUICK_REFERENCE.md`)
  - Command reference card
  - Endpoint table
  - Common snippets
  
- **Architecture** (`docs/api/MT5_API_ARCHITECTURE.md`)
  - System design
  - Component diagrams
  - Data flow
  
- **File Index** (`docs/api/MT5_API_FILE_INDEX.md`)
  - Complete file listing
  - Descriptions
  - Quick access guide
  
- **Summary** (`docs/api/MT5_API_SUMMARY.md`)
  - Implementation summary
  - Statistics
  - Feature checklist

#### Dependencies Added
- `fastapi==0.115.0` - Web framework
- `uvicorn[standard]==0.32.0` - ASGI server
- `pydantic==2.9.2` - Data validation
- `python-multipart==0.0.12` - Form data support

#### Security Features
- Token-based authentication (Bearer tokens)
- Password hashing (SHA-256)
- Session expiration (24 hours)
- Automatic session cleanup
- CORS configuration
- Input validation
- HTTPS ready

#### Organization
- Created `docs/api/` folder for all API documentation
- Created `examples/api/` folder for API examples
- Updated `requirements.txt` with better organization
- Updated README.md with new paths and structure

## [Previous Versions]

### Core Features (Existing)
- MT5 and cTrader client integration
- Real-time account monitoring
- Risk rule enforcement
- Web scraping and rule extraction
- Multi-account monitoring
- Smart alerts and notifications

---

**Format**: This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
**Versioning**: Adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
