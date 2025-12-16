# API Governance Assistant - Detailed Design

## Overview
Validates API specifications against governance rules stored in vector DB, identifies violations, and provides corrected specifications.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      API Governance Service                          │
└─────────────────────────────────────────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│   Ingestion   │         │  Validation   │         │  Correction   │
│   Pipeline    │         │    Engine     │         │    Engine     │
└───────────────┘         └───────────────┘         └───────────────┘
        │                          │                          │
        └──────────────────────────┼──────────────────────────┘
                                   ▼
                         ┌───────────────────┐
                         │   Vector DB       │
                         │ (Governance Rules)│
                         └───────────────────┘
```

## Component Details

### 1. Ingestion Pipeline

**Purpose**: Process and store API governance specifications in Vector DB

**Process Flow**:
```
PDF Upload → Text Extraction → Chunking → Embedding → Vector Storage
```

**Implementation**:
```python
class GovernanceIngestionPipeline:
    """
    Ingests API governance specification PDFs into vector database
    """
    
    def __init__(self, vector_db, embedding_model, llm):
        self.vector_db = vector_db
        self.embedding_model = embedding_model
        self.llm = llm
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    async def ingest_governance_pdf(self, pdf_path: str) -> dict:
        # Extract text from PDF
        documents = self.extract_pdf_content(pdf_path)
        
        # Parse and structure governance rules
        rules = self.parse_governance_rules(documents)
        
        # Create chunks with metadata
        chunks = self.create_semantic_chunks(rules)
        
        # Generate embeddings
        embeddings = await self.generate_embeddings(chunks)
        
        # Store in vector DB with metadata
        await self.store_in_vector_db(chunks, embeddings)
        
        return {"status": "success", "rules_count": len(rules)}
```

**Key Features**:
- PDF text extraction (PyPDF2, pdfplumber)
- Intelligent chunking (preserve rule context)
- Rule categorization (naming, versioning, security, etc.)
- Metadata tagging (severity, category, examples)
- Incremental updates (version control)

**Metadata Structure**:
```json
{
  "rule_id": "API-GOV-001",
  "category": "naming_convention",
  "severity": "high",
  "description": "API endpoints must use kebab-case",
  "examples": ["good: /user-profile", "bad: /userProfile"],
  "violation_message": "Endpoint names must use kebab-case",
  "auto_correctable": true,
  "version": "1.0"
}
```

### 2. Validation Engine

**Purpose**: Validate input API specifications against governance rules

**Process Flow**:
```
API Spec Input → Parse Spec → Extract Features → Vector Search → 
Rule Matching → Violation Detection → Report Generation
```

**Implementation**:
```python
class APISpecValidator:
    """
    Validates API specifications against governance rules
    """
    
    async def validate_specification(
        self, 
        spec: dict,  # OpenAPI/Swagger spec
        format: str = "openapi"
    ) -> ValidationReport:
        
        # Parse specification
        parsed_spec = self.parse_spec(spec, format)
        
        # Extract key features
        features = self.extract_features(parsed_spec)
        
        # Retrieve relevant governance rules
        relevant_rules = await self.retrieve_rules(features)
        
        # Validate against each rule
        violations = []
        for rule in relevant_rules:
            violation = self.check_rule(parsed_spec, rule)
            if violation:
                violations.append(violation)
        
        # Generate detailed report
        return self.generate_report(violations, parsed_spec)
```

**Validation Categories**:

1. **Naming Conventions**
   - Endpoint naming (kebab-case, camelCase, snake_case)
   - Resource naming standards
   - HTTP method appropriateness

2. **Versioning**
   - Version format (v1, v1.0, 2023-01-01)
   - Version placement (URL, header)
   - Deprecation policies

3. **Authentication & Security**
   - Required authentication methods
   - API key formats
   - OAuth 2.0 flows
   - Rate limiting requirements

4. **Request/Response Standards**
   - Required headers
   - Content-Type restrictions
   - Error response format
   - Pagination standards

5. **Documentation**
   - Description completeness
   - Example presence
   - Schema definitions
   - Response codes documentation

**Rule Retrieval Strategy**:
```python
async def retrieve_rules(self, features: dict) -> List[Rule]:
    """
    Hybrid retrieval: Vector search + metadata filtering
    """
    # Generate query embedding from features
    query_text = self.create_query_from_features(features)
    query_embedding = await self.embedding_model.encode(query_text)
    
    # Vector search with metadata filters
    results = await self.vector_db.search(
        embedding=query_embedding,
        filter={
            "category": {"$in": features["categories"]},
            "severity": {"$gte": "medium"}
        },
        top_k=20
    )
    
    # Rerank by relevance
    rules = self.rerank_rules(results, features)
    
    return rules
```

### 3. Correction Engine

**Purpose**: Generate corrected API specification based on violations

**Process Flow**:
```
Violations → Rule Examples → LLM Prompt → Corrected Spec → 
Validation → Final Output
```

**Implementation**:
```python
class APISpecCorrector:
    """
    Automatically corrects API specification violations
    """
    
    async def correct_specification(
        self,
        original_spec: dict,
        violations: List[Violation]
    ) -> CorrectedSpec:
        
        corrections = []
        
        for violation in violations:
            if violation.auto_correctable:
                # Retrieve correction examples
                examples = await self.get_correction_examples(violation)
                
                # Generate correction with LLM
                correction = await self.generate_correction(
                    violation, 
                    examples,
                    original_spec
                )
                
                corrections.append(correction)
        
        # Apply corrections
        corrected_spec = self.apply_corrections(original_spec, corrections)
        
        # Re-validate
        validation = await self.validator.validate_specification(corrected_spec)
        
        return {
            "corrected_spec": corrected_spec,
            "corrections_applied": corrections,
            "remaining_violations": validation.violations
        }
```

**LLM Prompt Template**:
```python
CORRECTION_PROMPT = """
You are an API governance expert. Given an API specification violation, 
correct it according to the governance rules.

Original Specification:
{original_spec}

Violation:
- Rule: {rule_name}
- Description: {rule_description}
- Current Issue: {violation_details}

Governance Rule Examples:
{rule_examples}

Provide the corrected specification section in {format} format.
Only modify the parts necessary to fix the violation.

Corrected Specification:
"""
```

### 4. API Endpoints

**REST API**:
```yaml
POST /api/v1/governance/ingest
  - Upload governance PDF
  - Returns: ingestion_id, rules_count

POST /api/v1/governance/validate
  - Body: API specification (JSON/YAML)
  - Returns: ValidationReport with violations

POST /api/v1/governance/correct
  - Body: API specification + violations
  - Returns: Corrected specification

GET /api/v1/governance/rules
  - Query: category, severity
  - Returns: List of governance rules

GET /api/v1/governance/validate/{id}
  - Returns: Validation report for async validation
```

## Data Models

### Validation Report
```python
class ValidationReport(BaseModel):
    validation_id: str
    timestamp: datetime
    specification_format: str
    total_rules_checked: int
    violations: List[Violation]
    compliance_score: float  # 0-100
    severity_breakdown: Dict[str, int]
    
class Violation(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    severity: str  # critical, high, medium, low
    location: str  # Path in spec where violation occurs
    description: str
    current_value: Any
    expected_value: Any
    auto_correctable: bool
    correction_suggestion: Optional[str]
```

## Vector DB Schema

**Collection**: `api_governance_rules`

**Namespace Structure**:
```
api_governance_rules/
├── naming_conventions/
├── versioning/
├── authentication/
├── request_response/
├── documentation/
└── security/
```

**Vector Metadata**:
```json
{
  "id": "rule-uuid",
  "rule_id": "API-GOV-001",
  "category": "naming_convention",
  "subcategory": "endpoint_naming",
  "severity": "high",
  "title": "Endpoint Naming Convention",
  "description": "All API endpoints must use kebab-case",
  "examples_good": ["GET /user-profile", "POST /order-items"],
  "examples_bad": ["GET /userProfile", "POST /orderItems"],
  "correction_pattern": "Convert camelCase to kebab-case",
  "auto_correctable": true,
  "related_rules": ["API-GOV-002", "API-GOV-003"],
  "version": "1.0",
  "last_updated": "2025-12-14"
}
```

## Processing Workflow

### Complete Validation Flow
```
1. Client submits API specification (OpenAPI/Swagger)
   ↓
2. Parser extracts endpoints, methods, schemas
   ↓
3. Feature extractor identifies key characteristics
   ↓
4. Vector search retrieves relevant governance rules (top-20)
   ↓
5. Rule matcher applies each rule to specification
   ↓
6. Violation detector identifies non-compliant elements
   ↓
7. For auto-correctable violations:
   - Retrieve correction examples from vector DB
   - Generate correction with LLM + examples
   - Apply correction to specification
   ↓
8. Generate comprehensive report:
   - Violations list with severity
   - Compliance score
   - Corrected specification (if requested)
   - Correction diff
   ↓
9. Store validation history in PostgreSQL
   ↓
10. Return report to client
```

## Performance Optimizations

1. **Caching**:
   - Cache governance rules (Redis, 1 hour TTL)
   - Cache embeddings for common queries
   - Cache validation results (5 minutes)

2. **Batch Processing**:
   - Validate multiple endpoints concurrently
   - Batch embedding generation
   - Parallel rule checking

3. **Async Processing**:
   - Queue large specification validations
   - Background correction generation
   - Webhook notifications for completion

## Monitoring & Metrics

- Validation requests per minute
- Average validation time
- Compliance score trends
- Most common violations
- Auto-correction success rate
- LLM token usage
- Vector DB query latency
