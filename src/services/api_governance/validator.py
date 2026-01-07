"""
API Governance Service - Validation Engine
Validates API specifications against governance rules
"""
from typing import List, Dict, Any, Optional
import logging
import json
import yaml

from src.core.rag_engine.embeddings import get_embedding_model
from src.core.rag_engine.vector_store import get_vector_store
from src.core.rag_engine.llm_client import get_llm_client
from src.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GovernanceValidator:
    """API governance validation engine"""
    
    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.vector_store = get_vector_store(settings.PINECONE_INDEX_API_GOVERNANCE)
        self.llm_client = get_llm_client()
    
    async def validate_spec(
        self,
        spec_content: str,
        spec_format: str = "json",
        request_id: str = None
    ) -> Dict[str, Any]:
        """Validate API specification against governance rules"""
        
        log_extra = {"request_id": request_id} if request_id else {}
        logger.info("Starting API specification validation", extra=log_extra)
        
        try:
            # Parse the spec
            spec = self._parse_spec(spec_content, spec_format)
            
            # Extract features for validation
            features = self._extract_features(spec)
            
            # Retrieve relevant governance rules
            rules = await self._retrieve_rules(features)
            
            # Validate against rules
            violations = await self._check_violations(spec, features, rules)
            
            # Calculate compliance score (0.0 to 1.0)
            total_rules = len(rules)
            violations_count = len(violations)
            compliance_score = (
                max(0.0, ((total_rules - violations_count) / total_rules))
                if total_rules > 0 else 1.0
            )
            
            result = {
                "valid": len(violations) == 0,
                "compliance_score": compliance_score,
                "violations": violations,
                "rules_checked": total_rules,
                "features_analyzed": len(features)
            }
            
            logger.info(f"Validation complete. Compliance: {compliance_score * 100:.2f}%")
            return result
        
        except Exception as e:
            logger.error(f"Error validating spec: {e}")
            raise
    
    def _parse_spec(self, content: str, format: str) -> Dict[str, Any]:
        """Parse API specification"""
        
        if format.lower() == "json":
            return json.loads(content)
        elif format.lower() in ["yaml", "yml"]:
            return yaml.safe_load(content)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _extract_features(self, spec: Dict[str, Any]) -> List[str]:
        """Extract key features from API spec for validation"""
        
        features = []
        
        # OpenAPI/Swagger features
        if "openapi" in spec or "swagger" in spec:
            # Version
            version = spec.get("openapi") or spec.get("swagger")
            features.append(f"API Specification Version: {version}")
            
            # Info
            info = spec.get("info", {})
            if info.get("title"):
                features.append(f"API Title: {info['title']}")
            if info.get("version"):
                features.append(f"API Version: {info['version']}")
            
            # Paths/Endpoints
            paths = spec.get("paths", {})
            features.append(f"Number of Endpoints: {len(paths)}")
            
            for path, methods in paths.items():
                for method in methods.keys():
                    if method in ["get", "post", "put", "patch", "delete"]:
                        features.append(f"Endpoint: {method.upper()} {path}")
            
            # Security
            security = spec.get("security", [])
            if security:
                features.append(f"Security Schemes: {json.dumps(security)}")
            
            # Components/Definitions
            components = spec.get("components", {}) or spec.get("definitions", {})
            if components:
                schemas = components.get("schemas", components)
                features.append(f"Number of Schemas: {len(schemas)}")
        
        return features
    
    async def _retrieve_rules(self, features: List[str]) -> List[Dict[str, Any]]:
        """Retrieve relevant governance rules using vector search"""
        
        # Create query from features
        query_text = " ".join(features)
        logger.info(f"Retrieving rules for query: {query_text[:100]}...")
        
        # Generate embedding
        query_embedding = await self.embedding_model.embed(query_text)
        
        # Search vector DB - get top 10 most relevant rules
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=settings.RETRIEVAL_TOP_K,
            filter=None  # Get all governance rules
        )
        
        # Filter by similarity threshold (0.3 is reasonable for semantic search)
        similarity_threshold = 0.3
        rules = [
            result for result in results
            if result["score"] >= similarity_threshold
        ]
        
        logger.info(f"Retrieved {len(rules)} relevant governance rules (threshold: {similarity_threshold})")
        return rules
    
    async def _check_violations(
        self,
        spec: Dict[str, Any],
        features: List[str],
        rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for violations using LLM with retrieved governance rules"""
        
        if not rules:
            logger.warning("No governance rules retrieved for validation")
            return []
        
        violations = []
        
        # Prepare the full API spec as JSON for context
        spec_json = json.dumps(spec, indent=2)
        
        # Build comprehensive governance context from all retrieved rules
        governance_context = []
        for i, rule in enumerate(rules, 1):
            rule_text = rule["metadata"].get("text", "")
            score = rule["score"]
            chunk_index = rule["metadata"].get("chunk_index", "?")
            governance_context.append(
                f"[Rule {i} - Relevance: {score:.2f} - Chunk: {chunk_index}]\n{rule_text}"
            )
        
        all_rules_text = "\n\n".join(governance_context)
        
        # Create comprehensive validation prompt
        prompt = f"""You are an expert API governance validator. Your task is to validate an API specification against enterprise governance standards.

GOVERNANCE RULES (Retrieved from vector database):
{all_rules_text}

API SPECIFICATION TO VALIDATE:
{spec_json}

API FEATURES EXTRACTED:
{chr(10).join('- ' + f for f in features)}

VALIDATION TASK:
1. Analyze the API specification against ALL the governance rules provided above
2. Check for violations in these key areas:
   - URI/Resource naming conventions (nouns, plural, lowercase, hyphens)
   - HTTP methods and status codes usage
   - Request/response schema standards
   - Error handling and error model format
   - Security (authentication, authorization)
   - API versioning approach
   - Documentation completeness (OpenAPI standards)
   - Pagination, filtering, sorting
   
3. For each violation found, provide:
   - Which specific rule was violated
   - Why it's a violation
   - Severity (critical/high/medium/low)
   - Specific recommendation to fix it

Respond in JSON format with an array of violations:
{{
    "violations": [
        {{
            "rule_violated": "Brief description of the rule",
            "violation_details": "What exactly is wrong in the API spec",
            "severity": "critical|high|medium|low",
            "recommendation": "Specific steps to fix this violation",
            "examples": "Code example showing the fix (if applicable)"
        }}
    ],
    "summary": {{
        "total_violations": 0,
        "critical_count": 0,
        "high_count": 0,
        "medium_count": 0,
        "low_count": 0
    }}
}}

If NO violations are found, return an empty violations array with counts set to 0.
"""
        
        try:
            logger.info(f"Validating API spec against {len(rules)} governance rules using LLM...")
            
            response = await self.llm_client.generate_json(
                prompt=prompt,
                system_message="You are an expert API governance validator with deep knowledge of REST API best practices, OpenAPI standards, and enterprise API design patterns."
            )
            
            # Extract violations from LLM response
            violation_list = response.get("violations", [])
            summary = response.get("summary", {})
            
            logger.info(f"Validation complete. Found {summary.get('total_violations', len(violation_list))} violations")
            
            # Format violations for response
            for i, v in enumerate(violation_list, 1):
                violations.append({
                    "violation_number": i,
                    "rule": v.get("rule_violated", "Unknown rule"),
                    "details": v.get("violation_details", ""),
                    "severity": v.get("severity", "medium"),
                    "recommendation": v.get("recommendation", ""),
                    "examples": v.get("examples", "")
                })
            
        except Exception as e:
            logger.error(f"Error during LLM validation: {e}", exc_info=True)
            # Return a generic error violation
            violations.append({
                "violation_number": 1,
                "rule": "Validation Error",
                "details": f"Error occurred during validation: {str(e)}",
                "severity": "high",
                "recommendation": "Please check the API specification format and try again"
            })
        
        return violations


def get_validator_service() -> GovernanceValidator:
    """Get validator service instance"""
    return GovernanceValidator()
