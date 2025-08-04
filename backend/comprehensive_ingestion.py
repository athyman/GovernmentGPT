#!/usr/bin/env python3
"""
Comprehensive data ingestion to pull all bills and EOs from beginning of 2024/2025
Ensures we capture major legislation that might be missed by basic ingestion
"""
import asyncio
import httpx
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, update, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine
from minimal_init import Document

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./governmentgpt_local.db"
engine = create_async_engine(DATABASE_URL, echo=False, future=True, poolclass=StaticPool, connect_args={"check_same_thread": False})
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class ComprehensiveDataIngestion:
    def __init__(self):
        self.congress_api_key = "jiiYz2O0zWf5j9AnupTVZdeKA0ISr1joKxhN0RBB"
        self.session = None
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=30)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_comprehensive_bill_list(self, congress: int = 119) -> List[Dict]:
        """Get comprehensive list of all bills from Congress API"""
        all_bills = []
        
        # Get all bill types
        bill_types = ["hr", "s", "hjres", "sjres", "hconres", "sconres", "hres", "sres"]
        
        for bill_type in bill_types:
            print(f"Fetching {bill_type.upper()} bills from {congress}th Congress...")
            
            offset = 0
            limit = 250  # Max per request
            
            while True:
                try:
                    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}"
                    params = {
                        "api_key": self.congress_api_key,
                        "offset": offset,
                        "limit": limit,
                        "sort": "introducedDate+desc"
                    }
                    
                    response = await self.session.get(url, params=params)
                    
                    if response.status_code != 200:
                        print(f"  Error {response.status_code} for {bill_type} at offset {offset}")
                        break
                    
                    data = response.json()
                    bills = data.get("bills", [])
                    
                    if not bills:
                        break
                    
                    print(f"  Retrieved {len(bills)} {bill_type.upper()} bills (offset {offset})")
                    all_bills.extend(bills)
                    
                    # Check if we have more
                    pagination = data.get("pagination", {})
                    if offset + limit >= pagination.get("count", 0):
                        break
                    
                    offset += limit
                    
                    # Brief pause to respect rate limits
                    await asyncio.sleep(0.2)
                    
                except Exception as e:
                    print(f"  Error fetching {bill_type} bills at offset {offset}: {str(e)}")
                    break
        
        print(f"Total bills retrieved: {len(all_bills)}")
        return all_bills
    
    async def get_executive_orders(self, start_date: str = "2024-01-01") -> List[Dict]:
        """Get executive orders from Federal Register API"""
        all_orders = []
        
        try:
            # Federal Register API for executive orders
            url = "https://www.federalregister.gov/api/v1/documents"
            params = {
                "conditions[type]": "PRESDOCU",
                "conditions[publication_date][gte]": start_date,
                "per_page": 1000,
                "order": "newest"
            }
            
            response = await self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                for doc in results:
                    if any(keyword in doc.get("title", "").lower() for keyword in ["executive order", "presidential"]):
                        all_orders.append({
                            "document_number": doc.get("document_number"),
                            "title": doc.get("title"),
                            "publication_date": doc.get("publication_date"),
                            "html_url": doc.get("html_url"),
                            "pdf_url": doc.get("pdf_url"),
                            "type": "executive_order",
                            "abstract": doc.get("abstract", ""),
                            "agencies": doc.get("agencies", [])
                        })
                
                print(f"Retrieved {len(all_orders)} executive orders")
            
        except Exception as e:
            print(f"Error fetching executive orders: {str(e)}")
        
        return all_orders
    
    async def search_for_specific_bills(self, search_terms: List[str]) -> List[Dict]:
        """Search for specific bills that might be missing"""
        found_bills = []
        
        for term in search_terms:
            print(f"Searching for: {term}")
            
            try:
                # Search Congress.gov API
                url = "https://api.congress.gov/v3/bill"
                params = {
                    "api_key": self.congress_api_key,
                    "q": term,
                    "limit": 50,
                    "sort": "introducedDate+desc"
                }
                
                response = await self.session.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    bills = data.get("bills", [])
                    
                    for bill in bills:
                        if any(word in bill.get("title", "").lower() for word in term.lower().split()):
                            found_bills.append(bill)
                            print(f"  Found: {bill.get('title')}")
                
                await asyncio.sleep(0.3)
                
            except Exception as e:
                print(f"  Error searching for '{term}': {str(e)}")
        
        return found_bills
    
    async def get_bill_details(self, congress: int, bill_type: str, bill_number: str) -> Optional[Dict]:
        """Get detailed information for a specific bill"""
        try:
            url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{bill_number}"
            params = {"api_key": self.congress_api_key}
            
            response = await self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("bill", {})
            
        except Exception as e:
            print(f"Error getting bill details for {bill_type}-{bill_number}: {str(e)}")
        
        return None
    
    async def process_and_store_bills(self, bills: List[Dict], db: AsyncSession):
        """Process and store bills in database"""
        for i, bill in enumerate(bills, 1):
            print(f"Processing bill {i}/{len(bills)}: {bill.get('number', 'Unknown')}")
            
            try:
                # Extract basic information
                bill_type = bill.get("type", "").lower()
                bill_number = bill.get("number", "")
                congress = bill.get("congress", 119)
                
                if not bill_type or not bill_number:
                    print(f"  Skipping bill with missing type or number")
                    continue
                
                identifier = f"{bill_type.upper()}-{bill_number}-{congress}"
                
                # Check if already exists
                existing = await db.execute(
                    select(Document).where(Document.identifier == identifier)
                )
                if existing.scalar_one_or_none():
                    print(f"  Already exists: {identifier}")
                    continue
                
                # Get detailed information
                detail = await self.get_bill_details(congress, bill_type, bill_number)
                
                if not detail:
                    print(f"  Could not get details for {identifier}")
                    continue
                
                # Extract sponsor information
                sponsors = detail.get("sponsors", [])
                sponsor_data = None
                if sponsors:
                    sponsor = sponsors[0]
                    sponsor_data = {
                        "bioguide_id": sponsor.get("bioguideId"),
                        "full_name": sponsor.get("fullName"),
                        "first_name": sponsor.get("firstName"),
                        "last_name": sponsor.get("lastName"),
                        "party": sponsor.get("party"),
                        "state": sponsor.get("state"),
                        "chamber": "house" if bill_type.startswith("h") else "senate"
                    }
                
                # Create comprehensive summary
                title = detail.get("title", "")
                summary_text = ""
                
                # Try to get CRS summary
                summaries = detail.get("summaries", {}).get("items", [])
                if summaries:
                    summary_text = summaries[0].get("text", "")[:2000]
                
                # Get latest action
                latest_action = detail.get("latestAction", {})
                latest_action_text = latest_action.get("text", "")
                latest_action_date = latest_action.get("actionDate")
                
                # Build comprehensive text content
                full_text_parts = [
                    f"TITLE: {title}",
                    f"BILL: {identifier}",
                    f"CONGRESS: {congress}th Congress"
                ]
                
                if sponsor_data:
                    full_text_parts.append(f"SPONSOR: {sponsor_data['full_name']} ({sponsor_data['party']}-{sponsor_data['state']})")
                
                if summary_text:
                    # Clean HTML from summary
                    clean_summary = re.sub(r'<[^>]+>', '', summary_text)
                    full_text_parts.append(f"SUMMARY: {clean_summary}")
                
                if latest_action_text:
                    full_text_parts.append(f"LATEST ACTION: {latest_action_text}")
                
                # Add subjects and policy areas
                policy_area = detail.get("policyArea", {}).get("name")
                if policy_area:
                    full_text_parts.append(f"POLICY AREA: {policy_area}")
                
                subjects = detail.get("subjects", {}).get("items", [])
                if subjects:
                    subject_names = [s.get("name", "") for s in subjects[:5]]
                    full_text_parts.append(f"SUBJECTS: {', '.join(subject_names)}")
                
                # Generate web URL
                web_url = f"https://www.congress.gov/bill/{congress}th-congress/"
                if bill_type == "hr":
                    web_url += f"house-bill/{bill_number}"
                elif bill_type == "s":
                    web_url += f"senate-bill/{bill_number}"
                elif bill_type == "hjres":
                    web_url += f"house-joint-resolution/{bill_number}"
                elif bill_type == "sjres":
                    web_url += f"senate-joint-resolution/{bill_number}"
                else:
                    web_url += f"{bill_type}/{bill_number}"
                
                # Create document
                document = Document(
                    document_type="bill",
                    identifier=identifier,
                    title=title,
                    summary=clean_summary[:1000] if summary_text else None,
                    full_text="\n\n".join(full_text_parts),
                    status=detail.get("latestAction", {}).get("text", "").split('.')[0] if latest_action_text else None,
                    introduced_date=detail.get("introducedDate"),
                    last_action_date=latest_action_date,
                    sponsor=sponsor_data,
                    doc_metadata={
                        "congress": congress,
                        "type": bill_type,
                        "number": bill_number,
                        "web_url": web_url,
                        "committees": detail.get("committees", {}),
                        "cosponsors_count": detail.get("cosponsors", {}).get("count", 0),
                        "text_fetched": True
                    }
                )
                
                db.add(document)
                await db.commit()
                
                print(f"  ✅ Stored: {identifier}")
                
                # Brief pause to respect API limits
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"  ❌ Error processing bill {i}: {str(e)}")
                await db.rollback()
                continue
    
    async def process_and_store_executive_orders(self, orders: List[Dict], db: AsyncSession):
        """Process and store executive orders in database"""
        for i, order in enumerate(orders, 1):
            print(f"Processing EO {i}/{len(orders)}: {order.get('document_number', 'Unknown')}")
            
            try:
                doc_number = order.get("document_number", "")
                if not doc_number:
                    continue
                
                identifier = f"EO-{doc_number}"
                
                # Check if already exists
                existing = await db.execute(
                    select(Document).where(Document.identifier == identifier)
                )
                if existing.scalar_one_or_none():
                    print(f"  Already exists: {identifier}")
                    continue
                
                title = order.get("title", "")
                abstract = order.get("abstract", "")
                
                # Build comprehensive text
                full_text_parts = [
                    f"TITLE: {title}",
                    f"DOCUMENT NUMBER: {doc_number}",
                    f"TYPE: Executive Order"
                ]
                
                if abstract:
                    full_text_parts.append(f"ABSTRACT: {abstract}")
                
                agencies = order.get("agencies", [])
                if agencies:
                    agency_names = [a.get("name", "") for a in agencies]
                    full_text_parts.append(f"AGENCIES: {', '.join(agency_names)}")
                
                document = Document(
                    document_type="executive_order",
                    identifier=identifier,
                    title=title,
                    summary=abstract[:1000] if abstract else None,
                    full_text="\n\n".join(full_text_parts),
                    status="published",
                    introduced_date=order.get("publication_date"),
                    last_action_date=order.get("publication_date"),
                    doc_metadata={
                        "document_number": doc_number,
                        "web_url": order.get("html_url"),
                        "pdf_url": order.get("pdf_url"),
                        "agencies": agencies,
                        "publication_date": order.get("publication_date")
                    }
                )
                
                db.add(document)
                await db.commit()
                
                print(f"  ✅ Stored: {identifier}")
                
            except Exception as e:
                print(f"  ❌ Error processing EO {i}: {str(e)}")
                await db.rollback()
                continue

async def run_comprehensive_ingestion():
    """Main function to run comprehensive data ingestion"""
    print("🚀 Starting comprehensive data ingestion...")
    
    async with ComprehensiveDataIngestion() as ingestion:
        async with AsyncSessionLocal() as db:
            # 1. Get all bills from 119th Congress (current)
            print("\n📋 Fetching all bills from 119th Congress...")
            all_bills = await ingestion.get_comprehensive_bill_list(congress=119)
            
            # 2. Search for specific major legislation
            print("\n🔍 Searching for specific major legislation...")
            major_terms = [
                "one big beautiful bill",
                "infrastructure investment",
                "chips and science",
                "inflation reduction",
                "bipartisan infrastructure",
                "build back better",
                "american rescue plan",
                "cares act",
                "national defense authorization"
            ]
            
            specific_bills = await ingestion.search_for_specific_bills(major_terms)
            all_bills.extend(specific_bills)
            
            # Remove duplicates
            seen_identifiers = set()
            unique_bills = []
            for bill in all_bills:
                bill_type = bill.get("type", "").lower()
                bill_number = bill.get("number", "")
                congress = bill.get("congress", 119)
                identifier = f"{bill_type}-{bill_number}-{congress}"
                
                if identifier not in seen_identifiers:
                    seen_identifiers.add(identifier)
                    unique_bills.append(bill)
            
            print(f"📊 Processing {len(unique_bills)} unique bills...")
            
            # 3. Process and store bills
            await ingestion.process_and_store_bills(unique_bills, db)
            
            # 4. Get executive orders
            print("\n📋 Fetching executive orders from 2024...")
            executive_orders = await ingestion.get_executive_orders(start_date="2024-01-01")
            
            # 5. Process and store executive orders
            await ingestion.process_and_store_executive_orders(executive_orders, db)
            
            # 6. Update search statistics
            print("\n📈 Updating database statistics...")
            await db.execute(text("ANALYZE"))
            await db.commit()
    
    print("\n✅ Comprehensive data ingestion complete!")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_ingestion())