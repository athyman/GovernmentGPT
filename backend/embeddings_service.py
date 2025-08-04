#!/usr/bin/env python3
"""
Document Embeddings Service for semantic search
Generates and manages document embeddings using sentence transformers
"""
import asyncio
import aiosqlite
import numpy as np
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_PATH = "./governmentgpt_local.db"

class EmbeddingsService:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load sentence transformer model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Loaded embedding model: {self.model_name}")
        except ImportError:
            logger.error("❌ sentence-transformers not installed. Run: pip install sentence-transformers")
            self.model = None
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            self.model = None
    
    async def generate_all_embeddings(self, batch_size: int = 50, force_regenerate: bool = False):
        """Generate embeddings for all documents in the database"""
        
        if not self.model:
            logger.error("❌ Embedding model not available")
            return False
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            try:
                # Get total document count
                cursor = await db.execute("SELECT COUNT(*) FROM documents")
                total_docs = (await cursor.fetchone())[0]
                
                if total_docs == 0:
                    logger.warning("⚠️  No documents found in database")
                    return False
                
                logger.info(f"📊 Processing {total_docs} documents for embeddings generation")
                
                # Get documents that need embeddings
                if force_regenerate:
                    query = "SELECT id, title, summary, full_text FROM documents ORDER BY created_at"
                else:
                    query = """
                    SELECT d.id, d.title, d.summary, d.full_text 
                    FROM documents d
                    LEFT JOIN document_embeddings e ON d.id = e.document_id
                    WHERE e.document_id IS NULL
                    ORDER BY d.created_at
                    """
                
                cursor = await db.execute(query)
                documents = await cursor.fetchall()
                
                if not documents:
                    logger.info("✅ All documents already have embeddings")
                    return True
                
                logger.info(f"🔄 Generating embeddings for {len(documents)} documents")
                
                processed = 0
                failed = 0
                
                # Process in batches
                for i in range(0, len(documents), batch_size):
                    batch = documents[i:i + batch_size]
                    batch_texts = []
                    batch_ids = []
                    
                    # Prepare batch data
                    for doc in batch:
                        doc_id, title, summary, full_text = doc
                        
                        # Combine title, summary, and truncated full text
                        combined_text = self._prepare_text_for_embedding(title, summary, full_text)
                        batch_texts.append(combined_text)
                        batch_ids.append(doc_id)
                    
                    try:
                        # Generate embeddings for batch
                        logger.info(f"🔄 Processing batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
                        embeddings = self.model.encode(batch_texts, show_progress_bar=False)
                        
                        # Store embeddings in database
                        for doc_id, embedding in zip(batch_ids, embeddings):
                            await self._store_embedding(db, doc_id, embedding)
                            processed += 1
                        
                        await db.commit()
                        
                        if (i // batch_size + 1) % 10 == 0:
                            logger.info(f"📈 Progress: {processed}/{len(documents)} documents processed")
                    
                    except Exception as e:
                        logger.error(f"❌ Batch processing failed: {e}")
                        failed += len(batch)
                        continue
                
                logger.info(f"✅ Embeddings generation complete: {processed} successful, {failed} failed")
                
                # Verify results
                await self._verify_embeddings(db)
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Embeddings generation failed: {e}")
                return False
    
    def _prepare_text_for_embedding(self, title: str, summary: str, full_text: str, max_length: int = 1000) -> str:
        """Prepare document text for embedding generation"""
        
        # Start with title (most important)
        combined = title or ""
        
        # Add summary if available
        if summary:
            combined += f" {summary}"
        
        # Add truncated full text
        if full_text:
            remaining_length = max_length - len(combined)
            if remaining_length > 100:  # Only add if we have significant space
                truncated_text = full_text[:remaining_length]
                combined += f" {truncated_text}"
        
        return combined.strip()
    
    async def _store_embedding(self, db, document_id: str, embedding: np.ndarray):
        """Store document embedding in database"""
        
        # Convert embedding to binary format
        embedding_blob = embedding.astype(np.float32).tobytes()
        
        # Insert or update embedding
        await db.execute("""
            INSERT OR REPLACE INTO document_embeddings 
            (document_id, embedding, embedding_model, updated_at)
            VALUES (?, ?, ?, ?)
        """, (document_id, embedding_blob, self.model_name, datetime.now().isoformat()))
    
    async def _verify_embeddings(self, db):
        """Verify embedding generation results"""
        
        # Count embeddings
        cursor = await db.execute("SELECT COUNT(*) FROM document_embeddings")
        embedding_count = (await cursor.fetchone())[0]
        
        # Count documents
        cursor = await db.execute("SELECT COUNT(*) FROM documents")
        doc_count = (await cursor.fetchone())[0]
        
        logger.info(f"📊 Verification: {embedding_count}/{doc_count} documents have embeddings")
        
        if embedding_count > 0:
            # Test embedding retrieval
            cursor = await db.execute("""
                SELECT document_id, embedding FROM document_embeddings LIMIT 1
            """)
            row = await cursor.fetchone()
            
            if row:
                doc_id, embedding_blob = row
                embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                logger.info(f"✅ Sample embedding for {doc_id}: shape {embedding.shape}, mean {embedding.mean():.4f}")
    
    async def search_similar_documents(self, query: str, limit: int = 10, threshold: float = 0.1) -> List[Dict]:
        """Search for documents similar to query using embeddings"""
        
        if not self.model:
            logger.error("❌ Embedding model not available")
            return []
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            try:
                # Generate query embedding
                query_embedding = self.model.encode([query])[0]
                
                # Retrieve all document embeddings
                cursor = await db.execute("""
                    SELECT d.id, d.identifier, d.title, d.summary, d.document_type, 
                           d.status, d.last_action_date, e.embedding
                    FROM documents d
                    JOIN document_embeddings e ON d.id = e.document_id
                    WHERE e.embedding IS NOT NULL
                """)
                
                results = []
                
                for row in cursor:
                    doc_id, identifier, title, summary, doc_type, status, date, embedding_blob = row
                    
                    # Convert embedding back to numpy array
                    doc_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                    
                    # Calculate cosine similarity
                    similarity = np.dot(query_embedding, doc_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                    )
                    
                    # Filter by threshold
                    if similarity >= threshold:
                        results.append({
                            'id': doc_id,
                            'identifier': identifier,
                            'title': title,
                            'summary': summary or '',
                            'document_type': doc_type,
                            'status': status or '',
                            'last_action_date': date,
                            'similarity': float(similarity)
                        })
                
                # Sort by similarity
                results.sort(key=lambda x: x['similarity'], reverse=True)
                
                return results[:limit]
                
            except Exception as e:
                logger.error(f"❌ Semantic search failed: {e}")
                return []
    
    async def update_document_embedding(self, document_id: str):
        """Update embedding for a specific document"""
        
        if not self.model:
            logger.error("❌ Embedding model not available")
            return False
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            try:
                # Get document
                cursor = await db.execute("""
                    SELECT title, summary, full_text FROM documents WHERE id = ?
                """, (document_id,))
                
                row = await cursor.fetchone()
                if not row:
                    logger.error(f"❌ Document {document_id} not found")
                    return False
                
                title, summary, full_text = row
                
                # Prepare text and generate embedding
                combined_text = self._prepare_text_for_embedding(title, summary, full_text)
                embedding = self.model.encode([combined_text])[0]
                
                # Store embedding
                await self._store_embedding(db, document_id, embedding)
                await db.commit()
                
                logger.info(f"✅ Updated embedding for document {document_id}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to update embedding for {document_id}: {e}")
                return False
    
    async def get_embedding_stats(self) -> Dict:
        """Get statistics about document embeddings"""
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            try:
                # Total documents
                cursor = await db.execute("SELECT COUNT(*) FROM documents")
                total_docs = (await cursor.fetchone())[0]
                
                # Documents with embeddings
                cursor = await db.execute("SELECT COUNT(*) FROM document_embeddings")
                embedded_docs = (await cursor.fetchone())[0]
                
                # Embedding models used
                cursor = await db.execute("""
                    SELECT embedding_model, COUNT(*) 
                    FROM document_embeddings 
                    GROUP BY embedding_model
                """)
                models = dict(await cursor.fetchall())
                
                # Recent embeddings
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM document_embeddings 
                    WHERE created_at >= datetime('now', '-7 days')
                """)
                recent_embeddings = (await cursor.fetchone())[0]
                
                return {
                    'total_documents': total_docs,
                    'embedded_documents': embedded_docs,
                    'coverage_percentage': (embedded_docs / total_docs * 100) if total_docs > 0 else 0,
                    'embedding_models': models,
                    'recent_embeddings_7_days': recent_embeddings
                }
                
            except Exception as e:
                logger.error(f"❌ Failed to get embedding stats: {e}")
                return {}

async def test_embeddings_service():
    """Test the embeddings service"""
    
    service = EmbeddingsService()
    
    if not service.model:
        print("❌ Embedding model not available - install sentence-transformers")
        return
    
    # Get stats
    print("📊 Getting embedding statistics...")
    stats = await service.get_embedding_stats()
    
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test semantic search if embeddings exist
    if stats.get('embedded_documents', 0) > 0:
        print("\n🔍 Testing semantic search...")
        
        test_queries = [
            "infrastructure spending",
            "healthcare reform",
            "climate change policy"
        ]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = await service.search_similar_documents(query, limit=3)
            
            if results:
                for i, doc in enumerate(results, 1):
                    print(f"  {i}. {doc['identifier']}: {doc['title'][:60]}... (sim: {doc['similarity']:.3f})")
            else:
                print("  No similar documents found")

if __name__ == "__main__":
    async def main():
        print("🔧 Document Embeddings Service")
        print("1. Generate embeddings for all documents")
        print("2. Test semantic search")
        print("3. Show embedding statistics")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        service = EmbeddingsService()
        
        if choice == "1":
            print("\n🔄 Generating embeddings...")
            success = await service.generate_all_embeddings()
            if success:
                print("✅ Embeddings generation completed")
            else:
                print("❌ Embeddings generation failed")
        
        elif choice == "2":
            print("\n🧪 Testing embeddings service...")
            await test_embeddings_service()
        
        elif choice == "3":
            print("\n📊 Embedding statistics:")
            stats = await service.get_embedding_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")
        else:
            print("Invalid choice")
    
    asyncio.run(main())