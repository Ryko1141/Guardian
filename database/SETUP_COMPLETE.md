# Database Setup Complete! 🎉

## What Was Created

### Database Schema (`schema.sql`)
- ✅ **prop_firm** table - Stores firm information
- ✅ **help_document** table - Normalized document storage with versioning
- ✅ **document_paragraph** table - Fine-grained paragraph storage for RAG
- ✅ **firm_rule** table - Ready for structured rule extraction
- ✅ Comprehensive indexes for performance
- ✅ Views for common queries

### Utilities

#### `db_utils.py` - Core Functions
- `canonicalize_url()` - Strips query params, fragments, trailing slashes
- `compute_content_hash()` - SHA256 hashing with whitespace normalization
- `classify_document_type()` - Auto-detect article vs collection
- `split_into_paragraphs()` - Break text for RAG retrieval
- `deduplicate_urls()` - Remove duplicate URLs from lists

#### `ingest_documents.py` - Document Ingestion
- Load JSON scraped data
- Normalize URLs and detect duplicates
- Hash content for change detection
- Store with versioning support
- Extract paragraphs automatically

#### `query_db.py` - Database Queries
- List all firms
- Get current documents
- Search by text
- View document history
- Export to JSON
- Show statistics

## Results - FundedNext Ingestion

```
✓ Loaded 356 pages from JSON
✓ Created new firm: FundedNext (ID: 1)

Total processed:     356
✓ Inserted:          327
↻ Updated:           0
= Duplicates:        29
⊘ Skipped (empty):   0
✗ Errors:            0

Total documents:       327
Unique URLs:           327
Current versions:      327
Articles:              326
Collections:           0
Avg content length:    1980 chars
```

### Key Features Demonstrated

✅ **URL Canonicalization** - 29 duplicate URLs merged
- Removed query parameters (`?msclkid=...`, `?ref=...`)
- Removed fragment anchors (`#main-content`, `#h_...`)
- Normalized trailing slashes

✅ **Content Hashing** - SHA256 for change detection
- Whitespace normalized before hashing
- Enables duplicate detection
- Supports versioning on changes

✅ **Document Classification** - Auto-detected types
- 326 articles (substantive content)
- 0 collections (empty container pages skipped)

✅ **Paragraph Storage** - Ready for RAG
- Paragraphs extracted and stored separately
- Each with unique hash
- Linked back to parent document

## Quick Start Commands

```bash
# Initialize and ingest
python database/ingest_documents.py output/fundednext_complete.json \
    --firm-name "FundedNext" --init-db

# View statistics
python database/query_db.py --stats

# Search documents
python database/query_db.py --search "profit target"

# List firms
python database/query_db.py --list-firms

# Export to JSON
python database/query_db.py --export output/exported.json --firm "FundedNext"

# Run examples
python database/examples.py --example full
```

## Database File Location

```
c:\Users\sossi\propfirm-scraper\database\propfirm_scraper.db
```

## Next Steps

### 1. Integrate with Rule Extraction

```python
from database.query_db import DocumentDatabase
from src.hybrid_extractor import extract_rules_from_page

db = DocumentDatabase('propfirm_scraper.db')
docs = db.get_current_documents(firm_name='FundedNext', doc_type='article')

for doc in docs:
    if 'rule' in doc['title'].lower():
        rules = extract_rules_from_page({'body': doc['body_text']})
        # Store rules in firm_rule table
```

### 2. Create RAG Embeddings

```python
# Get documents and paragraphs
docs = db.get_current_documents(firm_name='FundedNext')

for doc in docs:
    paragraphs = db.get_document_paragraphs(doc['id'])
    for para in paragraphs:
        # Create embedding
        # Store in vector database with doc['id'] as reference
```

### 3. Monitor Changes

```python
# Re-scrape periodically
from src.scraper import crawl_site
crawl_site('https://help.fundednext.com/en', output_file='latest.json')

# Re-ingest - changes will be versioned
ingester.ingest_json_file('latest.json', 'FundedNext')

# Find what changed
cursor = db.conn.cursor()
cursor.execute("""
    SELECT base_url, COUNT(*) as versions
    FROM help_document
    WHERE firm_id = (SELECT id FROM prop_firm WHERE name = 'FundedNext')
    GROUP BY base_url
    HAVING versions > 1
""")
```

### 4. Add More Firms

```bash
# Scrape FTMO
python src/scraper.py https://ftmo.com/help

# Ingest
python database/ingest_documents.py output/ftmo.json --firm-name "FTMO"

# Compare
python database/query_db.py --stats --firm "FTMO"
python database/query_db.py --stats --firm "FundedNext"
```

## File Structure

```
propfirm-scraper/
├── database/
│   ├── schema.sql                    # Database schema
│   ├── db_utils.py                   # Core utilities
│   ├── ingest_documents.py           # Document ingestion
│   ├── query_db.py                   # Query interface
│   ├── examples.py                   # Workflow examples
│   ├── README.md                     # Detailed documentation
│   └── propfirm_scraper.db          # SQLite database
├── output/
│   └── fundednext_complete.json     # Scraped data (input)
└── src/
    ├── scraper.py                    # Web scraper
    ├── hybrid_extractor.py           # Rule extraction
    └── ...
```

## Documentation

- **Full Documentation**: `database/README.md`
- **Schema Details**: `database/schema.sql` (with inline comments)
- **Usage Examples**: `database/examples.py`
- **API Reference**: Docstrings in all Python files

## Benefits Achieved

✅ **Normalized Storage** - Clean, consistent data model
✅ **Deduplication** - No duplicate URLs or content
✅ **Versioning** - Track document changes over time
✅ **Change Detection** - Know when content updates
✅ **Fast Retrieval** - Indexed for performance
✅ **RAG Ready** - Paragraph-level storage
✅ **Multi-Firm** - Single database for all firms
✅ **Extensible** - Ready for rule extraction integration

## Support

- See `database/README.md` for detailed documentation
- Run `python database/examples.py` for interactive walkthrough
- Check `database/query_db.py --help` for query options
