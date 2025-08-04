#!/usr/bin/env python3
"""
Comprehensive Government Data Ingestion Service
Fetches bills, executive orders, and other documents from official APIs
"""
import asyncio
import aiosqlite
import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from dataclasses import dataclass
import time
import uuid

from data_quality_service import DataQualityService
from embeddings_service import EmbeddingsService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IngestionStats:
    total_processed: int = 0
    total_inserted: int = 0
    total_updated: int = 0
    total_errors: int = 0
    total_duplicates: int = 0
    processing_time: float = 0.0

class GovernmentDataIngestion:
    """Comprehensive government data ingestion service"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.congress_api_key = api_key
        self.db_path = "./governmentgpt_local.db"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.data_quality = DataQualityService()
        self.embeddings_service = EmbeddingsService()
        
        # Rate limiting
        self.request_delay = 0.2  # 200ms between requests (5 requests/second)
        self.last_request_time = 0
        
        # Congress.gov API endpoints
        self.congress_base_url = "https://api.congress.gov/v3"
    
    async def ingest_comprehensive_data(self, start_date: str = "2024-01-01", end_date: Optional[str] = None) -> IngestionStats:
        """Ingest comprehensive government data from multiple sources"""
        
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"🚀 Starting comprehensive data ingestion from {start_date} to {end_date}")
        
        start_time = time.time()
        total_stats = IngestionStats()
        
        try:
            # 1. Ingest House Bills
            logger.info("📋 Ingesting House Bills...")
            house_stats = await self._ingest_congress_documents("bill", "house", start_date, end_date)
            total_stats.total_processed += house_stats.total_processed
            total_stats.total_inserted += house_stats.total_inserted
            total_stats.total_updated += house_stats.total_updated
            total_stats.total_errors += house_stats.total_errors
            
            # 2. Ingest Senate Bills
            logger.info("📋 Ingesting Senate Bills...")
            senate_stats = await self._ingest_congress_documents("bill", "senate", start_date, end_date)
            total_stats.total_processed += senate_stats.total_processed
            total_stats.total_inserted += senate_stats.total_inserted
            total_stats.total_updated += senate_stats.total_updated
            total_stats.total_errors += senate_stats.total_errors
            
            # 3. Ingest Executive Orders (sample data since no public API)
            logger.info("📋 Ingesting Executive Orders...")
            eo_stats = await self._ingest_sample_executive_orders(start_date, end_date)
            total_stats.total_processed += eo_stats.total_processed
            total_stats.total_inserted += eo_stats.total_inserted
            
            # 4. Generate embeddings for new documents
            logger.info("🔄 Generating embeddings for new documents...")
            await self.embeddings_service.generate_all_embeddings(batch_size=50)
            
            total_stats.processing_time = time.time() - start_time
            
            logger.info(f"✅ Data ingestion complete!")
            logger.info(f"📊 Final Stats: {total_stats.total_inserted} inserted, {total_stats.total_updated} updated, {total_stats.total_errors} errors")
            logger.info(f"⏱️  Total time: {total_stats.processing_time:.2f} seconds")
            
            return total_stats
            
        except Exception as e:
            logger.error(f"❌ Data ingestion failed: {e}")
            total_stats.total_errors += 1
            return total_stats
    
    async def _ingest_congress_documents(self, doc_type: str, chamber: str, start_date: str, end_date: str) -> IngestionStats:
        """Ingest documents from Congress.gov API"""
        
        stats = IngestionStats()
        
        try:
            # Get list of bills
            bills_url = f"{self.congress_base_url}/{doc_type}"
            params = {
                "format": "json",
                "limit": 250,  # Maximum allowed
                "fromDateTime": f"{start_date}T00:00:00Z",
                "toDateTime": f"{end_date}T23:59:59Z"
            }
            
            if self.congress_api_key:
                params["api_key"] = self.congress_api_key
            
            # Fetch bills list
            await self._rate_limit()
            response = await self.client.get(bills_url, params=params)
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to fetch {chamber} {doc_type}s: {response.status_code}")
                return stats
            
            data = response.json()
            bills = data.get(f"{doc_type}s", [])
            
            logger.info(f"📥 Found {len(bills)} {chamber} {doc_type}s to process")
            
            # Process each bill
            for i, bill_summary in enumerate(bills):
                try:
                    # Get detailed bill information
                    bill_url = bill_summary.get("url")
                    if not bill_url:
                        continue
                    
                    await self._rate_limit()
                    detail_response = await self.client.get(f"{bill_url}?format=json")
                    
                    if detail_response.status_code == 200:
                        bill_detail = detail_response.json()
                        bill_data = bill_detail.get("bill", {})
                        
                        # Convert to standard format
                        document = await self._convert_congress_bill_to_document(bill_data, chamber)
                        
                        if document:
                            # Validate and process
                            validation_result = await self.data_quality.validate_and_process_document(document)
                            
                            if validation_result.is_valid:
                                # Store in database
                                success = await self._store_document(validation_result.processed_document)
                                if success:
                                    stats.total_inserted += 1
                                else:
                                    stats.total_errors += 1
                            else:
                                logger.warning(f"⚠️  Validation failed for {document.get('identifier', 'unknown')}: {validation_result.errors}")
                                stats.total_errors += 1
                        
                        stats.total_processed += 1
                        
                        # Progress update
                        if (i + 1) % 50 == 0:
                            logger.info(f"📈 Progress: {i + 1}/{len(bills)} {chamber} {doc_type}s processed")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing bill {i}: {e}")
                    stats.total_errors += 1
                    continue
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest {chamber} {doc_type}s: {e}")
            stats.total_errors += 1
            return stats
    
    async def _convert_congress_bill_to_document(self, bill_data: Dict, chamber: str) -> Optional[Dict]:
        """Convert Congress.gov bill data to standard document format"""
        
        try:
            # Extract basic info
            number = bill_data.get("number", "")
            congress = bill_data.get("congress", "")
            title = bill_data.get("title", "")
            
            # Create identifier
            chamber_prefix = "HR" if chamber.lower() == "house" else "S"
            identifier = f"{chamber_prefix}-{number}"
            
            # Get dates
            introduced_date = None
            if bill_data.get("introducedDate"):
                introduced_date = bill_data["introducedDate"]
            
            last_action_date = introduced_date
            if bill_data.get("latestAction", {}).get("actionDate"):
                last_action_date = bill_data["latestAction"]["actionDate"]
            
            # Get sponsor info
            sponsor_data = None
            sponsors = bill_data.get("sponsors", [])
            if sponsors:
                sponsor = sponsors[0]  # Primary sponsor
                sponsor_data = {
                    "full_name": sponsor.get("fullName", ""),
                    "party": sponsor.get("party", ""),
                    "state": sponsor.get("state", ""),
                    "bioguide_id": sponsor.get("bioguideId", ""),
                    "district": sponsor.get("district", "")
                }
            
            # Get summary
            summary = ""
            if bill_data.get("summaries"):
                summaries = bill_data["summaries"]
                if summaries and len(summaries) > 0:
                    latest_summary = summaries[0]  # Most recent summary
                    summary = latest_summary.get("text", "")
            
            # Get full text (use title + summary for now, as full text requires additional API calls)
            full_text = f"{title}\n\n{summary}" if summary else title
            
            # Get status
            status = "introduced"
            if bill_data.get("latestAction", {}).get("text"):
                action_text = bill_data["latestAction"]["text"].lower()
                if "passed" in action_text:
                    if "house" in action_text:
                        status = "passed_house"
                    elif "senate" in action_text:
                        status = "passed_senate"
                elif "enacted" in action_text or "signed" in action_text:
                    status = "enacted"
                elif "vetoed" in action_text:
                    status = "vetoed"
            
            # Create metadata
            metadata = {
                "congress": congress,
                "chamber": chamber,
                "bill_type": bill_data.get("type", ""),
                "origin_chamber": bill_data.get("originChamber", ""),
                "policy_area": bill_data.get("policyArea", {}).get("name", ""),
                "subjects": [subject.get("name", "") for subject in bill_data.get("subjects", {}).get("legislativeSubjects", [])],
                "latest_action": bill_data.get("latestAction", {}),
                "sponsor": sponsor_data
            }
            
            return {
                "identifier": identifier,
                "title": title,
                "summary": summary,
                "full_text": full_text,
                "document_type": "bill",
                "status": status,
                "introduced_date": introduced_date,
                "last_action_date": last_action_date,
                "sponsor": sponsor_data,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Error converting bill data: {e}")
            return None
    
    async def _ingest_sample_executive_orders(self, start_date: str, end_date: str) -> IngestionStats:
        """Ingest sample executive orders (since no comprehensive public API exists)"""
        
        stats = IngestionStats()
        
        # Sample executive orders for demonstration
        sample_eos = [
            {
                "identifier": "EO-14117",
                "title": "Promoting Access to Voting",
                "summary": "This executive order directs federal agencies to expand access to voter registration and election information.",
                "full_text": "By the authority vested in me as President by the Constitution and the laws of the United States of America, it is hereby ordered that federal agencies shall take appropriate steps to promote access to voter registration and election information.",
                "document_type": "executive_order",
                "status": "active",
                "introduced_date": "2024-03-07",
                "last_action_date": "2024-03-07",
                "sponsor": {"full_name": "President of the United States"},
                "metadata": {
                    "executive_order_number": "14117",
                    "presidential_document_type": "Executive Order",
                    "subject_areas": ["Elections", "Voting Rights", "Federal Agencies"]
                }
            },
            {
                "identifier": "EO-14118",
                "title": "Strengthening Supply Chain Resilience",
                "summary": "This executive order establishes measures to strengthen critical supply chains and reduce vulnerabilities in key industries.",
                "full_text": "The United States faces significant vulnerabilities in its supply chains that threaten national security, economic stability, and public health. This order directs agencies to assess and strengthen supply chain resilience across critical sectors.",
                "document_type": "executive_order",
                "status": "active",
                "introduced_date": "2024-04-15",
                "last_action_date": "2024-04-15",
                "sponsor": {"full_name": "President of the United States"},
                "metadata": {
                    "executive_order_number": "14118",
                    "presidential_document_type": "Executive Order",
                    "subject_areas": ["Supply Chain", "National Security", "Economic Policy"]
                }
            },
            {
                "identifier": "EO-14119",
                "title": "Advancing Climate Resilience",
                "summary": "This executive order directs federal agencies to prioritize climate adaptation and resilience in planning and operations.",
                "full_text": "Climate change poses significant risks to the United States. Federal agencies must integrate climate resilience into their planning, operations, and decision-making processes to protect communities and infrastructure.",
                "document_type": "executive_order",
                "status": "active",
                "introduced_date": "2024-05-22",
                "last_action_date": "2024-05-22",
                "sponsor": {"full_name": "President of the United States"},
                "metadata": {
                    "executive_order_number": "14119",
                    "presidential_document_type": "Executive Order",
                    "subject_areas": ["Climate Change", "Environmental Policy", "Resilience"]
                }
            }
        ]
        
        for eo_data in sample_eos:
            try:
                # Check if EO date is within range
                eo_date = datetime.strptime(eo_data["introduced_date"], "%Y-%m-%d").date()
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_dt = datetime.strptime(end_date.split('T')[0], "%Y-%m-%d").date()
                
                if start_dt <= eo_date <= end_dt:
                    # Validate and process
                    validation_result = await self.data_quality.validate_and_process_document(eo_data)
                    
                    if validation_result.is_valid:
                        success = await self._store_document(validation_result.processed_document)
                        if success:
                            stats.total_inserted += 1
                        else:
                            stats.total_errors += 1
                    else:
                        logger.warning(f"⚠️  EO validation failed: {validation_result.errors}")
                        stats.total_errors += 1
                
                stats.total_processed += 1
                
            except Exception as e:
                logger.error(f"❌ Error processing EO: {e}")
                stats.total_errors += 1
        
        logger.info(f"📥 Processed {stats.total_processed} executive orders, inserted {stats.total_inserted}")
        return stats
    
    async def _store_document(self, document: Dict) -> bool:
        """Store document in database"""
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Check if document already exists
                cursor = await db.execute(
                    "SELECT id FROM documents WHERE identifier = ? AND document_type = ?",
                    (document["identifier"], document["document_type"])
                )
                
                existing = await cursor.fetchone()
                
                if existing:
                    # Update existing document
                    await db.execute("""
                        UPDATE documents SET
                            title = ?, summary = ?, full_text = ?, status = ?,
                            introduced_date = ?, last_action_date = ?, doc_metadata = ?,
                            updated_at = ?
                        WHERE id = ?
                    """, (
                        document["title"],
                        document["summary"],
                        document["full_text"],
                        document["status"],
                        document["introduced_date"],
                        document["last_action_date"],
                        json.dumps(document.get("metadata", {})),
                        datetime.now().isoformat(),
                        existing[0]
                    ))
                else:
                    # Insert new document
                    doc_id = str(uuid.uuid4())
                    await db.execute("""
                        INSERT INTO documents (
                            id, document_type, identifier, title, summary, full_text,
                            status, introduced_date, last_action_date, doc_metadata,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        doc_id,
                        document["document_type"],
                        document["identifier"],
                        document["title"],
                        document["summary"],
                        document["full_text"],
                        document["status"],
                        document["introduced_date"],
                        document["last_action_date"],
                        json.dumps(document.get("metadata", {})),
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                
                await db.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to store document {document.get('identifier', 'unknown')}: {e}")
            return False
    
    async def _rate_limit(self):
        """Implement rate limiting for API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    async def get_ingestion_stats(self) -> Dict:
        """Get current database statistics"""
        
        async with aiosqlite.connect(self.db_path) as db:
            stats = {}
            
            # Total documents
            cursor = await db.execute("SELECT COUNT(*) FROM documents")
            stats["total_documents"] = (await cursor.fetchone())[0]
            
            # Documents by type
            cursor = await db.execute("""
                SELECT document_type, COUNT(*) 
                FROM documents 
                GROUP BY document_type
            """)
            stats["by_type"] = dict(await cursor.fetchall())
            
            # Recent documents (last 7 days)
            cursor = await db.execute("""
                SELECT COUNT(*) FROM documents 
                WHERE created_at >= datetime('now', '-7 days')
            """)
            stats["recent_documents"] = (await cursor.fetchone())[0]
            
            # Latest document
            cursor = await db.execute("""
                SELECT identifier, title, created_at 
                FROM documents 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            latest = await cursor.fetchone()
            if latest:
                stats["latest_document"] = {
                    "identifier": latest[0],
                    "title": latest[1][:100] + "..." if len(latest[1]) > 100 else latest[1],
                    "created_at": latest[2]
                }
            
            return stats
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.client.aclose()

async def test_data_ingestion():
    """Test the data ingestion service"""
    
    ingestion = GovernmentDataIngestion()
    
    try:
        # Get current stats
        print("📊 Current database statistics:")
        stats = await ingestion.get_ingestion_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Run sample ingestion
        print("\n🚀 Running sample data ingestion...")
        result = await ingestion.ingest_comprehensive_data(
            start_date="2024-01-01",
            end_date="2024-08-03"
        )
        
        print(f"\n📋 Ingestion Results:")
        print(f"  Processed: {result.total_processed}")
        print(f"  Inserted: {result.total_inserted}")
        print(f"  Updated: {result.total_updated}")
        print(f"  Errors: {result.total_errors}")
        print(f"  Time: {result.processing_time:.2f}s")
        
        # Get updated stats
        print("\n📊 Updated database statistics:")
        new_stats = await ingestion.get_ingestion_stats()
        for key, value in new_stats.items():
            print(f"  {key}: {value}")
    
    finally:
        await ingestion.cleanup()

if __name__ == "__main__":
    asyncio.run(test_data_ingestion())