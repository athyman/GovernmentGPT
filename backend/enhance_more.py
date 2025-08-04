#!/usr/bin/env python3
"""
Enhance more documents with full text - target popular search results
"""
import asyncio
from enhance_documents import DocumentEnhancer
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, update, or_
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine
from minimal_init import Document

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./governmentgpt_local.db"
engine = create_async_engine(DATABASE_URL, echo=False, future=True, poolclass=StaticPool, connect_args={"check_same_thread": False})
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def enhance_popular_documents():
    """Enhance documents that are likely to be searched"""
    enhancer = DocumentEnhancer()
    
    async with AsyncSessionLocal() as db:
        # Find documents likely to be searched (contain common terms)
        stmt = select(Document).where(
            or_(
                Document.title.ilike('%veteran%'),
                Document.title.ilike('%healthcare%'),
                Document.title.ilike('%tax%'),
                Document.title.ilike('%immigration%'),
                Document.title.ilike('%climate%'),
                Document.title.ilike('%infrastructure%'),
                Document.title.ilike('%education%')
            )
        ).limit(25)
        
        result = await db.execute(stmt)
        documents = result.scalars().all()
        
        print(f"Enhancing {len(documents)} popular search documents...")
        
        for i, doc in enumerate(documents, 1):
            print(f"Processing {i}/{len(documents)}: {doc.identifier}")
            
            try:
                # Check if already enhanced
                if doc.doc_metadata and doc.doc_metadata.get('text_fetched'):
                    print(f"  ✅ Already enhanced")
                    continue
                
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
                await asyncio.sleep(0.3)
                
            except Exception as e:
                print(f"  ❌ Error processing {doc.identifier}: {str(e)}")
                continue
        
        print("✅ Popular documents enhancement complete!")

if __name__ == "__main__":
    asyncio.run(enhance_popular_documents())