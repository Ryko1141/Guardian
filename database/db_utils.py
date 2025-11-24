"""
Database utilities for URL normalization, content hashing, and deduplication.
"""
import hashlib
import re
from urllib.parse import urlparse, urlunparse
from datetime import datetime


def canonicalize_url(url):
    """
    Normalize URL by removing query parameters, fragments, and standardizing format.
    
    Args:
        url: Original URL string
        
    Returns:
        Canonicalized base URL
        
    Examples:
        >>> canonicalize_url("https://help.fundednext.com/en/articles/123?ref=twitter#main")
        "https://help.fundednext.com/en/articles/123"
    """
    parsed = urlparse(url)
    
    # Remove query string and fragment
    canonical = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path.rstrip('/'),  # Remove trailing slash
        '',  # No params
        '',  # No query
        ''   # No fragment
    ))
    
    return canonical


def compute_content_hash(text):
    """
    Compute SHA256 hash of text content for change detection.
    
    Args:
        text: Content text to hash
        
    Returns:
        Hexadecimal hash string
    """
    if not text:
        return hashlib.sha256(b'').hexdigest()
    
    # Normalize whitespace before hashing for consistency
    normalized = re.sub(r'\s+', ' ', text.strip())
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def classify_document_type(title, url, body_text):
    """
    Classify document type based on content patterns.
    
    Args:
        title: Document title
        url: Document URL
        body_text: Document content
        
    Returns:
        Document type: 'article', 'collection', 'homepage'
    """
    title_lower = title.lower()
    url_lower = url.lower()
    
    # Homepage detection
    if any(x in url_lower for x in ['/en/', '/en', '/help/', '/help', '/faq/', '/faq']):
        if url_lower.rstrip('/').endswith(('/en', '/help', '/faq')):
            return 'homepage'
    
    # Collection page detection (category/section pages)
    collection_indicators = [
        'articles' in title_lower and len(body_text) < 2000,
        'faq' in title_lower and 'category' in title_lower,
        body_text.count('\n') > 50 and len(body_text) < 3000,  # Many links, little content
    ]
    
    if any(collection_indicators):
        # But check if it's actually empty
        if len(body_text.strip()) < 200:
            return 'collection'
    
    # Article - specific content page
    if '/articles/' in url_lower:
        return 'article'
    
    # Default to article if it has substantial content
    if len(body_text.strip()) > 200:
        return 'article'
    
    return 'collection'


def split_into_paragraphs(text, min_length=50):
    """
    Split document text into meaningful paragraphs for finer-grained retrieval.
    
    Args:
        text: Full document text
        min_length: Minimum paragraph length to keep
        
    Returns:
        List of paragraph strings
    """
    # Split on double newlines or multiple newlines
    paragraphs = re.split(r'\n\s*\n+', text)
    
    # Clean and filter paragraphs
    cleaned = []
    for para in paragraphs:
        para = para.strip()
        if len(para) >= min_length:
            cleaned.append(para)
    
    return cleaned


def extract_domain_from_url(url):
    """
    Extract domain name from URL.
    
    Args:
        url: Full URL
        
    Returns:
        Domain name (e.g., "help.fundednext.com")
    """
    parsed = urlparse(url)
    return parsed.netloc


def is_duplicate_content(existing_hash, new_hash):
    """
    Check if content has changed based on hash comparison.
    
    Args:
        existing_hash: Hash of existing document
        new_hash: Hash of new document
        
    Returns:
        True if content is identical, False if changed
    """
    return existing_hash == new_hash


def format_timestamp(dt=None):
    """
    Format datetime for database insertion.
    
    Args:
        dt: datetime object (defaults to now)
        
    Returns:
        ISO formatted timestamp string
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def deduplicate_urls(url_list):
    """
    Remove duplicate URLs from list after canonicalization.
    
    Args:
        url_list: List of URL strings
        
    Returns:
        List of unique canonicalized URLs
    """
    seen = set()
    unique = []
    
    for url in url_list:
        canonical = canonicalize_url(url)
        if canonical not in seen:
            seen.add(canonical)
            unique.append(url)
    
    return unique


def validate_document(doc):
    """
    Validate document has required fields.
    
    Args:
        doc: Dictionary with document data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['url', 'title', 'body']
    
    for field in required_fields:
        if field not in doc:
            return False, f"Missing required field: {field}"
        if not doc[field] or not str(doc[field]).strip():
            return False, f"Empty required field: {field}"
    
    return True, None


if __name__ == "__main__":
    # Test URL canonicalization
    test_urls = [
        "https://help.fundednext.com/en/articles/123?ref=twitter#main",
        "https://help.fundednext.com/en/articles/123#section",
        "https://help.fundednext.com/en/articles/123/",
        "https://help.fundednext.com/en/articles/123",
    ]
    
    print("URL Canonicalization Tests:")
    print("=" * 70)
    for url in test_urls:
        print(f"Original:    {url}")
        print(f"Canonical:   {canonicalize_url(url)}")
        print()
    
    # Test content hashing
    content1 = "This is test content."
    content2 = "This  is   test  content."  # Extra spaces
    content3 = "This is different content."
    
    print("\nContent Hash Tests:")
    print("=" * 70)
    hash1 = compute_content_hash(content1)
    hash2 = compute_content_hash(content2)
    hash3 = compute_content_hash(content3)
    
    print(f"Content 1 hash: {hash1[:16]}...")
    print(f"Content 2 hash: {hash2[:16]}... (whitespace normalized)")
    print(f"Content 3 hash: {hash3[:16]}...")
    print(f"Hash 1 == Hash 2: {hash1 == hash2} (should be True)")
    print(f"Hash 1 == Hash 3: {hash1 == hash3} (should be False)")
