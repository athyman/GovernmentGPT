"""
Congress.gov API integration for GovernmentGPT.
Fetches real congressional bills, sponsors, and legislative actions.
"""

import httpx
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
import logging
from urllib.parse import urlencode

from app.core.config import settings

logger = logging.getLogger(__name__)


class CongressAPI:
    """
    Congress.gov API client for fetching legislative data.
    
    API Documentation: https://api.congress.gov/
    Rate Limit: 5,000 requests per hour
    """
    
    def __init__(self):
        self.base_url = "https://api.congress.gov/v3"
        self.api_key = settings.CONGRESS_API_KEY
        self.session = None
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "X-API-Key": self.api_key,
                "User-Agent": "GovernmentGPT/1.0 (Civic Transparency Platform)"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """Make authenticated request to Congress.gov API"""
        if not self.api_key:
            raise ValueError("Congress.gov API key not configured")
            
        url = f"{self.base_url}/{endpoint}"
        if params:
            url += f"?{urlencode(params)}"
            
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Congress API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Congress API request failed: {str(e)}")
            raise
    
    async def get_recent_bills(self, 
                             congress: int = 118, 
                             limit: int = 250,
                             offset: int = 0,
                             bill_type: Optional[str] = None) -> Dict:
        """
        Fetch recent bills from Congress.gov
        
        Args:
            congress: Congress session (118 = 2023-2024)
            limit: Number of bills to fetch (max 250 per request)
            offset: Pagination offset
            bill_type: 'hr', 's', 'hjres', 'sjres', 'hconres', 'sconres', 'hres', 'sres'
        """
        endpoint = f"bill/{congress}"
        params = {
            "format": "json",
            "limit": min(limit, 250),  # API max is 250
            "offset": offset,
            "sort": "updateDate+desc"  # Most recently updated first
        }
        
        if bill_type:
            endpoint += f"/{bill_type}"
            
        return await self._make_request(endpoint, params)
    
    async def get_bill_details(self, congress: int, bill_type: str, bill_number: int) -> Dict:
        """
        Get detailed information for a specific bill
        
        Args:
            congress: Congress session number
            bill_type: Bill type ('hr', 's', etc.)
            bill_number: Bill number
        """
        endpoint = f"bill/{congress}/{bill_type}/{bill_number}"
        params = {"format": "json"}
        
        return await self._make_request(endpoint, params)
    
    async def get_bill_text(self, congress: int, bill_type: str, bill_number: int) -> Dict:
        """Get full text of a bill"""
        endpoint = f"bill/{congress}/{bill_type}/{bill_number}/text"
        params = {"format": "json"}
        
        return await self._make_request(endpoint, params)
    
    async def get_bill_actions(self, congress: int, bill_type: str, bill_number: int) -> Dict:
        """Get legislative actions for a bill"""
        endpoint = f"bill/{congress}/{bill_type}/{bill_number}/actions"
        params = {"format": "json", "limit": 250}
        
        return await self._make_request(endpoint, params)
    
    async def get_member_details(self, bioguide_id: str) -> Dict:
        """Get details for a member of Congress by bioguide ID"""
        endpoint = f"member/{bioguide_id}"
        params = {"format": "json"}
        
        return await self._make_request(endpoint, params)
    
    async def get_current_members(self, chamber: str = None) -> Dict:
        """
        Get current members of Congress
        
        Args:
            chamber: 'house' or 'senate', or None for both
        """
        endpoint = "member"
        params = {
            "format": "json",
            "limit": 250,
            "currentMember": "true"
        }
        
        if chamber:
            params["chamber"] = chamber
            
        return await self._make_request(endpoint, params)


class CongressDataProcessor:
    """Process and normalize data from Congress.gov API"""
    
    @staticmethod
    def extract_bill_data(api_response: Dict) -> Dict:
        """Extract and normalize bill data from API response"""
        bill = api_response.get("bill", {})
        
        # Basic bill information
        bill_data = {
            "identifier": f"{bill.get('type', '').upper()}-{bill.get('number', '')}-{bill.get('congress', '')}",
            "title": bill.get("title", "").strip(),
            "document_type": "bill",
            "congress_session": bill.get("congress"),
            "bill_type": bill.get("type", "").lower(),
            "bill_number": bill.get("number"),
        }
        
        # Dates
        if introduced_date := bill.get("introducedDate"):
            bill_data["introduced_date"] = datetime.fromisoformat(introduced_date).date()
            
        if updated_date := bill.get("updateDate"):
            bill_data["last_action_date"] = datetime.fromisoformat(updated_date).date()
        
        # Status and summary
        bill_data["summary"] = ""
        if latest_action := bill.get("latestAction", {}).get("text"):
            bill_data["summary"] = latest_action[:500] + "..." if len(latest_action) > 500 else latest_action
            
        # Policy area and subjects
        subjects = []
        if policy_area := bill.get("policyArea", {}).get("name"):
            subjects.append(policy_area)
            
        if legislative_subjects := bill.get("subjects", {}).get("legislativeSubjects"):
            subjects.extend([subj.get("name") for subj in legislative_subjects[:5]])
        
        # Sponsor information
        sponsor_info = {}
        if sponsors := bill.get("sponsors"):
            if sponsors and len(sponsors) > 0:
                sponsor = sponsors[0]  # Primary sponsor
                sponsor_info = {
                    "bioguide_id": sponsor.get("bioguideId"),
                    "full_name": sponsor.get("fullName"),
                    "party": sponsor.get("party"),
                    "state": sponsor.get("state"),
                    "district": sponsor.get("district")
                }
        
        # Additional metadata
        bill_data["metadata"] = {
            "congress_url": bill.get("url"),
            "policy_area": bill.get("policyArea", {}).get("name"),
            "subjects": subjects,
            "sponsor": sponsor_info,
            "cosponsors_count": bill.get("cosponsors", {}).get("count", 0),
            "committees": [comm.get("name") for comm in bill.get("committees", [])],
            "laws": bill.get("laws", []),
            "constitutional_authority": bill.get("constitutionalAuthorityStatementText")
        }
        
        return bill_data
    
    @staticmethod
    def extract_legislator_data(api_response: Dict) -> Dict:
        """Extract and normalize legislator data from API response"""
        member = api_response.get("member", {})
        
        # Basic information
        legislator_data = {
            "bioguide_id": member.get("bioguideId"),
            "first_name": member.get("firstName", ""),
            "last_name": member.get("lastName", ""),
            "full_name": member.get("directOrderName", ""),
            "party": member.get("partyName"),
            "state": member.get("state"),
            "chamber": "house" if member.get("chamber") == "House of Representatives" else "senate",
            "active": True
        }
        
        # District for House members
        if member.get("district"):
            legislator_data["district"] = str(member.get("district"))
            
        # Additional metadata
        legislator_data["metadata"] = {
            "official_website": member.get("officialWebsiteUrl"),
            "birth_year": member.get("birthYear"),
            "served_from": member.get("served", {}).get("House" if legislator_data["chamber"] == "house" else "Senate"),
            "leadership_roles": member.get("leadership", [])
        }
        
        return legislator_data


# Usage example and testing functions
async def test_congress_api():
    """Test function to verify Congress.gov API integration"""
    if not settings.CONGRESS_API_KEY:
        print("❌ Congress.gov API key not configured")
        return
        
    async with CongressAPI() as api:
        try:
            # Test fetching recent bills
            print("🏛️ Testing Congress.gov API...")
            bills_response = await api.get_recent_bills(congress=118, limit=5)
            
            if bills_response.get("bills"):
                print(f"✅ Successfully fetched {len(bills_response['bills'])} bills")
                
                # Process first bill
                first_bill = bills_response["bills"][0]
                bill_details = await api.get_bill_details(
                    congress=first_bill["congress"],
                    bill_type=first_bill["type"],
                    bill_number=first_bill["number"]
                )
                
                processed_bill = CongressDataProcessor.extract_bill_data(bill_details)
                print(f"✅ Processed bill: {processed_bill['identifier']} - {processed_bill['title'][:60]}...")
                
            else:
                print("❌ No bills returned from API")
                
        except Exception as e:
            print(f"❌ API test failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_congress_api())