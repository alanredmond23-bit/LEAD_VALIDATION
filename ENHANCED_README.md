# Anthony Lead Forensics - Enhanced Refund-Focused Validation System

## Mission Statement
**Detect fraudulent leads and secure refunds through quantifiable, evidence-based fraud scoring.**

### Core Principle
```
IF Fraud Score ≥ 25% → FULL BATCH REFUND
IF Fraud Score 15-24% → PARTIAL REFUND (pro-rata)
IF Fraud Score < 15% → NO REFUND (acceptable loss rate)
```

---

## Table of Contents
1. [Overview](#overview)
2. [Fraud Scoring System](#fraud-scoring-system)
3. [Fraud Indicators by Category](#fraud-indicators-by-category)
4. [Validation Tools & APIs](#validation-tools--apis)
5. [Fraud Detection Workflow](#fraud-detection-workflow)
6. [Refund Calculation Examples](#refund-calculation-examples)
7. [Evidence Package Requirements](#evidence-package-requirements)
8. [Implementation Roadmap](#implementation-roadmap)

---

## Overview

The Anthony Lead Forensics system is designed to validate vendor lead files (pet/dental "free scan/review" offers) and generate **quantifiable fraud scores** that justify refunds. This system focuses on **automated detection, statistical analysis, and irrefutable API-based evidence**.

### Key Directories
- `/Users/alanredmond/Desktop/anthony` - Input lead files
- `/Users/alanredmond/Desktop/anthony audit` - Output audit reports and evidence packages

### System Goals
1. **Quantify fraud** - Every lead gets a numerical fraud score (0-100%)
2. **Automate detection** - API-based validation removes subjectivity
3. **Justify refunds** - Clear threshold rules with evidence
4. **Generate proof** - Comprehensive evidence packages for disputes

---

## Fraud Scoring System

### Scoring Breakdown (100 Points Maximum)

| Category | Max Points | Weight | Purpose |
|----------|-----------|--------|---------|
| **Contact Validation** | 40 | 40% | Detect fake/invalid phone & email |
| **Duplicate Detection** | 25 | 25% | Identify recycled/copied leads |
| **Geographic Fraud** | 15 | 15% | Catch VPN/proxy/mismatched location |
| **Timing Patterns** | 10 | 10% | Detect bot submissions & velocity fraud |
| **Data Quality** | 10 | 10% | Flag gibberish/incomplete data |

### Lead-Level Fraud Classification
```
0-24 points (0-24%) = VALID LEAD
25-49 points (25-49%) = SUSPICIOUS LEAD
50-100 points (50-100%) = FRAUDULENT LEAD
```

### Batch-Level Refund Thresholds
```
Fraudulent Leads ≥ 25% of batch → FULL REFUND (100%)
Fraudulent Leads 15-24% of batch → PARTIAL REFUND (pro-rata)
Fraudulent Leads < 15% of batch → NO REFUND (acceptable tolerance)
```

---

## Fraud Indicators by Category

### 1. CONTACT VALIDATION FRAUD (40 Points Max)

#### Phone Number Fraud
| Indicator | Points | Detection Method | Tool |
|-----------|--------|------------------|------|
| Invalid format | 10 | Regex + parsing | phonenumbers library |
| Disconnected/non-working | 10 | Carrier lookup | Twilio Lookup API |
| VOIP/burner number | 8 | Line type detection | Twilio Lookup API |
| Repeated across leads | 10 | Database cross-reference | Custom SQL query |
| Invalid area code | 5 | Area code validation | phonenumbers library |
| Sequential numbers | 10 | Pattern detection | Custom algorithm |

**Automatic Fraud Flag:** If 3+ indicators present = 100% fraud

#### Email Fraud
| Indicator | Points | Detection Method | Tool |
|-----------|--------|------------------|------|
| Invalid format | 10 | Syntax validation | Regex + email-validator |
| Disposable email | 10 | Domain blacklist | ZeroBounce, Abstract API |
| Non-existent domain | 10 | MX record lookup | dnspython, ZeroBounce |
| Catch-all/role account | 5 | SMTP verification | ZeroBounce |
| Repeated across leads | 10 | Database cross-reference | Custom SQL query |
| Pattern matching | 8 | Regex detection | Custom patterns |
| Typo domains | 7 | Domain similarity | FuzzyWuzzy |

**Disposable Email Domains:** guerrillamail.com, temp-mail.org, 10minutemail.com, mailinator.com, etc.

### 2. DUPLICATE & PATTERN FRAUD (25 Points Max)

| Indicator | Points | Detection Method | Tool |
|-----------|--------|------------------|------|
| Exact duplicate | 15 | Hash comparison | MD5/SHA256 |
| Near duplicate | 10 | Fuzzy matching (85%+ similar) | FuzzyWuzzy |
| Duplicate phone | 12 | Phone normalization + search | phonenumbers + SQL |
| Duplicate email | 12 | Case-insensitive search | SQL LOWER() |
| Duplicate IP | 8 | IP address grouping | Pandas groupby |
| Sequential submissions | 10 | Time delta analysis | Pandas datetime |

**Near Duplicate Examples:**
- "John Smith" / "Jon Smith" / "J. Smith"
- john.smith@gmail.com / johnsmith@gmail.com
- (555) 123-4567 / 5551234567 / +1-555-123-4567

### 3. GEOGRAPHIC FRAUD (15 Points Max)

| Indicator | Points | Detection Method | Tool |
|-----------|--------|------------------|------|
| Area code mismatch | 8 | Phone area code ≠ address state | Custom validation |
| Impossible geography | 10 | IP location ≠ phone ≠ address | GeoIP2 + area codes |
| Foreign IP address | 12 | IP country detection | IPQualityScore |
| VPN/Proxy detection | 10 | Proxy database check | IPQualityScore |
| High-risk zip code | 5 | Fraud zip blacklist | Custom database |

**Example Geographic Fraud:**
```
Lead Data:
- Address: Los Angeles, CA 90210
- Phone: (212) 555-1234 (NY area code)
- IP Address: 123.45.67.89 (Russia)
- Detection: Foreign IP (12) + Area code mismatch (8) = 20 points
```

### 4. TIMING & VELOCITY FRAUD (10 Points Max)

| Indicator | Points | Detection Method | Tool |
|-----------|--------|------------------|------|
| Overnight spike | 8 | 20+ leads between 2-6 AM | Pandas time analysis |
| Weekend flood | 6 | 50%+ leads on Sat/Sun | Pandas datetime |
| Unnatural velocity | 10 | 100+ leads in 1 hour | Time-based aggregation |
| Same timestamp | 10 | Multiple leads same second | Duplicate timestamp check |
| Bot pattern | 10 | Submissions every X seconds | Statistical analysis |

**Bot Detection Example:**
```
Normal Pattern: Random intervals (12s, 45s, 2m, 5s, 1m)
Bot Pattern: Regular intervals (30s, 30s, 30s, 30s, 30s)
Detection: Standard deviation < 5 seconds = Bot
```

### 5. DATA QUALITY FRAUD (10 Points Max)

| Indicator | Points | Detection Method | Tool |
|-----------|--------|------------------|------|
| Missing critical fields | 10 | NULL/empty check | Pandas isnull() |
| Gibberish names | 10 | Pattern matching | Regex + custom rules |
| Invalid names | 8 | Single letter, numbers | Nameparser |
| Copy-paste pattern | 10 | Identical formatting | String comparison |
| Minimum effort | 7 | All single-word entries | Word count |
| Keyword stuffing | 8 | Marketing terms in name | Keyword blacklist |

**Gibberish Detection Examples:**
- "asdfgh", "qwerty", "test test", "xxx yyy"
- "123", "aaa", "zzz", "nnn"
- "Free Scan", "Click Here", "Submit"

---

## Validation Tools & APIs

### Tier 1: Essential APIs (Must Have)

#### 1. Twilio Lookup API
**Purpose:** Phone validation, carrier detection, line type
**Cost:** $0.005 per lookup (~$5 per 1,000 leads)
**Returns:**
- Phone number validity
- Carrier name
- Line type (mobile, landline, VOIP)
- Country code validation

**Implementation:**
```python
from twilio.rest import Client
client = Client(account_sid, auth_token)

phone_info = client.lookups.v1.phone_numbers(phone_number).fetch(type=['carrier'])
is_voip = phone_info.carrier['type'] == 'voip'
```

#### 2. ZeroBounce Email Validation
**Purpose:** Email validation, disposable detection, deliverability
**Cost:** $15 per 2,000 credits (~$7.50 per 1,000 leads)
**Returns:**
- Email validity status
- Disposable email detection
- Spam trap detection
- MX record validation
- Did you mean suggestions

**Implementation:**
```python
import zerobounce
zerobounce.initialize(api_key)

response = zerobounce.validate(email_address)
is_valid = response.status == "valid"
is_disposable = response.sub_status == "disposable"
```

#### 3. IPQualityScore
**Purpose:** IP fraud detection, VPN/proxy detection, geolocation
**Cost:** $13.99/month for 5,000 lookups
**Returns:**
- Fraud score (0-100)
- VPN/Proxy detection
- Geographic location
- ISP information
- Recent abuse detection

**Implementation:**
```python
import requests

url = f"https://ipqualityscore.com/api/json/ip/{api_key}/{ip_address}"
response = requests.get(url).json()
is_vpn = response['vpn']
fraud_score = response['fraud_score']
```

### Tier 2: Supporting Libraries (Free)

| Library | Purpose | Installation |
|---------|---------|--------------|
| **phonenumbers** | Phone parsing/validation | `pip install phonenumbers` |
| **email-validator** | Email syntax validation | `pip install email-validator` |
| **FuzzyWuzzy** | Fuzzy string matching | `pip install fuzzywuzzy python-Levenshtein` |
| **Pandas** | Data manipulation | `pip install pandas` |
| **dnspython** | DNS/MX record lookup | `pip install dnspython` |
| **Nameparser** | Name parsing/validation | `pip install nameparser` |

### Tier 3: Optional Enhancements

- **MaxMind GeoIP2** - Advanced geolocation ($12/month)
- **Hunter.io** - Email verification ($49/month for 5,000)
- **Whitepages Pro** - Phone intelligence ($50/month)
- **NumVerify** - International phone validation ($14.99/month)

---

## Fraud Detection Workflow

### Phase 1: Import & Format Validation (Instant)

```
INPUT: vendor_leads.csv
↓
1. Load CSV/Excel file (Pandas)
2. Normalize data (strip spaces, lowercase emails, format phones)
3. Format validation (regex checks)
   - Phone: Must be 10 digits
   - Email: Must match email regex
   - Name: Min 2 characters, no numbers
4. Flag format failures (10 points each)
↓
OUTPUT: Normalized DataFrame + Format Fraud Scores
```

### Phase 2: API Validation (2-3 seconds per lead)

```
For each lead:
├─ Phone Validation (Twilio Lookup API)
│  ├─ Check if working number
│  ├─ Detect VOIP/burner
│  └─ Validate area code
├─ Email Validation (ZeroBounce API)
│  ├─ Check deliverability
│  ├─ Detect disposable domains
│  └─ Verify MX records
└─ IP Validation (IPQualityScore API)
   ├─ Detect VPN/Proxy
   ├─ Get geolocation
   └─ Check fraud score
↓
OUTPUT: API validation results + Contact Fraud Scores
```

**Optimization:** Batch API calls (100 leads at a time) to reduce processing time

### Phase 3: Pattern Analysis (Batch Processing)

```
Analyze entire batch:
├─ Duplicate Detection
│  ├─ Exact match detection (hash comparison)
│  ├─ Fuzzy matching (FuzzyWuzzy 85%+ threshold)
│  └─ Cross-field duplicates (same phone, different name)
├─ Geographic Validation
│  ├─ Area code vs state matching
│  ├─ IP location vs address consistency
│  └─ Timezone analysis
├─ Timing Analysis
│  ├─ Submission velocity (leads per hour)
│  ├─ Time distribution (overnight spikes)
│  └─ Bot pattern detection (regular intervals)
└─ Statistical Anomaly Detection
   ├─ Z-score analysis
   ├─ Standard deviation outliers
   └─ Clustering algorithms (DBSCAN)
↓
OUTPUT: Pattern analysis + Full Fraud Scores
```

### Phase 4: Scoring & Refund Calculation

```
Calculate scores:
├─ Lead-level fraud score (0-100 per lead)
├─ Batch fraud percentage (fraudulent leads / total leads)
├─ Apply refund threshold rules
└─ Generate refund justification
↓
If fraud_percentage >= 25%:
   REFUND = 100% (FULL REFUND)
Elif fraud_percentage >= 15%:
   REFUND = fraud_percentage (PARTIAL REFUND)
Else:
   REFUND = 0% (NO REFUND)
↓
OUTPUT: Refund calculation + Justification
```

### Phase 5: Evidence Generation

```
Generate evidence package:
├─ Excel Analysis
│  ├─ Lead-by-lead breakdown (fraud scores, reasons)
│  ├─ Summary statistics
│  └─ Color-coded flags (red=fraud, yellow=suspicious, green=valid)
├─ PDF Report
│  ├─ Executive summary
│  ├─ Refund justification
│  ├─ Key findings
│  └─ Visualizations
├─ Charts & Graphs
│  ├─ Fraud distribution pie chart
│  ├─ Timeline velocity chart
│  ├─ Geographic heatmap
│  └─ Duplicate network diagram
└─ API Evidence
   ├─ Raw API responses (JSON exports)
   ├─ Validation timestamps
   └─ Carrier/provider information
↓
OUTPUT: Complete evidence package ready for dispute
```

---

## Refund Calculation Examples

### Example 1: Full Refund Scenario

```
VENDOR: PetLeads Pro
BATCH: 200 leads @ $5 per lead
TOTAL COST: $1,000

ANALYSIS RESULTS:
- Total Leads: 200
- Fraudulent Leads: 65
- Fraud Percentage: 32.5%

FRAUD BREAKDOWN:
- Invalid contacts: 28 leads (14%)
- Duplicates: 18 leads (9%)
- VOIP numbers: 12 leads (6%)
- VPN/Foreign IP: 7 leads (3.5%)

REFUND CALCULATION:
Fraud Score: 32.5% ≥ 25% threshold
RESULT: FULL REFUND
REFUND AMOUNT: $1,000 (100%)

JUSTIFICATION:
"Batch fraud rate of 32.5% exceeds acceptable threshold of 25%.
65 of 200 leads flagged as fraudulent through API validation.
Full refund justified per fraud detection policy."
```

### Example 2: Partial Refund Scenario

```
VENDOR: DentalScans LLC
BATCH: 500 leads @ $5 per lead
TOTAL COST: $2,500

ANALYSIS RESULTS:
- Total Leads: 500
- Fraudulent Leads: 95
- Fraud Percentage: 19%

FRAUD BREAKDOWN:
- Disconnected phones: 42 leads (8.4%)
- Disposable emails: 31 leads (6.2%)
- Duplicates: 22 leads (4.4%)

REFUND CALCULATION:
Fraud Score: 19% (falls in 15-24% range)
RESULT: PARTIAL REFUND (pro-rata)
REFUND AMOUNT: $2,500 × 19% = $475

JUSTIFICATION:
"Batch fraud rate of 19% exceeds acceptable tolerance but below
full refund threshold. Partial refund of 19% ($475) justified
for 95 fraudulent leads."
```

### Example 3: No Refund Scenario

```
VENDOR: QualityLeads Inc
BATCH: 1,000 leads @ $5 per lead
TOTAL COST: $5,000

ANALYSIS RESULTS:
- Total Leads: 1,000
- Fraudulent Leads: 120
- Fraud Percentage: 12%

FRAUD BREAKDOWN:
- Invalid emails: 45 leads (4.5%)
- Format issues: 38 leads (3.8%)
- Minor duplicates: 37 leads (3.7%)

REFUND CALCULATION:
Fraud Score: 12% < 15% threshold
RESULT: NO REFUND
REFUND AMOUNT: $0

JUSTIFICATION:
"Batch fraud rate of 12% falls within acceptable industry tolerance
(<15%). No refund warranted. Quality meets acceptable standards."
```

---

## Evidence Package Requirements

### 1. Executive Summary (1 page)

**Must Include:**
- Batch identifier and vendor name
- Analysis date and analyst
- Total leads analyzed
- **Fraud score percentage (highlighted)**
- **Refund amount and justification (highlighted)**
- Top 3 fraud patterns identified
- Comparison to industry benchmark (8-12% typical)
- Financial impact statement

**Template:**
```
FRAUD ANALYSIS EXECUTIVE SUMMARY
================================
Batch ID: [BATCH-12345]
Vendor: [Vendor Name]
Analysis Date: [Date]
Analyzed By: Anthony Lead Forensics

FINDINGS:
Total Leads: [X]
Fraudulent Leads: [Y]
Fraud Percentage: [Z%]

REFUND DETERMINATION:
Threshold Rule: ≥25% = Full Refund | 15-24% = Partial | <15% = None
Batch Fraud Score: [Z%]
REFUND STATUS: [FULL/PARTIAL/NONE]
REFUND AMOUNT: $[Amount]

KEY FRAUD PATTERNS:
1. [Pattern 1 with percentage]
2. [Pattern 2 with percentage]
3. [Pattern 3 with percentage]

INDUSTRY COMPARISON:
Industry standard fraud rate: 8-12%
This batch fraud rate: [Z%]
Deviation: [X]% above/below standard

FINANCIAL IMPACT:
Batch Cost: $[Total]
Fraudulent Lead Cost: $[Fraud Total]
Refund Justified: $[Refund Amount]
```

### 2. Detailed Fraud Analysis Spreadsheet (Excel)

**Sheet 1: Lead-by-Lead Breakdown**
| Column | Purpose |
|--------|---------|
| Lead ID | Unique identifier |
| Name | Lead name |
| Phone | Phone number |
| Email | Email address |
| Address | Full address |
| IP Address | Submission IP |
| Timestamp | Submission time |
| **Fraud Score** | 0-100 percentage |
| **Is Fraudulent** | TRUE/FALSE (≥50 points) |
| **Fraud Reasons** | Comma-separated list |
| Contact Score | Points from contact validation |
| Duplicate Score | Points from duplicate detection |
| Geographic Score | Points from geographic fraud |
| Timing Score | Points from timing analysis |
| Quality Score | Points from data quality |
| Phone Valid | API validation result |
| Phone Type | Mobile/Landline/VOIP |
| Email Valid | API validation result |
| Email Disposable | TRUE/FALSE |
| IP Fraud Score | IPQualityScore result |
| VPN Detected | TRUE/FALSE |

**Conditional Formatting:**
- Red fill: Fraud score ≥ 50%
- Yellow fill: Fraud score 25-49%
- Green fill: Fraud score < 25%

**Sheet 2: Summary Statistics**
- Total leads analyzed
- Fraudulent leads count/percentage
- Valid leads count/percentage
- Suspicious leads count/percentage
- Average fraud score
- Median fraud score
- Standard deviation
- Fraud by category breakdown
- Top 10 fraud indicators

**Sheet 3: Duplicates List**
- Groups of duplicate/near-duplicate leads
- Similarity score
- Matching fields
- Recommendation (keep which one)

**Sheet 4: API Validation Log**
- Timestamp of each API call
- API service used
- Request/response
- Validation result
- Processing time

### 3. Visual Evidence (Charts/Graphs)

#### Chart 1: Fraud Distribution Pie Chart
- Slices for each fraud category
- Percentages and lead counts
- Color-coded: Red (contact), Orange (duplicate), Yellow (geographic), Blue (timing), Green (quality)

#### Chart 2: Submission Timeline
- X-axis: Time (hourly buckets)
- Y-axis: Number of submissions
- Highlight bot spikes and overnight anomalies
- Show normal distribution curve for comparison

#### Chart 3: Geographic Heatmap
- Map showing IP locations
- Color intensity based on lead concentration
- Markers for VPN/Proxy detections
- Comparison overlay with claimed addresses

#### Chart 4: Fraud Score Distribution
- Histogram of fraud scores
- X-axis: Fraud score ranges (0-24%, 25-49%, 50-100%)
- Y-axis: Number of leads
- Highlight the 25% and 50% thresholds

#### Chart 5: Duplicate Network Diagram
- Nodes representing leads
- Edges showing duplicate connections
- Node size based on number of duplicates
- Color-coded by duplicate type

### 4. PDF Audit Report (5-10 pages)

**Page 1:** Executive Summary (from above)
**Page 2:** Methodology & Validation Tools Used
**Page 3-4:** Detailed Findings by Category
**Page 5-6:** Visual Evidence (embedded charts)
**Page 7:** Refund Calculation & Justification
**Page 8:** Recommendations & Next Steps
**Page 9-10:** Appendices (API documentation, raw data samples)

### 5. Raw API Evidence (JSON/CSV exports)

**Must Include:**
- All Twilio Lookup API responses
- All ZeroBounce validation responses
- All IPQualityScore results
- Timestamps proving when validation occurred
- API request/response logs
- Error logs (if any API calls failed)

**Format:**
```json
{
  "lead_id": "12345",
  "validation_timestamp": "2024-01-15T14:30:00Z",
  "phone_validation": {
    "api": "Twilio Lookup",
    "number": "+15551234567",
    "valid": false,
    "carrier": null,
    "line_type": "voip",
    "error": "Invalid number"
  },
  "email_validation": {
    "api": "ZeroBounce",
    "email": "test@guerrillamail.com",
    "status": "invalid",
    "sub_status": "disposable",
    "did_you_mean": null
  },
  "ip_validation": {
    "api": "IPQualityScore",
    "ip": "123.45.67.89",
    "fraud_score": 85,
    "country": "RU",
    "vpn": true,
    "proxy": true
  }
}
```

### 6. Refund Justification Document (1-2 pages)

**Structured Format:**
```
REFUND JUSTIFICATION REPORT
============================
Batch Information:
- Batch ID: [ID]
- Vendor: [Name]
- Purchase Date: [Date]
- Analysis Date: [Date]
- Number of Leads: [X]
- Cost Per Lead: $[X]
- Total Batch Cost: $[Total]

Fraud Analysis Summary:
- Fraudulent Leads Identified: [X] ([Y%])
- Valid Leads: [X] ([Y%])
- Suspicious Leads: [X] ([Y%])

Refund Threshold Policy:
≥ 25% fraud rate = 100% full refund
15-24% fraud rate = Pro-rata partial refund
< 15% fraud rate = No refund (acceptable tolerance)

Batch Fraud Score: [Z%]

REFUND DETERMINATION:
Status: [FULL REFUND / PARTIAL REFUND / NO REFUND]
Refund Percentage: [X%]
Refund Amount: $[Amount]

Detailed Fraud Breakdown:
1. Invalid Contact Information: [X] leads ([Y%])
   - Disconnected phones: [X]
   - VOIP/burner numbers: [X]
   - Disposable emails: [X]
   - Invalid formats: [X]

2. Duplicate & Recycled Leads: [X] leads ([Y%])
   - Exact duplicates: [X]
   - Near duplicates: [X]
   - Repeated contacts: [X]

3. Geographic Fraud: [X] leads ([Y%])
   - VPN/Proxy usage: [X]
   - Foreign IPs: [X]
   - Area code mismatches: [X]

4. Bot & Timing Fraud: [X] leads ([Y%])
   - Bot patterns detected: [X]
   - Velocity anomalies: [X]
   - Overnight spikes: [X]

5. Data Quality Issues: [X] leads ([Y%])
   - Gibberish data: [X]
   - Incomplete records: [X]
   - Fake names: [X]

Evidence Summary:
- API validations performed: [X]
- Validation tools used: Twilio Lookup, ZeroBounce, IPQualityScore
- Statistical analyses completed: [X]
- Pattern detection algorithms applied: [X]

Industry Comparison:
- Industry standard fraud rate: 8-12%
- This batch fraud rate: [Z%]
- Deviation from standard: [X]% above standard

Conclusion:
Based on comprehensive fraud analysis using industry-standard
validation APIs and statistical methods, this batch contains
[Z%] fraudulent leads, which [exceeds/falls within/below] the
acceptable threshold. A [full/partial/no] refund of $[Amount]
is justified per the refund threshold policy.

Supporting Documentation:
- Detailed Excel analysis: fraud_analysis_[batch_id].xlsx
- Visual evidence: charts_[batch_id].pdf
- API validation logs: api_evidence_[batch_id].json
- Audit report: audit_report_[batch_id].pdf

Prepared by: Anthony Lead Forensics
Date: [Date]
Contact: [Contact Information]
```

---

## Implementation Roadmap

### Phase 1: Quick Win Setup (Week 1)
**Goal:** Manual fraud detection with basic tools

**Tasks:**
1. ✅ Sign up for APIs:
   - Twilio Lookup (free trial available)
   - ZeroBounce (200 free credits)
   - IPQualityScore (500 free lookups)

2. ✅ Install Python libraries:
   ```bash
   pip install pandas openpyxl phonenumbers email-validator fuzzywuzzy python-Levenshtein twilio zerobounce dnspython
   ```

3. ✅ Create basic validation script:
   - Load CSV file
   - Validate phone formats
   - Validate email formats
   - Check for exact duplicates
   - Export to Excel with fraud flags

4. ✅ Create Excel template:
   - Lead data columns
   - Fraud score column
   - Fraud reasons column
   - Conditional formatting
   - Summary statistics sheet

**Deliverable:** Can manually process batches with 40% fraud detection accuracy

### Phase 2: API Integration (Week 2-3)
**Goal:** Automated API-based validation

**Tasks:**
1. ✅ Integrate Twilio Lookup API:
   - Phone validation function
   - VOIP detection
   - Batch processing
   - Error handling

2. ✅ Integrate ZeroBounce API:
   - Email validation function
   - Disposable detection
   - Batch processing
   - Rate limiting

3. ✅ Integrate IPQualityScore API:
   - IP validation function
   - VPN/Proxy detection
   - Geolocation
   - Fraud scoring

4. ✅ Build duplicate detection:
   - Fuzzy matching implementation
   - Hash-based exact matching
   - Cross-field duplicate detection

5. ✅ Create automated pipeline:
   - Input: CSV file
   - Process: All validations
   - Output: Scored Excel + summary

**Deliverable:** Automated fraud detection at 75% accuracy with API evidence

### Phase 3: Advanced Analytics (Week 4-5)
**Goal:** Statistical pattern detection and fraud scoring

**Tasks:**
1. ✅ Implement timing analysis:
   - Velocity detection
   - Bot pattern identification
   - Statistical anomaly detection
   - Overnight/weekend spike detection

2. ✅ Build geographic validation:
   - Area code vs state matching
   - IP vs claimed location
   - Impossible geography detection

3. ✅ Create fraud scoring system:
   - Point allocation by category
   - Weighted scoring algorithm
   - Threshold classification
   - Batch-level aggregation

4. ✅ Develop refund calculator:
   - Apply 25% threshold rule
   - Calculate partial refunds
   - Generate justification text

**Deliverable:** Complete fraud scoring with refund calculations

### Phase 4: Reporting & Evidence (Week 6)
**Goal:** Professional evidence packages for disputes

**Tasks:**
1. ✅ Build Excel report generator:
   - Lead-by-lead breakdown
   - Summary statistics
   - Duplicate lists
   - API validation log
   - Conditional formatting

2. ✅ Create visualization tools:
   - Fraud distribution charts (matplotlib/plotly)
   - Timeline velocity graphs
   - Geographic heatmaps
   - Score distribution histograms

3. ✅ Build PDF report generator:
   - Executive summary
   - Detailed findings
   - Embedded charts
   - Refund justification
   - ReportLab or WeasyPrint

4. ✅ Package evidence files:
   - Organize folder structure
   - Export API raw data
   - Create ZIP archive
   - Ready for Drive/Notion upload

**Deliverable:** Complete automated evidence package generation

### Phase 5: Database & History (Week 7-8)
**Goal:** Fraud history tracking and vendor profiles

**Tasks:**
1. ✅ Set up PostgreSQL database:
   - Leads table
   - Fraud scores table
   - Vendors table
   - Batches table
   - API validation cache

2. ✅ Build historical analysis:
   - Vendor fraud trends
   - Known fraud patterns
   - Blacklist management
   - Repeat offender tracking

3. ✅ Create dashboard (optional):
   - Jupyter notebook dashboard
   - Real-time fraud monitoring
   - Vendor scorecard
   - Trend analysis

**Deliverable:** Long-term fraud tracking and vendor intelligence

### Phase 6: Production Deployment (Week 9)
**Goal:** Production-ready automated system

**Tasks:**
1. ✅ Dockerize application:
   - Create Dockerfile
   - Docker Compose for dependencies
   - Environment configuration

2. ✅ Add error handling:
   - API failure recovery
   - Retry logic with exponential backoff
   - Logging and monitoring
   - Email alerts

3. ✅ Create documentation:
   - User guide
   - API setup instructions
   - Troubleshooting guide
   - Example workflows

4. ✅ Testing & validation:
   - Unit tests for fraud detection
   - Integration tests for APIs
   - Test with historical batches
   - Accuracy validation

**Deliverable:** Production-ready system with documentation

---

## Quick Reference: Fraud = Refund Matrix

| Fraud Type | Severity | Auto-Refund Trigger | Evidence Required |
|------------|----------|---------------------|-------------------|
| **Disconnected Phones** | HIGH | 30%+ of batch | Twilio API proof |
| **VOIP/Burner Numbers** | HIGH | 25%+ of batch | Twilio carrier data |
| **Disposable Emails** | HIGH | 30%+ of batch | ZeroBounce results |
| **Exact Duplicates** | CRITICAL | 20%+ of batch | Hash comparison log |
| **VPN/Proxy IPs** | HIGH | 25%+ of batch | IPQualityScore data |
| **Bot Patterns** | CRITICAL | 15%+ of batch | Timing analysis charts |
| **Foreign IPs** | MEDIUM | 35%+ of batch | GeoIP results |
| **Gibberish Data** | MEDIUM | 40%+ of batch | Pattern analysis |
| **Sequential Numbers** | CRITICAL | 10%+ of batch | Pattern detection |
| **Recycled Lists** | CRITICAL | ANY detected | Historical comparison |

**Master Rule:**
```
IF (ANY critical indicator ≥ threshold)
   OR (Combined fraud score ≥ 25%)
   OR (Multiple high-severity indicators)
   → FULL BATCH REFUND JUSTIFIED
```

---

## Support & Maintenance

### Regular Updates
- Monthly update of disposable email domain list
- Quarterly review of fraud score thresholds
- Annual audit of API costs vs accuracy

### Data Retention
- Keep all evidence packages for 2 years
- Archive API validation results
- Maintain vendor fraud history
- Document all refund disputes and outcomes

### Compliance
- GDPR compliance for lead data handling
- Data encryption for sensitive information
- Secure API key management
- Audit trail for all processing steps

---

## Success Metrics

### System Performance
- **Fraud Detection Accuracy:** Target 90%+
- **False Positive Rate:** Target <5%
- **Processing Time:** <5 seconds per lead (including API calls)
- **API Uptime:** Monitor and track (target 99%+)

### Business Impact
- **Refund Success Rate:** Track dispute outcomes
- **Cost Savings:** Document refunds secured
- **Vendor Quality:** Monitor vendor fraud trends
- **ROI:** API costs vs refunds secured

---

## Appendix

### Fraud Score Calculation Formula

```python
def calculate_lead_fraud_score(lead, batch_data):
    """
    Calculate comprehensive fraud score for a single lead.
    Returns score (0-100) and detailed reasons.
    """
    score = 0
    reasons = []

    # CONTACT VALIDATION (40 points max)
    contact_score = 0
    if not valid_phone_format(lead['phone']):
        contact_score += 10
        reasons.append("Invalid phone format")
    if is_disconnected_phone(lead['phone']):  # Twilio
        contact_score += 10
        reasons.append("Disconnected phone number")
    if is_voip_number(lead['phone']):  # Twilio
        contact_score += 8
        reasons.append("VOIP/burner number detected")
    if count_phone_duplicates(lead['phone'], batch_data) >= 3:
        contact_score += 10
        reasons.append("Phone number repeated 3+ times")

    if not valid_email_format(lead['email']):
        contact_score += 10
        reasons.append("Invalid email format")
    if is_disposable_email(lead['email']):  # ZeroBounce
        contact_score += 10
        reasons.append("Disposable email domain")
    if not email_domain_exists(lead['email']):
        contact_score += 10
        reasons.append("Non-existent email domain")

    score += min(contact_score, 40)  # Cap at 40

    # DUPLICATE DETECTION (25 points max)
    duplicate_score = 0
    exact_dup = find_exact_duplicate(lead, batch_data)
    if exact_dup:
        duplicate_score += 15
        reasons.append(f"Exact duplicate of lead {exact_dup['id']}")
    else:
        fuzzy_dup = find_fuzzy_duplicate(lead, batch_data, threshold=85)
        if fuzzy_dup:
            duplicate_score += 10
            reasons.append(f"Near duplicate of lead {fuzzy_dup['id']}")

    score += min(duplicate_score, 25)  # Cap at 25

    # GEOGRAPHIC VALIDATION (15 points max)
    geo_score = 0
    if not area_code_matches_state(lead['phone'], lead['state']):
        geo_score += 8
        reasons.append("Area code doesn't match state")

    ip_info = validate_ip(lead['ip'])  # IPQualityScore
    if ip_info['vpn']:
        geo_score += 10
        reasons.append("VPN/Proxy detected")
    if ip_info['country'] != 'US':
        geo_score += 12
        reasons.append(f"Foreign IP ({ip_info['country']})")

    score += min(geo_score, 15)  # Cap at 15

    # TIMING ANALYSIS (10 points max)
    timing_score = 0
    if is_bot_pattern(lead['timestamp'], batch_data):
        timing_score += 10
        reasons.append("Bot submission pattern detected")

    score += min(timing_score, 10)  # Cap at 10

    # DATA QUALITY (10 points max)
    quality_score = 0
    if is_gibberish_name(lead['name']):
        quality_score += 10
        reasons.append("Gibberish/fake name detected")
    if has_missing_critical_fields(lead):
        quality_score += 10
        reasons.append("Missing critical fields")

    score += min(quality_score, 10)  # Cap at 10

    # Final classification
    is_fraudulent = score >= 50
    classification = (
        "FRAUDULENT" if score >= 50 else
        "SUSPICIOUS" if score >= 25 else
        "VALID"
    )

    return {
        'fraud_score': score,
        'is_fraudulent': is_fraudulent,
        'classification': classification,
        'reasons': reasons,
        'breakdown': {
            'contact': min(contact_score, 40),
            'duplicate': min(duplicate_score, 25),
            'geographic': min(geo_score, 15),
            'timing': min(timing_score, 10),
            'quality': min(quality_score, 10)
        }
    }

def calculate_batch_refund(leads_df):
    """
    Calculate refund amount for entire batch based on fraud threshold.
    """
    total_leads = len(leads_df)
    fraudulent_leads = len(leads_df[leads_df['is_fraudulent'] == True])
    fraud_percentage = (fraudulent_leads / total_leads) * 100

    if fraud_percentage >= 25:
        refund_type = "FULL REFUND"
        refund_percentage = 100
    elif fraud_percentage >= 15:
        refund_type = "PARTIAL REFUND"
        refund_percentage = fraud_percentage
    else:
        refund_type = "NO REFUND"
        refund_percentage = 0

    return {
        'refund_type': refund_type,
        'refund_percentage': refund_percentage,
        'fraud_percentage': fraud_percentage,
        'fraudulent_leads': fraudulent_leads,
        'valid_leads': total_leads - fraudulent_leads,
        'total_leads': total_leads
    }
```

### Disposable Email Domain List (Top 100)

```
guerrillamail.com, temp-mail.org, 10minutemail.com, mailinator.com,
throwaway.email, tempmail.com, getnada.com, maildrop.cc,
sharklasers.com, guerrillamail.info, grr.la, guerrillamail.biz,
guerrillamail.de, spam4.me, tempmailaddress.com, yopmail.com,
fakeinbox.com, emailondeck.com, throwawaymail.com, trashmail.com,
guerrillamail.net, dispostable.com, mintemail.com, mt2015.com,
getairmail.com, armyspy.com, cuvox.de, dayrep.com, einrot.com,
fleckens.hu, gustr.com, jourrapide.com, rhyta.com, superrito.com,
teleworm.us, spambog.com, spambog.de, spambog.ru, spaml.com,
tempr.email, mohmal.com, coccocmail.com, anonbox.net, anonymbox.com
```
*Full list: https://github.com/disposable/disposable-email-domains*

---

**Version:** 2.0 Enhanced
**Last Updated:** 2024-01
**Author:** Anthony Lead Forensics System
**Purpose:** Refund-focused fraud detection with quantifiable evidence
