"""
Example: Complete workflow from scraping to database storage.
Demonstrates the full pipeline for normalizing and storing help center documents.
"""
import sys
import json
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ingest_documents import DocumentIngester
from query_db import DocumentDatabase
from db_utils import canonicalize_url, compute_content_hash


def example_full_workflow():
    """
    Complete example: scrape, normalize, store, and query documents.
    """
    print("\n" + "="*70)
    print("EXAMPLE: Complete Workflow - Scraping to Database")
    print("="*70 + "\n")
    
    # Step 1: Scrape website (simulated - using existing JSON)
    print("STEP 1: Scraping Website")
    print("-" * 70)
    print("Normally you would run:")
    print("  python src/scraper.py https://help.fundednext.com/en")
    print("\nFor this example, we'll use existing scraped data:")
    print("  c:\\Users\\sossi\\output\\fundednext_complete.json")
    print()
    
    input("Press Enter to continue to Step 2...")
    
    # Step 2: Initialize database and ingest
    print("\n\nSTEP 2: Normalize & Store in Database")
    print("-" * 70)
    
    db_path = 'example_workflow.db'
    json_file = 'c:\\Users\\sossi\\output\\fundednext_complete.json'
    
    ingester = DocumentIngester(db_path)
    ingester.connect()
    ingester.initialize_schema()
    
    print(f"Ingesting documents from {json_file}...")
    ingester.ingest_json_file(
        json_file=json_file,
        firm_name='FundedNext',
        store_paragraphs=True
    )
    ingester.close()
    
    print("\n✓ Documents normalized and stored!")
    print(f"  - URLs canonicalized (query params/fragments removed)")
    print(f"  - Content hashed (SHA256 for change detection)")
    print(f"  - Duplicates merged")
    print(f"  - Paragraphs extracted for RAG")
    
    input("\nPress Enter to continue to Step 3...")
    
    # Step 3: Query and analyze
    print("\n\nSTEP 3: Query Database")
    print("-" * 70)
    
    db = DocumentDatabase(db_path)
    
    # Get statistics
    stats = db.get_stats(firm_name='FundedNext')
    print(f"\n📊 Database Statistics:")
    print(f"   Total documents:    {stats['total_documents']}")
    print(f"   Unique URLs:        {stats['unique_urls']}")
    print(f"   Articles:           {stats['articles']}")
    print(f"   Avg content length: {stats['avg_content_length']:.0f} chars")
    
    # Search for specific content
    print(f"\n🔍 Searching for 'profit target'...")
    results = db.search_documents('profit target', firm_name='FundedNext')
    print(f"   Found {len(results)} matching documents")
    print(f"\n   First 3 results:")
    for doc in results[:3]:
        print(f"   • {doc['title'][:60]}...")
        print(f"     {doc['base_url']}")
    
    # Get document with paragraphs
    print(f"\n📄 Example Document with Paragraphs:")
    docs = db.get_current_documents(firm_name='FundedNext', doc_type='article')
    if docs:
        sample_doc = docs[0]
        print(f"   Title: {sample_doc['title']}")
        print(f"   URL: {sample_doc['base_url']}")
        
        paragraphs = db.get_document_paragraphs(sample_doc['id'])
        if paragraphs:
            print(f"   Paragraphs: {len(paragraphs)}")
            print(f"   First paragraph:")
            print(f"     {paragraphs[0]['paragraph_text'][:150]}...")
    
    db.close()
    
    input("\nPress Enter to continue to Step 4...")
    
    # Step 4: Demonstrate change detection
    print("\n\nSTEP 4: Change Detection Example")
    print("-" * 70)
    
    print("URL Canonicalization Examples:")
    test_urls = [
        "https://help.fundednext.com/en/articles/123?ref=twitter",
        "https://help.fundednext.com/en/articles/123#main-content",
        "https://help.fundednext.com/en/articles/123/",
    ]
    
    for url in test_urls:
        canonical = canonicalize_url(url)
        print(f"\n  Original:  {url}")
        print(f"  Canonical: {canonical}")
    
    print("\n\nContent Hash Example:")
    content1 = "Profit target is 10%"
    content2 = "Profit  target  is  10%"  # Extra spaces
    content3 = "Profit target is 8%"      # Different value
    
    hash1 = compute_content_hash(content1)
    hash2 = compute_content_hash(content2)
    hash3 = compute_content_hash(content3)
    
    print(f"  Content 1: '{content1}'")
    print(f"  Hash:      {hash1[:16]}...")
    print(f"\n  Content 2: '{content2}' (extra whitespace)")
    print(f"  Hash:      {hash2[:16]}...")
    print(f"  Same hash: {hash1 == hash2} ✓")
    print(f"\n  Content 3: '{content3}' (different content)")
    print(f"  Hash:      {hash3[:16]}...")
    print(f"  Same hash: {hash1 == hash3} ✗")
    
    print("\n\nWhen re-scraping:")
    print("  • If content hash unchanged → Skip (duplicate)")
    print("  • If content hash changed   → Create new version")
    print("  • Old versions marked with is_current = 0")
    
    print("\n\n" + "="*70)
    print("WORKFLOW COMPLETE!")
    print("="*70)
    print("\nNext Steps:")
    print("  1. Use query_db.py to explore the database")
    print("  2. Integrate with rule extraction (hybrid_extractor.py)")
    print("  3. Create embeddings for RAG retrieval")
    print("  4. Monitor changes by re-scraping periodically")
    print()


def example_rag_preparation():
    """
    Example: Prepare documents for RAG (Retrieval-Augmented Generation).
    """
    print("\n" + "="*70)
    print("EXAMPLE: Preparing Documents for RAG")
    print("="*70 + "\n")
    
    db = DocumentDatabase('propfirm_scraper.db')
    
    # Get all current articles
    docs = db.get_current_documents(firm_name='FundedNext', doc_type='article')
    
    print(f"Retrieved {len(docs)} current articles")
    print("\nRAG Preparation Steps:\n")
    
    # Simulate embedding creation
    print("1. Extract text from each document:")
    for i, doc in enumerate(docs[:3], 1):
        print(f"\n   Document {i}:")
        print(f"   ID: {doc['id']}")
        print(f"   Title: {doc['title'][:60]}...")
        print(f"   Content: {len(doc['body_text'])} chars")
        
        # Get paragraphs for finer-grained retrieval
        paragraphs = db.get_document_paragraphs(doc['id'])
        if paragraphs:
            print(f"   Paragraphs: {len(paragraphs)}")
    
    print("\n\n2. Create embeddings (pseudo-code):")
    print("""
    from openai import OpenAI
    
    client = OpenAI()
    
    for doc in docs:
        # Option A: Embed full document
        embedding = client.embeddings.create(
            input=doc['body_text'],
            model="text-embedding-3-small"
        )
        
        # Store: vector_db.upsert(
        #     id=doc['id'],
        #     vector=embedding.data[0].embedding,
        #     metadata={'title': doc['title'], 'url': doc['base_url']}
        # )
        
        # Option B: Embed paragraphs separately (better for specific queries)
        paragraphs = db.get_document_paragraphs(doc['id'])
        for para in paragraphs:
            para_embedding = client.embeddings.create(
                input=para['paragraph_text'],
                model="text-embedding-3-small"
            )
            # Store with doc_id + para_index as ID
    """)
    
    print("\n3. Query at runtime:")
    print("""
    # User asks: "What's the daily loss limit for Stellar 1-Step?"
    
    query_embedding = client.embeddings.create(
        input="daily loss limit stellar 1-step",
        model="text-embedding-3-small"
    )
    
    # Retrieve most similar documents
    results = vector_db.query(
        vector=query_embedding.data[0].embedding,
        top_k=5
    )
    
    # Fetch full content from our database
    for result in results:
        doc = db.conn.execute(
            "SELECT * FROM help_document WHERE id = ?",
            (result.id,)
        ).fetchone()
        
        # Use doc content in LLM prompt
        context = doc['body_text']
    """)
    
    db.close()
    
    print("\n" + "="*70)
    print("RAG preparation complete!")
    print("="*70 + "\n")


def example_multi_firm_comparison():
    """
    Example: Compare rules across multiple prop firms.
    """
    print("\n" + "="*70)
    print("EXAMPLE: Multi-Firm Comparison")
    print("="*70 + "\n")
    
    print("To compare multiple firms:\n")
    print("1. Ingest each firm's help center:")
    print("""
    python ingest_documents.py output/fundednext.json --firm-name "FundedNext"
    python ingest_documents.py output/ftmo.json --firm-name "FTMO"
    python ingest_documents.py output/mff.json --firm-name "MyForexFunds"
    """)
    
    print("\n2. Query all firms:")
    print("""
    db = DocumentDatabase('propfirm_scraper.db')
    firms = db.get_all_firms()
    
    for firm in firms:
        stats = db.get_stats(firm_name=firm['name'])
        print(f"{firm['name']}: {stats['current_documents']} documents")
    """)
    
    print("\n3. Compare specific topics:")
    print("""
    # Search for profit targets across all firms
    for firm_name in ['FundedNext', 'FTMO', 'MyForexFunds']:
        results = db.search_documents('profit target', firm_name=firm_name)
        print(f"{firm_name}: {len(results)} documents mention profit targets")
    """)
    
    print("\n4. Extract and compare rules:")
    print("""
    # After rule extraction (using hybrid_extractor.py)
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT 
            f.name as firm_name,
            r.rule_type,
            r.value,
            r.challenge_type
        FROM firm_rule r
        JOIN prop_firm f ON r.firm_id = f.id
        WHERE r.rule_type = 'profit_target'
        ORDER BY f.name, r.challenge_type
    ''')
    """)
    
    print("\n" + "="*70)
    print("Multi-firm comparison setup complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Workflow examples for PropFirm Scraper Database'
    )
    parser.add_argument(
        '--example',
        choices=['full', 'rag', 'multi-firm'],
        default='full',
        help='Which example to run'
    )
    
    args = parser.parse_args()
    
    if args.example == 'full':
        example_full_workflow()
    elif args.example == 'rag':
        example_rag_preparation()
    elif args.example == 'multi-firm':
        example_multi_firm_comparison()
