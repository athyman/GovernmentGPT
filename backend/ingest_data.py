#!/usr/bin/env python3
"""
GovernmentGPT Data Ingestion CLI

This script fetches real government data from Congress.gov and Federal Register APIs
and populates the database with current bills and executive orders.

Usage:
    python ingest_data.py --help
    python ingest_data.py --test-apis      # Test API connectivity
    python ingest_data.py --recent         # Fetch recent data (last 7 days)
    python ingest_data.py --full           # Full ingestion (last 30 days)
    python ingest_data.py --backfill       # Historical backfill (last 365 days)
"""

import asyncio
import argparse
import sys
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import our services
from app.services.data_ingestion import DataIngestionService
from app.services.congress_api import test_congress_api
from app.services.federal_register_api import test_federal_register_api
from app.core.config import settings


async def test_api_connectivity():
    """Test connectivity to government APIs"""
    print("🔍 Testing Government API Connectivity")
    print("=" * 50)
    
    # Test Congress.gov API
    if settings.CONGRESS_API_KEY:
        print("\n📊 Testing Congress.gov API...")
        await test_congress_api()
    else:
        print("\n❌ Congress.gov API key not configured")
        print("   Set CONGRESS_API_KEY in your .env file")
        print("   Get your key at: https://api.congress.gov/sign-up/")
    
    # Test Federal Register API (no key required)
    print("\n📋 Testing Federal Register API...")
    await test_federal_register_api()
    
    print("\n✅ API connectivity tests complete!")


async def ingest_recent_data():
    """Ingest recent government data (last 7 days)"""
    print("🔄 Ingesting Recent Government Data (Last 7 Days)")
    print("=" * 55)
    
    ingestion_service = DataIngestionService()
    
    try:
        results = await ingestion_service.run_full_ingestion(
            congress_session=118,
            days_back=7
        )
        
        print("\n✅ Recent data ingestion complete!")
        print_ingestion_results(results)
        
    except Exception as e:
        print(f"\n❌ Recent data ingestion failed: {str(e)}")
        sys.exit(1)


async def ingest_full_data():
    """Ingest comprehensive government data (last 30 days)"""
    print("🔄 Ingesting Full Government Data (Last 30 Days)")
    print("=" * 55)
    
    ingestion_service = DataIngestionService()
    
    try:
        results = await ingestion_service.run_full_ingestion(
            congress_session=118,
            days_back=30
        )
        
        print("\n✅ Full data ingestion complete!")
        print_ingestion_results(results)
        
    except Exception as e:
        print(f"\n❌ Full data ingestion failed: {str(e)}")
        sys.exit(1)


async def backfill_historical_data():
    """Backfill historical government data (last 365 days)"""
    print("🔄 Backfilling Historical Government Data (Last 365 Days)")
    print("=" * 65)
    print("⚠️  This may take 10-30 minutes depending on API rate limits...")
    
    ingestion_service = DataIngestionService()
    
    try:
        # Backfill in chunks to respect rate limits
        all_results = {"bills": {"processed": 0, "new": 0, "updated": 0, "errors": 0},
                      "executive_orders": {"processed": 0, "new": 0, "updated": 0, "errors": 0}}
        
        # Congress sessions to backfill (118th Congress: 2023-2024, 117th: 2021-2022)
        sessions = [118, 117]
        
        for session in sessions:
            print(f"\n📊 Processing Congress Session {session}...")
            
            # Process in 90-day chunks to manage API rate limits
            for chunk in range(0, 365, 90):
                days_back = min(90, 365 - chunk)
                print(f"   Processing days {chunk} to {chunk + days_back}...")
                
                chunk_results = await ingestion_service.run_full_ingestion(
                    congress_session=session,
                    days_back=days_back
                )
                
                # Accumulate results
                for source in ["bills", "executive_orders"]:
                    for metric in ["processed", "new", "updated", "errors"]:
                        all_results[source][metric] += chunk_results.get(source, {}).get(metric, 0)
                
                # Rate limiting pause
                print("   Pausing 30 seconds for API rate limits...")
                await asyncio.sleep(30)
        
        # Calculate totals
        all_results["totals"] = {
            "processed": sum(r.get("processed", 0) for r in all_results.values() if isinstance(r, dict)),
            "new": sum(r.get("new", 0) for r in all_results.values() if isinstance(r, dict)),
            "updated": sum(r.get("updated", 0) for r in all_results.values() if isinstance(r, dict)),
            "errors": sum(r.get("errors", 0) for r in all_results.values() if isinstance(r, dict))
        }
        
        print("\n✅ Historical backfill complete!")
        print_ingestion_results(all_results)
        
    except Exception as e:
        print(f"\n❌ Historical backfill failed: {str(e)}")
        sys.exit(1)


def print_ingestion_results(results: dict):
    """Pretty print ingestion results"""
    print("\n📊 Ingestion Summary:")
    print("-" * 30)
    
    for source, stats in results.items():
        if isinstance(stats, dict) and "processed" in stats:
            print(f"{source.replace('_', ' ').title()}:")
            print(f"  • Processed: {stats.get('processed', 0):,}")
            print(f"  • New: {stats.get('new', 0):,}")
            print(f"  • Updated: {stats.get('updated', 0):,}")
            if stats.get('errors', 0) > 0:
                print(f"  • Errors: {stats.get('errors', 0):,}")
    
    print("\n🎯 Next Steps:")
    print("  1. Start the backend: uvicorn main:app --reload")
    print("  2. Start the frontend: npm run dev")
    print("  3. Visit http://localhost:3000 to search real government data!")


def setup_argument_parser():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(
        description="GovernmentGPT Data Ingestion CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ingest_data.py --test-apis     # Test API connectivity
  python ingest_data.py --recent        # Quick update (last 7 days)
  python ingest_data.py --full          # Standard ingestion (last 30 days)  
  python ingest_data.py --backfill      # Historical data (last 365 days)

API Keys Required:
  - Congress.gov: Set CONGRESS_API_KEY in .env file
    Get your key: https://api.congress.gov/sign-up/
  - Federal Register: No API key required

Database:
  - Ensure your database is running and configured in .env
  - Run 'alembic upgrade head' before first ingestion
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--test-apis",
        action="store_true",
        help="Test connectivity to government APIs"
    )
    group.add_argument(
        "--recent", 
        action="store_true",
        help="Ingest recent data (last 7 days) - Quick update"
    )
    group.add_argument(
        "--full",
        action="store_true", 
        help="Ingest comprehensive data (last 30 days) - Standard operation"
    )
    group.add_argument(
        "--backfill",
        action="store_true",
        help="Backfill historical data (last 365 days) - Initial setup"
    )
    
    return parser


async def main():
    """Main CLI entry point"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    print(f"🏛️ GovernmentGPT Data Ingestion CLI")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        if args.test_apis:
            await test_api_connectivity()
        elif args.recent:
            await ingest_recent_data()
        elif args.full:
            await ingest_full_data()
        elif args.backfill:
            await backfill_historical_data()
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())