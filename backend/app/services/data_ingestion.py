"""
Main data ingestion service for GovernmentGPT.
Coordinates fetching data from government APIs and storing in database.
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.document import Document
from app.models.legislator import Legislator
from app.services.congress_api import CongressAPI, CongressDataProcessor
from app.services.federal_register_api import FederalRegisterAPI, FederalRegisterProcessor
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class DataIngestionService:
    """
    Main service for ingesting government data from multiple sources.
    Handles deduplication, validation, and database storage.
    """
    
    def __init__(self):
        self.congress_processor = CongressDataProcessor()
        self.fr_processor = FederalRegisterProcessor()
    
    async def ingest_recent_bills(self, 
                                congress_session: int = 118,
                                days_back: int = 30,
                                limit: int = 100) -> Dict[str, int]:
        """
        Ingest recent bills from Congress.gov
        
        Returns:
            Dict with counts of processed, new, and updated documents
        """
        stats = {"processed": 0, "new": 0, "updated": 0, "errors": 0}
        
        async with CongressAPI() as congress_api:
            async with AsyncSessionLocal() as db:
                try:
                    # Fetch recent bills
                    logger.info(f"Fetching recent bills from Congress {congress_session}, last {days_back} days")
                    
                    bills_response = await congress_api.get_recent_bills(
                        congress=congress_session,
                        limit=limit
                    )
                    
                    bills = bills_response.get("bills", [])
                    logger.info(f"Retrieved {len(bills)} bills from Congress.gov")
                    
                    for bill in bills:
                        try:
                            stats["processed"] += 1
                            
                            # Get detailed bill information
                            bill_details = await congress_api.get_bill_details(
                                congress=bill["congress"],
                                bill_type=bill["type"],
                                bill_number=bill["number"]
                            )
                            
                            # Process bill data
                            bill_data = self.congress_processor.extract_bill_data(bill_details)
                            
                            # Check if bill already exists
                            existing_bill = await db.execute(
                                select(Document).where(
                                    Document.identifier == bill_data["identifier"]
                                )
                            )
                            existing_bill = existing_bill.scalar_one_or_none()
                            
                            if existing_bill:
                                # Update existing bill
                                for key, value in bill_data.items():
                                    if key not in ["id", "created_at"] and value is not None:
                                        setattr(existing_bill, key, value)
                                existing_bill.updated_at = datetime.utcnow()
                                stats["updated"] += 1
                                logger.debug(f"Updated bill: {bill_data['identifier']}")
                            else:
                                # Create new bill
                                # First, handle sponsor if present
                                sponsor_id = None
                                if sponsor_info := bill_data["metadata"].get("sponsor", {}).get("bioguide_id"):
                                    sponsor_id = await self._ensure_legislator_exists(db, sponsor_info, congress_api)
                                
                                new_bill = Document(
                                    identifier=bill_data["identifier"],
                                    title=bill_data["title"],
                                    summary=bill_data["summary"],
                                    full_text=bill_data.get("full_text", bill_data["summary"]),
                                    document_type=bill_data["document_type"],
                                    status=bill_data.get("status", "introduced"),
                                    introduced_date=bill_data.get("introduced_date"),
                                    last_action_date=bill_data.get("last_action_date"),
                                    sponsor_id=sponsor_id,
                                    metadata=bill_data["metadata"]
                                )
                                
                                db.add(new_bill)
                                stats["new"] += 1
                                logger.debug(f"Added new bill: {bill_data['identifier']}")
                            
                            # Commit every 10 bills to avoid large transactions
                            if stats["processed"] % 10 == 0:
                                await db.commit()
                                logger.info(f"Processed {stats['processed']} bills so far...")
                                
                        except Exception as e:
                            stats["errors"] += 1
                            logger.error(f"Error processing bill {bill.get('number', 'unknown')}: {str(e)}")
                            continue
                    
                    # Final commit
                    await db.commit()
                    logger.info(f"Bill ingestion complete: {stats}")
                    
                except Exception as e:
                    logger.error(f"Error during bill ingestion: {str(e)}")
                    await db.rollback()
                    raise
        
        return stats
    
    async def ingest_executive_orders(self, 
                                    days_back: int = 90,
                                    limit: int = 50) -> Dict[str, int]:
        """
        Ingest recent executive orders from Federal Register
        
        Returns:
            Dict with counts of processed, new, and updated documents
        """
        stats = {"processed": 0, "new": 0, "updated": 0, "errors": 0}
        
        async with FederalRegisterAPI() as fr_api:
            async with AsyncSessionLocal() as db:
                try:
                    # Calculate date range
                    end_date = date.today()
                    start_date = end_date - timedelta(days=days_back)
                    
                    logger.info(f"Fetching executive orders from {start_date} to {end_date}")
                    
                    # Fetch executive orders
                    eo_response = await fr_api.get_executive_orders(
                        start_date=start_date,
                        end_date=end_date,
                        per_page=limit
                    )
                    
                    documents = eo_response.get("results", [])
                    logger.info(f"Retrieved {len(documents)} executive orders from Federal Register")
                    
                    for doc in documents:
                        try:
                            stats["processed"] += 1
                            
                            # Get detailed document information
                            doc_number = doc.get("document_number")
                            if doc_number:
                                doc_details = await fr_api.get_document_details(doc_number)
                            else:
                                doc_details = doc
                            
                            # Process document data
                            doc_data = self.fr_processor.extract_document_data(doc_details)
                            if not doc_data:
                                continue
                            
                            # Check if document already exists
                            existing_doc = await db.execute(
                                select(Document).where(
                                    Document.identifier == doc_data["identifier"]
                                )
                            )
                            existing_doc = existing_doc.scalar_one_or_none()
                            
                            if existing_doc:
                                # Update existing document
                                for key, value in doc_data.items():
                                    if key not in ["id", "created_at"] and value is not None:
                                        setattr(existing_doc, key, value)
                                existing_doc.updated_at = datetime.utcnow()
                                stats["updated"] += 1
                                logger.debug(f"Updated document: {doc_data['identifier']}")
                            else:
                                # Create new document
                                new_doc = Document(
                                    identifier=doc_data["identifier"],
                                    title=doc_data["title"],
                                    summary=doc_data["summary"],
                                    full_text=doc_data["full_text"],
                                    document_type=doc_data["document_type"],
                                    status=doc_data["status"],
                                    introduced_date=doc_data.get("introduced_date"),
                                    last_action_date=doc_data.get("last_action_date"),
                                    metadata=doc_data["metadata"]
                                )
                                
                                db.add(new_doc)
                                stats["new"] += 1
                                logger.debug(f"Added new document: {doc_data['identifier']}")
                            
                            # Commit every 10 documents
                            if stats["processed"] % 10 == 0:
                                await db.commit()
                                logger.info(f"Processed {stats['processed']} executive orders so far...")
                                
                        except Exception as e:
                            stats["errors"] += 1
                            logger.error(f"Error processing document {doc.get('document_number', 'unknown')}: {str(e)}")
                            continue
                    
                    # Final commit
                    await db.commit()
                    logger.info(f"Executive order ingestion complete: {stats}")
                    
                except Exception as e:
                    logger.error(f"Error during executive order ingestion: {str(e)}")
                    await db.rollback()
                    raise
        
        return stats
    
    async def _ensure_legislator_exists(self, 
                                     db: AsyncSession, 
                                     bioguide_id: str,
                                     congress_api: CongressAPI) -> Optional[str]:
        """Ensure legislator exists in database, create if not found"""
        try:
            # Check if legislator exists
            existing = await db.execute(
                select(Legislator).where(Legislator.bioguide_id == bioguide_id)
            )
            existing_legislator = existing.scalar_one_or_none()
            
            if existing_legislator:
                return existing_legislator.id
            
            # Fetch legislator details from Congress.gov
            member_details = await congress_api.get_member_details(bioguide_id)
            legislator_data = self.congress_processor.extract_legislator_data(member_details)
            
            # Create new legislator
            new_legislator = Legislator(
                bioguide_id=legislator_data["bioguide_id"],
                first_name=legislator_data["first_name"],
                last_name=legislator_data["last_name"],
                full_name=legislator_data["full_name"],
                party=legislator_data["party"],
                state=legislator_data["state"],
                district=legislator_data.get("district"),
                chamber=legislator_data["chamber"],
                active=legislator_data["active"]
            )
            
            db.add(new_legislator)
            await db.flush()  # Get the ID
            
            logger.debug(f"Added new legislator: {legislator_data['full_name']}")
            return new_legislator.id
            
        except Exception as e:
            logger.error(f"Error ensuring legislator exists for {bioguide_id}: {str(e)}")
            return None
    
    async def run_full_ingestion(self, 
                               congress_session: int = 118,
                               days_back: int = 30) -> Dict[str, Dict]:
        """
        Run complete data ingestion from all sources
        
        Returns:
            Dict with statistics from each data source
        """
        logger.info("Starting full data ingestion...")
        
        results = {}
        
        try:
            # Ingest bills
            logger.info("Phase 1: Ingesting congressional bills...")
            results["bills"] = await self.ingest_recent_bills(
                congress_session=congress_session,
                days_back=days_back,
                limit=100
            )
            
            # Ingest executive orders
            logger.info("Phase 2: Ingesting executive orders...")
            results["executive_orders"] = await self.ingest_executive_orders(
                days_back=days_back,
                limit=50
            )
            
            # Calculate totals
            results["totals"] = {
                "processed": sum(r.get("processed", 0) for r in results.values()),
                "new": sum(r.get("new", 0) for r in results.values()),
                "updated": sum(r.get("updated", 0) for r in results.values()),
                "errors": sum(r.get("errors", 0) for r in results.values())
            }
            
            logger.info(f"Full ingestion complete: {results['totals']}")
            
        except Exception as e:
            logger.error(f"Error during full ingestion: {str(e)}")
            raise
        
        return results


# CLI functions for manual testing
async def test_ingestion():
    """Test the data ingestion process"""
    ingestion_service = DataIngestionService()
    
    try:
        # Test with small batches
        print("🏛️ Testing government data ingestion...")
        
        results = await ingestion_service.run_full_ingestion(
            congress_session=118,
            days_back=7  # Just last week for testing
        )
        
        print("✅ Ingestion test results:")
        for source, stats in results.items():
            print(f"  {source}: {stats}")
            
    except Exception as e:
        print(f"❌ Ingestion test failed: {str(e)}")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_ingestion())