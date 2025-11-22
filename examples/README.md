# Examples

This directory contains example scripts demonstrating the prop-risk-monitor features.

## test_rules_offline.py

**Demonstrates pure logic rules engine testing without API dependencies.**

Run with:
```bash
python examples/test_rules_offline.py
```

Or with proper Python path:
```bash
set PYTHONPATH=%CD%
python examples/test_rules_offline.py
```

### Example Output

The script shows 8 different scenarios with rich console formatting:

#### Example 1: Clean Account ✅
```
Balance: $100,000.00
Daily P&L: $500.00
Breaches: 0
✅ All rules passed!
```

#### Example 2: Daily Drawdown Warning ⚠️
```
Balance: $100,000.00
Daily P&L: $-4,200.00 (-4.20%)
Breaches: 1
╭─────────────────────────────────────────────────────╮
│ FTMO-Example:                                       │
│ WARN DAILY_DD – ⚠️ Daily DD warning: -4.20%         │
│                 approaching -5.0%                   │
╰─────────────────────────────────────────────────────╯
```

#### Example 3: Daily Drawdown VIOLATION 🚨
```
Balance: $100,000.00
Daily P&L: $-5,500.00 (-5.50%)
Breaches: 1
╭─────────────────────────────────────────────────────╮
│ FTMO-Example:                                       │
│ HARD DAILY_DD – 🚨 Daily DD limit breached:         │
│                 -5.50% <= -5.0%                     │
╰─────────────────────────────────────────────────────╯
```

#### Example 7: Multiple Violations 🚨🚨🚨
```
Starting Balance: $100,000.00
Current Balance: $88,000.00
Daily P&L: $-6,000.00 (-6.82%)
Total DD: -12.00%
Open Positions: 12
Total Lots: 18.00

Breaches: 4
╭─────────────────────────────────────────────────────╮
│ FTMO-Example:                                       │
│ HARD DAILY_DD – 🚨 Daily DD limit breached          │
│ HARD TOTAL_DD – 🚨 Total DD limit breached          │
│ WARN MAX_LOTS – ⚠️ Open lots warning                │
│ WARN MAX_POSITIONS – ⚠️ Position count exceeds      │
╰─────────────────────────────────────────────────────╯
```

### Key Features Demonstrated

1. **Pure Logic Testing**: No API connections required
2. **Rich Console Output**: Color-coded panels and formatted messages
3. **Warning vs Hard Limits**: 
   - WARN (🟡) triggers at 80% of limit
   - HARD (🔴) triggers at 100% of limit
4. **Multiple Breach Detection**: Catches all violations in single check
5. **Different Firm Rules**: Compare FTMO vs Alpha Capital rules
6. **Dummy Data Creation**: `create_test_snapshot()` helper function

### All Examples

1. **Clean Account** - No violations
2. **Daily DD Warning** - Approaching 5% limit
3. **Daily DD Violation** - Exceeded 5% limit
4. **Total DD Violation** - Exceeded 10% max drawdown
5. **Oversized Position** - Single position too large
6. **Too Many Lots** - Total lot size exceeded
7. **Multiple Violations** - Disaster scenario
8. **Different Firm Rules** - Compare FTMO vs Alpha Capital

## test_api.py

Tests cTrader Open API connection (REST).

```bash
python examples/test_api.py
```

## test_mt5.py

Tests MetaTrader 5 terminal connection.

```bash
python examples/test_mt5.py
```

## Quick Testing Workflow

1. **Test offline first** (no API):
   ```bash
   python examples/test_rules_offline.py
   ```

2. **Test API connection**:
   ```bash
   python examples/test_api.py    # or test_mt5.py
   ```

3. **Run unit tests**:
   ```bash
   python -m pytest tests/
   ```

4. **Start monitoring**:
   ```bash
   python -m src.runner
   ```

## Creating Your Own Test Scenarios

Use the `create_test_snapshot()` helper:

```python
from datetime import datetime
from src.models import AccountSnapshot, Position
from src.config import FTMO_RULES
from src.rules import check_account_rules
from src.notifier import notify_console

# Create custom scenario
snapshot = create_test_snapshot(
    balance=50000.0,
    daily_pnl=-2000.0,  # -4% loss
    positions=[],
    starting_balance=50000.0
)

# Check rules
breaches = check_account_rules(snapshot, FTMO_RULES)

# Display results
if breaches:
    notify_console("My-Account", breaches)
else:
    print("✅ All rules passed!")
```

This makes it easy to:
- Test edge cases
- Validate rule logic
- Debug breach detection
- Demo to stakeholders
- Train new users
