# Ollama Rule Violation Scanner

**AI-Powered Trading Rule Compliance Analysis**

Automatically scan MT5 trading accounts for rule violations using Ollama LLM and your propfirm rules database.

---

## Features

✅ **Database Integration** - Loads firm rules from SQLite database  
✅ **LLM Analysis** - Uses Ollama to intelligently analyze violations  
✅ **Hard & Soft Rules** - Distinguishes critical failures from warnings  
✅ **Comprehensive Reports** - JSON output with severity levels  
✅ **MT5 API Integration** - Real-time account scanning  
✅ **Multi-Firm Support** - Target specific firms or scan all  

---

## Requirements

### 1. Ollama (LLM Engine)

Install Ollama from https://ollama.ai

```bash
# Start Ollama server
ollama serve

# Pull a model (choose one)
ollama pull llama3.2       # Recommended: Fast, accurate
ollama pull qwen2.5-coder  # Great for code/data analysis
ollama pull mistral        # Alternative: Larger, more detailed
```

### 2. Python Dependencies

```bash
pip install requests
```

### 3. Database

Propfirm rules database must be populated:
```bash
python database/ingest_documents.py
python database/extract_rules.py
```

---

## Quick Start

### Example 1: Mock Data (No MT5 API Required)

```bash
python examples/ollama_scanner_example.py
```

Select option 1 for mock data.

### Example 2: Live MT5 Account

1. Start MT5 API:
```bash
python run_mt5_api.py
```

2. Get session token (via web client or API)

3. Run scanner:
```python
from src.ollama_rule_scanner import scan_mt5_account
import asyncio

report = asyncio.run(scan_mt5_account(
    api_url="http://localhost:8000",
    token="YOUR_SESSION_TOKEN",
    firm_name="FTMO",
    ollama_model="qwen2.5-coder"
))
```

---

## CLI Usage

```bash
python src/ollama_rule_scanner.py --help

# Scan with session token
python src/ollama_rule_scanner.py \
    --token YOUR_TOKEN \
    --firm FTMO \
    --model qwen2.5-coder

# Custom API endpoints
python src/ollama_rule_scanner.py \
    --api-url http://localhost:8000 \
    --ollama-url http://localhost:11434 \
    --token YOUR_TOKEN \
    --firm "MyForexFunds"
```

---

## API Reference

### OllamaRuleScanner Class

```python
from src.ollama_rule_scanner import OllamaRuleScanner

# Initialize
scanner = OllamaRuleScanner(
    ollama_url="http://localhost:11434",
    model="qwen2.5-coder",
    db_path="propfirm_scraper.db"
)

# Scan account
report = scanner.scan_account(
    account_data={...},  # Account snapshot from MT5 API
    firm_name="FTMO"     # Optional: target specific firm
)

# Print report
scanner.print_report(report)

# Save to file
scanner.save_report(report, "violation_report.json")
```

### Account Data Format

```python
account_data = {
    "balance": 100000.00,
    "equity": 95500.00,
    "profit": -4500.00,
    "margin": 2000.00,
    "margin_free": 93500.00,
    "margin_level": 4775.00,
    "positions": [
        {
            "ticket": 123456,
            "symbol": "EURUSD",
            "volume": 2.0,
            "profit": -600.00,
            "sl": 1.0800,
            "tp": 1.0900
        }
    ]
}
```

---

## Report Format

### Violation Object

```json
{
  "severity": "CRITICAL",
  "rule_type": "hard_rule",
  "category": "daily_drawdown",
  "description": "Daily drawdown exceeds maximum allowed limit",
  "current_value": 4500.00,
  "threshold_value": 4000.00,
  "firm_name": "FTMO",
  "recommendation": "Close losing positions immediately",
  "timestamp": "2025-11-28T12:00:00"
}
```

### Complete Report

```json
{
  "scan_timestamp": "2025-11-28T12:00:00",
  "firm_name": "FTMO",
  "model_used": "qwen2.5-coder",
  "account_summary": {
    "balance": 100000.00,
    "equity": 95500.00,
    "profit": -4500.00,
    "open_positions": 2
  },
  "rules_checked": 15,
  "documents_analyzed": 8,
  "violations": [...],
  "violation_count": {
    "critical": 1,
    "high": 2,
    "medium": 0,
    "low": 1
  },
  "hard_rules_violated": 1,
  "soft_rules_violated": 3,
  "summary": "Account approaching critical limits...",
  "llm_raw_response": "..."
}
```

---

## Severity Levels

| Severity | Icon | Meaning | Action Required |
|----------|------|---------|-----------------|
| CRITICAL | 🔴 | Account failure imminent | Close all positions |
| HIGH | 🟠 | Major rule violation | Immediate attention |
| MEDIUM | 🟡 | Warning threshold | Monitor closely |
| LOW | 🟢 | Best practice advice | Optional improvement |

---

## Rule Types

### Hard Rules
- **Definition**: Immediate account failure
- **Examples**:
  - Daily drawdown limit exceeded
  - Total drawdown limit breached
  - Maximum lot size violated
- **Action**: Account may be terminated

### Soft Rules
- **Definition**: Warnings and best practices
- **Examples**:
  - Missing stop losses
  - High margin usage
  - Too many open positions
- **Action**: Recommended improvements

---

## Database Schema

### firm_rule Table

```sql
CREATE TABLE firm_rule (
    id INTEGER PRIMARY KEY,
    firm_id INTEGER,
    rule_type TEXT,        -- profit_target, daily_loss, etc.
    rule_category TEXT,    -- hard_rule, soft_rule
    value TEXT,            -- "10%", "$5000"
    details TEXT,
    severity TEXT          -- critical, important, optional
);
```

### Query Examples

```python
# Get all critical rules for FTMO
cursor.execute("""
    SELECT * FROM firm_rule fr
    JOIN prop_firm pf ON fr.firm_id = pf.id
    WHERE pf.name = 'FTMO'
    AND fr.severity = 'critical'
""")

# Find daily drawdown rules
cursor.execute("""
    SELECT * FROM firm_rule
    WHERE rule_type LIKE '%daily%drawdown%'
""")
```

---

## Customization

### Change LLM Model

```python
scanner = OllamaRuleScanner(model="mistral")  # Use different model
```

Available models:
- `llama3.2` - Fast, accurate (recommended)
- `qwen2.5-coder` - Great for data analysis
- `mistral` - Detailed analysis
- `llama3.1` - Latest Llama model

### Adjust Temperature

```python
# In ollama_rule_scanner.py, modify _query_ollama()
"options": {
    "temperature": 0.1,  # Lower = more consistent
    "top_p": 0.9
}
```

### Custom System Prompt

Modify the `system_prompt` in `scan_account()` method to customize analysis behavior.

---

## Integration Examples

### 1. Real-Time Monitoring

```python
import asyncio
from src.ollama_rule_scanner import scan_mt5_account

async def monitor_account():
    while True:
        report = await scan_mt5_account(
            token=SESSION_TOKEN,
            firm_name="FTMO"
        )
        
        # Alert on critical violations
        if report['violation_count']['critical'] > 0:
            send_alert(report)
        
        await asyncio.sleep(300)  # Check every 5 minutes

asyncio.run(monitor_account())
```

### 2. Batch Analysis

```python
accounts = ["token1", "token2", "token3"]

for token in accounts:
    report = await scan_mt5_account(token=token)
    save_to_database(report)
```

### 3. Web Dashboard

```python
from fastapi import FastAPI
from src.ollama_rule_scanner import OllamaRuleScanner

app = FastAPI()

@app.get("/scan/{account_id}")
async def scan_account(account_id: str):
    scanner = OllamaRuleScanner()
    account_data = get_account_data(account_id)
    report = scanner.scan_account(account_data)
    return report
```

---

## Performance

### Typical Scan Times

| Component | Time |
|-----------|------|
| Database query | ~50ms |
| LLM analysis | 2-5s |
| Report generation | ~10ms |
| **Total** | **2-5s** |

### Optimization Tips

1. **Use faster models**: `llama3.2` over `mistral`
2. **Limit context**: Reduce number of documents analyzed
3. **Cache rules**: Load database rules once, reuse
4. **Parallel scans**: Use asyncio for multiple accounts

---

## Troubleshooting

### Ollama Not Running

```bash
# Start Ollama
ollama serve

# Check status
curl http://localhost:11434/api/tags
```

### No Models Available

```bash
# Pull a model
ollama pull llama3.2
```

### Database Not Found

```bash
# Check database exists
ls propfirm_scraper.db

# Populate database
python database/ingest_documents.py
python database/extract_rules.py
```

### MT5 API Connection Failed

```bash
# Start API server
python run_mt5_api.py

# Verify server running
curl http://localhost:8000/health
```

### JSON Parsing Errors

If LLM doesn't return valid JSON:
1. Try different model (qwen2.5-coder is good)
2. Reduce context (fewer rules/documents)
3. Adjust temperature (lower = more consistent)

---

## Roadmap

### Planned Features

- [ ] Email/Slack notifications for violations
- [ ] Historical violation tracking
- [ ] Trend analysis (recurring violations)
- [ ] Multi-account dashboard
- [ ] Custom rule builder UI
- [ ] PDF report generation
- [ ] Telegram bot integration
- [ ] Risk score calculation
- [ ] Predictive violation warnings

---

## Contributing

Improve the scanner:

1. **Add rule templates** - Contribute common rule patterns
2. **Improve prompts** - Better system prompts for accuracy
3. **Add integrations** - Connect to more platforms
4. **Optimize performance** - Faster analysis methods

---

## License

MIT License - See LICENSE file

---

## Support

- **Documentation**: `/docs`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

**Built with ❤️ for prop traders**
