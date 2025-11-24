"""Quick script to export rules to JSON."""
from rule_storage import RuleStorage
from query_db import DocumentDatabase

# Connect
db = DocumentDatabase('propfirm_scraper.db')
rs = RuleStorage('propfirm_scraper.db')
rs.connect()

# Get firm
firm = db.get_firm_by_name('FundedNext')
print(f"Exporting rules for {firm['name']} (ID: {firm['id']})")

# Export
rs.export_rules_to_json(firm['id'], 'output/fundednext_rules.json')

# Close
rs.close()
db.close()

print("Done!")
