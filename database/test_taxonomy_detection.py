"""
Test taxonomy-integrated challenge type detection.
"""
from soft_rule_detector import detect_challenge_type

# Test cases
test_cases = [
    ("Stellar 1 Step Challenge Rules", "stellar_1step"),
    ("Stellar 2 Step Phase 1", "stellar_2step"),
    ("Stellar Lite Account", "stellar_lite"),
    ("Stellar Instant Funding", "stellar_instant"),
    ("Evaluation Challenge", "evaluation_2step"),
    ("General Trading Rules", "general"),
]

print("="*70)
print("TESTING TAXONOMY-INTEGRATED CHALLENGE TYPE DETECTION")
print("="*70)
print()

all_passed = True

for title, expected in test_cases:
    result = detect_challenge_type("", title, "")
    status = "✓" if expected in result else "✗"
    
    if expected not in result:
        all_passed = False
    
    print(f"{status} {title:40s} -> {result[0] if result else 'None':20s} (expected: {expected})")

print()
print("="*70)
if all_passed:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED")
print("="*70)
