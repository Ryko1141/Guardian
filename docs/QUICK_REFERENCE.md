# Guardian - Quick Reference Guide

## Essential Commands

### Installation & Setup
```bash
# Clone and setup
git clone https://github.com/Ryko1141/Guardian.git
cd Guardian
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Configure accounts
cp accounts.json.example accounts.json
# Edit accounts.json with your account details
```

### Monitoring Commands
```bash
# Single account monitoring
python -m src.runner

# Multi-account monitoring
python -m src.multi_runner

# Async monitoring (for 3+ accounts)
python -m src.async_runner
```

### Scraping Commands
```bash
# Scrape help center
python -m src.propfirm_scraper.scraper "https://help.fundednext.com" --max-pages 100

# Fast extraction (patterns only)
python -m src.propfirm_scraper.fast_extractor output/scraped_pages.json

# Hybrid extraction (patterns + LLM)
python -m src.propfirm_scraper.hybrid_extractor output/scraped_pages.json

# Full LLM extraction
python -m src.propfirm_scraper.llm_extractor output/scraped_pages.json

# Validated extraction (with taxonomy)
python -m src.propfirm_scraper.validated_extractor output/scraped_pages.json --firm FundedNext
```

### Database Commands
```bash
# Ingest scraped documents
python database/ingest_documents.py output/scraped_pages.json

# Extract structured rules
python database/extract_rules.py

# Query rules
python database/query_rules.py --firm "FundedNext" --program "stellar_1step"

# Analyze database
python database/analyze_db.py

# Export rules
python database/export_rules.py --firm "FTMO" --output ftmo_rules.json
```

### Testing Commands
```bash
# Run all tests
python scripts/run_all_tests.py

# Run specific test suites
python -m pytest tests/test_rules.py
python -m pytest tests/test_program_taxonomy.py
python -m pytest tests/test_risk_monitor.py

# Test without live connection
python examples/test_rules_offline.py

# Test MT5 connection
python examples/test_mt5.py

# Test drawdown calculations
python examples/test_daily_dd_worst_case.py
```

## Configuration Files

### `.env` - Environment Variables
```env
# MT5 Configuration
MT5_ACCOUNT=12345678
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Demo

# cTrader Configuration
CTRADER_CLIENT_ID=your_client_id
CTRADER_CLIENT_SECRET=your_client_secret
CTRADER_ACCESS_TOKEN=your_access_token

# LLM API
OPENAI_API_KEY=sk-...

# Optional
PROGRAM_ID=stellar_1step
FIRM_NAME=FundedNext
STARTING_BALANCE=100000.0
```

### `accounts.json` - Multi-Account Setup
```json
{
  "accounts": [
    {
      "label": "FTMO Challenge 100k",
      "firm": "FTMO",
      "program_id": "challenge",
      "platform": "mt5",
      "account_id": "12345678",
      "starting_balance": 100000.0,
      "check_interval": 60,
      "enabled": true,
      "rules": {
        "name": "FTMO",
        "max_daily_drawdown_pct": 5.0,
        "max_total_drawdown_pct": 10.0,
        "max_risk_per_trade_pct": 1.0,
        "max_open_lots": 20.0,
        "max_positions": 10
      }
    }
  ]
}
```

## Common Workflows

### Workflow 1: Monitor Existing Account
```bash
# 1. Configure .env with account credentials
# 2. Run monitor
python -m src.runner
```

### Workflow 2: Add New Prop Firm
```bash
# 1. Scrape help center
python -m src.propfirm_scraper.scraper "https://help.newfirm.com" --max-pages 100

# 2. Extract and validate rules
python -m src.propfirm_scraper.validated_extractor output/scraped_pages.json --firm "NewFirm"

# 3. Ingest to database
python database/ingest_documents.py output/validated.json

# 4. Query extracted rules
python database/query_rules.py --firm "NewFirm"

# 5. Add to config.py predefined rules (optional)
# Edit src/config.py and add NEW_FIRM_RULES

# 6. Configure account in accounts.json
# Add entry with firm="NewFirm"

# 7. Start monitoring
python -m src.multi_runner
```

### Workflow 3: Research Multiple Firms
```bash
# Scrape multiple firms
python -m src.propfirm_scraper.scraper "https://help.ftmo.com"
python -m src.propfirm_scraper.scraper "https://help.fundednext.com"
python -m src.propfirm_scraper.scraper "https://help.fundedtrader.com"

# Extract all
for file in output/*.json; do
    python -m src.propfirm_scraper.hybrid_extractor "$file"
done

# Ingest all
python database/ingest_documents.py output/*.json

# Compare rules
python database/analyze_rules.py --compare "FTMO,FundedNext,FundedTrader"
```

## Rule Configuration

### Predefined Firms in `src/config.py`

```python
from src.config import (
    FTMO_RULES,
    ALPHA_CAPITAL_RULES,
    FUNDED_TRADER_RULES,
    FUNDED_NEXT_STELLAR_1STEP,
    FUNDED_NEXT_STELLAR_2STEP
)
```

### Custom Rules

```python
from src.config import PropRules

custom_rules = PropRules(
    name="Custom Firm",
    program_id="challenge_100k",
    max_daily_drawdown_pct=4.0,
    max_total_drawdown_pct=8.0,
    max_risk_per_trade_pct=2.0,
    max_open_lots=15.0,
    max_positions=8,
    warn_buffer_pct=0.75,  # Warn at 75% of limit
    require_stop_loss=True
)
```

## Programmatic Usage

### Monitor Single Account
```python
from src.mt5_client import MT5Client
from src.rules import check_account_rules
from src.config import FTMO_RULES
from src.notifier import notify_console

# Connect
client = MT5Client(account_number=12345, password="pass", server="Broker-Demo")
client.connect()

# Get snapshot
snapshot = client.get_account_snapshot()

# Check rules
breaches = check_account_rules(snapshot, FTMO_RULES, starting_balance=100000.0)

# Alert
if breaches:
    notify_console("FTMO-12345", breaches)
```

### Extract Rules from Scraped Data
```python
from src.propfirm_scraper.validated_extractor import ValidatedExtractor

extractor = ValidatedExtractor(firm_name="FundedNext")
rules = extractor.extract_from_file("output/scraped.json")

print(f"Found {len(rules['challenge_types'])} challenge types")
for challenge, details in rules['challenge_types'].items():
    print(f"- {challenge}: DD={details.get('max_drawdown')}%")
```

### Query Database
```python
from database.query_rules import query_rules_by_firm

rules = query_rules_by_firm("FundedNext", program_id="stellar_1step")
for rule in rules:
    print(f"{rule['rule_type']}: {rule['value']}")
```

## Troubleshooting

### Problem: MT5 connection fails
```bash
# Check MT5 terminal is running
# Verify credentials in .env
# Test connection
python examples/test_mt5.py
```

### Problem: Scraper blocked by Cloudflare
```bash
# The scraper will pause - solve challenge in browser window
# Or reduce max_pages and retry
python -m src.propfirm_scraper.scraper "URL" --max-pages 50
```

### Problem: LLM returns invalid program names
```bash
# Use validated extractor with taxonomy
python -m src.propfirm_scraper.validated_extractor \
    output/scraped.json \
    --firm FundedNext
```

### Problem: Rules not loading from database
```bash
# Check database exists
ls database/propfirm_scraper.db

# Verify data ingested
python database/analyze_db.py

# Test query
python database/query_rules.py --firm "YourFirm"
```

## Alert Severity Levels

| Level | Emoji | Description | When Triggered |
|-------|-------|-------------|----------------|
| WARN  | ⚠️ | Warning | At 80% of limit (configurable) |
| HARD  | 🚨 | Critical | At 100% of limit |

## Important Notes

### Daily Drawdown Calculation
Guardian uses the **"whichever is higher" rule**:
- Day start anchor = `max(day_start_balance, day_start_equity)`
- Daily loss = `max(balance_loss, equity_loss)`
- This prevents hiding floating losses

### Time Zones
- MT5: Uses server timezone from broker
- cTrader: Uses UTC
- Day reset: Configurable (default: 00:00 server time)

### Rate Limits
- MT5: No rate limits (local API)
- cTrader: Follow Open API rate limits
- LLM: Respect OpenAI rate limits (10 req/min on free tier)

## Support & Resources

- **Full Documentation**: `docs/` directory
- **Examples**: `examples/` directory
- **Tests**: `tests/` directory
- **GitHub**: https://github.com/Ryko1141/Guardian
- **Issues**: https://github.com/Ryko1141/Guardian/issues

## Version Info

**Current Version**: 1.0  
**Python Required**: 3.8+  
**Platforms**: Windows, Linux, macOS  
**License**: MIT

---

For detailed documentation, see [README.md](../README.md) and [docs/](.)
