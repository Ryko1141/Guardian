"""
Analyze database content to identify coverage and quality metrics.
"""
import sqlite3
import sys
from collections import defaultdict


def analyze_database(db_path='propfirm_scraper.db'):
    """Generate comprehensive analysis of database content."""
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("DATABASE CONTENT ANALYSIS")
    print("="*70 + "\n")
    
    # 1. Firm overview
    print("1. FIRMS")
    print("-" * 70)
    cursor.execute("SELECT name, domain, COUNT(*) as doc_count FROM prop_firm LEFT JOIN help_document ON prop_firm.id = help_document.firm_id WHERE is_current = 1 GROUP BY prop_firm.id")
    for row in cursor.fetchall():
        print(f"   • {row['name']}: {row['doc_count']} documents")
        print(f"     Domain: {row['domain']}")
    
    # 2. Content distribution
    print("\n\n2. CONTENT DISTRIBUTION")
    print("-" * 70)
    
    cursor.execute("""
        SELECT 
            doc_type,
            COUNT(*) as count,
            AVG(LENGTH(body_text)) as avg_length,
            MIN(LENGTH(body_text)) as min_length,
            MAX(LENGTH(body_text)) as max_length
        FROM help_document
        WHERE is_current = 1
        GROUP BY doc_type
    """)
    
    for row in cursor.fetchall():
        print(f"\n   {row['doc_type'].upper()}")
        print(f"   Count: {row['count']}")
        print(f"   Avg length: {row['avg_length']:.0f} chars")
        print(f"   Range: {row['min_length']} - {row['max_length']} chars")
    
    # 3. Content quality metrics
    print("\n\n3. CONTENT QUALITY")
    print("-" * 70)
    
    # Documents by length category
    cursor.execute("""
        SELECT 
            CASE 
                WHEN LENGTH(body_text) < 500 THEN 'Short (< 500)'
                WHEN LENGTH(body_text) < 1000 THEN 'Medium (500-1K)'
                WHEN LENGTH(body_text) < 2000 THEN 'Good (1K-2K)'
                WHEN LENGTH(body_text) < 5000 THEN 'Long (2K-5K)'
                ELSE 'Very Long (5K+)'
            END as length_category,
            COUNT(*) as count
        FROM help_document
        WHERE is_current = 1
        GROUP BY length_category
        ORDER BY MIN(LENGTH(body_text))
    """)
    
    print("\n   Content Length Distribution:")
    for row in cursor.fetchall():
        print(f"   {row['length_category']:20} {row['count']:4} documents")
    
    # 4. Topic coverage (keyword analysis)
    print("\n\n4. TOPIC COVERAGE")
    print("-" * 70)
    
    keywords = [
        ('profit target', 'Profit Targets'),
        ('daily loss', 'Daily Loss Limits'),
        ('drawdown', 'Drawdown Rules'),
        ('prohibited', 'Prohibited Strategies'),
        ('challenge', 'Challenge Types'),
        ('payout', 'Payout Information'),
        ('verification', 'Verification/KYC'),
        ('leverage', 'Leverage Rules'),
        ('copy trading', 'Copy Trading'),
        ('scaling', 'Account Scaling'),
    ]
    
    print("\n   Documents by Topic:")
    for keyword, label in keywords:
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM help_document
            WHERE is_current = 1
            AND (LOWER(title) LIKE ? OR LOWER(body_text) LIKE ?)
            """,
            (f'%{keyword}%', f'%{keyword}%')
        )
        count = cursor.fetchone()['count']
        print(f"   {label:25} {count:4} documents")
    
    # 5. URL patterns
    print("\n\n5. URL PATTERNS")
    print("-" * 70)
    
    cursor.execute("""
        SELECT 
            SUBSTR(base_url, 1, INSTR(SUBSTR(base_url, 9), '/') + 8) as url_prefix,
            COUNT(*) as count
        FROM help_document
        WHERE is_current = 1
        GROUP BY url_prefix
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("\n   Top URL Prefixes:")
    for row in cursor.fetchall():
        print(f"   {row['url_prefix']:50} {row['count']:4} docs")
    
    # 6. Paragraph analysis (if available)
    print("\n\n6. PARAGRAPH STORAGE")
    print("-" * 70)
    
    cursor.execute("SELECT COUNT(*) as count FROM document_paragraph")
    para_count = cursor.fetchone()['count']
    
    if para_count > 0:
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT document_id) as docs_with_paras,
                COUNT(*) as total_paras,
                AVG(para_count) as avg_paras_per_doc
            FROM (
                SELECT document_id, COUNT(*) as para_count
                FROM document_paragraph
                GROUP BY document_id
            )
        """)
        row = cursor.fetchone()
        
        print(f"\n   Documents with paragraphs: {row['docs_with_paras']}")
        print(f"   Total paragraphs: {row['total_paras']}")
        print(f"   Avg paragraphs/doc: {row['avg_paras_per_doc']:.1f}")
        
        cursor.execute("""
            SELECT 
                AVG(LENGTH(paragraph_text)) as avg_length,
                MIN(LENGTH(paragraph_text)) as min_length,
                MAX(LENGTH(paragraph_text)) as max_length
            FROM document_paragraph
        """)
        row = cursor.fetchone()
        print(f"   Avg paragraph length: {row['avg_length']:.0f} chars")
        print(f"   Range: {row['min_length']} - {row['max_length']} chars")
    else:
        print("\n   No paragraphs stored (use --store-paragraphs during ingestion)")
    
    # 7. Versioning info
    print("\n\n7. VERSIONING & HISTORY")
    print("-" * 70)
    
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT base_url) as unique_urls,
            COUNT(*) as total_versions,
            MAX(version) as max_version
        FROM help_document
    """)
    row = cursor.fetchone()
    
    print(f"\n   Unique URLs: {row['unique_urls']}")
    print(f"   Total versions: {row['total_versions']}")
    print(f"   Highest version number: {row['max_version']}")
    
    cursor.execute("""
        SELECT base_url, MAX(version) as versions
        FROM help_document
        GROUP BY base_url
        HAVING versions > 1
    """)
    changed_docs = cursor.fetchall()
    
    if changed_docs:
        print(f"\n   Documents with multiple versions: {len(changed_docs)}")
        print(f"   Top 5 most changed:")
        for row in changed_docs[:5]:
            print(f"   {row['versions']} versions: {row['base_url'][:60]}...")
    else:
        print(f"\n   No documents with multiple versions yet")
    
    # 8. Database size
    print("\n\n8. DATABASE METRICS")
    print("-" * 70)
    
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    db_size = cursor.fetchone()['size']
    
    cursor.execute("SELECT SUM(LENGTH(body_text)) as total_text FROM help_document WHERE is_current = 1")
    total_text = cursor.fetchone()['total_text']
    
    print(f"\n   Database size: {db_size / 1024 / 1024:.2f} MB")
    print(f"   Total text content: {total_text / 1024 / 1024:.2f} MB")
    print(f"   Compression ratio: {total_text / db_size:.2f}x")
    
    # 9. Recommendations
    print("\n\n9. RECOMMENDATIONS")
    print("-" * 70)
    
    recommendations = []
    
    # Check for short documents
    cursor.execute("SELECT COUNT(*) as count FROM help_document WHERE is_current = 1 AND LENGTH(body_text) < 500")
    short_count = cursor.fetchone()['count']
    if short_count > 10:
        recommendations.append(f"• {short_count} documents have < 500 chars - consider filtering these out")
    
    # Check paragraph coverage
    cursor.execute("SELECT COUNT(*) as count FROM help_document WHERE is_current = 1")
    total_docs = cursor.fetchone()['count']
    if para_count == 0 and total_docs > 0:
        recommendations.append("• No paragraphs stored - use --store-paragraphs for RAG support")
    
    # Check for topic coverage gaps
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM help_document
        WHERE is_current = 1
        AND LOWER(title) LIKE '%rule%'
    """)
    rule_docs = cursor.fetchone()['count']
    if rule_docs < 10:
        recommendations.append(f"• Only {rule_docs} documents about rules - may need better coverage")
    
    if recommendations:
        print()
        for rec in recommendations:
            print(f"   {rec}")
    else:
        print("\n   ✓ Database looks good! No issues found.")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70 + "\n")
    
    conn.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze database content')
    parser.add_argument(
        '--db-path',
        default='propfirm_scraper.db',
        help='Path to database file'
    )
    
    args = parser.parse_args()
    
    try:
        analyze_database(args.db_path)
    except Exception as e:
        print(f"\n✗ Error analyzing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
