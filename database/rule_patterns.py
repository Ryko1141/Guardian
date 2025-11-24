"""
Enhanced regex patterns for comprehensive rule extraction.
Extends the original patterns.py with additional rule types.
"""
import re

# ============================================================================
# ACCOUNT SIZE PATTERNS
# ============================================================================
ACCOUNT_SIZE_PATTERNS = [
    r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:account|balance|capital)',
    r'(?:account|balance|capital)[:\s]+\$(\d{1,3}(?:,\d{3})*)',
    r'\$(\d+)k\s*(?:account|balance)',
    r'(\d+)k\s*(?:account|balance)',
]

# ============================================================================
# PROFIT TARGET PATTERNS
# ============================================================================
PROFIT_TARGET_PATTERNS = [
    r'(?:profit target|target profit|profit goal)[:\s]+(\d+(?:\.\d+)?)%',
    r'(\d+(?:\.\d+)?)%\s+(?:profit target|target)',
    r'achieve.*?(\d+(?:\.\d+)?)%.*?profit',
    r'reach.*?(\d+(?:\.\d+)?)%.*?profit',
]

# ============================================================================
# DAILY LOSS PATTERNS
# ============================================================================
DAILY_LOSS_PATTERNS = [
    r'daily loss limit[:\s]+(?:is[:\s]+)?(\d+(?:\.\d+)?)%',
    r'(\d+(?:\.\d+)?)%\s+daily loss',
    r'daily[:\s]+(?:loss|drawdown)[^\d]*(\d+(?:\.\d+)?)%',
    r'loss.*?per day[^\d]*(\d+(?:\.\d+)?)%',
]

# ============================================================================
# MAX DRAWDOWN PATTERNS
# ============================================================================
MAX_DRAWDOWN_PATTERNS = [
    r'max(?:imum)?[:\s]+(?:loss|drawdown)[^\d]+(\d+(?:\.\d+)?)%',
    r'(\d+(?:\.\d+)?)%\s+max(?:imum)?[:\s]+(?:loss|drawdown)',
    r'overall[:\s]+drawdown[^\d]+(\d+(?:\.\d+)?)%',
    r'total[:\s]+(?:loss|drawdown)[^\d]+(\d+(?:\.\d+)?)%',
]

# ============================================================================
# TRAILING DRAWDOWN PATTERNS
# ============================================================================
TRAILING_DRAWDOWN_PATTERNS = [
    r'trailing[:\s]+(?:drawdown|loss)[^\d]*(\d+(?:\.\d+)?)%',
    r'(\d+(?:\.\d+)?)%\s+trailing',
]

# ============================================================================
# PROFIT SPLIT PATTERNS
# ============================================================================
PROFIT_SPLIT_PATTERNS = [
    r'(?:profit split|reward share|profit share)[:\s]+(?:up to[:\s]+)?(\d+(?:\.\d+)?)%',
    r'(\d+(?:\.\d+)?)%\s+(?:profit split|reward share)',
    r'(?:you|trader)[^\d]+(?:receive|get|keep)[^\d]+(\d+(?:\.\d+)?)%',
]

# ============================================================================
# MINIMUM TRADING DAYS PATTERNS
# ============================================================================
MIN_TRADING_DAYS_PATTERNS = [
    r'(?:minimum|min)[:\s]+(\d+)\s+(?:trading\s+)?days?',
    r'(\d+)\s+(?:trading\s+)?days?\s+(?:minimum|required|needed)',
    r'at least[:\s]+(\d+)\s+(?:trading\s+)?days?',
    r'must trade[^\d]+(\d+)\s+days?',
]

# ============================================================================
# MAXIMUM TRADING DAYS PATTERNS
# ============================================================================
MAX_TRADING_DAYS_PATTERNS = [
    r'(?:maximum|max)[:\s]+(\d+)\s+(?:trading\s+)?days?',
    r'(\d+)\s+(?:trading\s+)?days?\s+(?:maximum|limit)',
    r'within[:\s]+(\d+)\s+(?:trading\s+)?days?',
    r'complete.*?(?:within|in)[:\s]+(\d+)\s+days?',
]

# ============================================================================
# LEVERAGE PATTERNS
# ============================================================================
LEVERAGE_PATTERNS = [
    r'(?:leverage|leverage ratio)[:\s]+1:(\d+)',
    r'1:(\d+)\s+leverage',
    r'(\d+):1\s+leverage',
]

# ============================================================================
# EA (EXPERT ADVISOR) PATTERNS
# ============================================================================
EA_PATTERNS = [
    r'(?:EA|expert advisor|automated trading|robot)[:\s]+(?:is\s+)?(?:allowed|permitted|yes)',
    r'(?:you\s+)?(?:can|may)\s+use\s+(?:EA|expert advisor|robot)',
    r'(?:EA|expert advisor|automated trading|robot)[:\s]+(?:is\s+)?(?:not allowed|prohibited|forbidden|no)',
]

# ============================================================================
# COPY TRADING PATTERNS
# ============================================================================
COPY_TRADING_PATTERNS = [
    r'copy trading[:\s]+(?:is\s+)?(?:not allowed|prohibited|forbidden|strictly prohibited)',
    r'(?:you\s+)?(?:cannot|must not|may not)\s+(?:use\s+)?copy trading',
    r'copy trading[:\s]+(?:is\s+)?(?:allowed|permitted)',
]

# ============================================================================
# HEDGING PATTERNS
# ============================================================================
HEDGING_PATTERNS = [
    r'hedging[:\s]+(?:is\s+)?(?:allowed|permitted)',
    r'(?:same\s+)?account hedging[:\s]+(?:allowed|permitted)',
    r'hedging[:\s]+(?:is\s+)?(?:not allowed|prohibited|forbidden)',
    r'cross[:\s-]+account hedging[:\s]+(?:prohibited|not allowed|forbidden)',
    r'hedging.*?(?:same account only|within same account)',
]

# ============================================================================
# WEEKEND HOLDING PATTERNS
# ============================================================================
WEEKEND_HOLDING_PATTERNS = [
    r'(?:hold|holding|keep).*?(?:position|trade).*?(?:over|during|through).*?weekend',
    r'weekend[:\s]+(?:hold|holding)[:\s]+(?:allowed|permitted|yes)',
    r'weekend[:\s]+(?:hold|holding)[:\s]+(?:not allowed|prohibited|no)',
    r'(?:positions|trades).*?(?:can|may|must).*?(?:be\s+)?(?:held|kept).*?(?:over|during)\s+weekend',
]

# ============================================================================
# NEWS TRADING PATTERNS
# ============================================================================
NEWS_TRADING_PATTERNS = [
    r'news trading[:\s]+(?:is\s+)?(?:not allowed|prohibited|restricted|forbidden)',
    r'(?:you\s+)?(?:cannot|must not|may not)\s+trade.*?(?:during|around)\s+news',
    r'news trading[:\s]+(?:is\s+)?(?:allowed|permitted)',
    r'(?:avoid|refrain from)\s+trading.*?(?:during|around|before|after)\s+news',
]

# ============================================================================
# CONSISTENCY RULE PATTERNS
# ============================================================================
CONSISTENCY_PATTERNS = [
    r'consistency rule[:\s]+(\d+(?:\.\d+)?)%',
    r'no single day.*?(?:more than|exceed).*?(\d+(?:\.\d+)?)%',
    r'maximum.*?(\d+(?:\.\d+)?)%.*?(?:in\s+)?(?:one|single)\s+day',
]

# ============================================================================
# LOT SIZE PATTERNS
# ============================================================================
LOT_SIZE_PATTERNS = [
    r'(?:maximum|max)[:\s]+lot[:\s]+(?:size[:\s]+)?(\d+(?:\.\d+)?)',
    r'(\d+(?:\.\d+)?)\s+lots?\s+(?:maximum|max)',
    r'lot size.*?(?:limit|restriction)[^\d]*(\d+(?:\.\d+)?)',
]

# ============================================================================
# MARGIN USAGE PATTERNS
# ============================================================================
MARGIN_PATTERNS = [
    r'(?:maximum|max)[:\s]+margin[:\s]+(?:usage[:\s]+)?(\d+(?:\.\d+)?)%',
    r'(\d+(?:\.\d+)?)%\s+(?:maximum\s+)?margin',
    r'margin.*?(?:should not exceed|must not exceed|cannot exceed)[^\d]*(\d+(?:\.\d+)?)%',
]

# ============================================================================
# PAYOUT PATTERNS
# ============================================================================
MIN_PAYOUT_PATTERNS = [
    r'(?:minimum|min)[:\s]+payout[:\s]+\$?(\d{1,3}(?:,\d{3})*)',
    r'payout.*?(?:starts at|from|minimum of)[:\s]+\$?(\d{1,3}(?:,\d{3})*)',
]

PAYOUT_FREQUENCY_PATTERNS = [
    r'payout[:\s]+(?:frequency[:\s]+)?(?:is\s+)?(daily|weekly|bi-weekly|biweekly|monthly|on-demand)',
    r'(?:withdraw|payout).*?(daily|weekly|bi-weekly|biweekly|monthly|on-demand)',
]

# ============================================================================
# PROHIBITED STRATEGIES (exact keywords)
# ============================================================================
PROHIBITED_STRATEGIES = [
    'copy trading',
    'tick scalping',
    'HFT',
    'high frequency trading',
    'martingale',
    'grid trading',
    'arbitrage',
    'gambling',
    'hedging',
    'news trading',
    'account rolling',
    'one sided betting',
    'hyperactivity',
    'latency trading',
    'quick strike',
    'reverse engineering',
    'exploiting',
]

# ============================================================================
# SOFT RULE INDICATORS (behavioral patterns)
# ============================================================================
SOFT_RULE_INDICATORS = {
    'gambling': [
        r'gambling',
        r'excessive risk',
        r'margin.*?(?:above|over|exceed).*?70%',
        r'irresponsible.*?trading',
    ],
    'hyperactivity': [
        r'hyperactivity',
        r'excessive.*?(?:trades|trading|activity)',
        r'(?:too many|excessive)\s+(?:orders|trades)',
        r'\d+.*?(?:trades|orders).*?per\s+(?:minute|hour)',
    ],
    'cross_account_hedging': [
        r'cross[:\s-]+account.*?hedging',
        r'hedging.*?(?:across|between).*?accounts?',
        r'mirror.*?(?:trades|positions).*?(?:across|between)',
    ],
    'consistency': [
        r'consistency',
        r'consistent.*?trading',
        r'avoid.*?(?:one|single).*?large.*?(?:trade|profit)',
    ],
    'risk_management': [
        r'risk management',
        r'proper.*?risk',
        r'manage.*?(?:your\s+)?risk',
        r'stop loss',
    ],
    'trading_style': [
        r'trading style',
        r'disciplined.*?trading',
        r'professional.*?approach',
    ],
}

# ============================================================================
# CHALLENGE TYPE KEYWORDS
# ============================================================================
CHALLENGE_TYPE_KEYWORDS = {
    'stellar_1_step': ['stellar 1-step', 'stellar one step', 'stellar 1 step', '1-step challenge', 'one step challenge'],
    'stellar_2_step': ['stellar 2-step', 'stellar two step', 'stellar 2 step', '2-step challenge', 'two step challenge'],
    'stellar_lite': ['stellar lite', 'lite challenge', 'lite account'],
    'stellar_instant': ['stellar instant', 'instant funding', 'instant account'],
    'evaluation': ['evaluation', 'challenge phase', 'assessment'],
    'funded': ['funded account', 'live account', 'express funded'],
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_with_pattern(text, patterns, context_chars=100):
    """
    Extract values using regex patterns and return with context.
    
    Args:
        text: Text to search
        patterns: List of regex patterns
        context_chars: Characters of context to include
        
    Returns:
        List of (value, context_span) tuples
    """
    results = []
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            value = match.group(1) if match.groups() else match.group(0)
            
            # Get surrounding context
            start = max(0, match.start() - context_chars)
            end = min(len(text), match.end() + context_chars)
            context = text[start:end].strip()
            
            results.append((value, context))
    
    return results


def check_keyword_presence(text, keywords):
    """
    Check if any keywords are present in text.
    
    Args:
        text: Text to search
        keywords: List of keywords
        
    Returns:
        List of (keyword, context) tuples for found keywords
    """
    results = []
    text_lower = text.lower()
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            # Find position and get context
            pos = text_lower.find(keyword.lower())
            start = max(0, pos - 100)
            end = min(len(text), pos + len(keyword) + 100)
            context = text[start:end].strip()
            
            results.append((keyword, context))
    
    return results


def classify_permission(text):
    """
    Classify if something is allowed, prohibited, or restricted.
    
    Args:
        text: Text describing the rule
        
    Returns:
        'allowed', 'prohibited', 'restricted', or 'unclear'
    """
    text_lower = text.lower()
    
    # Check for clear prohibition
    prohibited_words = ['prohibited', 'forbidden', 'not allowed', 'cannot', 'must not', 'strictly forbidden']
    if any(word in text_lower for word in prohibited_words):
        return 'prohibited'
    
    # Check for restrictions
    restricted_words = ['restricted', 'limited', 'only', 'except', 'must be', 'should be']
    if any(word in text_lower for word in restricted_words):
        return 'restricted'
    
    # Check for permission
    allowed_words = ['allowed', 'permitted', 'can', 'may', 'yes']
    if any(word in text_lower for word in allowed_words):
        return 'allowed'
    
    return 'unclear'
