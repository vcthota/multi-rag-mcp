"""
Direct ChromaDB initialization - bypasses PDF reader for text content
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.core.rag_engine.embeddings import get_embedding_model
from src.core.rag_engine.vector_store import get_vector_store
from src.config.settings import get_settings
import uuid


GOVERNANCE_RULES = """
# REST API Design and Governance Standards

## 1. Resource Naming Conventions
Use plural nouns for collections (e.g., /users, /orders, /products). Resource names MUST use lowercase letters with hyphens for multi-word resources. Avoid verbs in URLs - use HTTP methods to indicate actions.

## 2. HTTP Methods
GET for retrieval (safe, idempotent). POST for creation (201 Created). PUT for full updates (idempotent). PATCH for partial updates. DELETE for removal (idempotent, 204 No Content).

## 3. HTTP Status Codes
200 OK for successful requests. 201 Created for POST. 204 No Content for DELETE. 400 Bad Request for invalid data. 401 Unauthorized for authentication failures. 403 Forbidden for permission issues. 404 Not Found for missing resources. 500 Internal Server Error for server errors.

## 4. Response Format
Always return JSON with application/json content type. Use consistent error structure with error code, message, and details. Include metadata for paginated responses (total, page, page_size, links).

## 5. API Versioning
Version MUST be in URL path (e.g., /api/v1/users). Use semantic versioning with major version numbers. Support at least one previous major version during transitions.

## 6. Security
Always use HTTPS in production. Implement authentication (OAuth 2.0, JWT, API keys). Implement authorization with RBAC. Validate all user inputs. Implement rate limiting (429 Too Many Requests).

## 7. Documentation
Provide OpenAPI 3.0+ specification at /openapi.json. Document all endpoints with descriptions, parameters, responses, and examples. Include authentication requirements and error documentation.

## 8. Error Handling
Provide meaningful, actionable error messages. Include unique request_id for tracing. Never leak sensitive information (database queries, file paths, stack traces, credentials).

## 9. Performance
Implement pagination for large datasets. Support field filtering. Enable gzip compression. Use appropriate Cache-Control headers.

## 10. API Evolution
Announce deprecations with 6 months notice. Include Deprecation and Sunset headers. Maintain backward compatibility in minor versions.
"""


async def main():
    print("🚀 Initializing API Governance Rules (Direct Method)...")
    print("=" * 60)
    
    try:
        settings = get_settings()
        
        # Initialize components
        print("🔧 Initializing embeddings and vector store...")
        embedding_model = get_embedding_model()
        vector_store = get_vector_store(settings.PINECONE_INDEX_API_GOVERNANCE)
        
        # Split text into chunks
        print("✂️  Splitting text into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_text(GOVERNANCE_RULES)
        chunks = [chunk for chunk in chunks if len(chunk.strip()) > 50]
        
        print(f"📝 Created {len(chunks)} chunks")
        
        # Generate embeddings
        print("🔮 Generating embeddings...")
        embeddings = await embedding_model.embed_batch(chunks)
        
        # Store in vector database
        print("💾 Storing in ChromaDB...")
        doc_id = str(uuid.uuid4())
        
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metadatas = [{
            "source": "API Governance Standards",
            "type": "governance_rules",
            "version": "1.0",
            "chunk_id": i,
            "doc_id": doc_id,
            "text": chunks[i]  # Store text in metadata
        } for i in range(len(chunks))]
        
        await vector_store.upsert(
            ids=ids,
            embeddings=embeddings,
            metadata=metadatas
        )
        
        print("\n✅ Initialization Complete!")
        print("=" * 60)
        print(f"📊 Results:")
        print(f"   - Chunks stored: {len(chunks)}")
        print(f"   - Document ID: {doc_id}")
        print(f"   - Collection: {settings.PINECONE_INDEX_API_GOVERNANCE}")
        print("=" * 60)
        
        print("\n🎉 API Governance rules are now available!")
        print("   You can now use the validation and correction endpoints.")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
