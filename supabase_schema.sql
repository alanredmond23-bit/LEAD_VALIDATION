-- Anthony Lead Forensics - Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor to create all required tables

-- =============================================================================
-- VENDORS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS vendors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_name TEXT NOT NULL UNIQUE,
    vendor_email TEXT,
    vendor_phone TEXT,
    first_batch_date TIMESTAMP WITH TIME ZONE,
    last_batch_date TIMESTAMP WITH TIME ZONE,
    total_batches INTEGER DEFAULT 0,
    total_leads_received INTEGER DEFAULT 0,
    total_fraudulent_leads INTEGER DEFAULT 0,
    average_fraud_rate DECIMAL(5,2) DEFAULT 0.00,
    total_refunds_issued DECIMAL(10,2) DEFAULT 0.00,
    vendor_status TEXT DEFAULT 'active' CHECK (vendor_status IN ('active', 'warning', 'suspended', 'blacklisted')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast vendor lookups
CREATE INDEX IF NOT EXISTS idx_vendors_name ON vendors(vendor_name);
CREATE INDEX IF NOT EXISTS idx_vendors_status ON vendors(vendor_status);

-- =============================================================================
-- BATCHES TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID REFERENCES vendors(id) ON DELETE CASCADE,
    batch_identifier TEXT NOT NULL,
    batch_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    lead_count INTEGER NOT NULL,
    fraudulent_count INTEGER DEFAULT 0,
    suspicious_count INTEGER DEFAULT 0,
    valid_count INTEGER DEFAULT 0,
    fraud_percentage DECIMAL(5,2) DEFAULT 0.00,

    -- Refund information
    cost_per_lead DECIMAL(10,2),
    total_batch_cost DECIMAL(10,2),
    refund_status TEXT CHECK (refund_status IN ('FULL REFUND', 'PARTIAL REFUND', 'NO REFUND')),
    refund_percentage DECIMAL(5,2) DEFAULT 0.00,
    refund_amount DECIMAL(10,2) DEFAULT 0.00,

    -- Fraud breakdown by category (average scores)
    avg_contact_score DECIMAL(5,2) DEFAULT 0.00,
    avg_duplicate_score DECIMAL(5,2) DEFAULT 0.00,
    avg_geographic_score DECIMAL(5,2) DEFAULT 0.00,
    avg_timing_score DECIMAL(5,2) DEFAULT 0.00,
    avg_quality_score DECIMAL(5,2) DEFAULT 0.00,
    avg_fraud_score DECIMAL(5,2) DEFAULT 0.00,

    -- Auto-refund triggers
    auto_refund_triggered BOOLEAN DEFAULT FALSE,
    auto_refund_reason TEXT,

    -- Analysis metadata
    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analysis_version TEXT DEFAULT '2.0',
    analyst_name TEXT DEFAULT 'Anthony Lead Forensics',

    -- File references
    input_filename TEXT,
    output_filename TEXT,
    evidence_package_path TEXT,

    -- Notes and status
    notes TEXT,
    dispute_status TEXT CHECK (dispute_status IN ('pending', 'submitted', 'won', 'lost', 'settled')),
    dispute_notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(vendor_id, batch_identifier)
);

-- Indexes for fast batch lookups
CREATE INDEX IF NOT EXISTS idx_batches_vendor ON batches(vendor_id);
CREATE INDEX IF NOT EXISTS idx_batches_date ON batches(batch_date);
CREATE INDEX IF NOT EXISTS idx_batches_fraud_rate ON batches(fraud_percentage);
CREATE INDEX IF NOT EXISTS idx_batches_refund_status ON batches(refund_status);

-- =============================================================================
-- LEADS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID REFERENCES batches(id) ON DELETE CASCADE,

    -- Lead information (PII - handle with care)
    lead_name TEXT,
    lead_email TEXT,
    lead_phone TEXT,
    lead_address TEXT,
    lead_city TEXT,
    lead_state TEXT,
    lead_zip TEXT,
    lead_ip_address INET,
    submission_timestamp TIMESTAMP WITH TIME ZONE,

    -- Fraud scoring
    fraud_score INTEGER NOT NULL CHECK (fraud_score >= 0 AND fraud_score <= 100),
    classification TEXT NOT NULL CHECK (classification IN ('VALID', 'SUSPICIOUS', 'FRAUDULENT')),
    is_fraudulent BOOLEAN NOT NULL,

    -- Fraud breakdown by category
    contact_score INTEGER DEFAULT 0,
    duplicate_score INTEGER DEFAULT 0,
    geographic_score INTEGER DEFAULT 0,
    timing_score INTEGER DEFAULT 0,
    quality_score INTEGER DEFAULT 0,

    -- Fraud reasons (comma-separated)
    fraud_reasons TEXT,

    -- API validation results
    phone_valid BOOLEAN,
    phone_carrier TEXT,
    phone_line_type TEXT,
    phone_is_voip BOOLEAN,
    email_valid BOOLEAN,
    email_disposable BOOLEAN,
    email_status TEXT,
    ip_fraud_score INTEGER,
    ip_country TEXT,
    ip_vpn_detected BOOLEAN,
    ip_proxy_detected BOOLEAN,

    -- Duplicate detection
    is_exact_duplicate BOOLEAN DEFAULT FALSE,
    is_fuzzy_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of_lead_id UUID REFERENCES leads(id),
    similarity_score DECIMAL(5,2),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for fast lead lookups
CREATE INDEX IF NOT EXISTS idx_leads_batch ON leads(batch_id);
CREATE INDEX IF NOT EXISTS idx_leads_classification ON leads(classification);
CREATE INDEX IF NOT EXISTS idx_leads_fraud_score ON leads(fraud_score);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(lead_email);
CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(lead_phone);

-- =============================================================================
-- FRAUD PATTERNS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS fraud_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name TEXT NOT NULL,
    pattern_type TEXT CHECK (pattern_type IN ('bot_ring', 'recycled_list', 'fraud_farm', 'incentivized_gaming', 'email_scraping', 'voip_flood', 'other')),
    description TEXT,
    detection_criteria JSONB,
    severity TEXT CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    auto_refund_trigger BOOLEAN DEFAULT FALSE,
    times_detected INTEGER DEFAULT 0,
    last_detected TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- BATCH_FRAUD_PATTERNS (Junction Table)
-- =============================================================================
CREATE TABLE IF NOT EXISTS batch_fraud_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID REFERENCES batches(id) ON DELETE CASCADE,
    fraud_pattern_id UUID REFERENCES fraud_patterns(id) ON DELETE CASCADE,
    affected_lead_count INTEGER,
    pattern_confidence DECIMAL(5,2),
    notes TEXT,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(batch_id, fraud_pattern_id)
);

-- =============================================================================
-- TOP FRAUD INDICATORS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS batch_fraud_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID REFERENCES batches(id) ON DELETE CASCADE,
    indicator_name TEXT NOT NULL,
    indicator_category TEXT CHECK (indicator_category IN ('contact', 'duplicate', 'geographic', 'timing', 'quality')),
    affected_lead_count INTEGER,
    percentage DECIMAL(5,2),
    points_per_lead INTEGER,
    total_points INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_indicators_batch ON batch_fraud_indicators(batch_id);

-- =============================================================================
-- API VALIDATION LOG TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS api_validation_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    api_service TEXT NOT NULL CHECK (api_service IN ('twilio', 'zerobounce', 'ipqualityscore', 'other')),
    request_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    response_timestamp TIMESTAMP WITH TIME ZONE,
    request_data JSONB,
    response_data JSONB,
    success BOOLEAN,
    error_message TEXT,
    api_cost DECIMAL(6,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_api_log_lead ON api_validation_log(lead_id);
CREATE INDEX IF NOT EXISTS idx_api_log_service ON api_validation_log(api_service);

-- =============================================================================
-- DISPOSABLE EMAILS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS disposable_email_domains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain TEXT NOT NULL UNIQUE,
    times_detected INTEGER DEFAULT 0,
    last_detected TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    source TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_disposable_domains ON disposable_email_domains(domain);

-- Prepopulate with known disposable domains
INSERT INTO disposable_email_domains (domain, source) VALUES
    ('guerrillamail.com', 'initial_seed'),
    ('temp-mail.org', 'initial_seed'),
    ('10minutemail.com', 'initial_seed'),
    ('mailinator.com', 'initial_seed'),
    ('throwaway.email', 'initial_seed'),
    ('tempmail.com', 'initial_seed'),
    ('getnada.com', 'initial_seed'),
    ('maildrop.cc', 'initial_seed'),
    ('yopmail.com', 'initial_seed'),
    ('fakeinbox.com', 'initial_seed'),
    ('emailondeck.com', 'initial_seed'),
    ('throwawaymail.com', 'initial_seed'),
    ('trashmail.com', 'initial_seed'),
    ('sharklasers.com', 'initial_seed'),
    ('spam4.me', 'initial_seed')
ON CONFLICT (domain) DO NOTHING;

-- =============================================================================
-- FRAUD BLACKLIST TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS fraud_blacklist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blacklist_type TEXT CHECK (blacklist_type IN ('email', 'phone', 'ip', 'domain')),
    value TEXT NOT NULL,
    reason TEXT,
    times_detected INTEGER DEFAULT 1,
    first_detected TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_detected TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(blacklist_type, value)
);

CREATE INDEX IF NOT EXISTS idx_blacklist_type ON fraud_blacklist(blacklist_type);
CREATE INDEX IF NOT EXISTS idx_blacklist_value ON fraud_blacklist(value);

-- =============================================================================
-- ANALYTICS VIEWS
-- =============================================================================

-- Vendor fraud summary view
CREATE OR REPLACE VIEW vendor_fraud_summary AS
SELECT
    v.id,
    v.vendor_name,
    v.vendor_status,
    v.total_batches,
    v.total_leads_received,
    v.total_fraudulent_leads,
    v.average_fraud_rate,
    v.total_refunds_issued,
    COUNT(b.id) FILTER (WHERE b.refund_status = 'FULL REFUND') as full_refund_count,
    COUNT(b.id) FILTER (WHERE b.refund_status = 'PARTIAL REFUND') as partial_refund_count,
    AVG(b.fraud_percentage) as avg_fraud_percentage,
    MAX(b.fraud_percentage) as max_fraud_percentage,
    MIN(b.fraud_percentage) as min_fraud_percentage
FROM vendors v
LEFT JOIN batches b ON v.id = b.vendor_id
GROUP BY v.id, v.vendor_name, v.vendor_status, v.total_batches,
         v.total_leads_received, v.total_fraudulent_leads,
         v.average_fraud_rate, v.total_refunds_issued;

-- Recent high fraud batches view
CREATE OR REPLACE VIEW recent_high_fraud_batches AS
SELECT
    b.id,
    b.batch_identifier,
    v.vendor_name,
    b.batch_date,
    b.lead_count,
    b.fraudulent_count,
    b.fraud_percentage,
    b.refund_status,
    b.refund_amount,
    b.auto_refund_triggered,
    b.auto_refund_reason
FROM batches b
JOIN vendors v ON b.vendor_id = v.id
WHERE b.fraud_percentage >= 25.0
ORDER BY b.batch_date DESC
LIMIT 50;

-- Fraud indicator frequency view
CREATE OR REPLACE VIEW fraud_indicator_frequency AS
SELECT
    indicator_name,
    indicator_category,
    COUNT(*) as times_detected,
    SUM(affected_lead_count) as total_leads_affected,
    AVG(percentage) as avg_percentage,
    MAX(percentage) as max_percentage
FROM batch_fraud_indicators
GROUP BY indicator_name, indicator_category
ORDER BY times_detected DESC;

-- =============================================================================
-- FUNCTIONS
-- =============================================================================

-- Function to update vendor statistics
CREATE OR REPLACE FUNCTION update_vendor_stats(vendor_uuid UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE vendors
    SET
        total_batches = (SELECT COUNT(*) FROM batches WHERE vendor_id = vendor_uuid),
        total_leads_received = (SELECT COALESCE(SUM(lead_count), 0) FROM batches WHERE vendor_id = vendor_uuid),
        total_fraudulent_leads = (SELECT COALESCE(SUM(fraudulent_count), 0) FROM batches WHERE vendor_id = vendor_uuid),
        average_fraud_rate = (SELECT COALESCE(AVG(fraud_percentage), 0) FROM batches WHERE vendor_id = vendor_uuid),
        total_refunds_issued = (SELECT COALESCE(SUM(refund_amount), 0) FROM batches WHERE vendor_id = vendor_uuid),
        last_batch_date = (SELECT MAX(batch_date) FROM batches WHERE vendor_id = vendor_uuid),
        updated_at = NOW()
    WHERE id = vendor_uuid;

    -- Update vendor status based on fraud rate
    UPDATE vendors
    SET vendor_status = CASE
        WHEN average_fraud_rate >= 40 THEN 'blacklisted'
        WHEN average_fraud_rate >= 30 THEN 'suspended'
        WHEN average_fraud_rate >= 20 THEN 'warning'
        ELSE 'active'
    END
    WHERE id = vendor_uuid;
END;
$$ LANGUAGE plpgsql;

-- Function to add to fraud blacklist
CREATE OR REPLACE FUNCTION add_to_blacklist(
    p_type TEXT,
    p_value TEXT,
    p_reason TEXT
)
RETURNS UUID AS $$
DECLARE
    blacklist_id UUID;
BEGIN
    INSERT INTO fraud_blacklist (blacklist_type, value, reason, times_detected, first_detected, last_detected)
    VALUES (p_type, p_value, p_reason, 1, NOW(), NOW())
    ON CONFLICT (blacklist_type, value)
    DO UPDATE SET
        times_detected = fraud_blacklist.times_detected + 1,
        last_detected = NOW(),
        is_active = TRUE
    RETURNING id INTO blacklist_id;

    RETURN blacklist_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Trigger to update vendor stats after batch insert/update
CREATE OR REPLACE FUNCTION trigger_update_vendor_stats()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM update_vendor_stats(NEW.vendor_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_batch_insert_update
AFTER INSERT OR UPDATE ON batches
FOR EACH ROW
EXECUTE FUNCTION trigger_update_vendor_stats();

-- Trigger to update timestamps
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp_vendors
BEFORE UPDATE ON vendors
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_timestamp_batches
BEFORE UPDATE ON batches
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- =============================================================================
-- ROW LEVEL SECURITY (Optional - Enable if needed)
-- =============================================================================

-- Enable RLS on all tables
-- ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE batches ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

-- Example policy: Allow all operations for authenticated users
-- CREATE POLICY "Allow all for authenticated users" ON vendors
-- FOR ALL USING (auth.role() = 'authenticated');

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Full-text search indexes (optional)
-- CREATE INDEX IF NOT EXISTS idx_leads_name_fts ON leads USING gin(to_tsvector('english', lead_name));
-- CREATE INDEX IF NOT EXISTS idx_leads_email_fts ON leads USING gin(to_tsvector('english', lead_email));

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE vendors IS 'Stores vendor information and aggregate fraud statistics';
COMMENT ON TABLE batches IS 'Stores batch-level fraud analysis results';
COMMENT ON TABLE leads IS 'Stores individual lead data and fraud scores (contains PII)';
COMMENT ON TABLE fraud_patterns IS 'Catalog of known fraud patterns';
COMMENT ON TABLE batch_fraud_patterns IS 'Links batches to detected fraud patterns';
COMMENT ON TABLE batch_fraud_indicators IS 'Top fraud indicators per batch';
COMMENT ON TABLE api_validation_log IS 'Logs all API validation calls for audit trail';
COMMENT ON TABLE disposable_email_domains IS 'List of known disposable email domains';
COMMENT ON TABLE fraud_blacklist IS 'Blacklist of known fraudulent emails, phones, IPs';

-- =============================================================================
-- COMPLETED
-- =============================================================================

-- Grant necessary permissions (adjust as needed)
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

SELECT 'Anthony Lead Forensics database schema created successfully!' as status;
