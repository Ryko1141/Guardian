"""
Soft rule detector for behavioral patterns and LLM-based classification.
Combines pattern matching with local LLM analysis for ambiguous rules.
"""
import re
import json
import requests
from typing import Dict, List, Any, Optional
from rule_patterns import SOFT_RULE_INDICATORS, check_keyword_presence


class SoftRuleDetector:
    """Detect soft (behavioral/guideline) rules using patterns and LLM."""
    
    def __init__(self, llm_model='qwen2.5-coder:14b'):
        """
        Initialize soft rule detector.
        
        Args:
            llm_model: Ollama model to use for classification
        """
        self.llm_model = llm_model
        self.llm_available = self._check_llm_available()
    
    def _check_llm_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(self.llm_model in m.get('name', '') for m in models)
        except:
            pass
        return False
    
    def extract_soft_rules(self, text: str, title: str = "", url: str = "") -> List[Dict[str, Any]]:
        """
        Extract soft rules using pattern detection + LLM classification.
        
        Args:
            text: Document text
            title: Document title
            url: Document URL
            
        Returns:
            List of soft rules with metadata
        """
        rules = []
        
        # Step 1: Pattern-based detection
        pattern_rules = self._detect_with_patterns(text)
        rules.extend(pattern_rules)
        
        # Step 2: LLM classification for ambiguous paragraphs
        if self.llm_available:
            # Split text into paragraphs
            paragraphs = self._split_into_paragraphs(text)
            
            # Filter paragraphs that might contain soft rules
            candidate_paragraphs = self._filter_candidate_paragraphs(paragraphs)
            
            # Classify with LLM
            llm_rules = self._classify_with_llm(candidate_paragraphs)
            rules.extend(llm_rules)
        
        # Add metadata
        for rule in rules:
            rule['source_title'] = title
            rule['source_url'] = url
            rule['is_soft_rule'] = True
        
        return rules
    
    def _detect_with_patterns(self, text: str) -> List[Dict]:
        """Detect soft rules using regex patterns."""
        rules = []
        
        for category, patterns in SOFT_RULE_INDICATORS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Get context
                    start = max(0, match.start() - 150)
                    end = min(len(text), match.end() + 150)
                    context = text[start:end].strip()
                    
                    rules.append({
                        'rule_type': f'soft_{category}',
                        'rule_code': f'SOFT_{category.upper()}',
                        'value': category.replace('_', ' ').title(),
                        'description': self._generate_description(category, context),
                        'raw_span': context,
                        'category': 'behavioral',
                    })
        
        return rules
    
    def _generate_description(self, category: str, context: str) -> str:
        """Generate human-readable description for soft rule."""
        descriptions = {
            'gambling': "Avoid excessive risk or gambling-like behavior",
            'hyperactivity': "Avoid excessive trading activity or overtrading",
            'cross_account_hedging': "Do not hedge positions across multiple accounts",
            'consistency': "Maintain consistent trading patterns",
            'risk_management': "Follow proper risk management practices",
            'trading_style': "Maintain disciplined trading approach",
        }
        
        base_desc = descriptions.get(category, f"Guideline regarding {category.replace('_', ' ')}")
        
        # Try to extract more specific guidance from context
        if 'margin' in context.lower() and '70' in context:
            return "Avoid using more than 70% margin (gambling indicator)"
        elif 'trades' in context.lower() or 'orders' in context.lower():
            return base_desc + " - limit number of trades per day"
        
        return base_desc
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        paragraphs = re.split(r'\n\s*\n+', text)
        return [p.strip() for p in paragraphs if len(p.strip()) > 50]
    
    def _filter_candidate_paragraphs(self, paragraphs: List[str]) -> List[str]:
        """Filter paragraphs that might contain soft rules."""
        candidates = []
        
        # Keywords that suggest soft rules
        soft_keywords = [
            'should', 'recommend', 'suggest', 'advised', 'encouraged',
            'guideline', 'best practice', 'avoid', 'refrain',
            'professional', 'disciplined', 'consistent', 'responsible',
            'appropriate', 'proper', 'reasonable', 'excessive',
        ]
        
        for para in paragraphs:
            para_lower = para.lower()
            # Check if paragraph contains soft rule indicators
            if any(keyword in para_lower for keyword in soft_keywords):
                # But skip if it's already covered by hard rules
                if not any(hard in para_lower for hard in ['%', 'prohibited', 'not allowed', 'days']):
                    candidates.append(para)
        
        return candidates[:20]  # Limit to 20 paragraphs to avoid long LLM processing
    
    def _classify_with_llm(self, paragraphs: List[str]) -> List[Dict]:
        """Use LLM to classify ambiguous paragraphs into rule categories."""
        if not paragraphs:
            return []
        
        rules = []
        
        for para in paragraphs:
            classification = self._query_llm_for_classification(para)
            if classification:
                rules.append(classification)
        
        return rules
    
    def _query_llm_for_classification(self, paragraph: str) -> Optional[Dict]:
        """Query LLM to classify a paragraph."""
        prompt = f"""You are a trading rule classifier. Analyze the following text and determine if it contains a soft rule or guideline.

SOFT RULE CATEGORIES:
1. gambling - Warnings about excessive risk, over-leveraging, or gambling-like behavior
2. hyperactivity - Guidelines about excessive trading or overtrading
3. cross_account_hedging - Rules about hedging across multiple accounts
4. consistency - Guidelines about maintaining consistent trading patterns
5. risk_management - General risk management recommendations
6. trading_style - Recommendations about trading approach or discipline
7. other - Other behavioral guidelines

TEXT TO ANALYZE:
{paragraph[:500]}

TASK:
If this text contains a soft rule or guideline:
1. Identify the category (from list above)
2. Extract the key guidance
3. Respond with JSON only:

{{"category": "risk_management", "description": "Brief description of the guideline", "is_soft_rule": true}}

If NO soft rule is present, respond with:
{{"is_soft_rule": false}}

JSON RESPONSE:"""
        
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self.llm_model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {'temperature': 0.1}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('response', '').strip()
                
                # Extract JSON from response
                json_match = re.search(r'\{[^}]+\}', text)
                if json_match:
                    data = json.loads(json_match.group(0))
                    
                    if data.get('is_soft_rule'):
                        category = data.get('category', 'other')
                        description = data.get('description', 'Behavioral guideline')
                        
                        return {
                            'rule_type': f'soft_{category}',
                            'rule_code': f'SOFT_{category.upper()}_LLM',
                            'value': category.replace('_', ' ').title(),
                            'description': description,
                            'raw_span': paragraph[:300],
                            'category': 'behavioral',
                            'extraction_method': 'llm',
                            'confidence': 0.7,  # LLM-extracted rules have moderate confidence
                        }
        except Exception as e:
            print(f"  ⚠ LLM classification error: {e}")
        
        return None


def detect_challenge_type(text: str, title: str, url: str) -> List[str]:
    """
    Detect which challenge types this document is about.
    
    Args:
        text: Document text
        title: Document title
        url: Document URL
        
    Returns:
        List of challenge type identifiers
    """
    from rule_patterns import CHALLENGE_TYPE_KEYWORDS
    
    combined = (text + " " + title + " " + url).lower()
    detected_types = []
    
    for challenge_type, keywords in CHALLENGE_TYPE_KEYWORDS.items():
        if any(keyword in combined for keyword in keywords):
            detected_types.append(challenge_type)
    
    # If no specific type detected but mentions "challenge" or "account"
    if not detected_types:
        if 'challenge' in combined or 'evaluation' in combined:
            detected_types.append('general')
        elif 'funded' in combined or 'express' in combined:
            detected_types.append('funded')
    
    return detected_types if detected_types else ['general']


def merge_similar_rules(rules: List[Dict]) -> List[Dict]:
    """
    Merge similar soft rules to avoid duplication.
    
    Args:
        rules: List of extracted rules
        
    Returns:
        Merged list of rules
    """
    if not rules:
        return []
    
    # Group by rule_type
    grouped = {}
    for rule in rules:
        rule_type = rule.get('rule_type', 'unknown')
        if rule_type not in grouped:
            grouped[rule_type] = []
        grouped[rule_type].append(rule)
    
    # Keep best representative from each group
    merged = []
    for rule_type, group in grouped.items():
        if len(group) == 1:
            merged.append(group[0])
        else:
            # Prefer LLM-extracted rules (higher confidence)
            # Otherwise take the first one
            llm_rules = [r for r in group if r.get('extraction_method') == 'llm']
            if llm_rules:
                merged.append(llm_rules[0])
            else:
                merged.append(group[0])
    
    return merged


if __name__ == "__main__":
    # Test the detector
    test_text = """
    Trading Guidelines:
    
    We recommend maintaining a disciplined approach to trading. Avoid overtrading
    or excessive activity that may indicate gambling behavior. Professional traders
    should focus on quality over quantity.
    
    Risk Management:
    It is advised to use proper risk management techniques. Do not use excessive
    margin - margin usage above 70% may be considered gambling and could lead to
    account termination.
    
    Cross-Account Trading:
    Traders should not engage in mirror trading or hedging positions across multiple
    accounts. This is considered manipulation of the evaluation process.
    
    Consistency is key to long-term success. Maintain reasonable trade sizes and
    avoid concentrating all profits in a single day or trade.
    """
    
    detector = SoftRuleDetector()
    
    if not detector.llm_available:
        print("⚠ Warning: Ollama LLM not available - using pattern detection only\n")
    
    rules = detector.extract_soft_rules(test_text, "Trading Guidelines", "https://test.com")
    rules = merge_similar_rules(rules)
    
    print(f"\nExtracted {len(rules)} soft rules:\n")
    for rule in rules:
        print(f"• {rule['rule_code']}: {rule['description']}")
        print(f"  Category: {rule['category']}")
        print(f"  Method: {rule.get('extraction_method', 'pattern')}")
        print(f"  Context: {rule['raw_span'][:100]}...")
        print()
    
    # Test challenge type detection
    print("\nChallenge Type Detection:")
    test_titles = [
        "Stellar 1-Step Challenge Rules",
        "Stellar 2-Step Phase 1 Requirements",
        "Stellar Lite Account Information",
        "Stellar Instant Funding",
        "General Trading Guidelines",
    ]
    
    for title in test_titles:
        types = detect_challenge_type("", title, "")
        print(f"  {title}: {', '.join(types)}")
