#!/usr/bin/env python3
"""
Database setup script for enhanced search capabilities
Creates FTS5 virtual table and document embeddings table
"""
import asyncio
import aiosqlite
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_PATH = "./governmentgpt_local.db"

async def setup_search_database():
    """Set up database with FTS5 and embeddings support"""
    
    if not Path(DATABASE_PATH).exists():
        logger.error(f"Database {DATABASE_PATH} does not exist. Run minimal_init.py first.")
        return False
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            # Enable FTS5 extension
            await db.execute("PRAGMA foreign_keys = ON")
            
            # Create FTS5 virtual table for full-text search
            logger.info("Creating FTS5 virtual table...")
            await db.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                    title, 
                    summary, 
                    full_text,
                    identifier,
                    content='documents', 
                    content_rowid='rowid'
                )
            """)
            
            # Create document embeddings table for semantic search
            logger.info("Creating document embeddings table...")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS document_embeddings (
                    document_id TEXT PRIMARY KEY,
                    embedding BLOB NOT NULL,
                    embedding_model TEXT DEFAULT 'all-MiniLM-L6-v2',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
                )
            """)
            
            # Create search optimization indexes
            logger.info("Creating search optimization indexes...")
            
            # Index for document type and status filtering
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_type_status 
                ON documents(document_type, status)
            """)
            
            # Index for date-based sorting with type filtering
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_date_type 
                ON documents(last_action_date DESC, document_type)
            """)
            
            # Index for identifier lookups
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_identifier 
                ON documents(identifier)
            """)
            
            # Index for recent documents queries
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_recent 
                ON documents(last_action_date DESC, created_at DESC)
            """)
            
            # Populate FTS5 table with existing documents
            logger.info("Populating FTS5 table with existing documents...")
            
            # Check if documents exist
            cursor = await db.execute("SELECT COUNT(*) FROM documents")
            doc_count = (await cursor.fetchone())[0]
            
            if doc_count > 0:
                # Clear existing FTS data
                await db.execute("DELETE FROM documents_fts")
                
                # Insert all documents into FTS
                await db.execute("""
                    INSERT INTO documents_fts(rowid, title, summary, full_text, identifier)
                    SELECT rowid, title, COALESCE(summary, ''), full_text, identifier 
                    FROM documents
                """)
                
                logger.info(f"Populated FTS5 table with {doc_count} documents")
            else:
                logger.warning("No documents found in database")
            
            # Create triggers to keep FTS5 in sync
            logger.info("Creating FTS5 sync triggers...")
            
            # Insert trigger
            await db.execute("""
                CREATE TRIGGER IF NOT EXISTS documents_fts_insert 
                AFTER INSERT ON documents 
                BEGIN
                    INSERT INTO documents_fts(rowid, title, summary, full_text, identifier)
                    VALUES (NEW.rowid, NEW.title, COALESCE(NEW.summary, ''), NEW.full_text, NEW.identifier);
                END
            """)
            
            # Update trigger
            await db.execute("""
                CREATE TRIGGER IF NOT EXISTS documents_fts_update 
                AFTER UPDATE ON documents 
                BEGIN
                    UPDATE documents_fts 
                    SET title = NEW.title,
                        summary = COALESCE(NEW.summary, ''),
                        full_text = NEW.full_text,
                        identifier = NEW.identifier
                    WHERE rowid = NEW.rowid;
                END
            """)
            
            # Delete trigger
            await db.execute("""
                CREATE TRIGGER IF NOT EXISTS documents_fts_delete 
                AFTER DELETE ON documents 
                BEGIN
                    DELETE FROM documents_fts WHERE rowid = OLD.rowid;
                END
            """)
            
            await db.commit()
            logger.info("✅ Database setup completed successfully")
            
            # Verify setup
            await verify_setup(db)
            
            return True
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            await db.rollback()
            return False

async def verify_setup(db):
    """Verify that all tables and indexes were created successfully"""
    
    # Check FTS5 table
    cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents_fts'")
    if await cursor.fetchone():
        logger.info("✅ FTS5 table created successfully")
        
        # Check FTS5 content
        cursor = await db.execute("SELECT COUNT(*) FROM documents_fts")
        fts_count = (await cursor.fetchone())[0]
        logger.info(f"✅ FTS5 table contains {fts_count} documents")
    else:
        logger.error("❌ FTS5 table not found")
    
    # Check embeddings table
    cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='document_embeddings'")
    if await cursor.fetchone():
        logger.info("✅ Document embeddings table created successfully")
    else:
        logger.error("❌ Document embeddings table not found")
    
    # Check indexes
    indexes = [
        'idx_documents_type_status',
        'idx_documents_date_type', 
        'idx_documents_identifier',
        'idx_documents_recent'
    ]
    
    for index in indexes:
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?", (index,))
        if await cursor.fetchone():
            logger.info(f"✅ Index {index} created successfully")
        else:
            logger.warning(f"⚠️  Index {index} not found")
    
    # Check triggers
    triggers = [
        'documents_fts_insert',
        'documents_fts_update',
        'documents_fts_delete'
    ]
    
    for trigger in triggers:
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name=?", (trigger,))
        if await cursor.fetchone():
            logger.info(f"✅ Trigger {trigger} created successfully")
        else:
            logger.warning(f"⚠️  Trigger {trigger} not found")

async def test_fts_search():
    """Test FTS5 search functionality"""
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            # Test basic FTS search
            cursor = await db.execute("""
                SELECT d.identifier, d.title, bm25(documents_fts) as rank_score
                FROM documents_fts 
                JOIN documents d ON documents_fts.rowid = d.rowid
                WHERE documents_fts MATCH 'infrastructure'
                ORDER BY rank_score
                LIMIT 3
            """)
            
            results = await cursor.fetchall()
            
            if results:
                logger.info("✅ FTS5 search test successful:")
                for row in results:
                    logger.info(f"  - {row[0]}: {row[1][:60]}... (score: {row[2]:.3f})")
            else:
                logger.warning("⚠️  FTS5 search returned no results")
                
        except Exception as e:
            logger.error(f"❌ FTS5 search test failed: {e}")

async def rebuild_fts_index():
    """Rebuild FTS5 index from scratch"""
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            logger.info("Rebuilding FTS5 index...")
            
            # Clear existing FTS data
            await db.execute("DELETE FROM documents_fts")
            
            # Repopulate from documents table
            await db.execute("""
                INSERT INTO documents_fts(rowid, title, summary, full_text, identifier)
                SELECT rowid, title, COALESCE(summary, ''), full_text, identifier 
                FROM documents
            """)
            
            await db.commit()
            
            # Get count
            cursor = await db.execute("SELECT COUNT(*) FROM documents_fts")
            count = (await cursor.fetchone())[0]
            
            logger.info(f"✅ FTS5 index rebuilt with {count} documents")
            
        except Exception as e:
            logger.error(f"❌ FTS5 index rebuild failed: {e}")

if __name__ == "__main__":
    async def main():
        print("🔧 Setting up enhanced search database...")
        success = await setup_search_database()
        
        if success:
            print("\n🧪 Testing FTS5 search...")
            await test_fts_search()
            
            print("\n✅ Database setup complete!")
            print("\n📋 Next steps:")
            print("1. Run the hybrid search service to test functionality")
            print("2. Generate document embeddings for semantic search")
            print("3. Update your server to use the new HybridSearchService")
        else:
            print("\n❌ Database setup failed!")
    
    asyncio.run(main())