#!/usr/bin/env python3
"""
Simple data ingestion for testing - fetches recent bills and executive orders
"""
import asyncio
import httpx
from datetime import datetime, date, timedelta
import json
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from sqlalchemy import select
from minimal_init import Document, Legislator, Base

DATABASE_URL = "sqlite+aiosqlite:///./governmentgpt_local.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class SimpleIngestion:
    def __init__(self):
        self.congress_api_key = "jiiYz2O0zWf5j9AnupTVZdeKA0ISr1joKxhN0RBB"
        
    async def fetch_recent_bills(self, limit=200):
        """Fetch recent bills from Congress.gov"""
        print(f"🏛️ Fetching {limit} recent bills from Congress.gov...")
        
        url = "https://api.congress.gov/v3/bill"
        params = {
            "api_key": self.congress_api_key,
            "limit": limit,
            "sort": "updateDate+desc",
            "format": "json"
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            bills = data.get("bills", [])
            print(f"   Retrieved {len(bills)} bills")
            
            async with AsyncSessionLocal() as db:
                new_count = 0
                for bill in bills:
                    try:
                        # Extract basic bill info
                        bill_type = bill.get("type", "")
                        bill_number = bill.get("number", "")
                        congress = bill.get("congress", 118)
                        
                        identifier = f"{bill_type}-{bill_number}-{congress}"
                        
                        # Check if exists
                        existing = await db.execute(
                            select(Document).where(Document.identifier == identifier)
                        )
                        if existing.scalar_one_or_none():
                            continue
                            
                        # Create document
                        doc = Document(
                            identifier=identifier,
                            title=bill.get("title", "")[:500],  # Truncate long titles
                            summary=bill.get("summary", {}).get("text", "")[:1000] if bill.get("summary") else "",
                            full_text=bill.get("title", ""),  # Use title as full text for now
                            document_type="bill",
                            status=bill.get("latestAction", {}).get("actionDate", "introduced"),
                            introduced_date=self._parse_date(bill.get("introducedDate")),
                            last_action_date=self._parse_date(bill.get("latestAction", {}).get("actionDate")),
                            doc_metadata={
                                "congress": congress,
                                "type": bill_type,
                                "number": bill_number,
                                "url": bill.get("url"),
                                "latest_action": bill.get("latestAction", {}).get("text", "")
                            }
                        )
                        
                        db.add(doc)
                        new_count += 1
                        
                    except Exception as e:
                        print(f"   Error processing bill {bill.get('number', 'unknown')}: {e}")
                        continue
                
                await db.commit()
                print(f"   ✅ Added {new_count} new bills to database")
                return new_count
    
    async def fetch_executive_orders(self, days_back=180):
        """Fetch executive orders from Federal Register"""
        print(f"📋 Fetching executive orders from last {days_back} days...")
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        url = "https://www.federalregister.gov/api/v1/documents"
        params = {
            "conditions[type][]": ["EXECORD", "PRESDOCU"],
            "conditions[publication_date][gte]": start_date.strftime("%Y-%m-%d"),
            "conditions[publication_date][lte]": end_date.strftime("%Y-%m-%d"),
            "per_page": 100,
            "order": "newest"
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            documents = data.get("results", [])
            print(f"   Retrieved {len(documents)} documents")
            
            async with AsyncSessionLocal() as db:
                new_count = 0
                for doc in documents:
                    try:
                        doc_number = doc.get("document_number", "")
                        identifier = f"FR-{doc_number}"
                        
                        # Check if exists
                        existing = await db.execute(
                            select(Document).where(Document.identifier == identifier)
                        )
                        if existing.scalar_one_or_none():
                            continue
                        
                        # Determine document type
                        doc_type = "executive_order" if doc.get("type") == "EXECORD" else "presidential_document"
                        
                        document = Document(
                            identifier=identifier,
                            title=doc.get("title", "")[:500],
                            summary=doc.get("abstract", "")[:1000] if doc.get("abstract") else "",
                            full_text=doc.get("title", ""),
                            document_type=doc_type,
                            status="signed",
                            introduced_date=self._parse_date(doc.get("publication_date")),
                            last_action_date=self._parse_date(doc.get("publication_date")),
                            doc_metadata={
                                "document_number": doc_number,
                                "publication_date": doc.get("publication_date"),
                                "agencies": [agency.get("name") for agency in doc.get("agencies", [])],
                                "url": doc.get("html_url"),
                                "pdf_url": doc.get("pdf_url")
                            }
                        )
                        
                        db.add(document)
                        new_count += 1
                        
                    except Exception as e:
                        print(f"   Error processing document {doc.get('document_number', 'unknown')}: {e}")
                        continue
                
                await db.commit()
                print(f"   ✅ Added {new_count} new documents to database")
                return new_count
    
    def _parse_date(self, date_str):
        """Parse date string to date object"""
        if not date_str:
            return None
        try:
            if "T" in date_str:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
            else:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return None

async def main():
    print("🚀 Starting simple data ingestion for 6 months of data...")
    
    ingestion = SimpleIngestion()
    
    # Fetch bills
    bills_added = await ingestion.fetch_recent_bills(limit=500)  # Last ~6 months of bills
    
    # Fetch executive orders  
    eos_added = await ingestion.fetch_executive_orders(days_back=180)  # Last 6 months
    
    # Check total documents
    async with AsyncSessionLocal() as db:
        total_docs = await db.execute(select(Document))
        total_count = len(total_docs.scalars().all())
    
    print("\n🎉 Data Ingestion Complete!")
    print(f"   Bills added: {bills_added}")
    print(f"   Executive orders added: {eos_added}")
    print(f"   Total documents in database: {total_count}")
    print("\n🌐 Ready to test search at: http://localhost:3000")

if __name__ == "__main__":
    asyncio.run(main())