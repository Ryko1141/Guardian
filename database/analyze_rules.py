"""Analyze and visualize extracted rules."""
from rule_storage import RuleStorage
from query_db import DocumentDatabase
from collections import Counter

# Connect
db = DocumentDatabase('propfirm_scraper.db')
rs = RuleStorage('propfirm_scraper.db')
rs.connect()

# Get firm
firm = db.get_firm_by_name('FundedNext')
firm_id = firm['id']

# Get all rules
all_rules = rs.get_rules_for_firm(firm_id)

print("="*70)
print(f"FUNDEDNEXT RULE ANALYSIS - {len(all_rules)} Total Rules")
print("="*70)

# Analyze by rule type
rule_types = Counter(r['rule_type'] for r in all_rules)
print("\n" + "="*70)
print("TOP 20 RULE TYPES")
print("="*70)
for rule_type, count in rule_types.most_common(20):
    bar = "#" * (count // 5)
    print(f"{rule_type:30s} {count:3d} {bar}")

# Analyze permissions
print("\n" + "="*70)
print("PERMISSION RULES BREAKDOWN")
print("="*70)

ea_rules = [r for r in all_rules if r['rule_type'] == 'ea_permission']
ea_values = Counter(r['value'] for r in ea_rules)
print(f"\nEA Permissions ({len(ea_rules)} rules):")
for value, count in ea_values.most_common():
    print(f"  {value:12s}: {count:3d}")

copy_rules = [r for r in all_rules if r['rule_type'] == 'copy_trading']
copy_values = Counter(r['value'] for r in copy_rules)
print(f"\nCopy Trading ({len(copy_rules)} rules):")
for value, count in copy_values.most_common():
    print(f"  {value:12s}: {count:3d}")

hedge_rules = [r for r in all_rules if r['rule_type'] == 'hedging']
hedge_values = Counter(r['value'] for r in hedge_rules)
print(f"\nHedging ({len(hedge_rules)} rules):")
for value, count in hedge_values.most_common():
    print(f"  {value:12s}: {count:3d}")

# Analyze profit targets
print("\n" + "="*70)
print("PROFIT TARGET DISTRIBUTION")
print("="*70)
profit_rules = [r for r in all_rules if r['rule_type'] == 'profit_target']
profit_values = Counter(r['value'] for r in profit_rules)
print(f"\nProfit Targets ({len(profit_rules)} rules):")
for value, count in sorted(profit_values.items(), key=lambda x: float(x[0].rstrip('%')) if x[0].rstrip('%').replace('.','').isdigit() else 0):
    bar = "#" * count
    print(f"  {value:8s}: {count:3d} {bar}")

# Analyze loss limits
print("\n" + "="*70)
print("LOSS LIMIT DISTRIBUTION")
print("="*70)
daily_loss_rules = [r for r in all_rules if r['rule_type'] == 'daily_loss_limit']
daily_loss_values = Counter(r['value'] for r in daily_loss_rules)
print(f"\nDaily Loss Limits ({len(daily_loss_rules)} rules):")
for value, count in sorted(daily_loss_values.items(), key=lambda x: float(x[0].rstrip('%')) if x[0].rstrip('%').replace('.','').isdigit() else 0):
    bar = "#" * count
    print(f"  {value:8s}: {count:3d} {bar}")

max_dd_rules = [r for r in all_rules if r['rule_type'] == 'max_drawdown']
max_dd_values = Counter(r['value'] for r in max_dd_rules)
print(f"\nMax Drawdown Limits ({len(max_dd_rules)} rules):")
for value, count in sorted(max_dd_values.items(), key=lambda x: float(x[0].rstrip('%')) if x[0].rstrip('%').replace('.','').isdigit() else 0):
    bar = "#" * count
    print(f"  {value:8s}: {count:3d} {bar}")

# Analyze account sizes
print("\n" + "="*70)
print("ACCOUNT SIZE OPTIONS")
print("="*70)
size_rules = [r for r in all_rules if r['rule_type'] == 'account_size']
size_values = Counter(r['value'] for r in size_rules)
print(f"\nAccount Sizes ({len(size_rules)} rules):")
for value, count in sorted(size_values.items(), key=lambda x: float(x[0].lstrip('$').replace('K', '000').replace(',', '')) if any(c.isdigit() for c in x[0]) else 0):
    print(f"  {value:10s}: {count:3d}")

# Analyze by challenge type
print("\n" + "="*70)
print("RULES BY CHALLENGE TYPE")
print("="*70)
challenge_rules = Counter(r['challenge_type'] for r in all_rules)
for challenge, count in challenge_rules.most_common():
    pct = count / len(all_rules) * 100
    bar = "#" * (count // 10)
    print(f"{challenge:20s} {count:3d} ({pct:5.1f}%) {bar}")

# Documents with most rules
print("\n" + "="*70)
print("TOP DOCUMENTS BY RULE COUNT")
print("="*70)
doc_rules = Counter(r['source_document_id'] for r in all_rules if r['source_document_id'])

# Get document info via SQL
import sqlite3
conn = sqlite3.connect('propfirm_scraper.db')
cursor = conn.cursor()
for doc_id, count in doc_rules.most_common(10):
    cursor.execute("SELECT title FROM help_document WHERE id = ?", (doc_id,))
    result = cursor.fetchone()
    if result:
        print(f"{count:3d} rules: {result[0][:60]}")
conn.close()

print("\n" + "="*70)

# Close
rs.close()
db.close()
