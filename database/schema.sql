-- PropFirm Scraper Database Schema
-- Normalized storage for help center documents with versioning and change detection

-- ============================================================================
-- TABLE: prop_firm
-- Stores information about each proprietary trading firm
-- ============================================================================
CREATE TABLE IF NOT EXISTS prop_firm (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    domain TEXT NOT NULL,
    website_url TEXT,
    help_center_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast lookups by domain
CREATE INDEX IF NOT EXISTS idx_prop_firm_domain ON prop_firm(domain);

-- ============================================================================
-- TABLE: help_document
-- Stores normalized help center articles and pages
-- ============================================================================
CREATE TABLE IF NOT EXISTS help_document (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id INTEGER NOT NULL,
    
    -- URL information
    url TEXT NOT NULL,                    -- Original URL as scraped
    base_url TEXT NOT NULL,               -- Canonicalized URL (no query params/fragments)
    
    -- Document metadata
    title TEXT NOT NULL,
    doc_type TEXT DEFAULT 'article',      -- article, collection, homepage
    
    -- Content
    body_text TEXT NOT NULL,
    content_hash TEXT NOT NULL,           -- SHA256 hash of body_text for change detection
    
    -- Timestamps
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata
    is_current BOOLEAN DEFAULT 1,         -- For versioning: current version of this base_url
    version INTEGER DEFAULT 1,
    
    -- Foreign key
    FOREIGN KEY (firm_id) REFERENCES prop_firm(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_help_document_firm_id ON help_document(firm_id);
CREATE INDEX IF NOT EXISTS idx_help_document_base_url ON help_document(base_url);
CREATE INDEX IF NOT EXISTS idx_help_document_content_hash ON help_document(content_hash);
CREATE INDEX IF NOT EXISTS idx_help_document_doc_type ON help_document(doc_type);
CREATE INDEX IF NOT EXISTS idx_help_document_is_current ON help_document(is_current);
CREATE UNIQUE INDEX IF NOT EXISTS idx_help_document_firm_base_url_current 
    ON help_document(firm_id, base_url, is_current) 
    WHERE is_current = 1;

-- ============================================================================
-- TABLE: document_paragraph
-- Optional: Break documents into paragraphs for finer-grained RAG retrieval
-- ============================================================================
CREATE TABLE IF NOT EXISTS document_paragraph (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    paragraph_index INTEGER NOT NULL,
    paragraph_text TEXT NOT NULL,
    paragraph_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (document_id) REFERENCES help_document(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_document_paragraph_document_id ON document_paragraph(document_id);
CREATE INDEX IF NOT EXISTS idx_document_paragraph_hash ON document_paragraph(paragraph_hash);

-- ============================================================================
-- TABLE: firm_rule (for future structured rule extraction)
-- ============================================================================
CREATE TABLE IF NOT EXISTS firm_rule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id INTEGER NOT NULL,
    source_document_id INTEGER,
    
    -- Rule identification
    rule_type TEXT NOT NULL,              -- profit_target, daily_loss, max_drawdown, etc.
    rule_category TEXT,                   -- hard_rule, soft_rule, guideline
    challenge_type TEXT,                  -- stellar_1_step, stellar_2_step, etc.
    
    -- Rule content
    value TEXT,                           -- The actual value (e.g., "10%", "$5000")
    details TEXT,                         -- Full explanation
    conditions TEXT,                      -- Conditions or qualifications
    severity TEXT,                        -- critical, important, optional
    
    -- Metadata
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extraction_method TEXT,               -- pattern, llm, hybrid, manual
    confidence_score REAL,                -- 0.0 to 1.0
    
    FOREIGN KEY (firm_id) REFERENCES prop_firm(id) ON DELETE CASCADE,
    FOREIGN KEY (source_document_id) REFERENCES help_document(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_firm_rule_firm_id ON firm_rule(firm_id);
CREATE INDEX IF NOT EXISTS idx_firm_rule_type ON firm_rule(rule_type);
CREATE INDEX IF NOT EXISTS idx_firm_rule_challenge_type ON firm_rule(challenge_type);
CREATE INDEX IF NOT EXISTS idx_firm_rule_source_document ON firm_rule(source_document_id);

-- ============================================================================
-- VIEWS: Useful queries
-- ============================================================================

-- Current documents only (for RAG retrieval)
CREATE VIEW IF NOT EXISTS current_documents AS
SELECT 
    d.id,
    d.firm_id,
    f.name as firm_name,
    d.base_url,
    d.title,
    d.doc_type,
    d.body_text,
    d.scraped_at,
    d.last_updated_at
FROM help_document d
JOIN prop_firm f ON d.firm_id = f.id
WHERE d.is_current = 1;

-- Document change history
CREATE VIEW IF NOT EXISTS document_history AS
SELECT 
    d.firm_id,
    f.name as firm_name,
    d.base_url,
    d.title,
    d.version,
    d.content_hash,
    d.scraped_at,
    d.is_current
FROM help_document d
JOIN prop_firm f ON d.firm_id = f.id
ORDER BY d.base_url, d.version DESC;

-- Documents by type
CREATE VIEW IF NOT EXISTS documents_by_type AS
SELECT 
    f.name as firm_name,
    d.doc_type,
    COUNT(*) as document_count,
    AVG(LENGTH(d.body_text)) as avg_content_length
FROM help_document d
JOIN prop_firm f ON d.firm_id = f.id
WHERE d.is_current = 1
GROUP BY f.name, d.doc_type;
