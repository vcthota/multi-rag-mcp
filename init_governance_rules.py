"""
Initialize ChromaDB with API Governance Rules
Run this script to populate the vector database with sample governance rules.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.api_governance.ingestion import GovernanceIngestion


SAMPLE_GOVERNANCE_RULES = """
# REST API Design and Governance Standards

## 1. Resource Naming Conventions

### Rule: Use Plural Nouns for Collections
All collection resources MUST use plural nouns (e.g., /users, /orders, /products).
Never use singular nouns for collections (/user, /order is incorrect).

### Rule: Lowercase with Hyphens
Resource names MUST use lowercase letters with hyphens for multi-word resources.
Examples:
- Correct: /product-categories, /order-items
- Incorrect: /ProductCategories, /order_items

### Rule: Avoid Verbs in URLs
Resource URLs MUST NOT contain verbs. Use HTTP methods to indicate actions.
Examples:
- Correct: POST /users, DELETE /users/123
- Incorrect: /createUser, /deleteUser/123

## 2. HTTP Methods and Semantics

### Rule: GET for Retrieval
GET requests MUST be used only for retrieving resources.
GET MUST be safe (no side effects) and idempotent.

### Rule: POST for Creation
POST MUST be used for creating new resources.
Response SHOULD include Location header with new resource URI.
Status code MUST be 201 Created on success.

### Rule: PUT for Full Updates
PUT MUST replace the entire resource.
PUT MUST be idempotent (multiple identical requests have same effect as one).
Status code SHOULD be 200 OK or 204 No Content.

### Rule: PATCH for Partial Updates
PATCH MUST be used for partial resource updates.
Only specified fields SHOULD be modified.

### Rule: DELETE for Removal
DELETE MUST be used to remove resources.
DELETE MUST be idempotent.
Status code SHOULD be 204 No Content on success.

## 3. HTTP Status Codes

### Success Codes
- 200 OK: Successful GET, PUT, PATCH requests
- 201 Created: Successful POST that creates a resource
- 204 No Content: Successful DELETE or PUT with no response body

### Client Error Codes
- 400 Bad Request: Invalid request data or malformed syntax
- 401 Unauthorized: Authentication is required and has failed
- 403 Forbidden: User lacks permission to access resource
- 404 Not Found: Resource does not exist
- 409 Conflict: Request conflicts with current state (e.g., duplicate)
- 422 Unprocessable Entity: Validation errors in request data

### Server Error Codes
- 500 Internal Server Error: Unexpected server error
- 503 Service Unavailable: Service temporarily unavailable

## 4. Response Format Standards

### Rule: Always Return JSON
All API responses MUST use application/json content type.
XML or other formats SHOULD NOT be used unless explicitly required.

### Rule: Consistent Error Structure
Error responses MUST follow a consistent structure:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

### Rule: Include Metadata
Paginated responses MUST include metadata:
- total: Total number of items
- page: Current page number
- page_size: Items per page
- links: HATEOAS navigation links

## 5. API Versioning

### Rule: Version in URL Path
API version MUST be included in the URL path (e.g., /api/v1/users).
Versioning in headers or query parameters SHOULD NOT be used.

### Rule: Semantic Versioning
Use major version numbers (v1, v2, v3).
Increment version when introducing breaking changes.

### Rule: Support Previous Versions
At least one previous major version SHOULD be supported during transitions.

## 6. Security Requirements

### Rule: Always Use HTTPS
All API endpoints MUST use HTTPS in production.
HTTP MUST redirect to HTTPS automatically.

### Rule: Implement Authentication
All non-public endpoints MUST require authentication.
Use OAuth 2.0, JWT, or API keys as appropriate.

### Rule: Implement Authorization
Authorization checks MUST be performed for all protected resources.
Use role-based access control (RBAC) or similar mechanisms.

### Rule: Validate All Inputs
All user inputs MUST be validated before processing.
Reject invalid data with 400 Bad Request or 422 Unprocessable Entity.

### Rule: Rate Limiting
APIs MUST implement rate limiting to prevent abuse.
Return 429 Too Many Requests when limits are exceeded.

## 7. Documentation Standards

### Rule: Provide OpenAPI/Swagger Specification
Every API MUST have an OpenAPI 3.0+ specification.
Specification SHOULD be available at /openapi.json or /swagger.json.

### Rule: Document All Endpoints
Each endpoint MUST include:
- Description and purpose
- Request parameters and body schema
- Response schema for all status codes
- Example requests and responses
- Authentication requirements

### Rule: Include Error Documentation
All possible error responses MUST be documented with:
- Status code
- Error code
- When the error occurs
- How to resolve it

## 8. Error Handling Best Practices

### Rule: Provide Meaningful Error Messages
Error messages MUST be clear and actionable.
Include context about what went wrong and how to fix it.

### Rule: Include Request IDs
All error responses SHOULD include a unique request_id for tracing.

### Rule: Don't Leak Sensitive Information
Error messages MUST NOT expose:
- Database queries or structure
- Internal file paths
- Stack traces (in production)
- Credentials or tokens

## 9. Performance and Optimization

### Rule: Implement Pagination
Collection endpoints MUST support pagination for large datasets.
Use limit/offset or cursor-based pagination.

### Rule: Support Field Filtering
APIs SHOULD support field selection (e.g., ?fields=id,name,email).

### Rule: Enable Compression
APIs SHOULD support gzip compression for responses.

### Rule: Use Caching Headers
Appropriate Cache-Control headers MUST be set.

## 10. API Evolution and Deprecation

### Rule: Announce Deprecations
Deprecated endpoints MUST be announced with at least 6 months notice.

### Rule: Include Deprecation Headers
Deprecated endpoints SHOULD return Deprecation and Sunset headers.

### Rule: Maintain Backward Compatibility
Minor version updates MUST maintain backward compatibility.
"""


async def main():
    """Initialize ChromaDB with governance rules"""
    print("🚀 Initializing API Governance Rules...")
    print("=" * 60)
    
    try:
        # Create temporary file with rules
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_GOVERNANCE_RULES)
            temp_path = f.name
        
        print(f"📝 Created temporary rules file: {temp_path}")
        
        # Initialize ingestion pipeline
        print("🔧 Initializing ingestion pipeline...")
        ingestion = GovernanceIngestion()
        
        # Ingest rules
        print("📥 Ingesting governance rules into ChromaDB...")
        result = await ingestion.ingest_pdf(
            temp_path,
            metadata={
                "source": "API Governance Standards",
                "type": "governance_rules",
                "version": "1.0",
                "category": "REST API Design"
            }
        )
        
        print("\n✅ Ingestion Complete!")
        print("=" * 60)
        print(f"📊 Results:")
        print(f"   - Chunks created: {result.get('chunks_count', 'N/A')}")
        print(f"   - Status: {result.get('status', 'N/A')}")
        print(f"   - Collection ID: {result.get('collection_id', 'N/A')}")
        print("=" * 60)
        
        # Cleanup
        import os
        os.unlink(temp_path)
        print("🧹 Cleaned up temporary file")
        
        print("\n🎉 API Governance rules are now available!")
        print("   You can now use the validation and correction endpoints.")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
