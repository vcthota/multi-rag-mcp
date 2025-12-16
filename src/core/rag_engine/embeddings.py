"""
Core RAG Engine - Embeddings
Handles text embedding generation
"""
from typing import List
from openai import AsyncOpenAI
import logging

from src.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingModel:
    """Embedding model for text vectorization"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        self.batch_size = settings.EMBEDDING_BATCH_SIZE
    
    async def embed(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        embeddings = await self.embed_batch([text])
        return embeddings[0]
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts"""
        
        if not texts:
            return []
        
        try:
            # Process in batches
            all_embeddings = []
            
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i:i + self.batch_size]
                
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
        
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            raise


# Singleton instance
_embedding_model = None

def get_embedding_model() -> EmbeddingModel:
    """Get embedding model instance"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model
