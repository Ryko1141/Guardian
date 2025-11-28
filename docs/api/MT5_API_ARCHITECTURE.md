# MT5 REST API - Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MT5 REST API System                          │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────── CLIENTS ────────────────────────────────────┐
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Python     │  │     Web      │  │    cURL /    │             │
│  │   Client     │  │   Browser    │  │   Mobile     │             │
│  │              │  │              │  │              │             │
│  │ test_mt5_    │  │ mt5_api_     │  │  Any HTTP    │             │
│  │  api.py      │  │ client.html  │  │   Client     │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                 │                 │                      │
│         └─────────────────┼─────────────────┘                      │
│                           │                                        │
└───────────────────────────┼────────────────────────────────────────┘
                            │
                            │ HTTP/HTTPS
                            │ POST /api/v1/login
                            │ GET  /api/v1/account
                            │ GET  /api/v1/positions
                            │ etc.
                            │
┌───────────────────────────▼────────────────────────────────────────┐
│                     FASTAPI SERVER                                 │
│                   (src/mt5_api.py)                                 │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              Authentication Layer                          │   │
│  │  • Session Token Generation (Bearer Token)                │   │
│  │  • Password Hashing (SHA-256)                             │   │
│  │  • Token Validation                                       │   │
│  │  • 24-hour Expiration                                     │   │
│  └────────────────────────────────────────────────────────────┘   │
│                            │                                       │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              Session Management                            │   │
│  │  • In-Memory Session Storage                              │   │
│  │  • Multiple Concurrent Users                              │   │
│  │  • Automatic Cleanup                                      │   │
│  │  • Connection Pooling                                     │   │
│  └────────────────────────────────────────────────────────────┘   │
│                            │                                       │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              API Endpoints (15+)                           │   │
│  │                                                            │   │
│  │  Authentication:                                           │   │
│  │    • POST /api/v1/login                                   │   │
│  │    • POST /api/v1/logout                                  │   │
│  │                                                            │   │
│  │  Account Data:                                            │   │
│  │    • GET /api/v1/account                                  │   │
│  │    • GET /api/v1/balance                                  │   │
│  │    • GET /api/v1/equity                                   │   │
│  │    • GET /api/v1/snapshot                                 │   │
│  │                                                            │   │
│  │  Trading Data:                                            │   │
│  │    • GET /api/v1/positions                                │   │
│  │    • GET /api/v1/orders                                   │   │
│  │    • GET /api/v1/history                                  │   │
│  │                                                            │   │
│  │  Market Data:                                             │   │
│  │    • GET /api/v1/symbol/{symbol}                          │   │
│  │    • GET /api/v1/server-time                              │   │
│  │                                                            │   │
│  │  System:                                                  │   │
│  │    • GET /                                                │   │
│  │    • GET /health                                          │   │
│  │    • GET /docs (Swagger UI)                               │   │
│  └────────────────────────────────────────────────────────────┘   │
│                            │                                       │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              CORS Middleware                               │   │
│  │  • Allow Origins: * (configurable)                        │   │
│  │  • Allow Credentials: Yes                                 │   │
│  │  • Allow Methods: All                                     │   │
│  └────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬───────────────────────────────────────┘
                             │
                             │ Uses
                             │
┌────────────────────────────▼───────────────────────────────────────┐
│                     MT5 CLIENT WRAPPER                             │
│                   (src/mt5_client.py)                              │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              MT5Client Class                               │   │
│  │  • Connection Management                                   │   │
│  │  • Auto-reconnection                                      │   │
│  │  • Account Operations                                     │   │
│  │  • Position Management                                    │   │
│  │  • History Retrieval                                      │   │
│  │  • Market Data Access                                     │   │
│  └────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬───────────────────────────────────────┘
                             │
                             │ Uses
                             │
┌────────────────────────────▼───────────────────────────────────────┐
│                  METATRADER 5 PYTHON API                           │
│                   (MetaTrader5 package)                            │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  • mt5.initialize()                                       │   │
│  │  • mt5.login()                                            │   │
│  │  • mt5.account_info()                                     │   │
│  │  • mt5.positions_get()                                    │   │
│  │  • mt5.orders_get()                                       │   │
│  │  • mt5.history_deals_get()                                │   │
│  │  • mt5.symbol_info()                                      │   │
│  └────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬───────────────────────────────────────┘
                             │
                             │ Connects to
                             │
┌────────────────────────────▼───────────────────────────────────────┐
│                  METATRADER 5 TERMINAL                             │
│                   (Desktop Application)                            │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  • Account Management                                     │   │
│  │  • Trading Platform                                       │   │
│  │  • Market Data Feed                                       │   │
│  │  • Trade Execution                                        │   │
│  └────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬───────────────────────────────────────┘
                             │
                             │ Connects to
                             │
┌────────────────────────────▼───────────────────────────────────────┐
│                      BROKER SERVERS                                │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  • Trade Server                                           │   │
│  │  • Market Data Server                                     │   │
│  │  • Account Server                                         │   │
│  └────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════

                        DATA FLOW EXAMPLE

═══════════════════════════════════════════════════════════════════════

1. LOGIN REQUEST
   ─────────────
   
   Client                    API Server              MT5 Client          MT5 Terminal
     │                          │                        │                    │
     │  POST /api/v1/login      │                        │                    │
     │  {account, pass, srv}    │                        │                    │
     ├─────────────────────────>│                        │                    │
     │                          │  MT5Client(...)        │                    │
     │                          ├───────────────────────>│                    │
     │                          │                        │  mt5.initialize()  │
     │                          │                        ├───────────────────>│
     │                          │                        │  mt5.login()       │
     │                          │                        ├───────────────────>│
     │                          │                        │<───────────────────┤
     │                          │  Connection OK         │  Connected         │
     │                          │<───────────────────────┤                    │
     │  {session_token}         │                        │                    │
     │<─────────────────────────┤                        │                    │
     │                          │                        │                    │

2. GET ACCOUNT DATA
   ────────────────
   
   Client                    API Server              MT5 Client          MT5 Terminal
     │                          │                        │                    │
     │  GET /api/v1/account     │                        │                    │
     │  Auth: Bearer token      │                        │                    │
     ├─────────────────────────>│                        │                    │
     │                          │  Validate Token        │                    │
     │                          │  Get Session           │                    │
     │                          │  client.get_account()  │                    │
     │                          ├───────────────────────>│                    │
     │                          │                        │  mt5.account_info()│
     │                          │                        ├───────────────────>│
     │                          │                        │<───────────────────┤
     │                          │  Account Data          │  Account Info      │
     │                          │<───────────────────────┤                    │
     │  {balance, equity...}    │                        │                    │
     │<─────────────────────────┤                        │                    │
     │                          │                        │                    │

3. GET POSITIONS
   ─────────────
   
   Client                    API Server              MT5 Client          MT5 Terminal
     │                          │                        │                    │
     │  GET /api/v1/positions   │                        │                    │
     │  Auth: Bearer token      │                        │                    │
     ├─────────────────────────>│                        │                    │
     │                          │  Validate Token        │                    │
     │                          │  client.get_positions()│                    │
     │                          ├───────────────────────>│                    │
     │                          │                        │  mt5.positions_get()│
     │                          │                        ├───────────────────>│
     │                          │                        │<───────────────────┤
     │                          │  Positions List        │  Open Positions    │
     │                          │<───────────────────────┤                    │
     │  [{pos1}, {pos2}...]     │                        │                    │
     │<─────────────────────────┤                        │                    │
     │                          │                        │                    │

4. LOGOUT
   ──────
   
   Client                    API Server              MT5 Client          MT5 Terminal
     │                          │                        │                    │
     │  POST /api/v1/logout     │                        │                    │
     │  Auth: Bearer token      │                        │                    │
     ├─────────────────────────>│                        │                    │
     │                          │  Invalidate Session    │                    │
     │                          │  client.disconnect()   │                    │
     │                          ├───────────────────────>│                    │
     │                          │                        │  mt5.shutdown()    │
     │                          │                        ├───────────────────>│
     │                          │                        │<───────────────────┤
     │                          │  Disconnected          │  Connection Closed │
     │                          │<───────────────────────┤                    │
     │  {message: "success"}    │                        │                    │
     │<─────────────────────────┤                        │                    │
     │                          │                        │                    │


═══════════════════════════════════════════════════════════════════════

                        SECURITY ARCHITECTURE

═══════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│                         SECURITY LAYERS                             │
│                                                                     │
│  1. Network Layer                                                   │
│     └─> HTTPS/TLS (Production)                                     │
│                                                                     │
│  2. CORS Layer                                                      │
│     └─> Origin validation                                          │
│     └─> Credential checks                                          │
│                                                                     │
│  3. Authentication Layer                                            │
│     └─> Bearer Token (32-byte secure random)                       │
│     └─> Token validation on each request                           │
│                                                                     │
│  4. Session Layer                                                   │
│     └─> Password hashing (SHA-256)                                 │
│     └─> 24-hour expiration                                         │
│     └─> Automatic cleanup                                          │
│                                                                     │
│  5. Input Validation                                                │
│     └─> Pydantic models                                            │
│     └─> Type checking                                              │
│     └─> Data sanitization                                          │
│                                                                     │
│  6. Error Handling                                                  │
│     └─> Generic error messages                                     │
│     └─> No sensitive data in errors                                │
│     └─> Proper status codes                                        │
└─────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════

                        FILE ORGANIZATION

═══════════════════════════════════════════════════════════════════════

Guardian/
│
├── Core Implementation (API Logic)
│   ├── src/mt5_api.py              [584 lines] Main API server
│   ├── run_mt5_api.py              [ 27 lines] Server launcher
│   └── setup_mt5_api.py            [134 lines] Setup automation
│
├── Client Libraries (Integration)
│   ├── examples/test_mt5_api.py   [234 lines] Python client
│   └── examples/mt5_api_client.html [287 lines] Web client
│
├── Testing (Quality Assurance)
│   └── tests/test_mt5_api.py      [150 lines] API tests
│
├── Documentation (Learning)
│   ├── GETTING_STARTED_API.md     [251 lines] Beginner guide
│   ├── MT5_API_QUICK_REFERENCE.md [158 lines] Quick lookup
│   ├── MT5_API_SUMMARY.md         [193 lines] Implementation summary
│   └── docs/
│       ├── MT5_REST_API.md        [457 lines] Complete reference
│       ├── MT5_API_QUICKSTART.md  [276 lines] Quick start
│       └── MT5_API_IMPLEMENTATION.md [193 lines] Technical details
│
└── Configuration
    ├── requirements.txt            [Modified] Dependencies
    └── README.md                   [Modified] Project overview

Total: 14 files, ~2,936 lines of code and documentation


═══════════════════════════════════════════════════════════════════════

                        DEPLOYMENT OVERVIEW

═══════════════════════════════════════════════════════════════════════

Development Environment:
┌────────────────────────────────────┐
│ python run_mt5_api.py              │
│ http://localhost:8000              │
│ • Auto-reload: No                  │
│ • CORS: All origins                │
│ • Session storage: In-memory       │
│ • Logging: Console                 │
└────────────────────────────────────┘

Production Environment:
┌────────────────────────────────────┐
│ uvicorn with SSL/TLS               │
│ https://your-domain.com            │
│ • Auto-reload: No                  │
│ • CORS: Specific origins           │
│ • Session storage: Redis           │
│ • Logging: File + monitoring       │
│ • Reverse proxy: Nginx             │
│ • Rate limiting: Yes               │
│ • Load balancer: Optional          │
└────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════

End of Architecture Diagram
