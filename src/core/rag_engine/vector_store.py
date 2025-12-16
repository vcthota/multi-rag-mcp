"""
Core RAG Engine - Vector Store
Handles vector database operations (Pinecone/ChromaDB)
"""
from typing import List, Dict, Any, Optional
import logging

from src.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorStore:
    """Vector database interface"""
    
    def __init__(self, index_name: str):
        self.index_name = index_name
        
        if settings.use_pinecone:
            self._init_pinecone()
        else:
            self._init_chromadb()
    
    def _init_pinecone(self):
        """Initialize Pinecone client"""
        import pinecone
        
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        
        self.index = pinecone.Index(self.index_name)
        self.backend = "pinecone"
        logger.info(f"Initialized Pinecone index: {self.index_name}")
    
    def _init_chromadb(self):
        """Initialize ChromaDB client"""
        import chromadb
        
        self.client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT
        )
        
        self.collection = self.client.get_or_create_collection(
            name=self.index_name,
            metadata={"dimension": settings.EMBEDDING_DIMENSION}
        )
        
        self.backend = "chromadb"
        logger.info(f"Initialized ChromaDB collection: {self.index_name}")
    
    async def upsert(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]]
    ):
        """Upsert vectors with metadata"""
        
        if self.backend == "pinecone":
            # Pinecone format
            vectors = [
                (id_, emb, meta)
                for id_, emb, meta in zip(ids, embeddings, metadata)
            ]
            self.index.upsert(vectors=vectors)
        
        else:  # chromadb
            # ChromaDB format
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadata
            )
        
        logger.info(f"Upserted {len(ids)} vectors to {self.index_name}")
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 20,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        
        if self.backend == "pinecone":
            # Pinecone search
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter,
                include_metadata=True
            )
            
            return [
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                }
                for match in results.matches
            ]
        
        else:  # chromadb
            # ChromaDB search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter
            )
            
            return [
                {
                    "id": id_,
                    "score": 1 - distance,  # Convert distance to similarity
                    "metadata": meta
                }
                for id_, distance, meta in zip(
                    results['ids'][0],
                    results['distances'][0],
                    results['metadatas'][0]
                )
            ]
    
    async def delete(self, ids: List[str]):
        """Delete vectors by IDs"""
        
        if self.backend == "pinecone":
            self.index.delete(ids=ids)
        else:
            self.collection.delete(ids=ids)
        
        logger.info(f"Deleted {len(ids)} vectors from {self.index_name}")


def get_vector_store(index_name: str) -> VectorStore:
    """Get vector store instance"""
    return VectorStore(index_name)
