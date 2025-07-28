"""
Sample data seeding script for GovernmentGPT development and testing.
Creates realistic government documents, legislators, and test data.
"""

import asyncio
import uuid
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.models.document import Document
from app.models.legislator import Legislator
from app.models.search import PopularSearches
from app.core.database import Base

# Sample data
SAMPLE_LEGISLATORS = [
    {
        "bioguide_id": "S000148",
        "first_name": "Charles",
        "last_name": "Schumer",
        "full_name": "Charles E. Schumer",
        "party": "D",
        "state": "NY",
        "chamber": "senate",
        "active": True
    },
    {
        "bioguide_id": "M000133",
        "first_name": "Edward",
        "last_name": "Markey",
        "full_name": "Edward J. Markey",
        "party": "D",
        "state": "MA",
        "chamber": "senate",
        "active": True
    },
    {
        "bioguide_id": "A000374",
        "first_name": "Ralph",
        "last_name": "Abraham",
        "full_name": "Ralph Lee Abraham Jr.",
        "party": "R",
        "state": "LA",
        "chamber": "house",
        "district": "5",
        "active": True
    },
    {
        "bioguide_id": "P000197",
        "first_name": "Nancy",
        "last_name": "Pelosi",
        "full_name": "Nancy Pelosi",
        "party": "D",
        "state": "CA",
        "chamber": "house",
        "district": "11",
        "active": True
    }
]

SAMPLE_BILLS = [
    {
        "identifier": "HR-1-118",
        "title": "For the People Act of 2023",
        "summary": "This bill addresses voter access, election integrity and security, campaign finance, and ethics for the three branches of government. Specifically, the bill expands voter registration (e.g., automatic and same-day registration) and voting access (e.g., vote-by-mail and early voting). It also limits removing voters from voter rolls.",
        "document_type": "bill",
        "status": "introduced",
        "introduced_date": date(2023, 1, 9),
        "last_action_date": date(2023, 1, 9),
        "full_text": """SEC. 1. SHORT TITLE; TABLE OF CONTENTS.

(a) Short Title.—This Act may be cited as the "For the People Act of 2023".

(b) Table of Contents.—The table of contents for this Act is as follows:

TITLE I—ELECTION ACCESS

Subtitle A—Voter Registration

Sec. 1001. Automatic voter registration.
Sec. 1002. Same day registration.
Sec. 1003. Online voter registration.

This comprehensive election reform bill aims to expand access to the ballot box, reduce the influence of big money in politics, strengthen ethics rules for public servants, and implement other anti-corruption measures for the purpose of fortifying our democracy.

The bill would establish automatic voter registration nationwide, which would add tens of millions of eligible voters to the rolls. It would expand early voting, standardize hours that polls are open, and make Election Day a federal holiday so that more people have the opportunity to vote.

The legislation would also restore voting rights to people with past felony convictions and take steps to enhance election security, including requiring paper ballots and post-election audits.

On campaign finance, the bill would establish a voluntary small-dollar public campaign financing system for House candidates, expand disclosure requirements for political spending, and restructure the Federal Election Commission to reduce partisan gridlock.

The bill includes the most comprehensive ethics reforms since Watergate, requiring the president and vice president to disclose their tax returns and divest conflicting business interests, slowing the revolving door between government and lobbying, and strengthening oversight of foreign agents."""
    },
    {
        "identifier": "S-1-118",
        "title": "Climate Emergency Act",
        "summary": "This bill declares that a climate emergency exists and requires the President to use emergency authorities to address the climate crisis. The bill outlines specific actions the President should take, including mobilizing resources, prioritizing environmental justice, and implementing a just transition for workers.",
        "document_type": "bill",
        "status": "introduced",
        "introduced_date": date(2023, 1, 11),
        "last_action_date": date(2023, 3, 15),
        "full_text": """SEC. 1. SHORT TITLE.

This Act may be cited as the "Climate Emergency Act".

SEC. 2. FINDINGS.

Congress finds the following:

(1) Climate change is a direct existential threat to the economy, environment, and general welfare of the United States.

(2) The United States has disproportionately contributed to the climate crisis with approximately 25 percent of global greenhouse gas emissions since 1850.

(3) The impacts of climate change disproportionately harm communities of color, indigenous communities, and low-income communities.

SEC. 3. DECLARATION OF CLIMATE EMERGENCY.

Congress hereby declares that a climate emergency exists that requires immediate action to prevent catastrophic climate change.

SEC. 4. REQUIRED ACTIONS.

(a) In General.—The President shall use the emergency authorities provided by this Act to address the climate emergency by—

(1) immediately commencing a national mobilization to restore a safe climate;
(2) prioritizing the protection of frontline and vulnerable communities;
(3) ensuring a just transition for energy workers;
(4) achieving net-zero greenhouse gas emissions by 2030;
(5) implementing measures to draw down atmospheric carbon dioxide levels;
(6) mobilizing funding at the scale necessary to address the climate emergency.

This legislation recognizes that climate change poses an existential threat requiring immediate emergency action. The bill would grant the President broad authorities to combat climate change through a coordinated national response, similar to wartime mobilization efforts."""
    },
    {
        "identifier": "HR-3684-117",
        "title": "Infrastructure Investment and Jobs Act",
        "summary": "This bill addresses provisions related to federal-aid highway, transit, highway safety, motor carrier, research, hazardous materials, and rail programs of the Department of Transportation (DOT). The bill also addresses drinking water and wastewater infrastructure, broadband infrastructure, and power infrastructure.",
        "document_type": "bill",
        "status": "signed",
        "introduced_date": date(2021, 6, 4),
        "last_action_date": date(2021, 11, 15),
        "full_text": """SEC. 1. SHORT TITLE; TABLE OF CONTENTS.

(a) Short Title.—This Act may be cited as the "Infrastructure Investment and Jobs Act".

DIVISION A—SURFACE TRANSPORTATION

TITLE I—FEDERAL-AID HIGHWAYS

SEC. 11101. FEDERAL-AID HIGHWAY PROGRAM.

This historic bipartisan infrastructure law invests in America's infrastructure and competitiveness. The legislation will rebuild America's roads, bridges and rails, expand access to clean drinking water, ensure every American has access to high-speed internet, tackle the climate crisis, advance environmental justice, and invest in communities that have too often been left behind.

The bipartisan Infrastructure Investment and Jobs Act will:

ROADS AND BRIDGES: Repair and rebuild our roads and bridges with a focus on climate change mitigation, resilience, equity, and safety for all users. This includes the largest dedicated bridge investment since the construction of the interstate highway system.

PUBLIC TRANSIT: Provide the largest federal investment in public transit in history, improving accessibility for seniors and people with disabilities.

RAIL: Make the most significant investment in passenger rail since the creation of Amtrak 50 years ago.

BROADBAND: Deliver affordable, reliable, high-speed broadband to every American, including more than 35 million Americans who live in areas where there is no broadband infrastructure.

ELECTRIC VEHICLES: Build a national network of electric vehicle chargers to accelerate the adoption of electric vehicles.

CLEAN DRINKING WATER: Replace lead pipes and service lines to deliver clean drinking water to American families and businesses.

This investment represents the largest infrastructure investment since the Interstate Highway System and will create millions of good-paying, union jobs."""
    },
    {
        "identifier": "EO-14008",
        "title": "Executive Order on Tackling the Climate Crisis at Home and Abroad",
        "summary": "This executive order establishes climate change as an essential element of United States foreign policy and national security. It directs federal agencies to develop strategies for integrating climate considerations into their international work and calls for hosting a climate summit.",
        "document_type": "executive_order",
        "status": "signed",
        "introduced_date": date(2021, 1, 27),
        "last_action_date": date(2021, 1, 27),
        "full_text": """By the authority vested in me as President by the Constitution and the laws of the United States of America, it is hereby ordered as follows:

Section 1. Policy. The United States and the world face a profound climate crisis with consequences for our national security, economy, and public health. We must act with urgency to address this crisis.

It is the policy of my Administration that climate considerations shall be an essential element of United States foreign policy and national security. Through this order, I am directing my Administration to organize and deploy the full capacity of its agencies to combat the climate crisis.

Sec. 2. Climate Summit. I hereby direct the Secretary of State to host a climate summit within 100 days of this order to discuss climate action commitments.

Sec. 3. Rejoining the Paris Agreement. The United States will rejoin the Paris Climate Agreement and work with international partners to enhance global climate ambition.

Sec. 4. Revoking the Keystone XL Pipeline Permit. The Presidential permit granted to TransCanada Keystone Pipeline, L.P. on March 29, 2017, for the Keystone XL pipeline is hereby revoked.

Sec. 5. Federal Clean Electricity and Vehicle Procurement Strategy. The Chair of the Council on Environmental Quality and the Director of the Office of Management and Budget shall develop a comprehensive plan to create good-paying, union jobs while transforming the Federal fleet, including the United States Postal Service fleet, to clean electric vehicles.

This executive order puts the climate crisis at the center of United States foreign policy and national security planning. It demonstrates America's commitment to leading a clean energy revolution and creating millions of good-paying, union jobs."""
    }
]

SAMPLE_POPULAR_SEARCHES = [
    {"query": "climate change", "normalized_query": "climate change", "search_count": 156, "recent_searches": 45},
    {"query": "infrastructure bill", "normalized_query": "infrastructure bill", "search_count": 134, "recent_searches": 32},
    {"query": "voting rights", "normalized_query": "voting rights", "search_count": 89, "recent_searches": 28},
    {"query": "healthcare reform", "normalized_query": "healthcare reform", "search_count": 67, "recent_searches": 21},
    {"query": "immigration policy", "normalized_query": "immigration policy", "search_count": 45, "recent_searches": 15},
]

async def seed_database():
    """Seed the database with sample data for development and testing."""
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=True
    )
    
    # Create session factory
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    try:
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with async_session() as session:
            print("🌱 Seeding database with sample data...")
            
            # Create legislators
            legislators = {}
            for leg_data in SAMPLE_LEGISLATORS:
                legislator = Legislator(**leg_data)
                session.add(legislator)
                legislators[leg_data["bioguide_id"]] = legislator
            
            await session.flush()  # Get IDs for relationships
            
            # Create bills with sponsor relationships
            for i, bill_data in enumerate(SAMPLE_BILLS):
                # Assign sponsors
                sponsor_mapping = {
                    0: "P000197",  # Pelosi for HR-1
                    1: "M000133",  # Markey for S-1
                    2: "S000148",  # Schumer for Infrastructure
                    3: None        # No sponsor for Executive Order
                }
                
                bill_data = bill_data.copy()
                sponsor_bioguide = sponsor_mapping.get(i)
                if sponsor_bioguide:
                    bill_data["sponsor_id"] = legislators[sponsor_bioguide].id
                
                document = Document(**bill_data)
                session.add(document)
            
            # Create popular searches
            for search_data in SAMPLE_POPULAR_SEARCHES:
                popular_search = PopularSearches(**search_data)
                session.add(popular_search)
            
            await session.commit()
            print("✅ Database seeded successfully!")
            print(f"   - {len(SAMPLE_LEGISLATORS)} legislators")
            print(f"   - {len(SAMPLE_BILLS)} documents") 
            print(f"   - {len(SAMPLE_POPULAR_SEARCHES)} popular searches")
            
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("🚀 Starting database seeding...")
    asyncio.run(seed_database())