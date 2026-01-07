"""
Script to test retrieval from ChromaDB
Queries the API Governance rules vector store
"""
import asyncio
import sys
import logging
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def retrieve_governance_rules(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve governance rules from ChromaDB based on a query
    
    Args:
        query: The search query (e.g., "REST API naming conventions")
        top_k: Number of top results to return
        
    Returns:
        List of matching governance rules with scores
    """
    try:
        # Import dependencies
        from src.core.rag_engine.embeddings import get_embedding_model
        from src.core.rag_engine.vector_store import get_vector_store
        from src.config.settings import get_settings
        
        settings = get_settings()
        
        logger.info(f"Querying ChromaDB for: '{query}'")
        logger.info(f"Collection: {settings.PINECONE_INDEX_API_GOVERNANCE}")
        logger.info(f"Top K: {top_k}")
        logger.info("=" * 80)
        
        # Initialize components
        embedding_model = get_embedding_model()
        vector_store = get_vector_store(settings.PINECONE_INDEX_API_GOVERNANCE)
        
        # Generate query embedding
        logger.info("Generating query embedding...")
        query_embedding = await embedding_model.embed(query)
        
        # Search vector store
        logger.info("Searching vector store...")
        results = await vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k
        )
        
        # Display results
        logger.info("=" * 80)
        logger.info(f"FOUND {len(results)} RESULTS")
        logger.info("=" * 80)
        
        for i, result in enumerate(results, 1):
            logger.info(f"\n--- Result {i} ---")
            logger.info(f"Score: {result['score']:.4f}")
            logger.info(f"ID: {result['id']}")
            
            metadata = result['metadata']
            logger.info(f"Source: {metadata.get('source', 'N/A')}")
            logger.info(f"Type: {metadata.get('type', 'N/A')}")
            logger.info(f"Chunk Index: {metadata.get('chunk_index', 'N/A')}")
            
            # Display text content (truncated)
            text = metadata.get('text', 'No text available')
            preview = text[:300] + "..." if len(text) > 300 else text
            logger.info(f"\nContent Preview:\n{preview}")
            logger.info("-" * 80)
        
        return results
        
    except Exception as e:
        logger.error(f"Retrieval failed: {e}", exc_info=True)
        raise


async def main():
    """Run retrieval examples"""
    
    # Example queries
    queries = [
        "REST API naming conventions and best practices",
        "API versioning strategies",
        "Error handling in REST APIs",
        "Authentication and authorization",
        "API documentation requirements"
    ]
    
    print("\n" + "=" * 80)
    print("API GOVERNANCE RULES RETRIEVAL TEST")
    print("=" * 80)
    print("\nAvailable test queries:")
    for i, q in enumerate(queries, 1):
        print(f"{i}. {q}")
    
    # Allow user to select or provide custom query
    print("\nEnter query number (1-5) or type your own query:")
    user_input = input("> ").strip()
    
    if user_input.isdigit() and 1 <= int(user_input) <= len(queries):
        query = queries[int(user_input) - 1]
    elif user_input:
        query = user_input
    else:
        # Default query
        query = queries[0]
    
    print(f"\nUsing query: {query}")
    print("=" * 80 + "\n")
    
    try:
        # Perform retrieval
        results = await retrieve_governance_rules(query, top_k=5)
        
        # Summary
        print("\n" + "=" * 80)
        print("RETRIEVAL COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"Query: {query}")
        print(f"Results Found: {len(results)}")
        
        if results:
            print(f"Best Match Score: {results[0]['score']:.4f}")
            print(f"Worst Match Score: {results[-1]['score']:.4f}")
        
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
