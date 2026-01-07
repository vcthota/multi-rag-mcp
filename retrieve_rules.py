"""
Simple retrieval script for ChromaDB - query from command line
Usage: python retrieve_rules.py "your query here" [top_k]
"""
import asyncio
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def retrieve(query: str, top_k: int = 3):
    """Retrieve governance rules from ChromaDB"""
    
    from src.core.rag_engine.embeddings import get_embedding_model
    from src.core.rag_engine.vector_store import get_vector_store
    from src.config.settings import get_settings
    
    settings = get_settings()
    
    logger.info(f"Query: '{query}' | Top-K: {top_k}")
    
    # Initialize
    embedding_model = get_embedding_model()
    vector_store = get_vector_store(settings.PINECONE_INDEX_API_GOVERNANCE)
    
    # Generate embedding and search
    query_embedding = await embedding_model.embed(query)
    results = await vector_store.search(query_embedding, top_k=top_k)
    
    # Display results
    print("\n" + "=" * 100)
    print(f"QUERY: {query}")
    print("=" * 100)
    
    for i, result in enumerate(results, 1):
        score = result['score']
        metadata = result['metadata']
        text = metadata.get('text', '')
        
        print(f"\n[{i}] Score: {score:.4f} | Chunk: {metadata.get('chunk_index', '?')}")
        print("-" * 100)
        print(text[:500] + "..." if len(text) > 500 else text)
        print("-" * 100)
    
    print(f"\nFound {len(results)} results\n")
    return results


async def main():
    if len(sys.argv) < 2:
        print("Usage: python retrieve_rules.py 'your query here' [top_k]")
        print("\nExample:")
        print("  python retrieve_rules.py 'REST API naming conventions' 5")
        sys.exit(1)
    
    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    try:
        await retrieve(query, top_k)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
