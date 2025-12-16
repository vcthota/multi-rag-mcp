# GraphQL Schema Validator - Detailed Design

## Overview
Validates GraphQL schemas, performs linting, and generates centralized supergraph documentation from multiple subgraphs.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GraphQL Validator Service                         │
└─────────────────────────────────────────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│    Schema     │         │     Linter    │         │  Supergraph   │
│   Validator   │         │    Engine     │         │   Generator   │
└───────────────┘         └───────────────┘         └───────────────┘
        │                          │                          │
        └──────────────────────────┼──────────────────────────┘
                                   ▼
                         ┌───────────────────┐
                         │   Vector DB       │
                         │ (Schema Patterns) │
                         └───────────────────┘
```

## Component Details

### 1. Schema Validator

**Purpose**: Validate GraphQL schemas against best practices and federation requirements

**Validation Categories**:

1. **Syntax & Structure**
   - Valid GraphQL SDL syntax
   - Proper type definitions
   - Field type consistency
   - Directive usage

2. **Naming Conventions**
   - PascalCase for types and interfaces
   - camelCase for fields and arguments
   - SCREAMING_SNAKE_CASE for enums
   - Descriptive naming patterns

3. **Federation Compliance** (Apollo Federation / GraphQL Federation)
   - Proper @key directive usage
   - Entity definitions
   - Shareable fields
   - External field references

4. **Schema Design**
   - Nullable vs non-nullable fields
   - Connection patterns for pagination
   - Input type validation
   - Circular dependency detection

**Implementation**:
```python
class GraphQLSchemaValidator:
    """
    Validates GraphQL schemas against best practices
    """
    
    def __init__(self, vector_db, llm):
        self.vector_db = vector_db
        self.llm = llm
        self.graphql_validator = GraphQLValidator()
    
    async def validate_schema(self, schema_sdl: str) -> ValidationResult:
        # Parse SDL
        parsed_schema = self.parse_schema(schema_sdl)
        
        # Syntax validation
        syntax_errors = self.validate_syntax(parsed_schema)
        
        # Semantic validation
        semantic_errors = await self.validate_semantics(parsed_schema)
        
        # Best practices check
        best_practice_warnings = await self.check_best_practices(parsed_schema)
        
        # Federation validation
        federation_errors = self.validate_federation(parsed_schema)
        
        return ValidationResult(
            is_valid=len(syntax_errors + federation_errors) == 0,
            errors=syntax_errors + semantic_errors + federation_errors,
            warnings=best_practice_warnings,
            score=self.calculate_quality_score(parsed_schema)
        )
```

**Best Practice Patterns in Vector DB**:
```json
{
  "pattern_id": "gql-bp-001",
  "category": "pagination",
  "title": "Connection Pattern for Pagination",
  "description": "Use Connection pattern for list fields",
  "good_example": "type UserConnection { edges: [UserEdge!]! }",
  "bad_example": "type Query { users: [User!]! }",
  "severity": "medium",
  "auto_fixable": false,
  "documentation_link": "https://relay.dev/graphql/connections.htm"
}
```

### 2. Linter Engine

**Purpose**: Enforce GraphQL linting rules and style guidelines

**Linting Rules**:

1. **Type Rules**
   - No unused types
   - No duplicate type names
   - Consistent description format
   - Deprecation notices

2. **Field Rules**
   - Required descriptions
   - Argument validation
   - Return type appropriateness
   - Resolver complexity hints

3. **Query/Mutation Rules**
   - Input object usage for mutations
   - Query depth limits
   - Field naming conventions
   - Operation complexity

4. **Performance Rules**
   - N+1 query prevention hints
   - DataLoader recommendations
   - Batch field suggestions
   - Cost analysis annotations

**Implementation**:
```python
class GraphQLLinter:
    """
    Lints GraphQL schemas with configurable rules
    """
    
    def __init__(self, config: LinterConfig):
        self.config = config
        self.rules = self.load_linting_rules()
    
    async def lint_schema(self, schema_sdl: str) -> LintReport:
        parsed = parse_schema(schema_sdl)
        
        violations = []
        
        # Apply each rule
        for rule in self.rules:
            if rule.enabled:
                rule_violations = rule.check(parsed)
                violations.extend(rule_violations)
        
        # Retrieve similar issues from vector DB
        similar_issues = await self.get_similar_issues(violations)
        
        # Enhance with suggestions
        enhanced_violations = self.add_suggestions(
            violations, 
            similar_issues
        )
        
        return LintReport(
            violations=enhanced_violations,
            stats=self.calculate_stats(violations),
            auto_fix_available=self.count_auto_fixable(violations)
        )
    
    async def auto_fix(self, schema_sdl: str, violations: List[Violation]) -> str:
        """Auto-fix fixable violations"""
        fixed_schema = schema_sdl
        
        for violation in violations:
            if violation.auto_fixable:
                fixed_schema = violation.apply_fix(fixed_schema)
        
        return fixed_schema
```

**Linter Configuration**:
```yaml
# .graphql-lint.yml
rules:
  naming-convention:
    enabled: true
    severity: error
    config:
      types: PascalCase
      fields: camelCase
      enums: SCREAMING_SNAKE_CASE
  
  require-description:
    enabled: true
    severity: warning
    types: [Query, Mutation, Type]
  
  no-unused-types:
    enabled: true
    severity: error
  
  pagination-pattern:
    enabled: true
    severity: warning
    pattern: connection
  
  max-query-depth:
    enabled: true
    severity: error
    depth: 10
  
  require-deprecation-reason:
    enabled: true
    severity: error
```

### 3. Supergraph Generator

**Purpose**: Generate centralized documentation from multiple subgraph schemas

**Process Flow**:
```
Subgraph Schemas → Composition → Validation → 
Documentation Generation → Publishing
```

**Implementation**:
```python
class SupergraphGenerator:
    """
    Generates supergraph documentation from subgraphs
    """
    
    def __init__(self, vector_db, llm):
        self.vector_db = vector_db
        self.llm = llm
        self.composer = FederationComposer()
    
    async def generate_supergraph(
        self, 
        subgraphs: List[SubgraphSchema]
    ) -> SupergraphDocument:
        
        # Validate each subgraph
        validated_subgraphs = []
        for subgraph in subgraphs:
            validation = await self.validate_subgraph(subgraph)
            if not validation.is_valid:
                raise ValidationError(f"Invalid subgraph: {subgraph.name}")
            validated_subgraphs.append(subgraph)
        
        # Compose supergraph
        composed_schema = self.composer.compose(validated_subgraphs)
        
        # Validate composition
        composition_errors = self.validate_composition(composed_schema)
        if composition_errors:
            raise CompositionError(composition_errors)
        
        # Generate documentation
        documentation = await self.generate_documentation(
            composed_schema, 
            subgraphs
        )
        
        # Store in vector DB for searchability
        await self.index_supergraph(composed_schema, documentation)
        
        return SupergraphDocument(
            schema=composed_schema,
            documentation=documentation,
            subgraphs=subgraphs,
            metadata=self.generate_metadata(composed_schema)
        )
```

**Documentation Structure**:
```
supergraph-docs/
├── overview.md                 # Supergraph overview
├── schema.graphql              # Complete composed schema
├── types/
│   ├── query.md               # All queries
│   ├── mutation.md            # All mutations
│   ├── subscription.md        # All subscriptions
│   └── types/
│       ├── User.md
│       ├── Product.md
│       └── Order.md
├── subgraphs/
│   ├── users-service.md
│   ├── products-service.md
│   └── orders-service.md
├── federation/
│   ├── entities.md            # All federated entities
│   ├── keys.md                # Entity keys
│   └── composition-hints.md
└── api-reference.html         # Interactive docs
```

**Documentation Generation with LLM**:
```python
async def generate_type_documentation(
    self, 
    type_def: TypeDefinition,
    context: SchemaContext
) -> TypeDocumentation:
    """
    Generate rich documentation for a GraphQL type
    """
    
    # Retrieve similar types from vector DB
    similar_types = await self.vector_db.search(
        query_embedding=await self.embed(type_def.name),
        filter={"type": "graphql_type"},
        top_k=5
    )
    
    # Generate documentation with LLM
    prompt = f"""
    Generate comprehensive documentation for this GraphQL type:
    
    Type Definition:
    {type_def.sdl}
    
    Context:
    - Subgraph: {context.subgraph_name}
    - Related Types: {context.related_types}
    - Federation Role: {type_def.federation_role}
    
    Similar Types for Reference:
    {similar_types}
    
    Include:
    1. Overview and purpose
    2. Field descriptions with examples
    3. Usage examples (queries/mutations)
    4. Best practices
    5. Common patterns
    """
    
    documentation = await self.llm.generate(prompt)
    
    return TypeDocumentation(
        type_name=type_def.name,
        content=documentation,
        examples=self.extract_examples(documentation)
    )
```

### 4. Federation Composition

**Composition Validation**:
```python
class FederationComposer:
    """
    Composes multiple subgraph schemas into a supergraph
    """
    
    def compose(self, subgraphs: List[SubgraphSchema]) -> ComposedSchema:
        # Collect all type definitions
        all_types = self.collect_types(subgraphs)
        
        # Merge entity definitions
        entities = self.merge_entities(subgraphs)
        
        # Resolve field conflicts
        resolved_fields = self.resolve_conflicts(all_types)
        
        # Build supergraph schema
        supergraph = self.build_supergraph(resolved_fields, entities)
        
        # Validate composition rules
        self.validate_composition_rules(supergraph)
        
        return supergraph
    
    def validate_composition_rules(self, schema: ComposedSchema):
        """
        Validate federation composition rules
        """
        errors = []
        
        # Check entity key consistency
        for entity in schema.entities:
            if not self.validate_entity_keys(entity):
                errors.append(f"Invalid entity keys for {entity.name}")
        
        # Check for conflicting field types
        for field in schema.all_fields:
            if not self.validate_field_consistency(field):
                errors.append(f"Field type conflict: {field.name}")
        
        # Check shareable field rules
        for field in schema.shareable_fields:
            if not self.validate_shareable_field(field):
                errors.append(f"Invalid shareable field: {field.name}")
        
        if errors:
            raise CompositionError(errors)
```

### 5. API Endpoints

**REST API**:
```yaml
POST /api/v1/graphql/validate
  - Body: GraphQL schema (SDL)
  - Returns: ValidationResult

POST /api/v1/graphql/lint
  - Body: Schema SDL + linter config
  - Returns: LintReport

POST /api/v1/graphql/auto-fix
  - Body: Schema SDL + violations
  - Returns: Fixed schema

POST /api/v1/graphql/compose
  - Body: Array of subgraph schemas
  - Returns: Composed supergraph

POST /api/v1/graphql/generate-docs
  - Body: Supergraph + subgraphs
  - Returns: Documentation package

GET /api/v1/graphql/docs/{supergraph_id}
  - Returns: Generated documentation

POST /api/v1/graphql/subgraph/register
  - Body: Subgraph schema + metadata
  - Returns: Registration ID

GET /api/v1/graphql/subgraphs
  - Returns: List of registered subgraphs
```

## Data Models

### Validation Result
```python
class ValidationResult(BaseModel):
    validation_id: str
    timestamp: datetime
    is_valid: bool
    schema_hash: str
    errors: List[SchemaError]
    warnings: List[SchemaWarning]
    quality_score: float  # 0-100
    federation_compatible: bool
    
class SchemaError(BaseModel):
    error_id: str
    type: str  # syntax, semantic, federation
    severity: str  # error, warning
    location: Location
    message: str
    suggestion: Optional[str]
    
class Location(BaseModel):
    line: int
    column: int
    type_name: Optional[str]
    field_name: Optional[str]
```

### Supergraph Document
```python
class SupergraphDocument(BaseModel):
    supergraph_id: str
    version: str
    schema: str  # Complete SDL
    subgraphs: List[SubgraphInfo]
    entities: List[EntityInfo]
    documentation: Documentation
    created_at: datetime
    
class SubgraphInfo(BaseModel):
    name: str
    url: str
    schema: str
    version: str
    types_contributed: List[str]
    
class EntityInfo(BaseModel):
    name: str
    keys: List[str]
    contributing_subgraphs: List[str]
    resolvable_by: List[str]
```

## Vector DB Schema

**Collection**: `graphql_schemas`

**Document Structure**:
```json
{
  "id": "schema-uuid",
  "type": "graphql_type",
  "name": "User",
  "category": "entity",
  "fields": ["id", "name", "email"],
  "description": "Represents a user in the system",
  "best_practices": ["Use Connection pattern", "Add pagination"],
  "common_issues": ["Missing description", "N+1 queries"],
  "usage_examples": ["query { user(id: \"1\") { name } }"],
  "related_types": ["UserConnection", "UserEdge"],
  "federation_entity": true,
  "key_fields": ["id"],
  "subgraph": "users-service"
}
```

**Collection**: `graphql_patterns`

```json
{
  "id": "pattern-uuid",
  "pattern_name": "Connection Pattern",
  "category": "pagination",
  "description": "Relay-style cursor pagination",
  "example_sdl": "type UserConnection { edges: [...] }",
  "when_to_use": "For paginating large lists",
  "benefits": ["Cursor-based", "Forward/backward pagination"],
  "implementation_guide": "...",
  "related_patterns": ["Edge Pattern", "PageInfo"]
}
```

## Processing Workflow

### Complete Validation & Documentation Flow
```
1. Subgraph schemas submitted
   ↓
2. Individual schema validation
   - Syntax check
   - Semantic validation
   - Linting
   ↓
3. Federation composition
   - Entity merging
   - Conflict resolution
   - Composition validation
   ↓
4. Supergraph generation
   ↓
5. Documentation generation
   - Type documentation (LLM-enhanced)
   - API reference
   - Usage examples
   - Best practices
   ↓
6. Vector DB indexing
   - Schema embeddings
   - Pattern matching
   - Searchable documentation
   ↓
7. Publishing
   - Static site generation
   - API deployment
   - Version control
```

## Advanced Features

### 1. Schema Evolution
```python
class SchemaEvolutionAnalyzer:
    """
    Analyzes schema changes between versions
    """
    
    async def analyze_changes(
        self, 
        old_schema: str, 
        new_schema: str
    ) -> ChangeReport:
        
        # Detect breaking changes
        breaking = self.detect_breaking_changes(old_schema, new_schema)
        
        # Detect safe changes
        safe = self.detect_safe_changes(old_schema, new_schema)
        
        # Generate migration guide
        migration_guide = await self.generate_migration_guide(
            breaking, 
            safe
        )
        
        return ChangeReport(
            breaking_changes=breaking,
            safe_changes=safe,
            migration_guide=migration_guide
        )
```

### 2. Interactive Documentation
- GraphiQL/GraphQL Playground integration
- Auto-generated query builders
- Type explorer with search
- Real-time schema updates
- Version comparison

### 3. Schema Registry
- Centralized schema storage
- Version history
- Rollback capabilities
- Access control
- Webhook notifications

## Performance Optimizations

1. **Caching**:
   - Schema validation results (1 hour)
   - Composed supergraphs (until subgraph update)
   - Generated documentation (persistent)

2. **Parallel Processing**:
   - Concurrent subgraph validation
   - Parallel documentation generation
   - Batch embedding generation

3. **Incremental Updates**:
   - Only recompose affected types
   - Incremental documentation updates
   - Smart cache invalidation

## Integration Points

- **Apollo Router/Gateway**: Schema composition
- **GraphQL Code Generators**: Type generation
- **CI/CD Pipelines**: Pre-commit validation
- **Monitoring**: Schema usage analytics
- **Documentation Portals**: Gatsby, Docusaurus
