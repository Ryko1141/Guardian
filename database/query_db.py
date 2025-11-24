"""
Database query utilities for retrieving and analyzing stored documents.
"""
import sqlite3
import json
from pathlib import Path


class DocumentDatabase:
    """Query interface for normalized help center documents."""
    
    def __init__(self, db_path='propfirm_scraper.db'):
        """Connect to database."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    
    def get_all_firms(self):
        """Get list of all firms in database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM prop_firm ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_firm_by_name(self, name):
        """Get firm by name."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM prop_firm WHERE name = ?", (name,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_current_documents(self, firm_name=None, doc_type=None):
        """
        Get all current documents (latest versions).
        
        Args:
            firm_name: Optional filter by firm name
            doc_type: Optional filter by document type
        """
        query = """
            SELECT 
                d.id,
                f.name as firm_name,
                d.base_url,
                d.url as original_url,
                d.title,
                d.doc_type,
                d.body_text,
                d.content_hash,
                d.scraped_at,
                d.last_updated_at,
                d.version
            FROM help_document d
            JOIN prop_firm f ON d.firm_id = f.id
            WHERE d.is_current = 1
        """
        params = []
        
        if firm_name:
            query += " AND f.name = ?"
            params.append(firm_name)
        
        if doc_type:
            query += " AND d.doc_type = ?"
            params.append(doc_type)
        
        query += " ORDER BY d.base_url"
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_document_history(self, base_url):
        """Get version history for a document."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT 
                d.id,
                d.version,
                d.title,
                d.content_hash,
                d.scraped_at,
                d.is_current,
                LENGTH(d.body_text) as content_length
            FROM help_document d
            WHERE d.base_url = ?
            ORDER BY d.version DESC
            """,
            (base_url,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def search_documents(self, search_term, firm_name=None):
        """
        Search documents by text content.
        
        Args:
            search_term: Text to search for
            firm_name: Optional filter by firm name
        """
        query = """
            SELECT 
                d.id,
                f.name as firm_name,
                d.title,
                d.base_url,
                d.doc_type,
                d.scraped_at
            FROM help_document d
            JOIN prop_firm f ON d.firm_id = f.id
            WHERE d.is_current = 1
            AND (d.title LIKE ? OR d.body_text LIKE ?)
        """
        params = [f'%{search_term}%', f'%{search_term}%']
        
        if firm_name:
            query += " AND f.name = ?"
            params.append(firm_name)
        
        query += " ORDER BY d.title"
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_document_paragraphs(self, document_id):
        """Get all paragraphs for a document."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT 
                paragraph_index,
                paragraph_text,
                paragraph_hash
            FROM document_paragraph
            WHERE document_id = ?
            ORDER BY paragraph_index
            """,
            (document_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self, firm_name=None):
        """Get database statistics."""
        cursor = self.conn.cursor()
        
        # Basic counts
        if firm_name:
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_documents,
                    COUNT(DISTINCT base_url) as unique_urls,
                    SUM(CASE WHEN is_current = 1 THEN 1 ELSE 0 END) as current_documents,
                    SUM(CASE WHEN doc_type = 'article' THEN 1 ELSE 0 END) as articles,
                    SUM(CASE WHEN doc_type = 'collection' THEN 1 ELSE 0 END) as collections,
                    AVG(LENGTH(body_text)) as avg_content_length,
                    MAX(version) as max_version
                FROM help_document d
                JOIN prop_firm f ON d.firm_id = f.id
                WHERE f.name = ?
                """,
                (firm_name,)
            )
        else:
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_documents,
                    COUNT(DISTINCT base_url) as unique_urls,
                    SUM(CASE WHEN is_current = 1 THEN 1 ELSE 0 END) as current_documents,
                    SUM(CASE WHEN doc_type = 'article' THEN 1 ELSE 0 END) as articles,
                    SUM(CASE WHEN doc_type = 'collection' THEN 1 ELSE 0 END) as collections,
                    AVG(LENGTH(body_text)) as avg_content_length,
                    MAX(version) as max_version
                FROM help_document
                """
            )
        
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    def get_duplicates_removed(self):
        """Get count of duplicate URLs that were merged."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT 
                base_url,
                COUNT(*) as url_count,
                GROUP_CONCAT(url, '; ') as original_urls
            FROM help_document
            WHERE is_current = 1
            GROUP BY base_url
            HAVING COUNT(DISTINCT url) > 1
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def export_to_json(self, output_file, firm_name=None):
        """Export current documents to JSON file."""
        docs = self.get_current_documents(firm_name=firm_name)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(docs, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Exported {len(docs)} documents to {output_file}")
    
    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Interactive query interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Query help center documents')
    parser.add_argument(
        '--db-path',
        default='propfirm_scraper.db',
        help='Path to database'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics'
    )
    parser.add_argument(
        '--list-firms',
        action='store_true',
        help='List all firms'
    )
    parser.add_argument(
        '--search',
        help='Search documents'
    )
    parser.add_argument(
        '--firm',
        help='Filter by firm name'
    )
    parser.add_argument(
        '--export',
        help='Export documents to JSON file'
    )
    parser.add_argument(
        '--duplicates',
        action='store_true',
        help='Show duplicate URLs that were merged'
    )
    
    args = parser.parse_args()
    
    db = DocumentDatabase(args.db_path)
    
    try:
        if args.list_firms:
            firms = db.get_all_firms()
            print(f"\n{'='*70}")
            print("FIRMS IN DATABASE")
            print(f"{'='*70}\n")
            for firm in firms:
                print(f"• {firm['name']}")
                print(f"  Domain: {firm['domain']}")
                print(f"  Help Center: {firm['help_center_url']}")
                print(f"  Added: {firm['created_at']}")
                print()
        
        elif args.stats:
            stats = db.get_stats(firm_name=args.firm)
            print(f"\n{'='*70}")
            print(f"DATABASE STATISTICS{' - ' + args.firm if args.firm else ''}")
            print(f"{'='*70}\n")
            print(f"Total documents:       {stats.get('total_documents', 0)}")
            print(f"Unique URLs:           {stats.get('unique_urls', 0)}")
            print(f"Current versions:      {stats.get('current_documents', 0)}")
            print(f"Articles:              {stats.get('articles', 0)}")
            print(f"Collections:           {stats.get('collections', 0)}")
            print(f"Avg content length:    {stats.get('avg_content_length', 0):.0f} chars")
            print(f"Max version number:    {stats.get('max_version', 0)}")
            print()
        
        elif args.search:
            results = db.search_documents(args.search, firm_name=args.firm)
            print(f"\n{'='*70}")
            print(f"SEARCH RESULTS: '{args.search}'")
            print(f"{'='*70}\n")
            print(f"Found {len(results)} matching documents:\n")
            for doc in results[:20]:  # Show first 20
                print(f"• {doc['title']}")
                print(f"  {doc['base_url']}")
                print(f"  Type: {doc['doc_type']} | Firm: {doc['firm_name']}")
                print()
        
        elif args.duplicates:
            dupes = db.get_duplicates_removed()
            print(f"\n{'='*70}")
            print("DUPLICATE URLs MERGED")
            print(f"{'='*70}\n")
            if dupes:
                for item in dupes:
                    print(f"Base URL: {item['base_url']}")
                    print(f"Variants: {item['url_count']}")
                    print(f"Original URLs:\n  {item['original_urls'].replace('; ', '\n  ')}")
                    print()
            else:
                print("No duplicate URLs found (all unique)")
        
        elif args.export:
            db.export_to_json(args.export, firm_name=args.firm)
        
        else:
            parser.print_help()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
