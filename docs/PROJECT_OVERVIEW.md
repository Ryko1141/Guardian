# Guardian - Project Overview

## What is Guardian?

**Guardian** is a comprehensive real-time trading account monitoring and risk management system designed specifically for proprietary trading firms. It combines intelligent web scraping, automated rule extraction, and live account monitoring to help prop traders stay within their firm's risk parameters and avoid rule breaches.

## Core Capabilities

### 1. **Intelligent Rule Extraction System**

Guardian can automatically scrape and extract trading rules from prop firm help centers:

- **Cloudflare Bypass** - Stealth web scraping with Playwright
- **Hybrid Extraction** - Pattern matching + LLM analysis for accuracy
- **Taxonomy Validation** - Prevents LLM hallucinations with firm-specific program taxonomies
- **Database Storage** - SQLite with versioning and change detection
- **Structured Output** - JSON format with confidence scores

**Supported Firms:**
- FundedNext (Stellar 1-Step, Stellar 2-Step, Evaluation, etc.)
- FTMO
- Alpha Capital Group
- Funded Trader
- *Extensible to any prop firm*

### 2. **Real-Time Account Monitoring**

Connects directly to trading platforms and monitors account state in real-time:

**Supported Platforms:**
- ✅ MetaTrader 5 (Full support)
- ✅ cTrader Open API (Full support)
- 🔄 MetaTrader 4 (Planned)

**What's Monitored:**
- Account balance and equity
- Open positions and P&L
- Margin levels and usage
- Daily drawdown (with "whichever is higher" rule)
- Total drawdown from starting balance
- Position sizes and lot volumes

### 3. **Risk Rule Enforcement**

Guardian enforces critical prop firm risk rules with configurable thresholds:

| Rule Type | Description | Alert Levels |
|-----------|-------------|--------------|
| **Daily Drawdown** | Max % loss per day from day start | Warning (80%) + Critical (100%) |
| **Total Drawdown** | Max % loss from starting balance | Warning (80%) + Critical (100%) |
| **Risk Per Trade** | Max position size as % of balance | Warning (80%) + Critical (100%) |
| **Maximum Lots** | Total lot size across all positions | Warning (80%) + Critical (100%) |
| **Position Count** | Maximum concurrent open positions | Warning threshold |
| **Margin Level** | Minimum margin level percentage | Warning (100%) + Critical (50%) |
| **Stop Loss** | Required stop loss on all positions | Warning if missing |

**Key Features:**
- **Worst-Case Calculation** - Uses max(balance_loss, equity_loss) for daily DD
- **Warning Thresholds** - Alert at 80% of limit (configurable)
- **Multi-Account Support** - Monitor multiple accounts with different rules
- **Async Monitoring** - Efficient concurrent monitoring

### 4. **Smart Alert System**

Currently provides console notifications with extensible architecture:

- **Rich Console Formatting** - Color-coded alerts with panels
- **Structured Messages** - Clear breach details with values and thresholds
- **Extensible Design** - Ready for Telegram, Discord, Email, Slack

**Alert Example:**
```
╭──────────────────────────────────────────────────╮
│ FTMO-12345:                                      │
│ WARN DAILY_DD – ⚠️ Daily DD warning: -4.2%      │
│                   approaching -5.0%              │
│ HARD MAX_LOTS – 🚨 Max lot limit exceeded:      │
│                   22.5 > 20.0                    │
╰──────────────────────────────────────────────────╯
```

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     GUARDIAN SYSTEM                      │
└─────────────────────────────────────────────────────────┘
           │
           ├── 1. SCRAPING & EXTRACTION
           │      ├── Playwright Scraper (Cloudflare bypass)
           │      ├── Pattern Extractor (Fast, regex-based)
           │      ├── LLM Extractor (OpenAI GPT-4)
           │      ├── Hybrid Extractor (Pattern + LLM)
           │      └── Taxonomy Validator (Hallucination prevention)
           │             ↓
           │      ┌──────────────┐
           │      │ SQLite DB    │
           │      │ - Firms      │
           │      │ - Documents  │
           │      │ - Rules      │
           │      │ - Taxonomy   │
           │      └──────────────┘
           │
           ├── 2. ACCOUNT MONITORING
           │      ├── MT5 Client (MetaTrader5 API)
           │      ├── cTrader Client (Open API / WebSocket)
           │      ├── Account Snapshot Model
           │      └── Position Tracking
           │             ↓
           │      ┌──────────────┐
           │      │ Live Data    │
           │      │ - Balance    │
           │      │ - Equity     │
           │      │ - Positions  │
           │      │ - Margin     │
           │      └──────────────┘
           │
           ├── 3. RULE ENGINE
           │      ├── PropRules Configuration
           │      ├── RiskRuleEngine
           │      ├── Breach Detection
           │      └── Threshold Warnings
           │             ↓
           │      ┌──────────────┐
           │      │ Breaches     │
           │      │ - Level      │
           │      │ - Code       │
           │      │ - Message    │
           │      │ - Threshold  │
           │      └──────────────┘
           │
           └── 4. NOTIFICATION SYSTEM
                  ├── Console Notifier (Rich)
                  ├── [Future] Telegram Bot
                  ├── [Future] Discord Webhook
                  └── [Future] Email Alerts
```

## Key Technologies

### Core Stack
- **Python 3.8+** - Main language
- **Playwright** - Web scraping with stealth mode
- **MetaTrader5 API** - MT5 integration
- **cTrader Open API** - cTrader integration (REST + WebSocket)
- **SQLite** - Rule storage and versioning
- **Pydantic** - Data validation and configuration
- **Rich** - Console formatting

### AI/ML
- **OpenAI GPT-4** - LLM-based rule extraction
- **Fuzzy Matching** - Taxonomy validation (RapidFuzz)

### Testing & Quality
- **pytest** - Test framework
- **98% code coverage** - Comprehensive test suite
- **47+ test cases** - Unit, integration, and migration tests

## Project Statistics

| Metric | Value |
|--------|-------|
| **Total Files** | 60+ source files |
| **Lines of Code** | ~8,000+ lines |
| **Test Coverage** | 98% |
| **Test Cases** | 47+ |
| **Documentation** | 15+ markdown files |
| **Supported Platforms** | 2 (MT5, cTrader) |
| **Predefined Firm Rules** | 5+ firms |

## File Structure Summary

```
guardian/
├── src/                    # 10 core modules (~3,500 lines)
│   ├── Platform clients (MT5, cTrader)
│   ├── Rule engine
│   ├── Data models
│   ├── Runners (single, multi, async)
│   └── propfirm_scraper/ (7 modules ~2,000 lines)
├── database/               # 10 modules (~2,500 lines)
│   ├── Schema & utilities
│   ├── Rule extraction
│   └── Query interfaces
├── config/                 # 3 configuration files
│   ├── Taxonomy definitions
│   ├── Pattern library
│   └── Validators
├── examples/               # 7 usage examples
├── scripts/                # 4 utility scripts
├── tests/                  # 5 test modules (~1,800 lines)
└── docs/                   # 15+ documentation files
```

## Production Readiness

### ✅ Code Quality
- Type hints throughout codebase
- Pydantic validation on all inputs
- Comprehensive error handling
- Structured logging

### ✅ Testing
- 98% code coverage
- All integration points tested
- Edge cases handled
- Migration validation
- CI/CD ready

### ✅ Documentation
- Complete README with quick start
- 15+ specialized documentation files
- Usage examples for all features
- API references
- Troubleshooting guides

### ✅ Validation
- LLM output validation with taxonomy
- Database integrity checks
- Rule compatibility verification
- Backward compatibility maintained

## Use Cases

### 1. **Prop Trader Protection**
Monitor your challenge or funded account in real-time to avoid rule breaches:
- Get warned at 80% of daily drawdown limit
- Track total drawdown from starting balance
- Ensure position sizes stay within limits
- Prevent margin calls

### 2. **Multi-Account Management**
Manage multiple prop firm accounts simultaneously:
- Different rules per account
- Independent monitoring
- Consolidated alerts
- Async monitoring for efficiency

### 3. **Firm Rule Research**
Automatically extract and compare rules across prop firms:
- Scrape help centers
- Extract structured rules
- Store in searchable database
- Compare programs and firms

### 4. **Automated Compliance**
Integrate Guardian into trading bots or EAs:
- Real-time rule checking
- Programmatic breach detection
- API-friendly architecture
- Pure Python logic (no dependencies for rule engine)

## Roadmap

### ✅ Completed (v1.0)
- MT5 and cTrader integration
- Real-time monitoring
- Rule extraction system
- Database storage
- LLM guardrails
- Multi-account support
- Comprehensive testing

### 🔄 In Progress (v1.1)
- Web dashboard UI
- Telegram bot notifications
- Discord webhook integration
- Automated re-scraping

### 📋 Planned (v2.0)
- MetaTrader 4 support
- Advanced analytics dashboard
- Rule change detection and alerts
- Historical performance tracking
- Trading journal integration
- Mobile app (iOS/Android)

## Getting Started

See the main [README.md](../README.md) for:
- Installation instructions
- Configuration guide
- Quick start examples
- Usage documentation

## Contributing

Guardian is open source and welcomes contributions. See [CONTRIBUTING.md](guides/CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](../LICENSE) file.

## Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check documentation in `docs/` directory
- Review examples in `examples/` directory

---

**Guardian** - Keeping prop traders safe, one alert at a time.
