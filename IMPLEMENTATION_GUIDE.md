# Anthony Lead Forensics - Implementation Guide

## Quick Start (10 Minutes)

### 1. Install Required Python Libraries

```bash
# Core data processing
pip install pandas openpyxl numpy

# Phone validation
pip install phonenumbers twilio

# Email validation
pip install email-validator zerobounce dnspython

# Duplicate detection
pip install fuzzywuzzy python-Levenshtein

# Visualization
pip install matplotlib seaborn plotly

# PDF generation
pip install reportlab

# Optional: For web scraping/API calls
pip install requests
```

### 2. Set Up API Keys

Create a file `.env` in your project directory:

```env
# Twilio Lookup API
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here

# ZeroBounce API
ZEROBOUNCE_API_KEY=your_zerobounce_key_here

# IPQualityScore API
IPQS_API_KEY=your_ipqs_key_here
```

**Get API Keys:**
- Twilio: https://www.twilio.com/console (Free trial available)
- ZeroBounce: https://www.zerobounce.net/members/pricing/ (200 free credits)
- IPQualityScore: https://www.ipqualityscore.com/create-account (500 free lookups)

### 3. Download the Fraud Rules Config

The `fraud_rules_config.json` file contains all scoring rules and thresholds.

---

## Project Structure

```
anthony-lead-forensics/
├── config/
│   ├── .env                          # API keys (DO NOT commit!)
│   ├── fraud_rules_config.json       # Fraud scoring rules
│   └── disposable_emails.txt         # Extended disposable email list
├── data/
│   ├── input/
│   │   └── vendor_leads.csv          # Input lead files
│   ├── output/
│   │   ├── fraud_analysis.xlsx       # Main analysis output
│   │   ├── refund_report.pdf         # PDF audit report
│   │   └── evidence_package/         # All evidence files
│   └── databases/
│       └── fraud_history.db          # SQLite fraud history
├── src/
│   ├── __init__.py
│   ├── fraud_scorer.py               # Main fraud scoring engine
│   ├── api_validators.py             # API integration (Twilio, ZeroBounce, IPQS)
│   ├── duplicate_detector.py         # Duplicate detection logic
│   ├── pattern_analyzer.py           # Timing and pattern analysis
│   ├── report_generator.py           # Excel/PDF report generation
│   └── utils.py                      # Helper functions
├── tests/
│   ├── test_fraud_scorer.py
│   └── sample_data.csv
├── requirements.txt
├── README.md
└── main.py                            # Main entry point
```

---

## Implementation Steps

### Phase 1: Basic Validation (Week 1)

#### Step 1.1: Create Phone Validator

File: `src/phone_validator.py`

```python
import phonenumbers
from phonenumbers import carrier, geocoder
from twilio.rest import Client
import os

class PhoneValidator:
    def __init__(self):
        # Load Twilio credentials from environment
        self.twilio_client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )

    def validate_format(self, phone_number, region='US'):
        """
        Validate phone number format using phonenumbers library.
        Returns: (is_valid, formatted_number, error)
        """
        try:
            parsed = phonenumbers.parse(phone_number, region)
            is_valid = phonenumbers.is_valid_number(parsed)
            formatted = phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.E164
            )
            return is_valid, formatted, None
        except Exception as e:
            return False, None, str(e)

    def validate_with_twilio(self, phone_number):
        """
        Validate phone number using Twilio Lookup API.
        Returns: dict with validation results
        """
        try:
            result = self.twilio_client.lookups.v1.phone_numbers(
                phone_number
            ).fetch(type=['carrier'])

            return {
                'valid': result.phone_number is not None,
                'carrier_name': result.carrier.get('name'),
                'carrier_type': result.carrier.get('type'),  # mobile, landline, voip
                'is_voip': result.carrier.get('type') == 'voip',
                'error': None
            }
        except Exception as e:
            return {
                'valid': False,
                'carrier_name': None,
                'carrier_type': None,
                'is_voip': False,
                'error': str(e)
            }

    def get_area_code(self, phone_number):
        """Extract area code from phone number."""
        try:
            parsed = phonenumbers.parse(phone_number, 'US')
            # US numbers: first 3 digits after country code
            national_number = str(parsed.national_number)
            return national_number[:3]
        except:
            return None
```

#### Step 1.2: Create Email Validator

File: `src/email_validator.py`

```python
import re
from email_validator import validate_email as ev_validate
import dns.resolver
import zerobounce

class EmailValidator:
    def __init__(self, api_key=None):
        if api_key:
            zerobounce.initialize(api_key)
        self.disposable_domains = self.load_disposable_domains()

    def load_disposable_domains(self):
        """Load disposable email domain list."""
        # Load from fraud_rules_config.json or file
        return set([
            'guerrillamail.com', 'temp-mail.org', '10minutemail.com',
            'mailinator.com', 'throwaway.email', 'tempmail.com',
            # ... add all from config
        ])

    def validate_format(self, email):
        """Validate email format."""
        try:
            validated = ev_validate(email)
            return True, validated.email, None
        except Exception as e:
            return False, None, str(e)

    def is_disposable(self, email):
        """Check if email domain is disposable."""
        domain = email.split('@')[-1].lower()
        return domain in self.disposable_domains

    def check_mx_records(self, email):
        """Check if email domain has MX records."""
        domain = email.split('@')[-1]
        try:
            dns.resolver.resolve(domain, 'MX')
            return True
        except:
            return False

    def validate_with_zerobounce(self, email):
        """Validate email using ZeroBounce API."""
        try:
            response = zerobounce.validate(email)
            return {
                'status': response.status,  # valid, invalid, catch-all, unknown
                'sub_status': response.sub_status,  # disposable, role_based, etc
                'is_disposable': response.sub_status == 'disposable',
                'is_valid': response.status == 'valid',
                'error': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'sub_status': None,
                'is_disposable': False,
                'is_valid': False,
                'error': str(e)
            }
```

#### Step 1.3: Create Main Fraud Scorer

File: `src/fraud_scorer.py`

```python
import pandas as pd
import json
from phone_validator import PhoneValidator
from email_validator import EmailValidator

class FraudScorer:
    def __init__(self, config_path='config/fraud_rules_config.json'):
        # Load fraud rules configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.phone_validator = PhoneValidator()
        self.email_validator = EmailValidator(
            api_key=os.getenv('ZEROBOUNCE_API_KEY')
        )

    def score_lead(self, lead, batch_data=None):
        """
        Calculate fraud score for a single lead.
        Returns: dict with score, classification, and reasons
        """
        score = 0
        reasons = []
        breakdown = {
            'contact': 0,
            'duplicate': 0,
            'geographic': 0,
            'timing': 0,
            'quality': 0
        }

        # CONTACT VALIDATION (40 points max)
        contact_score, contact_reasons = self._score_contact(lead)
        breakdown['contact'] = min(contact_score, 40)
        score += breakdown['contact']
        reasons.extend(contact_reasons)

        # DUPLICATE DETECTION (25 points max)
        if batch_data is not None:
            dup_score, dup_reasons = self._score_duplicates(lead, batch_data)
            breakdown['duplicate'] = min(dup_score, 25)
            score += breakdown['duplicate']
            reasons.extend(dup_reasons)

        # GEOGRAPHIC VALIDATION (15 points max)
        geo_score, geo_reasons = self._score_geography(lead)
        breakdown['geographic'] = min(geo_score, 15)
        score += breakdown['geographic']
        reasons.extend(geo_reasons)

        # DATA QUALITY (10 points max)
        quality_score, quality_reasons = self._score_quality(lead)
        breakdown['quality'] = min(quality_score, 10)
        score += breakdown['quality']
        reasons.extend(quality_reasons)

        # Classify lead
        if score >= 50:
            classification = 'FRAUDULENT'
            is_fraudulent = True
        elif score >= 25:
            classification = 'SUSPICIOUS'
            is_fraudulent = False
        else:
            classification = 'VALID'
            is_fraudulent = False

        return {
            'fraud_score': score,
            'classification': classification,
            'is_fraudulent': is_fraudulent,
            'reasons': reasons,
            'breakdown': breakdown
        }

    def _score_contact(self, lead):
        """Score contact validation (phone + email)."""
        score = 0
        reasons = []

        # Phone validation
        phone = lead.get('phone', '')
        if phone:
            # Format check
            is_valid_format, formatted, error = self.phone_validator.validate_format(phone)
            if not is_valid_format:
                score += 10
                reasons.append('Invalid phone format')

            # Twilio validation
            twilio_result = self.phone_validator.validate_with_twilio(phone)
            if not twilio_result['valid']:
                score += 10
                reasons.append('Disconnected phone number')
            if twilio_result['is_voip']:
                score += 8
                reasons.append('VOIP/burner number detected')
        else:
            score += 10
            reasons.append('Missing phone number')

        # Email validation
        email = lead.get('email', '')
        if email:
            # Format check
            is_valid_format, validated, error = self.email_validator.validate_format(email)
            if not is_valid_format:
                score += 10
                reasons.append('Invalid email format')

            # Disposable check
            if self.email_validator.is_disposable(email):
                score += 10
                reasons.append('Disposable email domain')

            # MX record check
            if not self.email_validator.check_mx_records(email):
                score += 10
                reasons.append('Email domain has no MX records')

            # ZeroBounce validation
            zb_result = self.email_validator.validate_with_zerobounce(email)
            if not zb_result['is_valid']:
                score += 10
                reasons.append('Email validation failed (ZeroBounce)')
            if zb_result['is_disposable']:
                score += 10
                reasons.append('Disposable email confirmed (ZeroBounce)')
        else:
            score += 10
            reasons.append('Missing email address')

        return score, reasons

    def _score_duplicates(self, lead, batch_data):
        """Score duplicate detection."""
        # TODO: Implement duplicate detection
        # See duplicate_detector.py for full implementation
        return 0, []

    def _score_geography(self, lead):
        """Score geographic validation."""
        # TODO: Implement geographic validation
        # Check area code vs state, IP validation, etc.
        return 0, []

    def _score_quality(self, lead):
        """Score data quality."""
        score = 0
        reasons = []

        name = lead.get('name', '')
        if not name or len(name) < 2:
            score += 10
            reasons.append('Missing or invalid name')

        # Check for gibberish
        gibberish_patterns = self.config['gibberish_patterns']
        if name.lower() in gibberish_patterns:
            score += 10
            reasons.append('Gibberish name detected')

        return score, reasons
```

#### Step 1.4: Create Main Script

File: `main.py`

```python
import pandas as pd
from src.fraud_scorer import FraudScorer
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()

    # Initialize fraud scorer
    scorer = FraudScorer()

    # Load lead file
    input_file = 'data/input/vendor_leads.csv'
    leads_df = pd.read_csv(input_file)

    print(f"Loaded {len(leads_df)} leads from {input_file}")
    print("Starting fraud analysis...\n")

    # Score each lead
    results = []
    for idx, lead in leads_df.iterrows():
        print(f"Processing lead {idx + 1}/{len(leads_df)}...", end='\r')
        result = scorer.score_lead(lead.to_dict(), leads_df)
        results.append(result)

    # Add results to dataframe
    leads_df['fraud_score'] = [r['fraud_score'] for r in results]
    leads_df['classification'] = [r['classification'] for r in results]
    leads_df['is_fraudulent'] = [r['is_fraudulent'] for r in results]
    leads_df['fraud_reasons'] = [', '.join(r['reasons']) for r in results]

    # Calculate batch statistics
    total_leads = len(leads_df)
    fraudulent_leads = len(leads_df[leads_df['is_fraudulent'] == True])
    fraud_percentage = (fraudulent_leads / total_leads) * 100

    # Determine refund
    if fraud_percentage >= 25:
        refund_status = 'FULL REFUND'
        refund_percentage = 100
    elif fraud_percentage >= 15:
        refund_status = 'PARTIAL REFUND'
        refund_percentage = fraud_percentage
    else:
        refund_status = 'NO REFUND'
        refund_percentage = 0

    # Print summary
    print("\n" + "="*60)
    print("FRAUD ANALYSIS COMPLETE")
    print("="*60)
    print(f"Total Leads: {total_leads}")
    print(f"Fraudulent Leads: {fraudulent_leads} ({fraud_percentage:.1f}%)")
    print(f"Valid Leads: {total_leads - fraudulent_leads} ({100 - fraud_percentage:.1f}%)")
    print(f"\nFRAUD SCORE: {fraud_percentage:.1f}%")
    print(f"REFUND STATUS: {refund_status}")
    print(f"REFUND PERCENTAGE: {refund_percentage:.1f}%")
    print("="*60)

    # Save results
    output_file = 'data/output/fraud_analysis.xlsx'
    leads_df.to_excel(output_file, index=False)
    print(f"\nResults saved to: {output_file}")

if __name__ == '__main__':
    main()
```

#### Step 1.5: Test with Sample Data

Create `data/input/vendor_leads.csv`:

```csv
name,email,phone,address,city,state,zip
John Smith,john@example.com,5551234567,123 Main St,Los Angeles,CA,90210
Test Test,test@guerrillamail.com,5551234568,456 Oak Ave,New York,NY,10001
Jane Doe,jane@example.com,5551234567,789 Pine Rd,Chicago,IL,60601
asdfgh,fake@temp-mail.org,1234567890,111 Fake St,Miami,FL,33101
```

Run:
```bash
python main.py
```

---

### Phase 2: Full API Integration (Week 2-3)

#### Step 2.1: Implement Duplicate Detection

File: `src/duplicate_detector.py`

```python
from fuzzywuzzy import fuzz
import hashlib
import pandas as pd

class DuplicateDetector:
    def __init__(self, fuzzy_threshold=85):
        self.fuzzy_threshold = fuzzy_threshold
        self.seen_hashes = {}
        self.seen_phones = {}
        self.seen_emails = {}

    def find_exact_duplicate(self, lead, batch_data):
        """Find exact duplicates using hash comparison."""
        # Create hash of critical fields
        hash_string = f"{lead['name']}|{lead['email']}|{lead['phone']}"
        lead_hash = hashlib.md5(hash_string.encode()).hexdigest()

        if lead_hash in self.seen_hashes:
            return self.seen_hashes[lead_hash]

        self.seen_hashes[lead_hash] = lead
        return None

    def find_fuzzy_duplicate(self, lead, batch_data):
        """Find near-duplicates using fuzzy string matching."""
        lead_string = f"{lead['name']} {lead['email']} {lead['phone']}"

        for other_lead in batch_data:
            if lead == other_lead:
                continue

            other_string = f"{other_lead['name']} {other_lead['email']} {other_lead['phone']}"
            similarity = fuzz.ratio(lead_string, other_string)

            if similarity >= self.fuzzy_threshold:
                return {
                    'duplicate': other_lead,
                    'similarity': similarity
                }

        return None

    def check_phone_duplicate(self, phone, batch_data):
        """Check if phone number appears multiple times."""
        if phone in self.seen_phones:
            self.seen_phones[phone] += 1
        else:
            self.seen_phones[phone] = 1

        return self.seen_phones[phone]
```

#### Step 2.2: Implement IP Validation

File: `src/ip_validator.py`

```python
import requests
import os

class IPValidator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('IPQS_API_KEY')

    def validate_with_ipqualityscore(self, ip_address):
        """Validate IP using IPQualityScore API."""
        url = f"https://ipqualityscore.com/api/json/ip/{self.api_key}/{ip_address}"

        try:
            response = requests.get(url, timeout=30)
            data = response.json()

            return {
                'fraud_score': data.get('fraud_score', 0),
                'country': data.get('country_code', ''),
                'region': data.get('region', ''),
                'city': data.get('city', ''),
                'vpn': data.get('vpn', False),
                'proxy': data.get('proxy', False),
                'is_crawler': data.get('is_crawler', False),
                'recent_abuse': data.get('recent_abuse', False),
                'error': None
            }
        except Exception as e:
            return {
                'fraud_score': 0,
                'country': '',
                'vpn': False,
                'proxy': False,
                'error': str(e)
            }
```

#### Step 2.3: Implement Timing Analysis

File: `src/pattern_analyzer.py`

```python
import pandas as pd
import numpy as np
from datetime import datetime

class PatternAnalyzer:
    def analyze_submission_timing(self, timestamps):
        """Analyze submission timing patterns."""
        # Convert to datetime if needed
        if isinstance(timestamps[0], str):
            timestamps = pd.to_datetime(timestamps)

        # Calculate time deltas
        sorted_times = sorted(timestamps)
        deltas = [(t2 - t1).total_seconds() for t1, t2 in zip(sorted_times[:-1], sorted_times[1:])]

        # Statistical analysis
        mean_delta = np.mean(deltas)
        std_delta = np.std(deltas)

        # Bot detection: Very low std dev = regular intervals
        is_bot_pattern = std_delta < 5  # Less than 5 seconds variation

        # Velocity detection
        df = pd.DataFrame({'timestamp': timestamps})
        df['hour'] = df['timestamp'].dt.floor('H')
        leads_per_hour = df.groupby('hour').size()
        max_velocity = leads_per_hour.max()

        # Overnight detection (2-6 AM)
        overnight_leads = df[
            (df['timestamp'].dt.hour >= 2) &
            (df['timestamp'].dt.hour < 6)
        ]
        overnight_count = len(overnight_leads)

        return {
            'is_bot_pattern': is_bot_pattern,
            'std_dev': std_delta,
            'mean_interval': mean_delta,
            'max_velocity': max_velocity,
            'overnight_count': overnight_count,
            'overnight_percentage': overnight_count / len(timestamps) * 100
        }
```

---

### Phase 3: Report Generation (Week 4)

#### Step 3.1: Excel Report Generator

File: `src/excel_generator.py`

```python
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font
from openpyxl.utils import get_column_letter

class ExcelReportGenerator:
    def generate_report(self, leads_df, output_path):
        """Generate comprehensive Excel report."""

        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Lead Analysis
            leads_df.to_excel(writer, sheet_name='Lead Analysis', index=False)

            # Sheet 2: Summary Statistics
            summary = self._create_summary(leads_df)
            summary.to_excel(writer, sheet_name='Summary', index=False)

            # Sheet 3: Duplicates (if any)
            # ... implementation

        # Apply formatting
        self._apply_formatting(output_path)

    def _create_summary(self, df):
        """Create summary statistics."""
        total = len(df)
        fraudulent = len(df[df['is_fraudulent'] == True])
        suspicious = len(df[df['classification'] == 'SUSPICIOUS'])
        valid = len(df[df['classification'] == 'VALID'])

        summary_data = {
            'Metric': [
                'Total Leads',
                'Fraudulent Leads',
                'Suspicious Leads',
                'Valid Leads',
                'Fraud Percentage',
                'Average Fraud Score'
            ],
            'Value': [
                total,
                fraudulent,
                suspicious,
                valid,
                f"{fraudulent/total*100:.1f}%",
                f"{df['fraud_score'].mean():.1f}"
            ]
        }

        return pd.DataFrame(summary_data)

    def _apply_formatting(self, file_path):
        """Apply color coding to Excel file."""
        wb = load_workbook(file_path)
        ws = wb['Lead Analysis']

        # Find fraud_score column
        for col in range(1, ws.max_column + 1):
            if ws.cell(1, col).value == 'fraud_score':
                score_col = col
            if ws.cell(1, col).value == 'classification':
                class_col = col

        # Apply color coding
        for row in range(2, ws.max_row + 1):
            classification = ws.cell(row, class_col).value

            if classification == 'FRAUDULENT':
                fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')
            elif classification == 'SUSPICIOUS':
                fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
            else:
                fill = PatternFill(start_color='00FF00', end_color='00FF00', fill_type='solid')

            ws.cell(row, class_col).fill = fill

        wb.save(file_path)
```

---

## Testing

### Unit Tests

File: `tests/test_fraud_scorer.py`

```python
import unittest
from src.fraud_scorer import FraudScorer

class TestFraudScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = FraudScorer()

    def test_valid_lead(self):
        lead = {
            'name': 'John Smith',
            'email': 'john@gmail.com',
            'phone': '5551234567',
            'address': '123 Main St',
            'city': 'Los Angeles',
            'state': 'CA',
            'zip': '90210'
        }
        result = self.scorer.score_lead(lead)
        self.assertLess(result['fraud_score'], 25)
        self.assertEqual(result['classification'], 'VALID')

    def test_fraudulent_lead(self):
        lead = {
            'name': 'Test Test',
            'email': 'test@guerrillamail.com',
            'phone': '1234567890',
            'address': '',
            'city': '',
            'state': '',
            'zip': ''
        }
        result = self.scorer.score_lead(lead)
        self.assertGreaterEqual(result['fraud_score'], 50)
        self.assertEqual(result['classification'], 'FRAUDULENT')

if __name__ == '__main__':
    unittest.run()
```

---

## Deployment

### Docker Setup (Optional)

File: `Dockerfile`

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["python", "main.py"]
```

File: `docker-compose.yml`

```yaml
version: '3.8'

services:
  fraud-analyzer:
    build: .
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - ZEROBOUNCE_API_KEY=${ZEROBOUNCE_API_KEY}
      - IPQS_API_KEY=${IPQS_API_KEY}
```

---

## Troubleshooting

### Common Issues

**API Rate Limiting:**
- Implement exponential backoff
- Use batch API calls where available
- Cache results to avoid redundant calls

**Memory Issues with Large Files:**
- Process in chunks using pandas `chunksize` parameter
- Use generators instead of loading entire dataset

**Slow Processing:**
- Parallelize API calls using `concurrent.futures`
- Cache validation results in database
- Use async/await for I/O operations

---

## Next Steps

1. ✅ Complete Phase 1 (basic validation)
2. ✅ Integrate APIs (Phase 2)
3. ✅ Build report generation (Phase 3)
4. ⬜ Add database for fraud history
5. ⬜ Create web interface (optional)
6. ⬜ Implement ML-based pattern detection

---

## Support & Resources

- **Documentation:** See ENHANCED_README.md
- **Agent Prompt:** See ENHANCED_AGENT_PROMPT.md
- **Config:** See fraud_rules_config.json
- **Sample Code:** All files in `src/` directory

**Questions?** Open an issue or contact support.
