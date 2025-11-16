#!/usr/bin/env python3
"""
Anthony Lead Forensics - Vendor Fraud History Analyzer
=======================================================

Analyzes vendor fraud history from Supabase database and generates reports.

Usage:
    python vendor_history_analyzer.py --vendor "VendorName"
    python vendor_history_analyzer.py --list-vendors
    python vendor_history_analyzer.py --high-fraud
    python vendor_history_analyzer.py --summary

Requirements:
    pip install pandas supabase python-dotenv
"""

import sys
import argparse
from datetime import datetime, timedelta
import pandas as pd

try:
    from supabase_client import AnthonyLeadForensicsDB
except ImportError:
    print("ERROR: supabase_client.py not found")
    sys.exit(1)


class VendorHistoryAnalyzer:
    """
    Analyzes vendor fraud history from database.
    """

    def __init__(self):
        try:
            self.db = AnthonyLeadForensicsDB()
            if not self.db.test_connection():
                print("ERROR: Could not connect to Supabase database")
                sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to initialize database: {e}")
            sys.exit(1)

    def list_vendors(self):
        """List all vendors with summary stats."""
        print("\n" + "=" * 80)
        print("VENDOR LIST")
        print("=" * 80)

        vendors = self.db.get_vendor_summary()

        if not vendors:
            print("No vendors found in database.")
            return

        # Create DataFrame for easy formatting
        df = pd.DataFrame(vendors)

        # Select and format columns
        display_cols = [
            'vendor_name', 'vendor_status', 'total_batches',
            'total_leads_received', 'average_fraud_rate', 'total_refunds_issued'
        ]

        if not all(col in df.columns for col in display_cols):
            # Fallback if view doesn't exist
            print(f"Found {len(vendors)} vendors:")
            for vendor in vendors:
                print(f"\n  Vendor: {vendor.get('vendor_name')}")
                print(f"  Status: {vendor.get('vendor_status', 'unknown')}")
                print(f"  Total Batches: {vendor.get('total_batches', 0)}")
                print(f"  Avg Fraud Rate: {vendor.get('average_fraud_rate', 0):.1f}%")
            return

        # Format display
        print(f"\nFound {len(df)} vendors:\n")
        print(df[display_cols].to_string(index=False))

        # Highlight problem vendors
        problem_vendors = df[df['average_fraud_rate'] >= 25.0]
        if len(problem_vendors) > 0:
            print(f"\n⚠️  WARNING: {len(problem_vendors)} vendors with fraud rate ≥25%:")
            for _, vendor in problem_vendors.iterrows():
                print(f"  - {vendor['vendor_name']}: {vendor['average_fraud_rate']:.1f}%")

    def analyze_vendor(self, vendor_name):
        """Detailed analysis of a specific vendor."""
        print("\n" + "=" * 80)
        print(f"VENDOR FRAUD HISTORY ANALYSIS: {vendor_name}")
        print("=" * 80)

        # Get vendor
        vendor = self.db.get_vendor_by_name(vendor_name)
        if not vendor:
            print(f"ERROR: Vendor '{vendor_name}' not found in database.")
            return

        vendor_id = vendor['id']

        print(f"\nVendor Information:")
        print(f"  Name: {vendor['vendor_name']}")
        print(f"  Status: {vendor['vendor_status']}")
        print(f"  Total Batches: {vendor['total_batches']}")
        print(f"  Total Leads: {vendor['total_leads_received']}")
        print(f"  Fraudulent Leads: {vendor['total_fraudulent_leads']}")
        print(f"  Average Fraud Rate: {vendor['average_fraud_rate']:.2f}%")
        print(f"  Total Refunds: ${vendor['total_refunds_issued']:.2f}")

        # Get batch history
        batches = self.db.get_vendor_fraud_history(vendor_id)

        if not batches:
            print("\nNo batches found for this vendor.")
            return

        print(f"\n" + "-" * 80)
        print(f"BATCH HISTORY ({len(batches)} batches)")
        print("-" * 80)

        # Create DataFrame
        df = pd.DataFrame(batches)

        # Display each batch
        for idx, batch in enumerate(batches, 1):
            print(f"\nBatch #{idx}: {batch['batch_identifier']}")
            print(f"  Date: {batch['batch_date']}")
            print(f"  Leads: {batch['lead_count']}")
            print(f"  Fraudulent: {batch['fraudulent_count']} ({batch['fraud_percentage']:.1f}%)")
            print(f"  Refund Status: {batch['refund_status']}")
            if batch['refund_amount']:
                print(f"  Refund Amount: ${batch['refund_amount']:.2f}")
            if batch['auto_refund_triggered']:
                print(f"  ⚠️  AUTO-REFUND TRIGGERED: {batch['auto_refund_reason']}")

        # Statistics
        print(f"\n" + "-" * 80)
        print("FRAUD STATISTICS")
        print("-" * 80)

        avg_fraud = df['fraud_percentage'].mean()
        max_fraud = df['fraud_percentage'].max()
        min_fraud = df['fraud_percentage'].min()
        std_fraud = df['fraud_percentage'].std()

        print(f"  Average Fraud Rate: {avg_fraud:.2f}%")
        print(f"  Maximum Fraud Rate: {max_fraud:.2f}%")
        print(f"  Minimum Fraud Rate: {min_fraud:.2f}%")
        print(f"  Standard Deviation: {std_fraud:.2f}%")

        # Refund statistics
        full_refunds = len(df[df['refund_status'] == 'FULL REFUND'])
        partial_refunds = len(df[df['refund_status'] == 'PARTIAL REFUND'])
        no_refunds = len(df[df['refund_status'] == 'NO REFUND'])

        print(f"\n  Refund Breakdown:")
        print(f"    Full Refunds: {full_refunds} ({full_refunds/len(df)*100:.1f}%)")
        print(f"    Partial Refunds: {partial_refunds} ({partial_refunds/len(df)*100:.1f}%)")
        print(f"    No Refunds: {no_refunds} ({no_refunds/len(df)*100:.1f}%)")

        total_refunded = df['refund_amount'].sum()
        print(f"\n  Total Amount Refunded: ${total_refunded:.2f}")

        # Trend analysis
        print(f"\n" + "-" * 80)
        print("TREND ANALYSIS")
        print("-" * 80)

        if len(df) >= 3:
            recent_3 = df.head(3)['fraud_percentage'].mean()
            overall = df['fraud_percentage'].mean()

            print(f"  Last 3 batches avg: {recent_3:.2f}%")
            print(f"  Overall average: {overall:.2f}%")

            if recent_3 > overall + 5:
                print(f"  ⚠️  TREND: Fraud rate INCREASING")
            elif recent_3 < overall - 5:
                print(f"  ✓ TREND: Fraud rate DECREASING")
            else:
                print(f"  → TREND: Stable")
        else:
            print("  Not enough data for trend analysis (need 3+ batches)")

        # Recommendation
        print(f"\n" + "-" * 80)
        print("RECOMMENDATION")
        print("-" * 80)

        if avg_fraud >= 40:
            print("  🚫 BLACKLIST VENDOR - Consistently high fraud rate (≥40%)")
        elif avg_fraud >= 30:
            print("  ⛔ SUSPEND VENDOR - High fraud rate (≥30%)")
        elif avg_fraud >= 20:
            print("  ⚠️  WARNING - Elevated fraud rate (≥20%)")
        elif avg_fraud >= 15:
            print("  ⚡ MONITOR CLOSELY - Above acceptable threshold")
        else:
            print("  ✓ ACCEPTABLE - Within normal fraud tolerance")

    def high_fraud_report(self, threshold=25.0, days=30):
        """Report on high fraud batches."""
        print("\n" + "=" * 80)
        print(f"HIGH FRAUD BATCHES (≥{threshold}% fraud)")
        print("=" * 80)

        batches = self.db.get_high_fraud_batches(threshold=threshold)

        if not batches:
            print(f"\nNo batches found with fraud rate ≥{threshold}%")
            return

        print(f"\nFound {len(batches)} high fraud batches:\n")

        for idx, batch in enumerate(batches, 1):
            # Get vendor name
            vendor_name = batch.get('vendors', {}).get('vendor_name', 'Unknown') if isinstance(batch.get('vendors'), dict) else 'Unknown'

            print(f"{idx}. {vendor_name} - {batch['batch_identifier']}")
            print(f"   Date: {batch['batch_date']}")
            print(f"   Leads: {batch['lead_count']}")
            print(f"   Fraud Rate: {batch['fraud_percentage']:.1f}%")
            print(f"   Refund: {batch['refund_status']} - ${batch.get('refund_amount', 0):.2f}")
            if batch.get('auto_refund_triggered'):
                print(f"   Auto-Refund: {batch['auto_refund_reason']}")
            print()

    def overall_summary(self):
        """Overall fraud detection summary."""
        print("\n" + "=" * 80)
        print("FRAUD DETECTION SYSTEM - OVERALL SUMMARY")
        print("=" * 80)

        # Database stats
        stats = self.db.get_database_stats()

        print(f"\nDatabase Statistics:")
        print(f"  Vendors: {stats.get('vendors', 0)}")
        print(f"  Batches: {stats.get('batches', 0)}")
        print(f"  Leads: {stats.get('leads', 0)}")
        print(f"  Blacklist Entries: {stats.get('fraud_blacklist', 0)}")

        # Refund summary
        refund_summary = self.db.get_refund_summary()

        print(f"\nRefund Summary:")
        print(f"  Total Batches Analyzed: {refund_summary['total_batches']}")
        print(f"  Full Refunds: {refund_summary['full_refunds']}")
        print(f"  Partial Refunds: {refund_summary['partial_refunds']}")
        print(f"  No Refunds: {refund_summary['no_refunds']}")
        print(f"  Total Refunded: ${refund_summary['total_refund_amount']:.2f}")

        # Vendor summary
        vendors = self.db.get_vendor_summary()

        if vendors:
            df = pd.DataFrame(vendors)

            print(f"\nVendor Status Distribution:")
            if 'vendor_status' in df.columns:
                status_counts = df['vendor_status'].value_counts()
                for status, count in status_counts.items():
                    print(f"  {status.title()}: {count}")

            print(f"\nTop 10 Highest Fraud Rate Vendors:")
            if 'average_fraud_rate' in df.columns and 'vendor_name' in df.columns:
                top_fraud = df.nlargest(10, 'average_fraud_rate')
                for idx, vendor in enumerate(top_fraud.itertuples(), 1):
                    print(f"  {idx}. {vendor.vendor_name}: {vendor.average_fraud_rate:.1f}%")

        # Recent trends
        print(f"\nRecent Activity (Last 30 days):")
        trends = self.db.get_fraud_trends(days=30)

        if trends:
            df_trends = pd.DataFrame(trends)
            avg_recent = df_trends['fraud_percentage'].mean()
            print(f"  Batches Analyzed: {len(df_trends)}")
            print(f"  Average Fraud Rate: {avg_recent:.2f}%")

            high_fraud = len(df_trends[df_trends['fraud_percentage'] >= 25.0])
            if high_fraud > 0:
                print(f"  ⚠️  High Fraud Batches (≥25%): {high_fraud}")

    def export_vendor_report(self, vendor_name, output_file=None):
        """Export vendor analysis to Excel."""
        vendor = self.db.get_vendor_by_name(vendor_name)
        if not vendor:
            print(f"ERROR: Vendor '{vendor_name}' not found")
            return

        batches = self.db.get_vendor_fraud_history(vendor['id'])
        if not batches:
            print("No batch data to export")
            return

        # Create DataFrame
        df = pd.DataFrame(batches)

        # Prepare output file
        if not output_file:
            safe_name = vendor_name.replace(' ', '_').replace('/', '_')
            output_file = f"vendor_report_{safe_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"

        print(f"Exporting to: {output_file}")

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Batch history
            df.to_excel(writer, sheet_name='Batch History', index=False)

            # Vendor summary
            summary_data = {
                'Metric': [
                    'Vendor Name',
                    'Status',
                    'Total Batches',
                    'Total Leads',
                    'Fraudulent Leads',
                    'Average Fraud Rate',
                    'Total Refunds'
                ],
                'Value': [
                    vendor['vendor_name'],
                    vendor['vendor_status'],
                    vendor['total_batches'],
                    vendor['total_leads_received'],
                    vendor['total_fraudulent_leads'],
                    f"{vendor['average_fraud_rate']:.2f}%",
                    f"${vendor['total_refunds_issued']:.2f}"
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

        print(f"✓ Report exported successfully!")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='Anthony Lead Forensics - Vendor Fraud History Analyzer'
    )

    parser.add_argument('--vendor', '-v', help='Analyze specific vendor')
    parser.add_argument('--list-vendors', '-l', action='store_true', help='List all vendors')
    parser.add_argument('--high-fraud', '-hf', action='store_true', help='Show high fraud batches')
    parser.add_argument('--summary', '-s', action='store_true', help='Overall system summary')
    parser.add_argument('--export', '-e', action='store_true', help='Export vendor report to Excel')
    parser.add_argument('--threshold', '-t', type=float, default=25.0, help='Fraud threshold for high fraud report')

    args = parser.parse_args()

    # If no arguments, show help
    if not any([args.vendor, args.list_vendors, args.high_fraud, args.summary]):
        parser.print_help()
        sys.exit(0)

    print("=" * 80)
    print("ANTHONY LEAD FORENSICS - VENDOR HISTORY ANALYZER")
    print("=" * 80)

    # Initialize analyzer
    analyzer = VendorHistoryAnalyzer()

    # Execute requested analysis
    if args.list_vendors:
        analyzer.list_vendors()

    if args.vendor:
        analyzer.analyze_vendor(args.vendor)
        if args.export:
            analyzer.export_vendor_report(args.vendor)

    if args.high_fraud:
        analyzer.high_fraud_report(threshold=args.threshold)

    if args.summary:
        analyzer.overall_summary()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
