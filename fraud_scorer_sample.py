#!/usr/bin/env python3
"""
Anthony Lead Forensics - Sample Fraud Scoring Script
====================================================

This is a complete, runnable fraud detection script that demonstrates
the full fraud scoring system with 25% refund threshold.

Usage:
    python fraud_scorer_sample.py input_leads.csv

Requirements:
    pip install pandas openpyxl phonenumbers fuzzywuzzy python-Levenshtein
"""

import pandas as pd
import json
import re
import hashlib
from datetime import datetime
from collections import defaultdict
import sys

# If you have API keys, uncomment and use:
# from twilio.rest import Client
# import zerobounce
# import requests

class SimpleFraudScorer:
    """
    Simplified fraud scorer that works without API keys.
    For production, integrate Twilio, ZeroBounce, and IPQualityScore APIs.
    """

    def __init__(self):
        self.disposable_domains = {
            'guerrillamail.com', 'temp-mail.org', '10minutemail.com',
            'mailinator.com', 'throwaway.email', 'tempmail.com',
            'getnada.com', 'maildrop.cc', 'yopmail.com', 'fakeinbox.com',
            'emailondeck.com', 'throwawaymail.com', 'trashmail.com',
            'sharklasers.com', 'spam4.me', 'tempr.email'
        }

        self.gibberish_patterns = {
            'asdfgh', 'qwerty', 'zxcvbn', 'test test', 'test',
            'fake', 'xxx', 'aaa', 'zzz', 'nnn', '111', '123', 'abc'
        }

        self.seen_phones = defaultdict(int)
        self.seen_emails = defaultdict(int)
        self.seen_hashes = set()

    def validate_phone_format(self, phone):
        """Basic phone format validation."""
        if not phone:
            return False

        # Remove all non-digits
        digits = re.sub(r'\D', '', str(phone))

        # Should be 10 digits (US) or 11 with country code
        if len(digits) == 10 or len(digits) == 11:
            return True

        return False

    def validate_email_format(self, email):
        """Basic email format validation."""
        if not email:
            return False

        # Simple regex for email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email)))

    def is_disposable_email(self, email):
        """Check if email domain is disposable."""
        if not email:
            return False

        domain = str(email).split('@')[-1].lower()
        return domain in self.disposable_domains

    def is_gibberish_name(self, name):
        """Check if name is gibberish."""
        if not name:
            return True

        name_lower = str(name).lower().strip()

        # Check against known gibberish patterns
        if name_lower in self.gibberish_patterns:
            return True

        # Check for single character names
        if len(name_lower) <= 1:
            return True

        # Check for numbers in name
        if any(char.isdigit() for char in name_lower):
            return True

        return False

    def find_exact_duplicate(self, lead):
        """Check for exact duplicates using hash."""
        hash_string = f"{lead.get('name', '')}|{lead.get('email', '')}|{lead.get('phone', '')}"
        lead_hash = hashlib.md5(hash_string.encode()).hexdigest()

        if lead_hash in self.seen_hashes:
            return True

        self.seen_hashes.add(lead_hash)
        return False

    def check_repeated_contact(self, lead):
        """Check if phone/email appears multiple times."""
        phone = str(lead.get('phone', ''))
        email = str(lead.get('email', ''))

        self.seen_phones[phone] += 1
        self.seen_emails[email] += 1

        repeated_phone = self.seen_phones[phone] >= 3
        repeated_email = self.seen_emails[email] >= 3

        return repeated_phone, repeated_email

    def score_lead(self, lead, batch_data=None):
        """
        Calculate fraud score for a single lead.

        Returns:
            dict with fraud_score (0-100), classification, reasons, and breakdown
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

        # Phone validation
        phone = lead.get('phone', '')
        if not phone:
            score += 10
            breakdown['contact'] += 10
            reasons.append('Missing phone number')
        elif not self.validate_phone_format(phone):
            score += 10
            breakdown['contact'] += 10
            reasons.append('Invalid phone format')

        # Email validation
        email = lead.get('email', '')
        if not email:
            score += 10
            breakdown['contact'] += 10
            reasons.append('Missing email address')
        elif not self.validate_email_format(email):
            score += 10
            breakdown['contact'] += 10
            reasons.append('Invalid email format')
        elif self.is_disposable_email(email):
            score += 10
            breakdown['contact'] += 10
            reasons.append('Disposable email domain')

        # Check for repeated contacts
        repeated_phone, repeated_email = self.check_repeated_contact(lead)
        if repeated_phone:
            score += 10
            breakdown['contact'] += 10
            reasons.append('Phone number repeated 3+ times')
        if repeated_email:
            score += 10
            breakdown['contact'] += 10
            reasons.append('Email repeated 3+ times')

        # Cap contact score at 40
        breakdown['contact'] = min(breakdown['contact'], 40)

        # DUPLICATE DETECTION (25 points max)

        if self.find_exact_duplicate(lead):
            score += 15
            breakdown['duplicate'] += 15
            reasons.append('Exact duplicate detected')

        # Cap duplicate score at 25
        breakdown['duplicate'] = min(breakdown['duplicate'], 25)

        # DATA QUALITY (10 points max)

        name = lead.get('name', '')
        if not name or self.is_gibberish_name(name):
            score += 10
            breakdown['quality'] += 10
            reasons.append('Invalid or gibberish name')

        # Check for missing critical fields
        if not name or not email or not phone:
            if 'Missing' not in ' '.join(reasons):  # Avoid duplicate reason
                score += 10
                breakdown['quality'] += 10
                reasons.append('Missing critical fields')

        # Cap quality score at 10
        breakdown['quality'] = min(breakdown['quality'], 10)

        # CLASSIFY LEAD

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

    def calculate_batch_refund(self, leads_df):
        """Calculate refund for entire batch based on fraud percentage."""
        total_leads = len(leads_df)
        fraudulent_leads = len(leads_df[leads_df['is_fraudulent'] == True])
        fraud_percentage = (fraudulent_leads / total_leads) * 100

        if fraud_percentage >= 25:
            refund_type = 'FULL REFUND'
            refund_percentage = 100
        elif fraud_percentage >= 15:
            refund_type = 'PARTIAL REFUND'
            refund_percentage = fraud_percentage
        else:
            refund_type = 'NO REFUND'
            refund_percentage = 0

        return {
            'refund_type': refund_type,
            'refund_percentage': refund_percentage,
            'fraud_percentage': fraud_percentage,
            'fraudulent_leads': fraudulent_leads,
            'valid_leads': total_leads - fraudulent_leads,
            'total_leads': total_leads
        }


def generate_summary_report(leads_df, refund_info, batch_cost=None):
    """Generate a text summary report."""

    report = []
    report.append("=" * 70)
    report.append("ANTHONY LEAD FORENSICS - FRAUD ANALYSIS REPORT")
    report.append("=" * 70)
    report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    report.append("BATCH STATISTICS:")
    report.append("-" * 70)
    report.append(f"Total Leads Analyzed: {refund_info['total_leads']}")
    report.append(f"Fraudulent Leads: {refund_info['fraudulent_leads']} ({refund_info['fraud_percentage']:.1f}%)")
    report.append(f"Valid Leads: {refund_info['valid_leads']} ({100 - refund_info['fraud_percentage']:.1f}%)")
    report.append("")

    report.append("FRAUD BREAKDOWN BY CATEGORY:")
    report.append("-" * 70)
    avg_contact = leads_df['breakdown_contact'].mean()
    avg_duplicate = leads_df['breakdown_duplicate'].mean()
    avg_quality = leads_df['breakdown_quality'].mean()

    report.append(f"Contact Validation Issues: {avg_contact:.1f} points (avg)")
    report.append(f"Duplicate Detection: {avg_duplicate:.1f} points (avg)")
    report.append(f"Data Quality Issues: {avg_quality:.1f} points (avg)")
    report.append("")

    report.append("TOP FRAUD INDICATORS:")
    report.append("-" * 70)
    # Count reasons
    all_reasons = []
    for reasons_str in leads_df['fraud_reasons']:
        if reasons_str:
            all_reasons.extend(reasons_str.split(', '))

    reason_counts = pd.Series(all_reasons).value_counts().head(10)
    for idx, (reason, count) in enumerate(reason_counts.items(), 1):
        percentage = (count / len(leads_df)) * 100
        report.append(f"{idx}. {reason}: {count} leads ({percentage:.1f}%)")
    report.append("")

    report.append("REFUND DETERMINATION:")
    report.append("=" * 70)
    report.append("REFUND THRESHOLD POLICY:")
    report.append("  ≥ 25% fraud = Full refund (100%)")
    report.append("  15-24% fraud = Partial refund (pro-rata)")
    report.append("  < 15% fraud = No refund (acceptable tolerance)")
    report.append("")
    report.append(f"BATCH FRAUD SCORE: {refund_info['fraud_percentage']:.1f}%")
    report.append(f"REFUND STATUS: {refund_info['refund_type']}")
    report.append(f"REFUND PERCENTAGE: {refund_info['refund_percentage']:.1f}%")

    if batch_cost:
        refund_amount = batch_cost * (refund_info['refund_percentage'] / 100)
        report.append("")
        report.append(f"FINANCIAL IMPACT:")
        report.append(f"  Batch Cost: ${batch_cost:,.2f}")
        report.append(f"  Refund Amount: ${refund_amount:,.2f}")

    report.append("")
    report.append("INDUSTRY COMPARISON:")
    report.append("-" * 70)
    report.append("Industry Standard Fraud Rate: 8-12%")
    report.append(f"This Batch Fraud Rate: {refund_info['fraud_percentage']:.1f}%")

    deviation = refund_info['fraud_percentage'] - 10  # Compare to 10% midpoint
    if deviation > 0:
        report.append(f"Deviation: {deviation:.1f}% ABOVE industry standard")
    else:
        report.append(f"Deviation: {abs(deviation):.1f}% below industry standard")

    report.append("")
    report.append("CONCLUSION:")
    report.append("=" * 70)

    if refund_info['fraud_percentage'] >= 25:
        report.append("This batch contains an UNACCEPTABLE level of fraudulent leads.")
        report.append("RECOMMENDATION: Full refund is JUSTIFIED based on fraud threshold policy.")
    elif refund_info['fraud_percentage'] >= 15:
        report.append("This batch contains a MARGINAL level of fraudulent leads.")
        report.append("RECOMMENDATION: Partial refund is justified proportional to fraud rate.")
    else:
        report.append("This batch falls within ACCEPTABLE fraud tolerance.")
        report.append("RECOMMENDATION: No refund required, but monitor vendor quality.")

    report.append("")
    report.append("=" * 70)
    report.append("END OF REPORT")
    report.append("=" * 70)

    return "\n".join(report)


def main():
    """Main execution function."""

    # Check if input file provided
    if len(sys.argv) < 2:
        print("Usage: python fraud_scorer_sample.py <input_csv_file> [cost_per_lead]")
        print("\nExample:")
        print("  python fraud_scorer_sample.py vendor_leads.csv 5.00")
        sys.exit(1)

    input_file = sys.argv[1]
    cost_per_lead = float(sys.argv[2]) if len(sys.argv) > 2 else None

    print("=" * 70)
    print("ANTHONY LEAD FORENSICS - FRAUD DETECTION SYSTEM")
    print("=" * 70)
    print(f"Loading leads from: {input_file}")

    # Load lead file
    try:
        leads_df = pd.read_csv(input_file)
    except Exception as e:
        print(f"ERROR: Could not load file: {e}")
        sys.exit(1)

    print(f"Loaded {len(leads_df)} leads")
    print("\nStarting fraud analysis...")
    print("-" * 70)

    # Initialize scorer
    scorer = SimpleFraudScorer()

    # Score each lead
    results = []
    for idx, lead in leads_df.iterrows():
        progress = ((idx + 1) / len(leads_df)) * 100
        print(f"Processing lead {idx + 1}/{len(leads_df)} ({progress:.1f}%)...", end='\r')

        result = scorer.score_lead(lead.to_dict(), leads_df)
        results.append(result)

    print("\nScoring complete!                                                      ")

    # Add results to dataframe
    leads_df['fraud_score'] = [r['fraud_score'] for r in results]
    leads_df['classification'] = [r['classification'] for r in results]
    leads_df['is_fraudulent'] = [r['is_fraudulent'] for r in results]
    leads_df['fraud_reasons'] = [', '.join(r['reasons']) if r['reasons'] else '' for r in results]
    leads_df['breakdown_contact'] = [r['breakdown']['contact'] for r in results]
    leads_df['breakdown_duplicate'] = [r['breakdown']['duplicate'] for r in results]
    leads_df['breakdown_quality'] = [r['breakdown']['quality'] for r in results]

    # Calculate refund
    batch_cost = len(leads_df) * cost_per_lead if cost_per_lead else None
    refund_info = scorer.calculate_batch_refund(leads_df)

    # Generate report
    report = generate_summary_report(leads_df, refund_info, batch_cost)
    print("\n" + report)

    # Save results
    output_file = input_file.replace('.csv', '_fraud_analysis.xlsx')
    print(f"\nSaving detailed results to: {output_file}")

    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main analysis sheet
            leads_df.to_excel(writer, sheet_name='Lead Analysis', index=False)

            # Summary sheet
            summary_data = {
                'Metric': [
                    'Total Leads',
                    'Fraudulent Leads',
                    'Valid Leads',
                    'Fraud Percentage',
                    'Refund Status',
                    'Refund Percentage',
                    'Average Fraud Score',
                    'Median Fraud Score'
                ],
                'Value': [
                    refund_info['total_leads'],
                    refund_info['fraudulent_leads'],
                    refund_info['valid_leads'],
                    f"{refund_info['fraud_percentage']:.1f}%",
                    refund_info['refund_type'],
                    f"{refund_info['refund_percentage']:.1f}%",
                    f"{leads_df['fraud_score'].mean():.1f}",
                    f"{leads_df['fraud_score'].median():.1f}"
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

        print(f"✓ Results saved successfully!")

    except Exception as e:
        print(f"WARNING: Could not save Excel file: {e}")
        # Fall back to CSV
        csv_output = input_file.replace('.csv', '_fraud_analysis.csv')
        leads_df.to_csv(csv_output, index=False)
        print(f"✓ Results saved to CSV: {csv_output}")

    # Save text report
    report_file = input_file.replace('.csv', '_fraud_report.txt')
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"✓ Text report saved to: {report_file}")

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE!")
    print("=" * 70)

    # Return exit code based on refund status
    if refund_info['fraud_percentage'] >= 25:
        sys.exit(2)  # Full refund scenario
    elif refund_info['fraud_percentage'] >= 15:
        sys.exit(1)  # Partial refund scenario
    else:
        sys.exit(0)  # No refund scenario


if __name__ == '__main__':
    main()
