"""
Federal Register API integration for GovernmentGPT.
Fetches executive orders and presidential documents.
"""

import httpx
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
import logging
from urllib.parse import urlencode

from app.core.config import settings

logger = logging.getLogger(__name__)


class FederalRegisterAPI:
    """
    Federal Register API client for fetching executive orders and presidential documents.
    
    API Documentation: https://www.federalregister.gov/developers/api/v1
    Rate Limit: No official limit, but be respectful
    """
    
    def __init__(self):
        self.base_url = "https://www.federalregister.gov/api/v1"
        self.session = None
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "GovernmentGPT/1.0 (Civic Transparency Platform)",
                "Accept": "application/json"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """Make request to Federal Register API"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Federal Register API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Federal Register API request failed: {str(e)}")
            raise
    
    async def get_documents(self, 
                          document_types: List[str] = None,
                          start_date: date = None,
                          end_date: date = None,
                          per_page: int = 100,
                          page: int = 1) -> Dict:
        """
        Fetch documents from Federal Register
        
        Args:
            document_types: List of document types ('PRESDOCU', 'EXECORD', etc.)
            start_date: Start date for document search
            end_date: End date for document search
            per_page: Number of documents per page (max 1000)
            page: Page number for pagination
        """
        params = {
            "per_page": min(per_page, 1000),  # API max is 1000
            "page": page,
            "order": "newest"
        }
        
        # Document types filter
        if document_types:
            params["conditions[type][]"] = document_types
        else:
            # Default to Presidential Documents and Executive Orders
            params["conditions[type][]"] = ["PRESDOCU", "EXECORD"]
        
        # Date range filter
        if start_date:
            params["conditions[publication_date][gte]"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["conditions[publication_date][lte]"] = end_date.strftime("%Y-%m-%d")
        
        return await self._make_request("documents", params)
    
    async def get_document_details(self, document_number: str) -> Dict:
        """
        Get detailed information for a specific document
        
        Args:
            document_number: Federal Register document number
        """
        endpoint = f"documents/{document_number}"
        return await self._make_request(endpoint)
    
    async def get_executive_orders(self, 
                                 start_date: date = None,
                                 end_date: date = None,
                                 per_page: int = 100) -> Dict:
        """Get executive orders specifically"""
        return await self.get_documents(
            document_types=["EXECORD"],
            start_date=start_date,
            end_date=end_date,
            per_page=per_page
        )
    
    async def get_presidential_documents(self,
                                       start_date: date = None,
                                       end_date: date = None,
                                       per_page: int = 100) -> Dict:
        """Get presidential documents (including proclamations, memoranda)"""
        return await self.get_documents(
            document_types=["PRESDOCU"],
            start_date=start_date,
            end_date=end_date,
            per_page=per_page
        )
    
    async def search_documents(self, query: str, per_page: int = 20) -> Dict:
        """
        Search documents by text query
        
        Args:
            query: Search query text
            per_page: Number of results per page
        """
        params = {
            "conditions[term]": query,
            "per_page": per_page,
            "order": "relevance"
        }
        
        return await self._make_request("documents", params)


class FederalRegisterProcessor:
    """Process and normalize data from Federal Register API"""
    
    @staticmethod
    def extract_document_data(api_response: Dict) -> Dict:
        """Extract and normalize document data from API response"""
        
        # Handle both single document and document list responses
        if "results" in api_response:
            # This is a search/list response, take first result
            documents = api_response.get("results", [])
            if not documents:
                return None
            document = documents[0]
        else:
            # This is a single document response
            document = api_response
        
        # Determine document type
        doc_type = document.get("type")
        document_type = "executive_order"  # Default
        
        if doc_type == "EXECORD":
            document_type = "executive_order"
        elif doc_type == "PRESDOCU":
            # Check title for specific document types
            title = document.get("title", "").lower()
            if "executive order" in title:
                document_type = "executive_order"
            elif "proclamation" in title:
                document_type = "presidential_proclamation"
            elif "memorandum" in title:
                document_type = "presidential_memorandum"
            else:
                document_type = "presidential_document"
        
        # Generate identifier
        doc_number = document.get("document_number", "")
        identifier = f"FR-{doc_number}"
        
        # If it's an Executive Order, try to extract EO number
        if document_type == "executive_order":
            title = document.get("title", "")
            # Try to extract EO number from title
            import re
            eo_match = re.search(r"Executive Order (\d+)", title)
            if eo_match:
                identifier = f"EO-{eo_match.group(1)}"
        
        # Basic document information
        doc_data = {
            "identifier": identifier,
            "title": document.get("title", "").strip(),
            "document_type": document_type,
            "status": "signed",  # Federal Register documents are published/signed
        }
        
        # Dates
        if pub_date := document.get("publication_date"):
            doc_data["introduced_date"] = datetime.strptime(pub_date, "%Y-%m-%d").date()
            doc_data["last_action_date"] = doc_data["introduced_date"]
        
        if signing_date := document.get("signing_date"):
            doc_data["signing_date"] = datetime.strptime(signing_date, "%Y-%m-%d").date()
        
        # Summary/Abstract
        summary_parts = []
        if abstract := document.get("abstract"):
            summary_parts.append(abstract)
        if summary := document.get("summary"):
            summary_parts.append(summary)
        
        doc_data["summary"] = " ".join(summary_parts)[:1000]  # Limit summary length
        
        # Full text (if available)
        full_text = ""
        if body := document.get("body_html_url"):
            # Note: Full HTML text would need separate request
            # For now, use available text
            full_text = document.get("raw_text_url", "")
        
        doc_data["full_text"] = full_text or doc_data["summary"]
        
        # Metadata
        doc_data["metadata"] = {
            "document_number": document.get("document_number"),
            "federal_register_url": document.get("html_url"),
            "pdf_url": document.get("pdf_url"),
            "signing_date": document.get("signing_date"),
            "effective_date": document.get("effective_on"),
            "agencies": [agency.get("name") for agency in document.get("agencies", [])],
            "topics": document.get("topics", []),
            "citation": document.get("citation"),
            "pages": {
                "start": document.get("start_page"),
                "end": document.get("end_page")
            },
            "volume": document.get("volume"),
            "presidential": document.get("president", {})
        }
        
        return doc_data
    
    @staticmethod
    async def fetch_full_text(session: httpx.AsyncClient, text_url: str) -> str:
        """Fetch full text content from Federal Register text URL"""
        try:
            response = await session.get(text_url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.warning(f"Failed to fetch full text from {text_url}: {str(e)}")
            return ""


# Usage example and testing functions
async def test_federal_register_api():
    """Test function to verify Federal Register API integration"""
    async with FederalRegisterAPI() as api:
        try:
            print("🏛️ Testing Federal Register API...")
            
            # Test fetching recent executive orders
            end_date = date.today()
            start_date = end_date - timedelta(days=365)  # Last year
            
            eo_response = await api.get_executive_orders(
                start_date=start_date,
                end_date=end_date,
                per_page=5
            )
            
            if eo_response.get("results"):
                print(f"✅ Successfully fetched {len(eo_response['results'])} executive orders")
                
                # Process first executive order
                first_eo = eo_response["results"][0]
                processed_eo = FederalRegisterProcessor.extract_document_data({"results": [first_eo]})
                
                if processed_eo:
                    print(f"✅ Processed EO: {processed_eo['identifier']} - {processed_eo['title'][:60]}...")
                    
                    # Get detailed information
                    doc_number = first_eo.get("document_number")
                    if doc_number:
                        details = await api.get_document_details(doc_number)
                        detailed_doc = FederalRegisterProcessor.extract_document_data(details)
                        print(f"✅ Fetched detailed info for {detailed_doc['identifier']}")
                
            else:
                print("❌ No executive orders returned from API")
                
            # Test presidential documents
            pres_response = await api.get_presidential_documents(
                start_date=start_date,
                end_date=end_date,
                per_page=3
            )
            
            if pres_response.get("results"):
                print(f"✅ Successfully fetched {len(pres_response['results'])} presidential documents")
            
        except Exception as e:
            print(f"❌ Federal Register API test failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_federal_register_api())