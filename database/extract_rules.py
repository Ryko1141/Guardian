"""
Automated rule extraction pipeline.
End-to-end process: read documents → extract rules → classify → store in database.
"""
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add database module to path
sys.path.insert(0, str(Path(__file__).parent))

from query_db import DocumentDatabase
from rule_storage import RuleStorage
from hard_rule_extractor import HardRuleExtractor, deduplicate_rules
from soft_rule_detector import SoftRuleDetector, detect_challenge_type, merge_similar_rules


class RuleExtractionPipeline:
    """Automated pipeline for extracting and storing trading rules."""
    
    def __init__(self, db_path='propfirm_scraper.db', use_llm=True, llm_model='qwen2.5-coder:14b'):
        """
        Initialize extraction pipeline.
        
        Args:
            db_path: Path to database
            use_llm: Whether to use LLM for soft rule classification
            llm_model: Ollama model to use
        """
        self.db_path = db_path
        self.use_llm = use_llm
        
        # Initialize components
        self.doc_db = DocumentDatabase(db_path)
        self.rule_storage = RuleStorage(db_path)
        self.hard_extractor = HardRuleExtractor()
        self.soft_detector = SoftRuleDetector(llm_model) if use_llm else None
        
        # Statistics
        self.stats = {
            'documents_processed': 0,
            'hard_rules_extracted': 0,
            'soft_rules_extracted': 0,
            'total_rules_stored': 0,
            'errors': 0,
        }
    
    def extract_from_firm(self, firm_name: str, doc_types: List[str] = ['article'],
                         clear_existing=False, max_docs: int = None):
        """
        Extract rules from all documents for a specific firm.
        
        Args:
            firm_name: Name of the prop firm
            doc_types: Document types to process
            clear_existing: Whether to clear existing rules first
            max_docs: Maximum documents to process (for testing)
        """
        print(f"\n{'='*70}")
        print(f"AUTOMATED RULE EXTRACTION: {firm_name}")
        print(f"{'='*70}\n")
        
        # Connect to database
        self.rule_storage.connect()
        
        # Get firm ID
        firm = self.doc_db.get_firm_by_name(firm_name)
        if not firm:
            print(f"[ERROR] Firm '{firm_name}' not found in database")
            return False
        
        firm_id = firm['id']
        
        # Clear existing rules if requested
        if clear_existing:
            deleted = self.rule_storage.delete_rules_for_firm(firm_id)
            print(f"[CLEAR] Cleared {deleted} existing rules\n")
        
        # Get documents to process
        docs = []
        for doc_type in doc_types:
            docs.extend(self.doc_db.get_current_documents(
                firm_name=firm_name,
                doc_type=doc_type
            ))
        
        if max_docs:
            docs = docs[:max_docs]
        
        print(f"[INFO] Processing {len(docs)} documents...\n")
        
        # Process each document
        for idx, doc in enumerate(docs, 1):
            if idx % 25 == 0:
                print(f"  Progress: {idx}/{len(docs)} documents...")
            
            self._process_document(firm_id, doc)
        
        # Commit all changes
        self.rule_storage.conn.commit()
        
        # Print summary
        self._print_extraction_summary(firm_id)
        
        # Close connections
        self.rule_storage.close()
        self.doc_db.close()
        
        return True
    
    def _process_document(self, firm_id: int, doc: Dict):
        """Process a single document to extract rules."""
        try:
            self.stats['documents_processed'] += 1
            
            text = doc['body_text']
            title = doc['title']
            url = doc['base_url']
            doc_id = doc['id']
            
            # Skip very short documents
            if len(text.strip()) < 200:
                return
            
            # Detect program IDs using taxonomy (canonical program identifiers)
            program_ids = detect_challenge_type(text, title, url)

            # Extract hard rules
            hard_rules = self.hard_extractor.extract_all(text, title, url)
            hard_rules = deduplicate_rules(hard_rules)

            # Extract soft rules
            soft_rules = []
            if self.soft_detector:
                soft_rules = self.soft_detector.extract_soft_rules(text, title, url)
                soft_rules = merge_similar_rules(soft_rules)

            # Assign program_id to all rules (taxonomy-validated canonical IDs)
            all_rules = hard_rules + soft_rules
            for rule in all_rules:
                # If document is about specific program, assign it
                if len(program_ids) == 1 and program_ids[0] != 'general':
                    rule['program_id'] = program_ids[0]
                else:
                    # Keep existing or default to general
                    if 'program_id' not in rule:
                        rule['program_id'] = 'general'
                
                # Maintain backward compatibility - set challenge_type to program_id
                rule['challenge_type'] = rule['program_id']            # Store rules in database
            if all_rules:
                inserted = self.rule_storage.insert_rules_batch(firm_id, all_rules, doc_id)
                self.stats['hard_rules_extracted'] += len(hard_rules)
                self.stats['soft_rules_extracted'] += len(soft_rules)
                self.stats['total_rules_stored'] += inserted
        
        except Exception as e:
            print(f"  [ERROR] Error processing document '{doc.get('title', 'unknown')}': {e}")
            self.stats['errors'] += 1
    
    def _print_extraction_summary(self, firm_id: int):
        """Print extraction summary."""
        print(f"\n{'='*70}")
        print("EXTRACTION RESULTS")
        print(f"{'='*70}\n")
        
        print(f"Documents processed:     {self.stats['documents_processed']}")
        print(f"Hard rules extracted:    {self.stats['hard_rules_extracted']}")
        print(f"Soft rules extracted:    {self.stats['soft_rules_extracted']}")
        print(f"Total rules stored:      {self.stats['total_rules_stored']}")
        print(f"Errors:                  {self.stats['errors']}")
        
        # Get detailed statistics from database
        print()
        self.rule_storage.print_rule_summary(firm_id)
    
    def extract_sample_rules(self, firm_name: str, sample_size: int = 10):
        """
        Extract rules from a sample of documents for testing.
        
        Args:
            firm_name: Name of the prop firm
            sample_size: Number of documents to process
        """
        print(f"\n{'='*70}")
        print(f"SAMPLE EXTRACTION: {firm_name} ({sample_size} documents)")
        print(f"{'='*70}\n")
        
        # Get sample documents
        docs = self.doc_db.get_current_documents(firm_name=firm_name)
        
        if not docs:
            print(f"[ERROR] No documents found for {firm_name}")
            return
        
        # Filter for documents likely to contain rules
        rule_docs = [d for d in docs if any(keyword in d['title'].lower() 
                     for keyword in ['rule', 'challenge', 'stellar', 'prohibited', 'limit'])]
        
        if rule_docs:
            sample_docs = rule_docs[:sample_size]
        else:
            sample_docs = docs[:sample_size]
        
        print(f"Processing {len(sample_docs)} sample documents:\n")
        
        for doc in sample_docs:
            print(f"[DOC] {doc['title'][:60]}...")
            
            text = doc['body_text']
            title = doc['title']
            url = doc['base_url']
            
            # Extract rules
            hard_rules = self.hard_extractor.extract_all(text, title, url)
            hard_rules = deduplicate_rules(hard_rules)
            
            soft_rules = []
            if self.soft_detector:
                soft_rules = self.soft_detector.extract_soft_rules(text, title, url)
                soft_rules = merge_similar_rules(soft_rules)
            
            # Detect challenge types
            challenge_types = detect_challenge_type(text, title, url)
            
            print(f"  Challenge types: {', '.join(challenge_types)}")
            print(f"  Hard rules: {len(hard_rules)}")
            print(f"  Soft rules: {len(soft_rules)}")
            
            # Show sample rules
            all_rules = hard_rules + soft_rules
            if all_rules:
                print(f"  Sample rules:")
                for rule in all_rules[:3]:
                    print(f"    • {rule['rule_code']}: {rule['description'][:60]}...")
            print()
        
        print(f"{'='*70}\n")


def main():
    """Main entry point for rule extraction."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automated rule extraction from help center documents'
    )
    parser.add_argument(
        '--firm',
        default='FundedNext',
        help='Firm name to extract rules from'
    )
    parser.add_argument(
        '--db-path',
        default='propfirm_scraper.db',
        help='Path to database'
    )
    parser.add_argument(
        '--sample',
        type=int,
        metavar='N',
        help='Extract from N sample documents only (for testing)'
    )
    parser.add_argument(
        '--max-docs',
        type=int,
        metavar='N',
        help='Maximum number of documents to process'
    )
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Disable LLM-based soft rule extraction'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing rules before extraction'
    )
    parser.add_argument(
        '--model',
        default='qwen2.5-coder:14b',
        help='Ollama model to use for LLM extraction'
    )
    parser.add_argument(
        '--export',
        metavar='FILE',
        help='Export extracted rules to JSON file'
    )
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = RuleExtractionPipeline(
        db_path=args.db_path,
        use_llm=not args.no_llm,
        llm_model=args.model
    )
    
    try:
        if args.sample:
            # Sample extraction for testing
            pipeline.extract_sample_rules(args.firm, sample_size=args.sample)
        else:
            # Full extraction
            success = pipeline.extract_from_firm(
                firm_name=args.firm,
                clear_existing=args.clear,
                max_docs=args.max_docs
            )
            
            if success and args.export:
                # Export rules to JSON
                pipeline.rule_storage.connect()
                firm = pipeline.doc_db.get_firm_by_name(args.firm)
                if firm:
                    pipeline.rule_storage.export_rules_to_json(firm['id'], args.export)
                pipeline.rule_storage.close()
            
            if success:
                print("\n[SUCCESS] Rule extraction completed successfully!")
            else:
                print("\n[WARNING] Rule extraction completed with errors")
    
    except KeyboardInterrupt:
        print("\n\n[WARNING] Extraction interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
