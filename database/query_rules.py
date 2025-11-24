"""Query extracted rules from database."""
from rule_storage import RuleStorage
from query_db import DocumentDatabase

# Connect
db = DocumentDatabase('propfirm_scraper.db')
rs = RuleStorage('propfirm_scraper.db')
rs.connect()

# Get firm
firm = db.get_firm_by_name('FundedNext')
firm_id = firm['id']

print("="*70)
print("CRITICAL RULES")
print("="*70)
critical = rs.get_critical_rules(firm_id)
for rule in critical[:10]:
    print(f"\n{rule['rule_type']} ({rule['rule_category']})")
    print(f"  Value: {rule.get('value', 'N/A')}")
    print(f"  Details: {rule.get('details', 'N/A')[:80]}")
    print(f"  Challenge: {rule['challenge_type']}")

print("\n" + "="*70)
print("PROFIT TARGET RULES")
print("="*70)
profit_rules = [r for r in rs.get_rules_for_firm(firm_id) 
                if 'profit_target' in r['rule_type']]
for rule in profit_rules[:10]:
    print(f"\n{rule['rule_type']}")
    print(f"  Value: {rule.get('value', 'N/A')}")
    print(f"  Details: {rule.get('details', 'N/A')[:80]}")
    print(f"  Challenge: {rule['challenge_type']}")

print("\n" + "="*70)
print("PROHIBITED STRATEGIES")
print("="*70)
prohibited = [r for r in rs.get_rules_for_firm(firm_id) 
              if r['rule_category'] == 'prohibited_strategies']
for rule in prohibited[:15]:
    print(f"\n{rule['rule_type']}")
    print(f"  Value: {rule.get('value', 'N/A')}")
    print(f"  Details: {rule.get('details', 'N/A')[:80]}")

print("\n" + "="*70)
print("EA & COPY TRADING PERMISSIONS")
print("="*70)
ea_rules = [r for r in rs.get_rules_for_firm(firm_id) 
            if 'ea_' in r['rule_type'] or 'copy_' in r['rule_type']]
for rule in ea_rules[:10]:
    print(f"\n{rule['rule_type']}")
    print(f"  Value: {rule.get('value', 'N/A')}")
    print(f"  Details: {rule.get('details', 'N/A')[:80]}")
    print(f"  Challenge: {rule['challenge_type']}")

# Close
rs.close()
db.close()
