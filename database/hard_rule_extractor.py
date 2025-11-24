"""
Hard rule extractor using regex patterns.
Extracts numeric and explicit rules from text.
"""
import re
from typing import Dict, List, Tuple, Any
from rule_patterns import *


class HardRuleExtractor:
    """Extract hard (explicit) rules using regex patterns."""
    
    def __init__(self):
        self.extracted_rules = []
    
    def extract_all(self, text: str, title: str = "", url: str = "") -> List[Dict[str, Any]]:
        """
        Extract all hard rules from text.
        
        Args:
            text: Document text
            title: Document title
            url: Document URL
            
        Returns:
            List of extracted rules with metadata
        """
        rules = []
        
        # Extract profit targets
        rules.extend(self._extract_profit_targets(text))
        
        # Extract daily loss limits
        rules.extend(self._extract_daily_loss(text))
        
        # Extract max drawdown
        rules.extend(self._extract_max_drawdown(text))
        
        # Extract trailing drawdown
        rules.extend(self._extract_trailing_drawdown(text))
        
        # Extract profit split
        rules.extend(self._extract_profit_split(text))
        
        # Extract trading days
        rules.extend(self._extract_min_trading_days(text))
        rules.extend(self._extract_max_trading_days(text))
        
        # Extract leverage
        rules.extend(self._extract_leverage(text))
        
        # Extract account sizes
        rules.extend(self._extract_account_sizes(text))
        
        # Extract EA permissions
        rules.extend(self._extract_ea_permissions(text))
        
        # Extract copy trading rules
        rules.extend(self._extract_copy_trading(text))
        
        # Extract hedging rules
        rules.extend(self._extract_hedging(text))
        
        # Extract weekend holding
        rules.extend(self._extract_weekend_holding(text))
        
        # Extract news trading
        rules.extend(self._extract_news_trading(text))
        
        # Extract consistency rules
        rules.extend(self._extract_consistency(text))
        
        # Extract lot size limits
        rules.extend(self._extract_lot_size(text))
        
        # Extract margin limits
        rules.extend(self._extract_margin_limits(text))
        
        # Extract payout rules
        rules.extend(self._extract_payout_rules(text))
        
        # Extract prohibited strategies
        rules.extend(self._extract_prohibited_strategies(text))
        
        # Add metadata to all rules
        for rule in rules:
            rule['source_title'] = title
            rule['source_url'] = url
        
        return rules
    
    def _extract_profit_targets(self, text: str) -> List[Dict]:
        """Extract profit target percentages."""
        rules = []
        matches = extract_with_pattern(text, PROFIT_TARGET_PATTERNS)
        
        for value, context in matches:
            rules.append({
                'rule_type': 'profit_target',
                'rule_code': 'PROFIT_TARGET',
                'value': f"{value}%",
                'description': f"Profit target of {value}%",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'performance',
            })
        
        return rules
    
    def _extract_daily_loss(self, text: str) -> List[Dict]:
        """Extract daily loss limit percentages."""
        rules = []
        matches = extract_with_pattern(text, DAILY_LOSS_PATTERNS)
        
        for value, context in matches:
            rules.append({
                'rule_type': 'daily_loss_limit',
                'rule_code': 'DAILY_LOSS',
                'value': f"{value}%",
                'description': f"Daily loss limit of {value}%",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'risk',
            })
        
        return rules
    
    def _extract_max_drawdown(self, text: str) -> List[Dict]:
        """Extract maximum drawdown percentages."""
        rules = []
        matches = extract_with_pattern(text, MAX_DRAWDOWN_PATTERNS)
        
        for value, context in matches:
            rules.append({
                'rule_type': 'max_drawdown',
                'rule_code': 'MAX_DRAWDOWN',
                'value': f"{value}%",
                'description': f"Maximum drawdown of {value}%",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'risk',
            })
        
        return rules
    
    def _extract_trailing_drawdown(self, text: str) -> List[Dict]:
        """Extract trailing drawdown rules."""
        rules = []
        matches = extract_with_pattern(text, TRAILING_DRAWDOWN_PATTERNS)
        
        for value, context in matches:
            rules.append({
                'rule_type': 'trailing_drawdown',
                'rule_code': 'TRAILING_DRAWDOWN',
                'value': f"{value}%",
                'description': f"Trailing drawdown of {value}%",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'risk',
            })
        
        return rules
    
    def _extract_profit_split(self, text: str) -> List[Dict]:
        """Extract profit split percentages."""
        rules = []
        matches = extract_with_pattern(text, PROFIT_SPLIT_PATTERNS)
        
        for value, context in matches:
            rules.append({
                'rule_type': 'profit_split',
                'rule_code': 'PROFIT_SPLIT',
                'value': f"{value}%",
                'description': f"Profit split of {value}% for trader",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'payout',
            })
        
        return rules
    
    def _extract_min_trading_days(self, text: str) -> List[Dict]:
        """Extract minimum trading days requirement."""
        rules = []
        matches = extract_with_pattern(text, MIN_TRADING_DAYS_PATTERNS)
        
        for value, context in matches:
            rules.append({
                'rule_type': 'min_trading_days',
                'rule_code': 'MIN_DAYS',
                'value': value,
                'description': f"Minimum {value} trading days required",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'requirements',
            })
        
        return rules
    
    def _extract_max_trading_days(self, text: str) -> List[Dict]:
        """Extract maximum trading days limit."""
        rules = []
        matches = extract_with_pattern(text, MAX_TRADING_DAYS_PATTERNS)
        
        for value, context in matches:
            rules.append({
                'rule_type': 'max_trading_days',
                'rule_code': 'MAX_DAYS',
                'value': value,
                'description': f"Maximum {value} trading days to complete challenge",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'requirements',
            })
        
        return rules
    
    def _extract_leverage(self, text: str) -> List[Dict]:
        """Extract leverage ratios."""
        rules = []
        matches = extract_with_pattern(text, LEVERAGE_PATTERNS)
        
        for value, context in matches:
            rules.append({
                'rule_type': 'leverage',
                'rule_code': 'LEVERAGE',
                'value': f"1:{value}",
                'description': f"Leverage ratio of 1:{value}",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'trading_conditions',
            })
        
        return rules
    
    def _extract_account_sizes(self, text: str) -> List[Dict]:
        """Extract available account sizes."""
        rules = []
        matches = extract_with_pattern(text, ACCOUNT_SIZE_PATTERNS)
        
        for value, context in matches:
            # Clean value
            clean_value = value.replace(',', '')
            if 'k' in value.lower():
                clean_value = str(int(float(clean_value.replace('k', '').replace('K', '')) * 1000))
            
            rules.append({
                'rule_type': 'account_size',
                'rule_code': 'ACCOUNT_SIZE',
                'value': f"${clean_value}",
                'description': f"Account size option: ${clean_value}",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'account_options',
            })
        
        return rules
    
    def _extract_ea_permissions(self, text: str) -> List[Dict]:
        """Extract EA (Expert Advisor) permissions."""
        rules = []
        matches = extract_with_pattern(text, EA_PATTERNS)
        
        for value, context in matches:
            permission = classify_permission(context)
            
            rules.append({
                'rule_type': 'ea_permission',
                'rule_code': 'EA_ALLOWED' if permission == 'allowed' else 'EA_PROHIBITED',
                'value': permission,
                'description': f"Expert Advisors (EAs) are {permission}",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'trading_permissions',
            })
        
        return rules
    
    def _extract_copy_trading(self, text: str) -> List[Dict]:
        """Extract copy trading rules."""
        rules = []
        matches = extract_with_pattern(text, COPY_TRADING_PATTERNS)
        
        for value, context in matches:
            permission = classify_permission(context)
            
            rules.append({
                'rule_type': 'copy_trading',
                'rule_code': 'COPY_PROHIBITED' if permission == 'prohibited' else 'COPY_ALLOWED',
                'value': permission,
                'description': f"Copy trading is {permission}",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'prohibited_strategies',
            })
        
        return rules
    
    def _extract_hedging(self, text: str) -> List[Dict]:
        """Extract hedging rules."""
        rules = []
        matches = extract_with_pattern(text, HEDGING_PATTERNS)
        
        for value, context in matches:
            permission = classify_permission(context)
            
            # Check for cross-account hedging specifically
            if 'cross' in context.lower() and 'account' in context.lower():
                rules.append({
                    'rule_type': 'hedging',
                    'rule_code': 'CROSS_HEDGE_PROHIBITED',
                    'value': 'prohibited',
                    'description': "Cross-account hedging is prohibited",
                    'raw_span': context,
                    'is_soft_rule': False,
                    'category': 'prohibited_strategies',
                })
            else:
                rules.append({
                    'rule_type': 'hedging',
                    'rule_code': 'HEDGE_' + permission.upper(),
                    'value': permission,
                    'description': f"Hedging is {permission}",
                    'raw_span': context,
                    'is_soft_rule': False,
                    'category': 'trading_permissions',
                })
        
        return rules
    
    def _extract_weekend_holding(self, text: str) -> List[Dict]:
        """Extract weekend position holding rules."""
        rules = []
        matches = extract_with_pattern(text, WEEKEND_HOLDING_PATTERNS)
        
        for value, context in matches:
            permission = classify_permission(context)
            
            rules.append({
                'rule_type': 'weekend_holding',
                'rule_code': 'WEEKEND_' + permission.upper(),
                'value': permission,
                'description': f"Weekend position holding is {permission}",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'trading_permissions',
            })
        
        return rules
    
    def _extract_news_trading(self, text: str) -> List[Dict]:
        """Extract news trading rules."""
        rules = []
        matches = extract_with_pattern(text, NEWS_TRADING_PATTERNS)
        
        for value, context in matches:
            permission = classify_permission(context)
            
            rules.append({
                'rule_type': 'news_trading',
                'rule_code': 'NEWS_' + permission.upper(),
                'value': permission,
                'description': f"News trading is {permission}",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'trading_restrictions',
            })
        
        return rules
    
    def _extract_consistency(self, text: str) -> List[Dict]:
        """Extract consistency rules."""
        rules = []
        matches = extract_with_pattern(text, CONSISTENCY_PATTERNS)
        
        for value, context in matches:
            rules.append({
                'rule_type': 'consistency_rule',
                'rule_code': 'CONSISTENCY',
                'value': f"{value}%",
                'description': f"No single day should exceed {value}% of total profit",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'behavioral',
            })
        
        return rules
    
    def _extract_lot_size(self, text: str) -> List[Dict]:
        """Extract lot size limits."""
        rules = []
        matches = extract_with_pattern(text, LOT_SIZE_PATTERNS)
        
        for value, context in matches:
            rules.append({
                'rule_type': 'lot_size_limit',
                'rule_code': 'LOT_SIZE',
                'value': value,
                'description': f"Maximum lot size: {value} lots",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'trading_restrictions',
            })
        
        return rules
    
    def _extract_margin_limits(self, text: str) -> List[Dict]:
        """Extract margin usage limits."""
        rules = []
        matches = extract_with_pattern(text, MARGIN_PATTERNS)
        
        for value, context in matches:
            rules.append({
                'rule_type': 'margin_limit',
                'rule_code': 'MARGIN_LIMIT',
                'value': f"{value}%",
                'description': f"Maximum margin usage: {value}%",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'risk',
            })
        
        return rules
    
    def _extract_payout_rules(self, text: str) -> List[Dict]:
        """Extract payout-related rules."""
        rules = []
        
        # Minimum payout
        min_matches = extract_with_pattern(text, MIN_PAYOUT_PATTERNS)
        for value, context in min_matches:
            clean_value = value.replace(',', '')
            rules.append({
                'rule_type': 'min_payout',
                'rule_code': 'MIN_PAYOUT',
                'value': f"${clean_value}",
                'description': f"Minimum payout amount: ${clean_value}",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'payout',
            })
        
        # Payout frequency
        freq_matches = extract_with_pattern(text, PAYOUT_FREQUENCY_PATTERNS)
        for value, context in freq_matches:
            rules.append({
                'rule_type': 'payout_frequency',
                'rule_code': 'PAYOUT_FREQ',
                'value': value,
                'description': f"Payout frequency: {value}",
                'raw_span': context,
                'is_soft_rule': False,
                'category': 'payout',
            })
        
        return rules
    
    def _extract_prohibited_strategies(self, text: str) -> List[Dict]:
        """Extract prohibited trading strategies."""
        rules = []
        matches = check_keyword_presence(text, PROHIBITED_STRATEGIES)
        
        for keyword, context in matches:
            # Check if it's actually prohibited or just mentioned
            if any(word in context.lower() for word in ['prohibited', 'not allowed', 'forbidden', 'strictly']):
                rules.append({
                    'rule_type': 'prohibited_strategy',
                    'rule_code': 'PROHIBITED_' + keyword.upper().replace(' ', '_'),
                    'value': keyword,
                    'description': f"{keyword.title()} is prohibited",
                    'raw_span': context,
                    'is_soft_rule': False,
                    'category': 'prohibited_strategies',
                })
        
        return rules


def deduplicate_rules(rules: List[Dict]) -> List[Dict]:
    """
    Remove duplicate rules based on rule_type, value, and context similarity.
    
    Args:
        rules: List of extracted rules
        
    Returns:
        Deduplicated list of rules
    """
    seen = set()
    unique_rules = []
    
    for rule in rules:
        # Create signature for deduplication
        sig = (rule['rule_type'], rule.get('value', ''), rule.get('raw_span', '')[:50])
        
        if sig not in seen:
            seen.add(sig)
            unique_rules.append(rule)
    
    return unique_rules


if __name__ == "__main__":
    # Test the extractor
    test_text = """
    The Stellar 1-Step Challenge has the following rules:
    
    - Profit Target: 10%
    - Daily Loss Limit: 5%
    - Maximum Drawdown: 10%
    - Minimum Trading Days: 5 days
    - Leverage: 1:100
    - Expert Advisors (EAs) are allowed
    - Copy trading is strictly prohibited
    - Hedging is allowed within the same account only
    - You can hold positions over the weekend
    - News trading is restricted during major announcements
    - Account sizes: $5,000, $10,000, $25,000, $50,000, $100,000
    - Profit split: Up to 90%
    
    Prohibited strategies include: tick scalping, HFT, martingale, grid trading.
    """
    
    extractor = HardRuleExtractor()
    rules = extractor.extract_all(test_text, "Test Document", "https://test.com")
    rules = deduplicate_rules(rules)
    
    print(f"\nExtracted {len(rules)} unique rules:\n")
    for rule in rules[:10]:
        print(f"• {rule['rule_code']}: {rule['description']}")
        print(f"  Category: {rule['category']}")
        print(f"  Context: {rule['raw_span'][:80]}...")
        print()
