# Supabase Database Setup Guide

## Overview

This guide will help you set up Supabase database integration for the Anthony Lead Forensics fraud detection system. With database integration, you can:

- **Store all fraud analysis results** permanently
- **Track vendor fraud history** over time
- **Build vendor fraud profiles** automatically
- **Query historical data** for trends and patterns
- **Generate vendor performance reports**
- **Maintain fraud blacklists** (emails, phones, IPs)
- **Track API costs** and ROI

---

## Your Supabase Instance (ALREADY CONFIGURED!)

✅ Your production Supabase instance is **already configured** in `.env`:

```
Project URL: https://fifybuzwfaegloijrmqb.supabase.co
Project ID: fifybuzwfaegloijrmqb
Status: Active and ready to use!
```

**Next step:** Run the database schema SQL to create all tables.

---

## Step 1: Install Dependencies

```bash
pip install supabase python-dotenv pandas openpyxl
```

---

## Step 2: Create Database Schema

### Option A: Using Supabase Dashboard (Recommended)

1. **Open Supabase SQL Editor:**
   - Go to: https://fifybuzwfaegloijrmqb.supabase.co
   - Login to your Supabase dashboard
   - Click on "SQL Editor" in the left sidebar

2. **Run Schema SQL:**
   - Open the file `supabase_schema.sql` in a text editor
   - Copy all the SQL code (entire file)
   - Paste into the Supabase SQL Editor
   - Click "Run" button

3. **Verify Tables Created:**
   - Click on "Table Editor" in left sidebar
   - You should see these tables:
     - `vendors`
     - `batches`
     - `leads`
     - `fraud_patterns`
     - `batch_fraud_patterns`
     - `batch_fraud_indicators`
     - `api_validation_log`
     - `disposable_email_domains`
     - `fraud_blacklist`

### Option B: Using psql Command Line

```bash
# Get your database connection string from Supabase dashboard
# Settings > Database > Connection string > URI

psql "postgresql://postgres:[YOUR-PASSWORD]@db.fifybuzwfaegloijrmqb.supabase.co:5432/postgres" \
  -f supabase_schema.sql
```

---

## Step 3: Test Database Connection

Run the Supabase client test:

```bash
python supabase_client.py
```

**Expected output:**
```
✓ Connected to Supabase successfully!

Database Statistics:
  vendors: 0 records
  batches: 0 records
  leads: 0 records
  ...

No vendors found. Database is empty.
```

If you see this, **your database is ready!**

---

## Step 4: Run Your First Analysis with Database Integration

### Basic Usage:

```bash
python fraud_scorer_with_db.py sample_leads.csv \
  --vendor "Test Vendor" \
  --cost 5.00
```

### With Custom Batch ID:

```bash
python fraud_scorer_with_db.py vendor_leads_jan.csv \
  --vendor "PetLeads Pro" \
  --cost 5.00 \
  --batch-id "JAN2024_001"
```

### Without Database Save (local only):

```bash
python fraud_scorer_with_db.py sample_leads.csv \
  --vendor "Test Vendor" \
  --cost 5.00 \
  --no-db
```

---

## Step 5: Query Vendor History

### List All Vendors:

```bash
python vendor_history_analyzer.py --list-vendors
```

### Analyze Specific Vendor:

```bash
python vendor_history_analyzer.py --vendor "PetLeads Pro"
```

### Show High Fraud Batches:

```bash
python vendor_history_analyzer.py --high-fraud
```

### Overall System Summary:

```bash
python vendor_history_analyzer.py --summary
```

### Export Vendor Report to Excel:

```bash
python vendor_history_analyzer.py --vendor "PetLeads Pro" --export
```

---

## Database Schema Overview

### Core Tables

#### **vendors**
Stores vendor information and aggregate stats.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| vendor_name | TEXT | Vendor name (unique) |
| vendor_status | TEXT | active/warning/suspended/blacklisted |
| total_batches | INT | Total batches from this vendor |
| total_leads_received | INT | Total leads ever received |
| total_fraudulent_leads | INT | Total fraudulent leads detected |
| average_fraud_rate | DECIMAL | Average fraud percentage |
| total_refunds_issued | DECIMAL | Total dollar amount refunded |

#### **batches**
Stores batch-level fraud analysis results.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| vendor_id | UUID | Foreign key to vendors |
| batch_identifier | TEXT | Batch name/ID |
| batch_date | TIMESTAMP | When batch was received |
| lead_count | INT | Total leads in batch |
| fraudulent_count | INT | Number of fraudulent leads |
| fraud_percentage | DECIMAL | Fraud rate (0-100) |
| refund_status | TEXT | FULL REFUND/PARTIAL REFUND/NO REFUND |
| refund_amount | DECIMAL | Dollar amount refunded |
| cost_per_lead | DECIMAL | Cost per lead |
| total_batch_cost | DECIMAL | Total batch cost |

#### **leads**
Stores individual lead data and fraud scores.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| batch_id | UUID | Foreign key to batches |
| lead_name | TEXT | Lead name (PII) |
| lead_email | TEXT | Lead email (PII) |
| lead_phone | TEXT | Lead phone (PII) |
| fraud_score | INT | Fraud score (0-100) |
| classification | TEXT | VALID/SUSPICIOUS/FRAUDULENT |
| is_fraudulent | BOOLEAN | True if score ≥50 |
| contact_score | INT | Contact fraud points |
| duplicate_score | INT | Duplicate fraud points |
| quality_score | INT | Quality fraud points |
| fraud_reasons | TEXT | Comma-separated list of reasons |

#### **batch_fraud_indicators**
Top fraud indicators per batch.

| Column | Type | Description |
|--------|------|-------------|
| batch_id | UUID | Foreign key to batches |
| indicator_name | TEXT | Fraud indicator name |
| indicator_category | TEXT | contact/duplicate/geographic/timing/quality |
| affected_lead_count | INT | Number of leads affected |
| percentage | DECIMAL | Percentage of batch |
| points_per_lead | INT | Points awarded per lead |

#### **fraud_blacklist**
Blacklist of known fraudulent contacts.

| Column | Type | Description |
|--------|------|-------------|
| blacklist_type | TEXT | email/phone/ip/domain |
| value | TEXT | The blacklisted value |
| reason | TEXT | Why blacklisted |
| times_detected | INT | Number of times detected |
| is_active | BOOLEAN | Active or not |

---

## Key Features

### 1. Automatic Vendor Status Updates

The database automatically updates vendor status based on fraud rate:

- **Active:** < 20% fraud rate
- **Warning:** 20-29.99% fraud rate
- **Suspended:** 30-39.99% fraud rate
- **Blacklisted:** ≥ 40% fraud rate

### 2. Fraud Pattern Detection

The system tracks known fraud patterns:
- Bot rings
- Recycled lead lists
- Fraud farms
- Incentivized gaming
- Email scraping
- VOIP floods

### 3. Disposable Email Detection

Pre-populated with 40+ known disposable email domains. Automatically updated when new domains are detected.

### 4. API Cost Tracking

Logs all API calls with costs for ROI analysis:
- Twilio Lookup costs
- ZeroBounce costs
- IPQualityScore costs
- Total costs per batch

### 5. Views for Analytics

Pre-built views for common queries:
- `vendor_fraud_summary` - Aggregate vendor stats
- `recent_high_fraud_batches` - Recent batches with ≥25% fraud
- `fraud_indicator_frequency` - Most common fraud indicators

---

## Common Queries

### Find All Batches for a Vendor

```python
from supabase_client import AnthonyLeadForensicsDB

db = AnthonyLeadForensicsDB()
vendor = db.get_vendor_by_name("PetLeads Pro")
batches = db.get_vendor_fraud_history(vendor['id'])

for batch in batches:
    print(f"{batch['batch_identifier']}: {batch['fraud_percentage']:.1f}% fraud")
```

### Get High Fraud Batches

```python
high_fraud = db.get_high_fraud_batches(threshold=25.0, limit=50)

for batch in high_fraud:
    print(f"{batch['batch_identifier']}: {batch['fraud_percentage']:.1f}%")
```

### Search for Leads by Email

```python
leads = db.search_leads_by_email("john@example.com")

print(f"Found {len(leads)} leads with this email")
for lead in leads:
    print(f"Batch: {lead['batches']['batch_identifier']}, Fraud: {lead['fraud_score']}")
```

### Add to Blacklist

```python
db.add_to_blacklist(
    blacklist_type='email',
    value='fraud@example.com',
    reason='Detected in 5 high-fraud batches'
)
```

### Check Blacklist

```python
result = db.check_blacklist('email', 'fraud@example.com')
if result:
    print(f"Blacklisted: {result['reason']}")
    print(f"Times detected: {result['times_detected']}")
```

---

## Data Retention & Privacy

### PII Handling

The `leads` table contains personally identifiable information (PII):
- Names
- Emails
- Phone numbers
- Addresses

**Important:**
- Handle this data according to GDPR/CCPA requirements
- Consider encryption at rest
- Implement data retention policies
- Use row-level security (RLS) in Supabase if needed

### Recommended Data Retention

- **Leads table:** 90 days (then delete or anonymize)
- **Batches table:** 2 years
- **Vendors table:** Indefinite
- **Fraud blacklist:** Indefinite
- **API logs:** 30 days

### Enable Row-Level Security (Optional)

In Supabase SQL Editor:

```sql
-- Enable RLS on leads table
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

-- Create policy: Only authenticated users can access
CREATE POLICY "Authenticated access" ON leads
FOR ALL USING (auth.role() = 'authenticated');
```

---

## Troubleshooting

### Connection Issues

**Error:** `Could not connect to Supabase`

**Solutions:**
1. Check `.env` file exists and has correct credentials
2. Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set
3. Test connection:
   ```bash
   python supabase_client.py
   ```

### Table Not Found

**Error:** `relation "vendors" does not exist`

**Solution:**
- Run `supabase_schema.sql` in Supabase SQL Editor
- Verify tables created in Table Editor

### Permission Denied

**Error:** `permission denied for table vendors`

**Solution:**
- Use `SUPABASE_SERVICE_ROLE_KEY` instead of `SUPABASE_ANON_KEY`
- The service role key has full permissions

### Duplicate Key Error

**Error:** `duplicate key value violates unique constraint`

**Solution:**
- Use unique batch_identifier for each batch
- Or use timestamp-based IDs: `BATCH_20240112_143022`

---

## Performance Optimization

### Indexes

The schema includes indexes on commonly queried fields:
- `vendors(vendor_name)`
- `batches(vendor_id, batch_date, fraud_percentage)`
- `leads(batch_id, email, phone, classification)`

### Bulk Operations

When inserting large batches:
- Use bulk insert methods (already implemented in `supabase_client.py`)
- Batches are split into chunks of 500 leads
- Reduces API calls and improves speed

### Caching

For frequently accessed data:
- Cache vendor list in memory
- Cache disposable email list locally
- Use database functions for aggregations

---

## Backup & Recovery

### Automatic Backups

Supabase provides automatic daily backups:
- Go to Settings > Database > Backups
- Backups retained for 7 days on free tier
- Download backups for long-term storage

### Manual Export

Export all data:

```bash
# Using Supabase CLI
supabase db dump -f backup.sql

# Or using pg_dump
pg_dump "postgresql://postgres:[PASSWORD]@db.fifybuzwfaegloijrmqb.supabase.co:5432/postgres" \
  > backup.sql
```

---

## Next Steps

1. ✅ **Run schema SQL** in Supabase SQL Editor
2. ✅ **Test connection** with `python supabase_client.py`
3. ✅ **Process first batch** with `fraud_scorer_with_db.py`
4. ✅ **View results** with `vendor_history_analyzer.py`
5. ⬜ **Set up data retention policy**
6. ⬜ **Enable RLS** if needed
7. ⬜ **Schedule regular backups**

---

## Support

**Database Schema:** See `supabase_schema.sql`
**Client Code:** See `supabase_client.py`
**Example Usage:** See `fraud_scorer_with_db.py`

**Supabase Documentation:** https://supabase.com/docs
**Supabase Dashboard:** https://fifybuzwfaegloijrmqb.supabase.co

---

**You're all set! Start detecting fraud and building vendor profiles today!** 🚀
