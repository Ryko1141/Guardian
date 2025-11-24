# PropFirm Scraper Database

Normalized storage system for help center documents with URL canonicalization, content hashing, deduplication, and versioning support.

## Features

- ✅ **URL Canonicalization** - Strips query parameters, fragments, and trailing slashes
- ✅ **Content Hashing** - SHA256 hashing for change detection
- ✅ **Deduplication** - Automatically merges duplicate URLs
- ✅ **Versioning** - Tracks document history when content changes
- ✅ **Paragraph Storage** - Optional fine-grained storage for RAG retrieval
- ✅ **Multi-Firm Support** - Store documents from multiple prop firms
- ✅ **Structured Rules** - Ready for future rule extraction integration

## Database Schema

### Tables

#### `prop_firm`
Stores information about each proprietary trading firm.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Firm name (unique) |
| domain | TEXT | Domain name |
| website_url | TEXT | Main website |
| help_center_url | TEXT | Help center base URL |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

#### `help_document`
Stores normalized help center articles and pages.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| firm_id | INTEGER | Foreign key to prop_firm |
| url | TEXT | Original URL as scraped |
| base_url | TEXT | Canonicalized URL (no query/fragments) |
| title | TEXT | Document title |
| doc_type | TEXT | article, collection, or homepage |
| body_text | TEXT | Document content |
| content_hash | TEXT | SHA256 hash for change detection |
| scraped_at | TIMESTAMP | When scraped |
| first_seen_at | TIMESTAMP | When first discovered |
| last_updated_at | TIMESTAMP | Last content update |
| is_current | BOOLEAN | Current version flag |
| version | INTEGER | Version number |

#### `document_paragraph`
Optional paragraph-level storage for fine-grained retrieval.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| document_id | INTEGER | Foreign key to help_document |
| paragraph_index | INTEGER | Paragraph position |
| paragraph_text | TEXT | Paragraph content |
| paragraph_hash | TEXT | SHA256 hash |

#### `firm_rule`
Structured rule storage (for future use with rule extraction).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| firm_id | INTEGER | Foreign key to prop_firm |
| source_document_id | INTEGER | Foreign key to help_document |
| rule_type | TEXT | profit_target, daily_loss, etc. |
| rule_category | TEXT | hard_rule, soft_rule, guideline |
| challenge_type | TEXT | stellar_1_step, etc. |
| value | TEXT | Rule value (e.g., "10%") |
| details | TEXT | Full explanation |
| conditions | TEXT | Conditions or qualifications |
| severity | TEXT | critical, important, optional |
| extracted_at | TIMESTAMP | Extraction timestamp |
| extraction_method | TEXT | pattern, llm, hybrid, manual |
| confidence_score | REAL | 0.0 to 1.0 |

## Installation

```bash
cd propfirm-scraper/database
pip install -r requirements.txt  # sqlite3 is built-in with Python
```

## Quick Start

### 1. Initialize Database

```bash
python ingest_documents.py path/to/scraped.json --init-db --firm-name "FundedNext"
```

### 2. Ingest Scraped Documents

```bash
# Basic ingestion
python ingest_documents.py output/fundednext_complete.json --firm-name "FundedNext"

# Without paragraph storage (faster)
python ingest_documents.py output/fundednext_complete.json --firm-name "FundedNext" --no-paragraphs

# Custom database path
python ingest_documents.py output/fundednext_complete.json --firm-name "FundedNext" --db-path my_database.db
```

### 3. Query Database

```bash
# Show statistics
python query_db.py --stats

# List all firms
python query_db.py --list-firms

# Search documents
python query_db.py --search "profit target" --firm "FundedNext"

# Show duplicates that were merged
python query_db.py --duplicates

# Export to JSON
python query_db.py --export output/exported_docs.json --firm "FundedNext"
```

## Python API Usage

### Ingesting Documents

```python
from database.ingest_documents import DocumentIngester

# Create ingester
ingester = DocumentIngester('propfirm_scraper.db')
ingester.connect()
ingester.initialize_schema()

# Ingest documents
ingester.ingest_json_file(
    json_file='output/fundednext_complete.json',
    firm_name='FundedNext',
    store_paragraphs=True
)

ingester.close()
```

### Querying Documents

```python
from database.query_db import DocumentDatabase

# Connect to database
db = DocumentDatabase('propfirm_scraper.db')

# Get all current documents for a firm
docs = db.get_current_documents(firm_name='FundedNext', doc_type='article')

# Search documents
results = db.search_documents('daily loss', firm_name='FundedNext')

# Get document history
history = db.get_document_history('https://help.fundednext.com/en/articles/123')

# Get statistics
stats = db.get_stats(firm_name='FundedNext')

db.close()
```

### URL Normalization

```python
from database.db_utils import canonicalize_url, compute_content_hash

# Normalize URLs
url1 = "https://help.fundednext.com/en/articles/123?ref=twitter#main"
url2 = "https://help.fundednext.com/en/articles/123#section"
url3 = "https://help.fundednext.com/en/articles/123/"

canonical1 = canonicalize_url(url1)  # All three become:
canonical2 = canonicalize_url(url2)  # "https://help.fundednext.com/en/articles/123"
canonical3 = canonicalize_url(url3)

assert canonical1 == canonical2 == canonical3

# Content hashing
content = "This is test content."
hash1 = compute_content_hash(content)
hash2 = compute_content_hash("This  is   test  content.")  # Extra whitespace
assert hash1 == hash2  # Whitespace normalized before hashing
```

## How It Works

### URL Canonicalization

The system automatically normalizes URLs by:
1. Removing query parameters (`?msclkid=...`, `?ref=...`)
2. Removing fragment anchors (`#main-content`, `#h_...`)
3. Removing trailing slashes
4. Converting to lowercase (for case-insensitive comparison)

**Example:**
```
Input URLs:
- https://help.fundednext.com/en/articles/123?msclkid=abc#main-content
- https://help.fundednext.com/en/articles/123?ref=twitter
- https://help.fundednext.com/en/articles/123/#h_section

Canonicalized to:
- https://help.fundednext.com/en/articles/123
```

### Deduplication

When ingesting documents:
1. Each URL is canonicalized to its `base_url`
2. The system checks if `base_url` already exists for the firm
3. If it exists and content is identical (same hash), it's skipped
4. If content changed, a new version is created

### Versioning

When document content changes:
1. Old version is marked as `is_current = 0`
2. New version is inserted with incremented `version` number
3. `first_seen_at` timestamp is preserved from original
4. Both versions remain in database for history tracking

### Change Detection

Content hashing enables:
- **Duplicate detection**: Skip re-ingesting identical content
- **Change tracking**: Detect when help center articles are updated
- **Version history**: Track how rules evolve over time
- **Cache validation**: Know when to re-process documents

## Use Cases

### 1. RAG (Retrieval-Augmented Generation)

```python
# Get all current articles for embedding
db = DocumentDatabase('propfirm_scraper.db')
docs = db.get_current_documents(doc_type='article')

for doc in docs:
    # Create embeddings from doc['body_text']
    # Store in vector database with doc['id'] as reference
    pass
```

### 2. Rule Extraction

```python
# Process documents with rule extractor
docs = db.get_current_documents(firm_name='FundedNext')

for doc in docs:
    if 'rule' in doc['title'].lower():
        # Extract rules from doc['body_text']
        # Store in firm_rule table
        pass
```

### 3. Change Monitoring

```python
# Re-scrape periodically and ingest
ingester.ingest_json_file('latest_scrape.json', 'FundedNext')

# Find documents that changed
cursor = db.conn.cursor()
cursor.execute("""
    SELECT base_url, COUNT(*) as versions
    FROM help_document
    WHERE firm_id = (SELECT id FROM prop_firm WHERE name = 'FundedNext')
    GROUP BY base_url
    HAVING versions > 1
""")
changed_docs = cursor.fetchall()
```

### 4. Multi-Firm Analysis

```python
# Ingest multiple firms
ingester.ingest_json_file('fundednext.json', 'FundedNext')
ingester.ingest_json_file('ftmo.json', 'FTMO')
ingester.ingest_json_file('myforexfunds.json', 'MyForexFunds')

# Compare across firms
for firm in ['FundedNext', 'FTMO', 'MyForexFunds']:
    stats = db.get_stats(firm_name=firm)
    print(f"{firm}: {stats['current_documents']} documents")
```

## Database Maintenance

### Vacuum Database

```bash
sqlite3 propfirm_scraper.db "VACUUM;"
```

### Backup Database

```bash
# Simple file copy
cp propfirm_scraper.db propfirm_scraper_backup.db

# Or use sqlite3
sqlite3 propfirm_scraper.db ".backup propfirm_scraper_backup.db"
```

### Clear Old Versions

```sql
-- Keep only current versions (removes history)
DELETE FROM help_document WHERE is_current = 0;
```

## Performance

### Benchmarks (FundedNext - 1252 pages)

| Operation | Time | Notes |
|-----------|------|-------|
| Initial ingestion | ~15s | With paragraph storage |
| Initial ingestion | ~8s | Without paragraphs |
| Re-ingestion (no changes) | ~5s | All duplicates skipped |
| Query all current docs | ~0.2s | 245 documents |
| Search documents | ~0.3s | Full-text search |

### Indexes

The schema includes optimized indexes for:
- Firm lookups by domain
- Document lookups by base_URL
- Content hash comparisons
- Current version filtering
- Full-text searches

## Troubleshooting

### Database locked error

If you see "database is locked", ensure:
1. Only one process is writing at a time
2. Close connections properly with `db.close()`
3. Enable WAL mode for concurrent reads:
   ```python
   cursor.execute("PRAGMA journal_mode=WAL")
   ```

### Missing paragraphs

If paragraphs aren't stored:
1. Check `store_paragraphs=True` in ingestion
2. Verify documents have content > 100 characters
3. Check for errors during paragraph insertion

### URL not canonicalizing

If duplicate URLs aren't merging:
1. Check URL format is valid
2. Verify both have same scheme (http vs https)
3. Look for unusual characters or encoding

## Future Enhancements

- [ ] Full-text search with FTS5
- [ ] Automatic rule extraction pipeline
- [ ] Vector embeddings storage
- [ ] GraphQL API
- [ ] Web UI for browsing
- [ ] Export to other formats (CSV, Parquet)
- [ ] Integration with existing extractors

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](../LICENSE)
