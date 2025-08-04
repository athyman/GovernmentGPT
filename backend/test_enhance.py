#!/usr/bin/env python3
"""
Test enhanced document fetcher on a few documents
"""
import asyncio
from enhance_documents import DocumentEnhancer
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, update
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine
from minimal_init import Document

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./governmentgpt_local.db"
engine = create_async_engine(DATABASE_URL, echo=False, future=True, poolclass=StaticPool, connect_args={"check_same_thread": False})
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def test_enhance_documents():
    """Re-enhance a few documents with improved content"""
    enhancer = DocumentEnhancer()
    
    async with AsyncSessionLocal() as db:
        # Get a few specific documents to test
        test_ids = ["S-1071-119", "HR-3944-119", "S-2650-119"]
        
        for identifier in test_ids:
            stmt = select(Document).where(Document.identifier == identifier)
            result = await db.execute(stmt)
            doc = result.scalar_one_or_none()
            
            if doc:
                print(f"Re-enhancing {identifier}...")
                
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
                        
                        print(f"  ✅ Enhanced with {len(full_text)} characters")
                        print(f"  Preview: {full_text[:200]}...")
                    else:
                        print(f"  ⚠️ Could not enhance {identifier}")
                    
                    # Brief pause to respect API limits
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"  ❌ Error processing {identifier}: {str(e)}")
                    continue
        
        print("✅ Test enhancement complete!")

if __name__ == "__main__":
    asyncio.run(test_enhance_documents())