"""
Ingest scraped help center documents into normalized database.
Handles URL canonicalization, content hashing, deduplication, and versioning.
"""
import sqlite3
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add database module to path
sys.path.insert(0, str(Path(__file__).parent))

from db_utils import (
    canonicalize_url,
    compute_content_hash,
    classify_document_type,
    split_into_paragraphs,
    extract_domain_from_url,
    format_timestamp,
    validate_document
)


class DocumentIngester:
    """Handles ingestion of scraped documents into database."""
    
    def __init__(self, db_path='propfirm_scraper.db'):
        """
        Initialize database connection and create schema.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.stats = {
            'total_processed': 0,
            'inserted': 0,
            'duplicates': 0,
            'updated': 0,
            'skipped_empty': 0,
            'errors': 0
        }
    
    def connect(self):
        """Connect to database and initialize schema."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        print(f"✓ Connected to database: {self.db_path}")
    
    def initialize_schema(self):
        """Create database tables from schema file."""
        schema_path = Path(__file__).parent / 'schema.sql'
        
        if not schema_path.exists():
            print(f"✗ Schema file not found: {schema_path}")
            return False
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Execute schema (split on semicolons for multiple statements)
        try:
            self.cursor.executescript(schema_sql)
            self.conn.commit()
            print("✓ Database schema initialized")
            return True
        except sqlite3.Error as e:
            print(f"✗ Error initializing schema: {e}")
            return False
    
    def get_or_create_firm(self, firm_name, domain, website_url=None, help_center_url=None):
        """
        Get existing firm or create new one.
        
        Args:
            firm_name: Name of the prop firm
            domain: Domain name (e.g., help.fundednext.com)
            website_url: Main website URL
            help_center_url: Help center base URL
            
        Returns:
            firm_id: Database ID of the firm
        """
        # Check if firm exists
        self.cursor.execute(
            "SELECT id FROM prop_firm WHERE domain = ?",
            (domain,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new firm
        self.cursor.execute(
            """
            INSERT INTO prop_firm (name, domain, website_url, help_center_url)
            VALUES (?, ?, ?, ?)
            """,
            (firm_name, domain, website_url, help_center_url)
        )
        self.conn.commit()
        
        firm_id = self.cursor.lastrowid
        print(f"✓ Created new firm: {firm_name} (ID: {firm_id})")
        return firm_id
    
    def check_existing_document(self, firm_id, base_url):
        """
        Check if document already exists and get its content hash.
        
        Args:
            firm_id: Firm database ID
            base_url: Canonicalized URL
            
        Returns:
            Tuple of (document_id, content_hash, version) or (None, None, 0)
        """
        self.cursor.execute(
            """
            SELECT id, content_hash, version
            FROM help_document
            WHERE firm_id = ? AND base_url = ? AND is_current = 1
            """,
            (firm_id, base_url)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0], result[1], result[2]
        return None, None, 0
    
    def insert_document(self, firm_id, url, title, body_text, doc_type='article', 
                       store_paragraphs=True):
        """
        Insert new document into database.
        
        Args:
            firm_id: Firm database ID
            url: Original URL
            title: Document title
            body_text: Document content
            doc_type: Document type (article/collection/homepage)
            store_paragraphs: Whether to store paragraph breakdowns
            
        Returns:
            document_id or None on error
        """
        base_url = canonicalize_url(url)
        content_hash = compute_content_hash(body_text)
        
        # Check if document exists
        existing_id, existing_hash, current_version = self.check_existing_document(
            firm_id, base_url
        )
        
        if existing_id:
            if existing_hash == content_hash:
                # Duplicate - no changes
                self.stats['duplicates'] += 1
                return existing_id
            else:
                # Content changed - create new version
                return self.version_document(
                    firm_id, existing_id, url, title, body_text, 
                    doc_type, current_version, store_paragraphs
                )
        
        # Insert new document
        try:
            self.cursor.execute(
                """
                INSERT INTO help_document 
                (firm_id, url, base_url, title, doc_type, body_text, content_hash, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (firm_id, url, base_url, title, doc_type, body_text, content_hash)
            )
            document_id = self.cursor.lastrowid
            self.stats['inserted'] += 1
            
            # Store paragraphs if requested
            if store_paragraphs and len(body_text.strip()) > 100:
                self.store_paragraphs(document_id, body_text)
            
            return document_id
            
        except sqlite3.Error as e:
            print(f"✗ Error inserting document {url}: {e}")
            self.stats['errors'] += 1
            return None
    
    def version_document(self, firm_id, old_doc_id, url, title, body_text, 
                        doc_type, current_version, store_paragraphs):
        """
        Create new version of changed document.
        
        Args:
            firm_id: Firm database ID
            old_doc_id: ID of previous version
            url: Original URL
            title: Document title
            body_text: New content
            doc_type: Document type
            current_version: Current version number
            store_paragraphs: Whether to store paragraphs
            
        Returns:
            New document_id
        """
        base_url = canonicalize_url(url)
        content_hash = compute_content_hash(body_text)
        new_version = current_version + 1
        
        try:
            # Mark old version as not current
            self.cursor.execute(
                "UPDATE help_document SET is_current = 0 WHERE id = ?",
                (old_doc_id,)
            )
            
            # Insert new version
            self.cursor.execute(
                """
                INSERT INTO help_document 
                (firm_id, url, base_url, title, doc_type, body_text, content_hash, 
                 version, first_seen_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 
                        (SELECT first_seen_at FROM help_document WHERE id = ?))
                """,
                (firm_id, url, base_url, title, doc_type, body_text, content_hash, 
                 new_version, old_doc_id)
            )
            document_id = self.cursor.lastrowid
            self.stats['updated'] += 1
            
            # Store paragraphs
            if store_paragraphs and len(body_text.strip()) > 100:
                self.store_paragraphs(document_id, body_text)
            
            print(f"  ↻ Updated document (v{new_version}): {title[:50]}...")
            return document_id
            
        except sqlite3.Error as e:
            print(f"✗ Error versioning document {url}: {e}")
            self.stats['errors'] += 1
            return None
    
    def store_paragraphs(self, document_id, body_text):
        """
        Break document into paragraphs and store separately.
        
        Args:
            document_id: Document database ID
            body_text: Full document text
        """
        paragraphs = split_into_paragraphs(body_text)
        
        if not paragraphs:
            return
        
        try:
            for idx, para in enumerate(paragraphs):
                para_hash = compute_content_hash(para)
                self.cursor.execute(
                    """
                    INSERT INTO document_paragraph 
                    (document_id, paragraph_index, paragraph_text, paragraph_hash)
                    VALUES (?, ?, ?, ?)
                    """,
                    (document_id, idx, para, para_hash)
                )
        except sqlite3.Error as e:
            print(f"  ⚠ Warning: Error storing paragraphs: {e}")
    
    def ingest_json_file(self, json_file, firm_name, store_paragraphs=True):
        """
        Ingest all documents from scraped JSON file.
        
        Args:
            json_file: Path to JSON file with scraped pages
            firm_name: Name of the prop firm
            store_paragraphs: Whether to store paragraph breakdowns
        """
        print(f"\n{'='*70}")
        print(f"INGESTING: {json_file}")
        print(f"{'='*70}\n")
        
        # Load JSON data
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                pages = json.load(f)
            print(f"✓ Loaded {len(pages)} pages from JSON")
        except Exception as e:
            print(f"✗ Error loading JSON: {e}")
            return False
        
        # Extract domain from first URL
        if not pages:
            print("✗ No pages found in JSON")
            return False
        
        first_url = pages[0].get('url', '')
        domain = extract_domain_from_url(first_url)
        help_center_url = '/'.join(first_url.split('/')[:3])  # https://domain.com
        
        # Create or get firm
        firm_id = self.get_or_create_firm(
            firm_name=firm_name,
            domain=domain,
            help_center_url=help_center_url
        )
        
        print(f"\nProcessing documents...")
        print("-" * 70)
        
        # Process each page
        for idx, page in enumerate(pages, 1):
            self.stats['total_processed'] += 1
            
            # Validate document
            is_valid, error = validate_document(page)
            if not is_valid:
                print(f"  ⚠ Skipping invalid document #{idx}: {error}")
                self.stats['errors'] += 1
                continue
            
            url = page['url']
            title = page['title']
            body_text = page.get('body', page.get('html', ''))
            
            # Skip empty documents (collection containers)
            if len(body_text.strip()) < 50:
                self.stats['skipped_empty'] += 1
                continue
            
            # Classify document type
            doc_type = classify_document_type(title, url, body_text)
            
            # Insert document
            doc_id = self.insert_document(
                firm_id=firm_id,
                url=url,
                title=title,
                body_text=body_text,
                doc_type=doc_type,
                store_paragraphs=store_paragraphs
            )
            
            # Progress indicator
            if idx % 50 == 0:
                print(f"  Processed {idx}/{len(pages)} pages...")
        
        # Commit all changes
        self.conn.commit()
        
        # Print summary
        self.print_stats()
        return True
    
    def print_stats(self):
        """Print ingestion statistics."""
        print(f"\n{'='*70}")
        print("INGESTION SUMMARY")
        print(f"{'='*70}")
        print(f"Total processed:     {self.stats['total_processed']}")
        print(f"✓ Inserted:          {self.stats['inserted']}")
        print(f"↻ Updated:           {self.stats['updated']}")
        print(f"= Duplicates:        {self.stats['duplicates']}")
        print(f"⊘ Skipped (empty):   {self.stats['skipped_empty']}")
        print(f"✗ Errors:            {self.stats['errors']}")
        print(f"{'='*70}\n")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")


def main():
    """Main entry point for document ingestion."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Ingest scraped help center documents into database'
    )
    parser.add_argument(
        'json_file',
        help='Path to scraped JSON file'
    )
    parser.add_argument(
        '--firm-name',
        default='FundedNext',
        help='Name of the prop firm (default: FundedNext)'
    )
    parser.add_argument(
        '--db-path',
        default='propfirm_scraper.db',
        help='Path to SQLite database (default: propfirm_scraper.db)'
    )
    parser.add_argument(
        '--no-paragraphs',
        action='store_true',
        help='Skip paragraph storage (faster ingestion)'
    )
    parser.add_argument(
        '--init-db',
        action='store_true',
        help='Initialize database schema (first run only)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.json_file):
        print(f"✗ Error: File not found: {args.json_file}")
        sys.exit(1)
    
    # Create ingester
    ingester = DocumentIngester(args.db_path)
    
    try:
        # Connect to database
        ingester.connect()
        
        # Initialize schema if requested
        if args.init_db or not os.path.exists(args.db_path):
            ingester.initialize_schema()
        
        # Ingest documents
        success = ingester.ingest_json_file(
            json_file=args.json_file,
            firm_name=args.firm_name,
            store_paragraphs=not args.no_paragraphs
        )
        
        if success:
            print("\n✅ Ingestion completed successfully!")
        else:
            print("\n⚠ Ingestion completed with errors")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠ Ingestion interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        ingester.close()


if __name__ == "__main__":
    main()
