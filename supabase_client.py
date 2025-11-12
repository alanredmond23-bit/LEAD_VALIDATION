#!/usr/bin/env python3
"""
Anthony Lead Forensics - Supabase Client
=========================================

Wrapper client for interacting with Supabase database to store and retrieve
fraud analysis data, vendor history, and fraud patterns.

Requirements:
    pip install supabase python-dotenv
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError:
    print("ERROR: supabase library not installed. Run: pip install supabase")
    exit(1)


class AnthonyLeadForensicsDB:
    """
    Database client for Anthony Lead Forensics fraud detection system.
    """

    def __init__(self, url: str = None, key: str = None):
        """
        Initialize Supabase client.

        Args:
            url: Supabase project URL (or load from env)
            key: Supabase anon/service key (or load from env)
        """
        # Load environment variables
        load_dotenv()

        # Get credentials
        self.url = url or os.getenv('SUPABASE_URL')
        self.key = key or os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ANON_KEY')

        if not self.url or not self.key:
            raise ValueError(
                "Supabase credentials not found. "
                "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env file"
            )

        # Initialize client
        self.client: Client = create_client(self.url, self.key)

    # =========================================================================
    # VENDOR OPERATIONS
    # =========================================================================

    def get_or_create_vendor(self, vendor_name: str, **kwargs) -> Dict[str, Any]:
        """
        Get vendor by name, or create if doesn't exist.

        Args:
            vendor_name: Vendor name
            **kwargs: Additional vendor fields (email, phone, etc.)

        Returns:
            Vendor record dict
        """
        # Try to get existing vendor
        result = self.client.table('vendors').select('*').eq('vendor_name', vendor_name).execute()

        if result.data:
            return result.data[0]

        # Create new vendor
        vendor_data = {
            'vendor_name': vendor_name,
            'vendor_email': kwargs.get('vendor_email'),
            'vendor_phone': kwargs.get('vendor_phone'),
            'first_batch_date': datetime.now().isoformat(),
            'vendor_status': 'active'
        }

        result = self.client.table('vendors').insert(vendor_data).execute()
        return result.data[0]

    def get_vendor_by_id(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        """Get vendor by UUID."""
        result = self.client.table('vendors').select('*').eq('id', vendor_id).execute()
        return result.data[0] if result.data else None

    def get_vendor_by_name(self, vendor_name: str) -> Optional[Dict[str, Any]]:
        """Get vendor by name."""
        result = self.client.table('vendors').select('*').eq('vendor_name', vendor_name).execute()
        return result.data[0] if result.data else None

    def update_vendor_status(self, vendor_id: str, status: str, notes: str = None):
        """
        Update vendor status.

        Args:
            vendor_id: Vendor UUID
            status: active, warning, suspended, or blacklisted
            notes: Optional notes
        """
        update_data = {'vendor_status': status}
        if notes:
            update_data['notes'] = notes

        self.client.table('vendors').update(update_data).eq('id', vendor_id).execute()

    def get_vendor_fraud_history(self, vendor_id: str) -> List[Dict[str, Any]]:
        """Get all batches for a vendor ordered by date."""
        result = self.client.table('batches')\
            .select('*')\
            .eq('vendor_id', vendor_id)\
            .order('batch_date', desc=True)\
            .execute()
        return result.data

    # =========================================================================
    # BATCH OPERATIONS
    # =========================================================================

    def create_batch(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new batch record.

        Args:
            batch_data: Dict containing batch information:
                - vendor_id (required)
                - batch_identifier (required)
                - lead_count (required)
                - fraud_percentage (required)
                - refund_status (required)
                - etc.

        Returns:
            Created batch record
        """
        # Set defaults
        batch_data.setdefault('analysis_date', datetime.now().isoformat())
        batch_data.setdefault('analysis_version', '2.0')
        batch_data.setdefault('analyst_name', 'Anthony Lead Forensics')

        result = self.client.table('batches').insert(batch_data).execute()
        return result.data[0]

    def get_batch_by_id(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get batch by UUID."""
        result = self.client.table('batches').select('*').eq('id', batch_id).execute()
        return result.data[0] if result.data else None

    def update_batch(self, batch_id: str, update_data: Dict[str, Any]):
        """Update batch record."""
        self.client.table('batches').update(update_data).eq('id', batch_id).execute()

    def get_high_fraud_batches(self, threshold: float = 25.0, limit: int = 50) -> List[Dict[str, Any]]:
        """Get batches with fraud rate above threshold."""
        result = self.client.table('batches')\
            .select('*, vendors(vendor_name)')\
            .gte('fraud_percentage', threshold)\
            .order('batch_date', desc=True)\
            .limit(limit)\
            .execute()
        return result.data

    def get_recent_batches(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most recent batches."""
        result = self.client.table('batches')\
            .select('*, vendors(vendor_name)')\
            .order('batch_date', desc=True)\
            .limit(limit)\
            .execute()
        return result.data

    # =========================================================================
    # LEAD OPERATIONS
    # =========================================================================

    def create_leads(self, leads_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Bulk insert leads.

        Args:
            leads_data: List of lead dicts with fraud scores and details

        Returns:
            List of created lead records
        """
        # Supabase has a limit on bulk inserts (typically 1000)
        # Split into chunks if needed
        chunk_size = 500
        all_results = []

        for i in range(0, len(leads_data), chunk_size):
            chunk = leads_data[i:i + chunk_size]
            result = self.client.table('leads').insert(chunk).execute()
            all_results.extend(result.data)

        return all_results

    def get_leads_by_batch(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get all leads for a batch."""
        result = self.client.table('leads')\
            .select('*')\
            .eq('batch_id', batch_id)\
            .execute()
        return result.data

    def get_fraudulent_leads_by_batch(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get only fraudulent leads for a batch."""
        result = self.client.table('leads')\
            .select('*')\
            .eq('batch_id', batch_id)\
            .eq('is_fraudulent', True)\
            .execute()
        return result.data

    def search_leads_by_email(self, email: str) -> List[Dict[str, Any]]:
        """Search for leads by email across all batches."""
        result = self.client.table('leads')\
            .select('*, batches(batch_identifier, vendor_id)')\
            .eq('lead_email', email)\
            .execute()
        return result.data

    def search_leads_by_phone(self, phone: str) -> List[Dict[str, Any]]:
        """Search for leads by phone across all batches."""
        result = self.client.table('leads')\
            .select('*, batches(batch_identifier, vendor_id)')\
            .eq('lead_phone', phone)\
            .execute()
        return result.data

    # =========================================================================
    # FRAUD INDICATOR OPERATIONS
    # =========================================================================

    def create_fraud_indicators(self, batch_id: str, indicators: List[Dict[str, Any]]):
        """
        Save top fraud indicators for a batch.

        Args:
            batch_id: Batch UUID
            indicators: List of indicator dicts with name, category, count, etc.
        """
        # Add batch_id to each indicator
        for indicator in indicators:
            indicator['batch_id'] = batch_id

        self.client.table('batch_fraud_indicators').insert(indicators).execute()

    def get_fraud_indicators(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get fraud indicators for a batch."""
        result = self.client.table('batch_fraud_indicators')\
            .select('*')\
            .eq('batch_id', batch_id)\
            .order('affected_lead_count', desc=True)\
            .execute()
        return result.data

    def get_top_fraud_indicators_overall(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most common fraud indicators across all batches."""
        result = self.client.table('batch_fraud_indicators')\
            .select('indicator_name, indicator_category')\
            .execute()

        # Aggregate manually (Supabase free tier doesn't support all aggregations)
        from collections import Counter
        indicators = Counter((item['indicator_name'], item['indicator_category']) for item in result.data)

        return [
            {'indicator_name': name, 'indicator_category': category, 'count': count}
            for (name, category), count in indicators.most_common(limit)
        ]

    # =========================================================================
    # API VALIDATION LOG
    # =========================================================================

    def log_api_call(self, lead_id: str, api_service: str, request_data: Dict,
                     response_data: Dict, success: bool, api_cost: float = 0.0,
                     error_message: str = None):
        """
        Log an API validation call.

        Args:
            lead_id: Lead UUID
            api_service: 'twilio', 'zerobounce', 'ipqualityscore'
            request_data: Request parameters
            response_data: API response
            success: Whether call succeeded
            api_cost: Cost of the API call
            error_message: Error message if failed
        """
        log_data = {
            'lead_id': lead_id,
            'api_service': api_service,
            'request_timestamp': datetime.now().isoformat(),
            'request_data': request_data,
            'response_data': response_data,
            'success': success,
            'api_cost': api_cost,
            'error_message': error_message
        }

        self.client.table('api_validation_log').insert(log_data).execute()

    def get_api_logs_by_lead(self, lead_id: str) -> List[Dict[str, Any]]:
        """Get all API logs for a lead."""
        result = self.client.table('api_validation_log')\
            .select('*')\
            .eq('lead_id', lead_id)\
            .order('request_timestamp', desc=True)\
            .execute()
        return result.data

    def get_api_cost_summary(self, batch_id: str = None) -> Dict[str, float]:
        """Get total API costs for a batch or overall."""
        query = self.client.table('api_validation_log').select('api_service, api_cost')

        if batch_id:
            # Need to join through leads table
            query = query.eq('leads.batch_id', batch_id)

        result = query.execute()

        # Calculate costs by service
        costs = {'twilio': 0.0, 'zerobounce': 0.0, 'ipqualityscore': 0.0, 'total': 0.0}
        for log in result.data:
            service = log['api_service']
            cost = log['api_cost'] or 0.0
            if service in costs:
                costs[service] += cost
            costs['total'] += cost

        return costs

    # =========================================================================
    # BLACKLIST OPERATIONS
    # =========================================================================

    def add_to_blacklist(self, blacklist_type: str, value: str, reason: str) -> Dict[str, Any]:
        """
        Add email/phone/IP to fraud blacklist.

        Args:
            blacklist_type: 'email', 'phone', 'ip', or 'domain'
            value: The value to blacklist
            reason: Reason for blacklisting

        Returns:
            Blacklist record
        """
        # Check if already exists
        result = self.client.table('fraud_blacklist')\
            .select('*')\
            .eq('blacklist_type', blacklist_type)\
            .eq('value', value)\
            .execute()

        if result.data:
            # Update times_detected
            existing = result.data[0]
            self.client.table('fraud_blacklist')\
                .update({
                    'times_detected': existing['times_detected'] + 1,
                    'last_detected': datetime.now().isoformat(),
                    'is_active': True
                })\
                .eq('id', existing['id'])\
                .execute()
            return existing

        # Create new
        blacklist_data = {
            'blacklist_type': blacklist_type,
            'value': value,
            'reason': reason,
            'times_detected': 1,
            'first_detected': datetime.now().isoformat(),
            'last_detected': datetime.now().isoformat(),
            'is_active': True
        }

        result = self.client.table('fraud_blacklist').insert(blacklist_data).execute()
        return result.data[0]

    def check_blacklist(self, blacklist_type: str, value: str) -> Optional[Dict[str, Any]]:
        """Check if a value is in the blacklist."""
        result = self.client.table('fraud_blacklist')\
            .select('*')\
            .eq('blacklist_type', blacklist_type)\
            .eq('value', value)\
            .eq('is_active', True)\
            .execute()

        return result.data[0] if result.data else None

    def get_blacklist(self, blacklist_type: str = None) -> List[Dict[str, Any]]:
        """Get all blacklist entries, optionally filtered by type."""
        query = self.client.table('fraud_blacklist').select('*').eq('is_active', True)

        if blacklist_type:
            query = query.eq('blacklist_type', blacklist_type)

        result = query.order('times_detected', desc=True).execute()
        return result.data

    # =========================================================================
    # DISPOSABLE EMAIL OPERATIONS
    # =========================================================================

    def is_disposable_email(self, domain: str) -> bool:
        """Check if email domain is disposable."""
        result = self.client.table('disposable_email_domains')\
            .select('*')\
            .eq('domain', domain.lower())\
            .eq('is_active', True)\
            .execute()

        if result.data:
            # Update times_detected
            self.client.table('disposable_email_domains')\
                .update({
                    'times_detected': result.data[0]['times_detected'] + 1,
                    'last_detected': datetime.now().isoformat()
                })\
                .eq('domain', domain.lower())\
                .execute()
            return True

        return False

    def add_disposable_domain(self, domain: str, source: str = 'manual'):
        """Add a new disposable email domain."""
        domain_data = {
            'domain': domain.lower(),
            'times_detected': 0,
            'is_active': True,
            'source': source
        }

        self.client.table('disposable_email_domains')\
            .insert(domain_data)\
            .execute()

    # =========================================================================
    # ANALYTICS & REPORTS
    # =========================================================================

    def get_vendor_summary(self, vendor_id: str = None) -> List[Dict[str, Any]]:
        """Get vendor fraud summary (from view)."""
        query = self.client.table('vendor_fraud_summary').select('*')

        if vendor_id:
            query = query.eq('id', vendor_id)

        result = query.order('average_fraud_rate', desc=True).execute()
        return result.data

    def get_fraud_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get fraud trend data for the last N days."""
        from datetime import timedelta

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        result = self.client.table('batches')\
            .select('batch_date, fraud_percentage, refund_status')\
            .gte('batch_date', cutoff_date)\
            .order('batch_date', desc=False)\
            .execute()

        return result.data

    def get_refund_summary(self) -> Dict[str, Any]:
        """Get summary of all refunds."""
        result = self.client.table('batches').select('refund_status, refund_amount').execute()

        summary = {
            'total_batches': len(result.data),
            'full_refunds': 0,
            'partial_refunds': 0,
            'no_refunds': 0,
            'total_refund_amount': 0.0
        }

        for batch in result.data:
            status = batch.get('refund_status')
            amount = batch.get('refund_amount', 0.0) or 0.0

            if status == 'FULL REFUND':
                summary['full_refunds'] += 1
            elif status == 'PARTIAL REFUND':
                summary['partial_refunds'] += 1
            elif status == 'NO REFUND':
                summary['no_refunds'] += 1

            summary['total_refund_amount'] += amount

        return summary

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            result = self.client.table('vendors').select('id').limit(1).execute()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def get_database_stats(self) -> Dict[str, int]:
        """Get record counts for all tables."""
        stats = {}

        tables = ['vendors', 'batches', 'leads', 'fraud_blacklist',
                  'disposable_email_domains', 'api_validation_log']

        for table in tables:
            try:
                result = self.client.table(table).select('id', count='exact').execute()
                stats[table] = result.count
            except:
                stats[table] = 0

        return stats


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == '__main__':
    # Initialize client
    db = AnthonyLeadForensicsDB()

    # Test connection
    if db.test_connection():
        print("✓ Connected to Supabase successfully!")

        # Get database stats
        stats = db.get_database_stats()
        print("\nDatabase Statistics:")
        for table, count in stats.items():
            print(f"  {table}: {count} records")

        # Get vendor summary
        vendors = db.get_vendor_summary()
        if vendors:
            print(f"\nFound {len(vendors)} vendors in database")
        else:
            print("\nNo vendors found. Database is empty.")

    else:
        print("✗ Failed to connect to Supabase")
        print("Check your SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env file")
