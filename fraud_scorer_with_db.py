#!/usr/bin/env python3
"""
Anthony Lead Forensics - Fraud Scorer with Database Integration
================================================================

Enhanced fraud scorer that saves all results to Supabase database.

Usage:
    python fraud_scorer_with_db.py vendor_leads.csv --vendor "VendorName" --cost 5.00

Requirements:
    pip install pandas openpyxl phonenumbers fuzzywuzzy python-Levenshtin supabase python-dotenv
"""

import pandas as pd
import sys
import argparse
from datetime import datetime
from collections import defaultdict
import hashlib

# Import the simple fraud scorer
from fraud_scorer_sample import SimpleFraudScorer, generate_summary_report

# Import Supabase client
try:
    from supabase_client import AnthonyLeadForensicsDB
except ImportError:
    print("ERROR: supabase_client.py not found or supabase not installed")
    print("Run: pip install supabase python-dotenv")
    sys.exit(1)


class FraudScorerWithDB(SimpleFraudScorer):
    """
    Enhanced fraud scorer that saves results to Supabase.
    """

    def __init__(self, save_to_db=True):
        super().__init__()
        self.save_to_db = save_to_db
        self.db = None

        if save_to_db:
            try:
                self.db = AnthonyLeadForensicsDB()
                if not self.db.test_connection():
                    print("WARNING: Could not connect to Supabase. Results will not be saved to database.")
                    self.db = None
            except Exception as e:
                print(f"WARNING: Failed to initialize Supabase client: {e}")
                print("Results will not be saved to database.")
                self.db = None

    def process_batch(self, leads_df, vendor_name, batch_identifier=None,
                      cost_per_lead=None, input_filename=None):
        """
        Process entire batch and save to database.

        Args:
            leads_df: DataFrame with lead data
            vendor_name: Vendor name
            batch_identifier: Optional batch ID (defaults to timestamp)
            cost_per_lead: Cost per lead for refund calculation
            input_filename: Original input filename

        Returns:
            dict with batch results
        """
        print(f"\nProcessing batch for vendor: {vendor_name}")
        print(f"Total leads: {len(leads_df)}")

        # Score each lead
        print("\nScoring leads...")
        results = []
        for idx, lead in leads_df.iterrows():
            progress = ((idx + 1) / len(leads_df)) * 100
            print(f"  Processing lead {idx + 1}/{len(leads_df)} ({progress:.1f}%)...", end='\r')

            result = self.score_lead(lead.to_dict(), leads_df)
            results.append(result)

        print("\n✓ Scoring complete!")

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
        refund_info = self.calculate_batch_refund(leads_df)

        # Prepare batch data
        batch_data = {
            'vendor_name': vendor_name,
            'batch_identifier': batch_identifier or datetime.now().strftime('%Y%m%d_%H%M%S'),
            'lead_count': len(leads_df),
            'fraudulent_count': refund_info['fraudulent_leads'],
            'valid_count': refund_info['valid_leads'],
            'fraud_percentage': refund_info['fraud_percentage'],
            'refund_status': refund_info['refund_type'],
            'refund_percentage': refund_info['refund_percentage'],
            'refund_amount': batch_cost * (refund_info['refund_percentage'] / 100) if batch_cost else 0,
            'cost_per_lead': cost_per_lead,
            'total_batch_cost': batch_cost,
            'input_filename': input_filename,
            'leads_df': leads_df,
            'results': results
        }

        # Calculate averages
        batch_data['avg_fraud_score'] = leads_df['fraud_score'].mean()
        batch_data['avg_contact_score'] = leads_df['breakdown_contact'].mean()
        batch_data['avg_duplicate_score'] = leads_df['breakdown_duplicate'].mean()
        batch_data['avg_quality_score'] = leads_df['breakdown_quality'].mean()

        # Save to database if enabled
        if self.db:
            print("\nSaving results to database...")
            batch_data = self._save_to_database(batch_data)
            print("✓ Results saved to Supabase!")
        else:
            print("\nDatabase not available. Skipping database save.")

        return batch_data

    def _save_to_database(self, batch_data):
        """Save batch results to Supabase."""
        try:
            # 1. Get or create vendor
            print("  1/4 Getting/creating vendor record...")
            vendor = self.db.get_or_create_vendor(batch_data['vendor_name'])
            vendor_id = vendor['id']

            # 2. Create batch record
            print("  2/4 Creating batch record...")
            batch_record = {
                'vendor_id': vendor_id,
                'batch_identifier': batch_data['batch_identifier'],
                'batch_date': datetime.now().isoformat(),
                'lead_count': batch_data['lead_count'],
                'fraudulent_count': batch_data['fraudulent_count'],
                'valid_count': batch_data['valid_count'],
                'fraud_percentage': batch_data['fraud_percentage'],
                'refund_status': batch_data['refund_status'],
                'refund_percentage': batch_data['refund_percentage'],
                'refund_amount': batch_data['refund_amount'],
                'cost_per_lead': batch_data['cost_per_lead'],
                'total_batch_cost': batch_data['total_batch_cost'],
                'avg_fraud_score': batch_data['avg_fraud_score'],
                'avg_contact_score': batch_data['avg_contact_score'],
                'avg_duplicate_score': batch_data['avg_duplicate_score'],
                'avg_quality_score': batch_data['avg_quality_score'],
                'input_filename': batch_data['input_filename']
            }

            batch = self.db.create_batch(batch_record)
            batch_id = batch['id']
            batch_data['batch_id'] = batch_id

            # 3. Create lead records
            print(f"  3/4 Saving {batch_data['lead_count']} lead records...")
            leads_df = batch_data['leads_df']
            leads_to_insert = []

            for idx, (_, lead) in enumerate(leads_df.iterrows()):
                lead_record = {
                    'batch_id': batch_id,
                    'lead_name': lead.get('name'),
                    'lead_email': lead.get('email'),
                    'lead_phone': str(lead.get('phone', '')),
                    'lead_address': lead.get('address'),
                    'lead_city': lead.get('city'),
                    'lead_state': lead.get('state'),
                    'lead_zip': lead.get('zip'),
                    'fraud_score': int(lead['fraud_score']),
                    'classification': lead['classification'],
                    'is_fraudulent': bool(lead['is_fraudulent']),
                    'contact_score': int(lead['breakdown_contact']),
                    'duplicate_score': int(lead['breakdown_duplicate']),
                    'quality_score': int(lead['breakdown_quality']),
                    'fraud_reasons': lead['fraud_reasons']
                }
                leads_to_insert.append(lead_record)

            # Bulk insert leads
            self.db.create_leads(leads_to_insert)

            # 4. Create fraud indicators
            print("  4/4 Saving fraud indicators...")
            indicators = self._generate_fraud_indicators(leads_df)
            if indicators:
                self.db.create_fraud_indicators(batch_id, indicators)

            batch_data['vendor_id'] = vendor_id

            return batch_data

        except Exception as e:
            print(f"ERROR saving to database: {e}")
            import traceback
            traceback.print_exc()
            return batch_data

    def _generate_fraud_indicators(self, leads_df):
        """Generate top fraud indicators from batch."""
        indicators = []

        # Count fraud reasons
        all_reasons = []
        for reasons_str in leads_df['fraud_reasons']:
            if reasons_str:
                all_reasons.extend(reasons_str.split(', '))

        if not all_reasons:
            return indicators

        # Count occurrences
        reason_counts = pd.Series(all_reasons).value_counts()

        # Map reasons to categories
        category_map = {
            'Invalid phone format': 'contact',
            'Missing phone number': 'contact',
            'Invalid email format': 'contact',
            'Missing email address': 'contact',
            'Disposable email domain': 'contact',
            'Phone number repeated 3+ times': 'contact',
            'Email repeated 3+ times': 'contact',
            'Exact duplicate detected': 'duplicate',
            'Invalid or gibberish name': 'quality',
            'Missing critical fields': 'quality'
        }

        total_leads = len(leads_df)

        for reason, count in reason_counts.items():
            percentage = (count / total_leads) * 100

            # Estimate points per lead (this is approximate)
            points_map = {
                'Invalid phone format': 10,
                'Missing phone number': 10,
                'Invalid email format': 10,
                'Missing email address': 10,
                'Disposable email domain': 10,
                'Phone number repeated 3+ times': 10,
                'Email repeated 3+ times': 10,
                'Exact duplicate detected': 15,
                'Invalid or gibberish name': 10,
                'Missing critical fields': 10
            }

            indicator = {
                'indicator_name': reason,
                'indicator_category': category_map.get(reason, 'quality'),
                'affected_lead_count': int(count),
                'percentage': float(percentage),
                'points_per_lead': points_map.get(reason, 10),
                'total_points': int(count * points_map.get(reason, 10))
            }

            indicators.append(indicator)

        return indicators


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Anthony Lead Forensics - Fraud Detection with Database Integration'
    )
    parser.add_argument('input_file', help='Input CSV file with leads')
    parser.add_argument('--vendor', '-v', required=True, help='Vendor name')
    parser.add_argument('--cost', '-c', type=float, help='Cost per lead (for refund calculation)')
    parser.add_argument('--batch-id', '-b', help='Batch identifier (optional)')
    parser.add_argument('--no-db', action='store_true', help='Skip database save')

    args = parser.parse_args()

    print("=" * 70)
    print("ANTHONY LEAD FORENSICS - FRAUD DETECTION SYSTEM")
    print("With Supabase Database Integration")
    print("=" * 70)
    print(f"Input file: {args.input_file}")
    print(f"Vendor: {args.vendor}")
    if args.cost:
        print(f"Cost per lead: ${args.cost:.2f}")
    print(f"Database save: {'DISABLED' if args.no_db else 'ENABLED'}")
    print("-" * 70)

    # Load lead file
    try:
        leads_df = pd.read_csv(args.input_file)
    except Exception as e:
        print(f"ERROR: Could not load file: {e}")
        sys.exit(1)

    # Initialize scorer
    scorer = FraudScorerWithDB(save_to_db=not args.no_db)

    # Process batch
    batch_data = scorer.process_batch(
        leads_df=leads_df,
        vendor_name=args.vendor,
        batch_identifier=args.batch_id,
        cost_per_lead=args.cost,
        input_filename=args.input_file
    )

    # Generate summary report
    refund_info = {
        'total_leads': batch_data['lead_count'],
        'fraudulent_leads': batch_data['fraudulent_count'],
        'valid_leads': batch_data['valid_count'],
        'fraud_percentage': batch_data['fraud_percentage'],
        'refund_type': batch_data['refund_status'],
        'refund_percentage': batch_data['refund_percentage']
    }

    report = generate_summary_report(
        batch_data['leads_df'],
        refund_info,
        batch_data['total_batch_cost']
    )

    print("\n" + report)

    # Save Excel output
    output_file = args.input_file.replace('.csv', '_fraud_analysis.xlsx')
    print(f"\nSaving detailed results to: {output_file}")

    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main analysis sheet
            batch_data['leads_df'].to_excel(writer, sheet_name='Lead Analysis', index=False)

            # Summary sheet
            summary_data = {
                'Metric': [
                    'Vendor',
                    'Batch ID',
                    'Analysis Date',
                    'Total Leads',
                    'Fraudulent Leads',
                    'Valid Leads',
                    'Fraud Percentage',
                    'Refund Status',
                    'Refund Amount',
                    'Database Saved'
                ],
                'Value': [
                    args.vendor,
                    batch_data['batch_identifier'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    refund_info['total_leads'],
                    refund_info['fraudulent_leads'],
                    refund_info['valid_leads'],
                    f"{refund_info['fraud_percentage']:.1f}%",
                    refund_info['refund_type'],
                    f"${batch_data['refund_amount']:.2f}" if batch_data['refund_amount'] else 'N/A',
                    'Yes' if batch_data.get('batch_id') else 'No'
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

        print(f"✓ Results saved successfully!")

    except Exception as e:
        print(f"WARNING: Could not save Excel file: {e}")

    # Save text report
    report_file = args.input_file.replace('.csv', '_fraud_report.txt')
    with open(report_file, 'w') as f:
        f.write(report)
        if batch_data.get('batch_id'):
            f.write(f"\n\nDatabase Record ID: {batch_data['batch_id']}")
            f.write(f"\nVendor ID: {batch_data.get('vendor_id')}")
    print(f"✓ Text report saved to: {report_file}")

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE!")
    print("=" * 70)

    if batch_data.get('batch_id'):
        print(f"\n✓ Results saved to Supabase database")
        print(f"  Batch ID: {batch_data['batch_id']}")
        print(f"  Vendor ID: {batch_data['vendor_id']}")
        print(f"\nView your results at: https://fifybuzwfaegloijrmqb.supabase.co")

    # Return exit code based on refund status
    if refund_info['fraud_percentage'] >= 25:
        sys.exit(2)  # Full refund scenario
    elif refund_info['fraud_percentage'] >= 15:
        sys.exit(1)  # Partial refund scenario
    else:
        sys.exit(0)  # No refund scenario


if __name__ == '__main__':
    main()
