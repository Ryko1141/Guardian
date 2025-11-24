"""
Database storage module for firm rules.
Handles insertion and management of extracted rules in the firm_rule table.
"""
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime


class RuleStorage:
    """Store and manage extracted rules in database."""
    
    def __init__(self, db_path='propfirm_scraper.db'):
        """
        Initialize rule storage.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        print(f"[OK] Connected to database: {self.db_path}")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print("[OK] Database connection closed")
    
    def insert_rule(self, firm_id: int, rule: Dict[str, Any], 
                   source_document_id: Optional[int] = None) -> int:
        """
        Insert a single rule into the database.
        
        Args:
            firm_id: Firm database ID
            rule: Rule dictionary with extracted data
            source_document_id: Optional document ID this rule came from
            
        Returns:
            Inserted rule ID
        """
        try:
            self.cursor.execute(
                """
                INSERT INTO firm_rule (
                    firm_id, source_document_id, rule_type, rule_category,
                    challenge_type, value, details, conditions, severity,
                    extracted_at, extraction_method, confidence_score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    firm_id,
                    source_document_id,
                    rule.get('rule_type', 'unknown'),
                    rule.get('category', 'general'),
                    rule.get('challenge_type', 'general'),
                    rule.get('value', ''),
                    rule.get('description', ''),
                    rule.get('raw_span', ''),  # Store context in conditions field
                    self._determine_severity(rule),
                    datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    rule.get('extraction_method', 'pattern'),
                    rule.get('confidence', 1.0 if not rule.get('is_soft_rule') else 0.7)
                )
            )
            
            return self.cursor.lastrowid
            
        except sqlite3.Error as e:
            print(f"  [ERROR] Error inserting rule: {e}")
            return 0
    
    def insert_rules_batch(self, firm_id: int, rules: List[Dict[str, Any]],
                          source_document_id: Optional[int] = None) -> int:
        """
        Insert multiple rules in batch.
        
        Args:
            firm_id: Firm database ID
            rules: List of rule dictionaries
            source_document_id: Optional document ID
            
        Returns:
            Number of rules inserted
        """
        inserted = 0
        
        for rule in rules:
            rule_id = self.insert_rule(firm_id, rule, source_document_id)
            if rule_id > 0:
                inserted += 1
        
        self.conn.commit()
        return inserted
    
    def _determine_severity(self, rule: Dict) -> str:
        """
        Determine rule severity based on type and category.
        
        Args:
            rule: Rule dictionary
            
        Returns:
            Severity: 'critical', 'important', or 'optional'
        """
        rule_type = rule.get('rule_type', '')
        category = rule.get('category', '')
        is_soft = rule.get('is_soft_rule', False)
        
        # Critical rules (hard limits that can cause account breach)
        critical_types = [
            'daily_loss_limit', 'max_drawdown', 'trailing_drawdown',
            'prohibited_strategy', 'copy_trading'
        ]
        
        if any(t in rule_type for t in critical_types):
            return 'critical'
        
        # Important rules (requirements and restrictions)
        important_types = [
            'profit_target', 'min_trading_days', 'leverage',
            'ea_permission', 'hedging', 'news_trading'
        ]
        
        if any(t in rule_type for t in important_types):
            return 'important'
        
        # Soft rules are generally optional guidelines
        if is_soft:
            return 'optional'
        
        # Default based on category
        if category in ['risk', 'prohibited_strategies']:
            return 'critical'
        elif category in ['requirements', 'trading_permissions']:
            return 'important'
        else:
            return 'optional'
    
    def get_rules_for_firm(self, firm_id: int, challenge_type: Optional[str] = None) -> List[Dict]:
        """
        Get all rules for a specific firm.
        
        Args:
            firm_id: Firm database ID
            challenge_type: Optional filter by challenge type
            
        Returns:
            List of rules
        """
        if challenge_type:
            self.cursor.execute(
                """
                SELECT * FROM firm_rule
                WHERE firm_id = ? AND challenge_type = ?
                ORDER BY severity DESC, rule_type
                """,
                (firm_id, challenge_type)
            )
        else:
            self.cursor.execute(
                """
                SELECT * FROM firm_rule
                WHERE firm_id = ?
                ORDER BY severity DESC, rule_type
                """,
                (firm_id,)
            )
        
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def get_rules_by_type(self, firm_id: int, rule_type: str) -> List[Dict]:
        """Get rules of a specific type."""
        self.cursor.execute(
            """
            SELECT * FROM firm_rule
            WHERE firm_id = ? AND rule_type = ?
            ORDER BY extracted_at DESC
            """,
            (firm_id, rule_type)
        )
        
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def get_critical_rules(self, firm_id: int) -> List[Dict]:
        """Get all critical rules for a firm."""
        self.cursor.execute(
            """
            SELECT * FROM firm_rule
            WHERE firm_id = ? AND severity = 'critical'
            ORDER BY rule_type
            """,
            (firm_id,)
        )
        
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def delete_rules_for_firm(self, firm_id: int) -> int:
        """
        Delete all rules for a firm (e.g., before re-extraction).
        
        Args:
            firm_id: Firm database ID
            
        Returns:
            Number of rules deleted
        """
        self.cursor.execute("SELECT COUNT(*) FROM firm_rule WHERE firm_id = ?", (firm_id,))
        count = self.cursor.fetchone()[0]
        
        self.cursor.execute("DELETE FROM firm_rule WHERE firm_id = ?", (firm_id,))
        self.conn.commit()
        
        return count
    
    def get_rule_statistics(self, firm_id: int) -> Dict[str, Any]:
        """
        Get statistics about extracted rules.
        
        Args:
            firm_id: Firm database ID
            
        Returns:
            Dictionary with statistics
        """
        stats = {}
        
        # Total rules
        self.cursor.execute("SELECT COUNT(*) FROM firm_rule WHERE firm_id = ?", (firm_id,))
        stats['total_rules'] = self.cursor.fetchone()[0]
        
        # By severity
        self.cursor.execute(
            """
            SELECT severity, COUNT(*) as count
            FROM firm_rule
            WHERE firm_id = ?
            GROUP BY severity
            """,
            (firm_id,)
        )
        stats['by_severity'] = dict(self.cursor.fetchall())
        
        # By category
        self.cursor.execute(
            """
            SELECT rule_category, COUNT(*) as count
            FROM firm_rule
            WHERE firm_id = ?
            GROUP BY rule_category
            """,
            (firm_id,)
        )
        stats['by_category'] = dict(self.cursor.fetchall())
        
        # By challenge type
        self.cursor.execute(
            """
            SELECT challenge_type, COUNT(*) as count
            FROM firm_rule
            WHERE firm_id = ?
            GROUP BY challenge_type
            """,
            (firm_id,)
        )
        stats['by_challenge_type'] = dict(self.cursor.fetchall())
        
        # By extraction method
        self.cursor.execute(
            """
            SELECT extraction_method, COUNT(*) as count
            FROM firm_rule
            WHERE firm_id = ?
            GROUP BY extraction_method
            """,
            (firm_id,)
        )
        stats['by_extraction_method'] = dict(self.cursor.fetchall())
        
        return stats
    
    def print_rule_summary(self, firm_id: int):
        """Print a summary of rules for a firm."""
        stats = self.get_rule_statistics(firm_id)
        
        print(f"\n{'='*70}")
        print("RULE EXTRACTION SUMMARY")
        print(f"{'='*70}\n")
        
        print(f"Total Rules: {stats['total_rules']}\n")
        
        print("By Severity:")
        for severity, count in stats.get('by_severity', {}).items():
            print(f"  {severity:12} {count:4} rules")
        
        print("\nBy Category:")
        for category, count in stats.get('by_category', {}).items():
            print(f"  {category:25} {count:4} rules")
        
        print("\nBy Challenge Type:")
        for challenge, count in stats.get('by_challenge_type', {}).items():
            print(f"  {challenge:20} {count:4} rules")
        
        print("\nBy Extraction Method:")
        for method, count in stats.get('by_extraction_method', {}).items():
            print(f"  {method:12} {count:4} rules")
        
        print(f"\n{'='*70}\n")
    
    def export_rules_to_json(self, firm_id: int, output_file: str):
        """Export rules to JSON file."""
        import json
        
        rules = self.get_rules_for_firm(firm_id)
        
        # Convert datetime objects to strings
        for rule in rules:
            if 'extracted_at' in rule and rule['extracted_at']:
                rule['extracted_at'] = str(rule['extracted_at'])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Exported {len(rules)} rules to {output_file}")


if __name__ == "__main__":
    # Test the storage module
    storage = RuleStorage()
    storage.connect()
    
    # Test rule insertion
    test_rule = {
        'rule_type': 'profit_target',
        'rule_code': 'PROFIT_TARGET',
        'value': '10%',
        'description': 'Profit target of 10%',
        'raw_span': 'The profit target for this challenge is 10%',
        'is_soft_rule': False,
        'category': 'performance',
        'challenge_type': 'stellar_1_step',
    }
    
    # Get FundedNext firm ID
    storage.cursor.execute("SELECT id FROM prop_firm WHERE name = 'FundedNext'")
    result = storage.cursor.fetchone()
    
    if result:
        firm_id = result[0]
        
        # Insert test rule
        rule_id = storage.insert_rule(firm_id, test_rule)
        if rule_id > 0:
            print(f"[OK] Test rule inserted with ID: {rule_id}")
            
            # Get statistics
            storage.print_rule_summary(firm_id)
            
            # Clean up test rule
            storage.cursor.execute("DELETE FROM firm_rule WHERE id = ?", (rule_id,))
            storage.conn.commit()
            print("[OK] Test rule cleaned up")
    else:
        print("[ERROR] FundedNext firm not found in database")
    
    storage.close()
