#!/usr/bin/env python3
"""
Enhanced document fetcher to get full bill text and proper URLs
"""
import asyncio
import httpx
from typing import Optional
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, update
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine
from minimal_init import Document

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./governmentgpt_local.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class DocumentEnhancer:
    def __init__(self):
        self.congress_api_key = "jiiYz2O0zWf5j9AnupTVZdeKA0ISr1joKxhN0RBB"
        
    async def enhance_document_text(self, document: Document) -> bool:
        """Enhance a document with full text and proper URLs"""
        try:
            # Extract congress info from metadata
            metadata = document.doc_metadata or {}
            congress = metadata.get("congress", 119)
            bill_type = metadata.get("type", "").lower()
            bill_number = metadata.get("number", "")
            
            if not bill_type or not bill_number:
                print(f"  ⚠️ Missing bill info for {document.identifier}")
                return False
            
            # Get bill text from Congress.gov
            full_text = await self._fetch_bill_text(congress, bill_type, bill_number)
            
            # Generate proper web URL
            web_url = self._generate_congress_web_url(congress, bill_type, bill_number)
            
            # Update metadata with web URL
            updated_metadata = metadata.copy()
            updated_metadata["web_url"] = web_url
            updated_metadata["text_fetched"] = True
            
            return full_text, updated_metadata
            
        except Exception as e:
            print(f"  ❌ Error enhancing {document.identifier}: {str(e)}")
            return False
            
    async def _fetch_bill_text(self, congress: int, bill_type: str, bill_number: str) -> str:
        """Fetch comprehensive bill information from Congress.gov API"""
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                # Get comprehensive bill information
                bill_url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{bill_number}"
                bill_response = await client.get(bill_url, params={"api_key": self.congress_api_key})
                
                if bill_response.status_code == 200:
                    bill_data = bill_response.json()
                    bill_info = bill_data.get("bill", {})
                    
                    # Build comprehensive text content
                    content_parts = []
                    
                    # Add title
                    title = bill_info.get("title", "")
                    if title:
                        content_parts.append(f"TITLE: {title}")
                    
                    # Add sponsor information
                    sponsors = bill_info.get("sponsors", [])
                    if sponsors:
                        sponsor = sponsors[0]
                        sponsor_info = f"SPONSOR: {sponsor.get('fullName', '')} ({sponsor.get('party', '')}-{sponsor.get('state', '')})"
                        content_parts.append(sponsor_info)
                    
                    # Add committee information
                    committees = bill_info.get("committees", {}).get("items", [])
                    if committees:
                        committee_names = [c.get("name", "") for c in committees[:2]]
                        content_parts.append(f"COMMITTEES: {', '.join(committee_names)}")
                    
                    # Add summary if available
                    summaries = bill_info.get("summaries", {}).get("items", [])
                    if summaries:
                        summary_text = summaries[0].get("text", "")
                        if summary_text and len(summary_text) > 100:
                            # Clean up HTML tags if present
                            import re
                            clean_summary = re.sub(r'<[^>]+>', '', summary_text)
                            content_parts.append(f"SUMMARY: {clean_summary[:3000]}...")
                    
                    # Add recent actions
                    actions = bill_info.get("actions", {}).get("items", [])
                    if actions:
                        recent_actions = []
                        for action in actions[:5]:  # Get last 5 actions
                            action_text = action.get("text", "")
                            action_date = action.get("actionDate", "")
                            if action_text:
                                recent_actions.append(f"• {action_date}: {action_text}")
                        
                        if recent_actions:
                            content_parts.append(f"RECENT ACTIONS:\n{chr(10).join(recent_actions)}")
                    
                    # Add subjects/policy areas
                    policy_area = bill_info.get("policyArea", {}).get("name", "")
                    if policy_area:
                        content_parts.append(f"POLICY AREA: {policy_area}")
                    
                    # Add subjects
                    subjects = bill_info.get("subjects", {}).get("items", [])
                    if subjects:
                        subject_names = [s.get("name", "") for s in subjects[:5]]
                        content_parts.append(f"SUBJECTS: {', '.join(subject_names)}")
                    
                    # Try to get bill text
                    text_url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{bill_number}/text"
                    text_response = await client.get(text_url, params={"api_key": self.congress_api_key})
                    
                    if text_response.status_code == 200:
                        text_data = text_response.json()
                        text_versions = text_data.get("textVersions", [])
                        
                        if text_versions:
                            # Get the most recent text version
                            latest_version = text_versions[0]
                            version_code = latest_version.get("type")
                            
                            # Fetch the actual text
                            version_url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{bill_number}/text/{version_code}"
                            version_response = await client.get(version_url, params={"api_key": self.congress_api_key})
                            
                            if version_response.status_code == 200:
                                version_data = version_response.json()
                                
                                # Extract formatted text
                                if "textVersions" in version_data and version_data["textVersions"]:
                                    formats = version_data["textVersions"][0].get("formats", [])
                                    
                                    # Look for formatted text
                                    for fmt in formats:
                                        if fmt.get("type") == "Formatted Text":
                                            formatted_url = fmt.get("url")
                                            if formatted_url:
                                                # Fetch the formatted text
                                                text_content_response = await client.get(
                                                    formatted_url, 
                                                    params={"api_key": self.congress_api_key}
                                                )
                                                if text_content_response.status_code == 200:
                                                    bill_text = text_content_response.text[:8000]  # Limit size
                                                    content_parts.append(f"BILL TEXT:\n{bill_text}")
                                                    break
                    
                    # Combine all parts
                    if content_parts:
                        return "\n\n".join(content_parts)
                    else:
                        return f"Information not available for {bill_type.upper()}-{bill_number} from the {congress}th Congress."
                
            except Exception as e:
                print(f"    API error: {str(e)}")
                pass
        
        # Fallback text
        return f"Information not available. This is {bill_type.upper()}-{bill_number} from the {congress}th Congress."
    
    def _generate_congress_web_url(self, congress: int, bill_type: str, bill_number: str) -> str:
        """Generate the public Congress.gov web URL for citizens"""
        # Convert API bill type to web URL format
        url_type = bill_type.lower()
        if url_type == "s":
            url_type = "senate-bill"
        elif url_type == "hr":
            url_type = "house-bill"
        elif url_type == "hres":
            url_type = "house-resolution"
        elif url_type == "sres":
            url_type = "senate-resolution"
        elif url_type == "hjres":
            url_type = "house-joint-resolution"
        elif url_type == "sjres":
            url_type = "senate-joint-resolution"
        elif url_type == "hconres":
            url_type = "house-concurrent-resolution"
        elif url_type == "sconres":
            url_type = "senate-concurrent-resolution"
        
        return f"https://www.congress.gov/bill/{congress}th-congress/{url_type}/{bill_number}"

async def enhance_all_documents():
    """Enhance all documents with full text and proper URLs"""
    enhancer = DocumentEnhancer()
    
    async with AsyncSessionLocal() as db:
        # Get all documents
        stmt = select(Document).limit(50)  # Start with first 50 for testing
        result = await db.execute(stmt)
        documents = result.scalars().all()
        
        print(f"Enhancing {len(documents)} documents with full text and URLs...")
        
        for i, doc in enumerate(documents, 1):
            print(f"Processing {i}/{len(documents)}: {doc.identifier}")
            
            try:
                enhancement_result = await enhancer.enhance_document_text(doc)
                
                if enhancement_result:
                    full_text, updated_metadata = enhancement_result
                    
                    # Update document
                    update_stmt = update(Document).where(
                        Document.id == doc.id
                    ).values(
                        full_text=full_text,
                        doc_metadata=updated_metadata
                    )
                    
                    await db.execute(update_stmt)
                    await db.commit()
                    
                    print(f"  ✅ Enhanced with {len(full_text)} characters of text")
                else:
                    print(f"  ⚠️ Could not enhance {doc.identifier}")
                
                # Brief pause to respect API limits
                await asyncio.sleep(0.2)
                
            except Exception as e:
                print(f"  ❌ Error processing {doc.identifier}: {str(e)}")
                continue
        
        print("✅ Document enhancement complete!")

if __name__ == "__main__":
    asyncio.run(enhance_all_documents())