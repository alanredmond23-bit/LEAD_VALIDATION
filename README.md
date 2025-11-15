# Anthony Lead Forensics - Lead Validation System

**Version:** 2.0 Enhanced - Refund-Focused Fraud Detection
**Repository:** https://github.com/alanredmond23-bit/LEAD_VALIDATION

---

## Overview

The Anthony Lead Forensics system is a comprehensive fraud detection and lead validation platform designed to validate vendor lead files, quantify fraud, and justify refunds through evidence-based analysis.

### Core Mission
**Detect fraudulent leads ≥ 25% to secure FULL REFUND with quantifiable evidence.**

### Key Features
- ✅ **25% Refund Threshold** - Clear rule: ≥25% fraud = full refund
- ✅ **100-Point Fraud Scoring** - Every lead gets a quantifiable score
- ✅ **80+ Fraud Indicators** - Specific, measurable fraud detection
- ✅ **API-Based Validation** - Irrefutable proof from Twilio, ZeroBounce, IPQualityScore
- ✅ **Supabase Database** - Persistent storage, vendor history tracking
- ✅ **Automated Detection** - Bot patterns, duplicates, VPN/proxy, geographic fraud
- ✅ **Professional Reports** - Excel analysis, PDF reports, visual evidence
- ✅ **Vendor Intelligence** - Track fraud trends, auto-status updates

---

## Quick Start

### 1. Install Dependencies
```bash
pip install pandas openpyxl phonenumbers fuzzywuzzy python-Levenshtein supabase python-dotenv
```

### 2. Configure Credentials
Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Set Up Database
Run `supabase_schema.sql` in your Supabase SQL Editor:
- Go to: https://fifybuzwfaegloijrmqb.supabase.co
- Click "SQL Editor"
- Paste contents of `supabase_schema.sql`
- Click "Run"

### 4. Test Configuration
```bash
python test_env.py
```

### 5. Run Fraud Analysis
```bash
# Basic analysis (no APIs needed)
python fraud_scorer_sample.py sample_leads.csv 5.00

# With database integration
python fraud_scorer_with_db.py sample_leads.csv --vendor "VendorName" --cost 5.00
```

### 6. Query Vendor History
```bash
python vendor_history_analyzer.py --list-vendors
python vendor_history_analyzer.py --vendor "VendorName"
python vendor_history_analyzer.py --summary
```

---

## Repository Structure

```
LEAD_VALIDATION/
├── README.md                           # This file
├── .env.example                        # Template for environment variables
├── .gitignore                          # Git ignore rules (protects .env)
│
├── Documentation/
│   ├── ENHANCED_README.md              # Complete system documentation (48KB)
│   ├── ENHANCED_AGENT_PROMPT.md        # AI agent instructions (40KB)
│   ├── IMPLEMENTATION_GUIDE.md         # Step-by-step implementation (35KB)
│   ├── SUPABASE_SETUP_GUIDE.md         # Database setup guide (14KB)
│   ├── WHATS_NEW.md                    # Overview of enhancements (11KB)
│   ├── CREDENTIALS_SUMMARY.md          # Credentials status & config (15KB)
│   ├── LEADVALIDATIONREADME.md         # Original README (legacy)
│   └── agent prompt.md                 # Original agent prompt (legacy)
│
├── Configuration/
│   ├── fraud_rules_config.json         # Fraud scoring rules (13KB)
│   └── .env                            # Real credentials (NOT committed)
│
├── Database/
│   ├── supabase_schema.sql             # Database schema (9.2KB)
│   └── supabase_client.py              # Database client wrapper (18KB)
│
├── Scripts/
│   ├── fraud_scorer_sample.py          # Basic fraud scorer (17KB)
│   ├── fraud_scorer_with_db.py         # Fraud scorer with DB integration (13KB)
│   ├── vendor_history_analyzer.py      # Vendor history analysis (14KB)
│   └── test_env.py                     # Environment variable tester
│
├── Data/
│   └── sample_leads.csv                # Sample test data (20 leads)
│
└── .git/                               # Git repository (not shown)
```

---

## System Components

### 1. Fraud Detection Engine
- **fraud_scorer_sample.py** - Basic fraud scoring (works without APIs)
- **fraud_scorer_with_db.py** - Enhanced version with database integration
- **fraud_rules_config.json** - Configuration with all fraud rules and thresholds

### 2. Database Integration
- **supabase_schema.sql** - Complete database schema (9 tables)
- **supabase_client.py** - Python wrapper for all database operations

### 3. Analysis & Reporting
- **vendor_history_analyzer.py** - Query and analyze vendor fraud history
- Generates Excel reports, PDF audits, visual charts

### 4. Documentation
- **ENHANCED_README.md** - Complete system documentation
- **IMPLEMENTATION_GUIDE.md** - Step-by-step implementation
- **SUPABASE_SETUP_GUIDE.md** - Database setup instructions

---

## The Refund Formula

```
FRAUD SCORE = (Fraudulent Leads / Total Leads) × 100

IF Fraud Score ≥ 25% → FULL REFUND (100%)
IF Fraud Score 15-24% → PARTIAL REFUND (pro-rata)
IF Fraud Score < 15% → NO REFUND (acceptable tolerance)
```

### Example
```
Batch: 200 leads @ $5 each = $1,000 total
Fraudulent: 65 leads
Fraud Score: 32.5%

32.5% ≥ 25% → FULL REFUND = $1,000
```

---

## Fraud Scoring System

### Point Allocation (100 Points Maximum)

| Category | Max Points | Weight | What It Detects |
|----------|-----------|--------|-----------------|
| **Contact Validation** | 40 | 40% | Invalid/fake phone & email, VOIP, disposable emails |
| **Duplicate Detection** | 25 | 25% | Exact duplicates, fuzzy matches, recycled contacts |
| **Geographic Fraud** | 15 | 15% | VPN/proxy, foreign IPs, area code mismatches |
| **Timing Patterns** | 10 | 10% | Bot submissions, velocity spikes |
| **Data Quality** | 10 | 10% | Gibberish names, missing fields |

### Lead Classification
- **0-24 points:** VALID LEAD
- **25-49 points:** SUSPICIOUS LEAD
- **50-100 points:** FRAUDULENT LEAD

---

## API Integration

### Required APIs

| Service | Cost | Purpose | Status |
|---------|------|---------|--------|
| **Twilio Lookup** | $5/1K leads | Phone validation, VOIP detection | ⚠️ Pending |
| **ZeroBounce** | $7.50/1K leads | Email validation, disposable detection | ⚠️ Pending |
| **IPQualityScore** | $2.80/1K leads | IP fraud, VPN/proxy detection | ⚠️ Pending |
| **Supabase** | Free tier OK | Database storage, history tracking | ✅ Configured |
| **TOTAL** | **$15.30/1K** | Complete validation | - |

### Free Trials Available
- Twilio: Test credits included
- ZeroBounce: 200 free credits
- IPQualityScore: 500 free lookups

---

## Database Schema

### Core Tables (9 Total)

1. **vendors** - Vendor profiles and aggregate fraud statistics
2. **batches** - Batch-level fraud analysis results
3. **leads** - Individual lead data and fraud scores (contains PII)
4. **batch_fraud_indicators** - Top fraud indicators per batch
5. **fraud_patterns** - Catalog of known fraud patterns
6. **batch_fraud_patterns** - Links batches to detected patterns
7. **api_validation_log** - API call audit trail with costs
8. **disposable_email_domains** - Known disposable email domains (40+ preloaded)
9. **fraud_blacklist** - Blacklisted emails, phones, IPs, domains

### Views & Functions
- `vendor_fraud_summary` - Vendor analytics
- `recent_high_fraud_batches` - High fraud tracking
- `fraud_indicator_frequency` - Top indicators
- `update_vendor_stats()` - Auto-update vendor metrics
- `add_to_blacklist()` - Blacklist management

---

## Usage Examples

### Basic Fraud Detection
```bash
# Analyze leads without database
python fraud_scorer_sample.py vendor_leads.csv 5.00

# Output:
# - vendor_leads_fraud_analysis.xlsx
# - vendor_leads_fraud_report.txt
```

### With Database Integration
```bash
# Process and save to database
python fraud_scorer_with_db.py vendor_leads.csv \
  --vendor "PetLeads Pro" \
  --cost 5.00 \
  --batch-id "JAN2024_001"

# Output:
# - Excel analysis file
# - Text report
# - Saved to Supabase database
```

### Vendor History Analysis
```bash
# List all vendors
python vendor_history_analyzer.py --list-vendors

# Analyze specific vendor
python vendor_history_analyzer.py --vendor "PetLeads Pro"

# Show high fraud batches (≥25%)
python vendor_history_analyzer.py --high-fraud

# Overall system summary
python vendor_history_analyzer.py --summary

# Export vendor report to Excel
python vendor_history_analyzer.py --vendor "PetLeads Pro" --export
```

---

## Fraud Detection Capabilities

### With Current Setup (Basic)
✅ Format validation (phone, email, name)
✅ Duplicate detection (exact and fuzzy matching)
✅ Data quality scoring
✅ Database storage and history tracking
✅ Vendor trend analysis
✅ Excel and text report generation

### With Full API Integration
✅ Phone number validation (Twilio)
✅ VOIP/burner detection (Twilio)
✅ Carrier information (Twilio)
✅ Email deliverability (ZeroBounce)
✅ Disposable email detection (ZeroBounce)
✅ VPN/proxy detection (IPQualityScore)
✅ IP geolocation (IPQualityScore)
✅ IP fraud scoring (IPQualityScore)
✅ Complete 100-point fraud scoring

---

## Output Formats

### Excel Analysis File
- Lead-by-lead breakdown with fraud scores
- Color-coded classification (red/yellow/green)
- Fraud reasons for each lead
- Summary statistics
- Fraud category breakdown
- Top 10 fraud indicators

### Text Report
- Executive summary
- Batch statistics
- Fraud breakdown by category
- Refund determination with justification
- Industry comparison
- Recommendations

### Database Records
- Permanent storage of all results
- Vendor fraud history
- Batch analysis details
- Lead-level data with PII
- API validation logs

---

## Security & Privacy

### Credentials Management
✅ `.env` file contains all credentials (NOT committed)
✅ `.gitignore` prevents accidental commits
✅ `.env.example` provides safe template (committed)
✅ `test_env.py` verifies configuration

### PII Handling
- Leads table contains PII (names, emails, phones, addresses)
- Implement data retention policy (recommend 90 days)
- Consider row-level security (RLS) in Supabase
- Enable encryption at rest for sensitive data

### Recommended Retention
- **Leads (PII):** 90 days, then delete or anonymize
- **Batches:** 2 years
- **Vendors:** Indefinite
- **Fraud blacklist:** Indefinite
- **API logs:** 30 days

---

## ROI & Cost Analysis

### API Costs for 1,000 Leads
- Twilio Lookup: $5.00
- ZeroBounce: $7.50
- IPQualityScore: $2.80
- **Total: $15.30**

### Example ROI
```
Scenario: 1,000 leads @ $5 each = $5,000 total cost

Fraud Detection:
- 30% fraudulent (300 leads)
- Fraud value: 300 × $5 = $1,500

Validation Cost: $15.30
Refund Secured: $1,500
Net Savings: $1,484.70
ROI: 9,700%
```

---

## Auto-Refund Triggers

Critical fraud patterns that automatically justify full refund:

1. **Sequential Phone Numbers** - 10%+ of batch
2. **Disposable Email Majority** - 40%+ of batch
3. **Foreign IP Batch** - 80%+ IPs from foreign country (for US offers)
4. **VOIP Flood** - 25%+ VOIP/burner numbers
5. **Disconnected Phone Majority** - 50%+ disconnected numbers
6. **Bot Timestamp Clustering** - 50+ leads at exact same second

---

## Vendor Status Auto-Updates

Based on average fraud rate:
- **Active:** < 20%
- **Warning:** 20-29.99%
- **Suspended:** 30-39.99%
- **Blacklisted:** ≥ 40%

Status updates automatically when new batches are processed.

---

## Documentation Files

### Core Documentation
- **README.md** (this file) - Quick start and overview
- **ENHANCED_README.md** - Complete system documentation (48KB)
- **ENHANCED_AGENT_PROMPT.md** - AI agent instructions (40KB)

### Implementation Guides
- **IMPLEMENTATION_GUIDE.md** - Step-by-step setup (35KB)
- **SUPABASE_SETUP_GUIDE.md** - Database setup (14KB)
- **CREDENTIALS_SUMMARY.md** - Credentials status (15KB)

### Reference
- **WHATS_NEW.md** - Enhancement overview (11KB)
- **fraud_rules_config.json** - Machine-readable rules (13KB)

---

## Configuration Files

### fraud_rules_config.json
Contains all fraud scoring rules:
- Refund threshold definitions
- Fraud indicator points
- API service configurations
- Disposable email domain list (40+)
- Auto-refund trigger thresholds
- Industry benchmarks
- Processing settings

---

## Testing

### Test Configuration
```bash
python test_env.py
```

### Test with Sample Data
```bash
python fraud_scorer_sample.py sample_leads.csv 5.00
```

### Test Database Connection
```bash
python supabase_client.py
```

---

## Troubleshooting

### Database Connection Issues
1. Verify `.env` has correct credentials
2. Run `python test_env.py` to check configuration
3. Ensure `supabase_schema.sql` has been run in Supabase
4. Check Supabase dashboard for active project

### API Errors
1. Verify API keys in `.env`
2. Check API account has sufficient credits
3. Verify network connectivity
4. Check API service status pages

### Import Errors
```bash
pip install --upgrade pandas openpyxl phonenumbers fuzzywuzzy python-Levenshtein supabase python-dotenv
```

---

## Support & Resources

### Supabase
- **Dashboard:** https://fifybuzwfaegloijrmqb.supabase.co
- **Documentation:** https://supabase.com/docs

### GitHub
- **Repository:** https://github.com/alanredmond23-bit/LEAD_VALIDATION
- **Issues:** https://github.com/alanredmond23-bit/LEAD_VALIDATION/issues

### API Services
- **Twilio:** https://www.twilio.com/console
- **ZeroBounce:** https://www.zerobounce.net
- **IPQualityScore:** https://www.ipqualityscore.com

---

## Version History

### v2.0 Enhanced (Current)
- Complete refund-focused redesign
- 25% refund threshold implementation
- 100-point fraud scoring system
- Supabase database integration
- Vendor history tracking
- Auto-status updates
- 80+ fraud indicators
- API validation integration
- Professional evidence packages

### v1.0 (Legacy)
- Basic lead validation
- Manual quality assessment
- Vague fraud indicators
- No database integration

---

## License

This is proprietary software for internal use.

---

## Quick Reference

### Most Common Commands
```bash
# Test configuration
python test_env.py

# Basic fraud analysis
python fraud_scorer_sample.py leads.csv 5.00

# Full analysis with database
python fraud_scorer_with_db.py leads.csv --vendor "VendorName" --cost 5.00

# Vendor history
python vendor_history_analyzer.py --vendor "VendorName"

# System summary
python vendor_history_analyzer.py --summary
```

### Key Files
- `.env` - Your credentials (not committed)
- `fraud_rules_config.json` - Scoring rules
- `supabase_schema.sql` - Database schema
- `sample_leads.csv` - Test data

---

**System Version:** 2.0 Enhanced - Refund-Focused Fraud Detection
**Last Updated:** 2024-01-12
**Status:** Production Ready ✅
