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
        self.vector_store = get_vector_store(settings.PINECONE_INDEX_GOVERNANCE)
        self.llm_client = get_llm_client()
    
    async def validate_spec(
        self,
        spec_content: str,
        spec_format: str = "json"
    ) -> Dict[str, Any]:
        """Validate API specification against governance rules"""
        
        logger.info("Starting API specification validation")
        
        try:
            # Parse the spec
            spec = self._parse_spec(spec_content, spec_format)
            
            # Extract features for validation
            features = self._extract_features(spec)
            
            # Retrieve relevant governance rules
            rules = await self._retrieve_rules(features)
            
            # Validate against rules
            violations = await self._check_violations(spec, features, rules)
            
            # Calculate compliance score
            total_rules = len(rules)
            violations_count = len(violations)
            compliance_score = (
                ((total_rules - violations_count) / total_rules * 100)
                if total_rules > 0 else 100.0
            )
            
            result = {
                "valid": len(violations) == 0,
                "compliance_score": compliance_score,
                "violations": violations,
                "rules_checked": total_rules,
                "features_analyzed": len(features)
            }
            
            logger.info(f"Validation complete. Compliance: {compliance_score:.2f}%")
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
        
        # Generate embedding
        query_embedding = await self.embedding_model.embed(query_text)
        
        # Search vector DB
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=settings.TOP_K,
            filter={"type": "governance_rule"}
        )
        
        # Filter by similarity threshold
        rules = [
            result for result in results
            if result["score"] >= settings.SIMILARITY_THRESHOLD
        ]
        
        logger.info(f"Retrieved {len(rules)} relevant governance rules")
        return rules
    
    async def _check_violations(
        self,
        spec: Dict[str, Any],
        features: List[str],
        rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for violations using LLM"""
        
        violations = []
        
        # Group rules by relevance score
        high_priority_rules = [r for r in rules if r["score"] >= 0.9]
        
        # Check high priority rules with LLM
        for rule in high_priority_rules:
            rule_text = rule["metadata"].get("text", "")
            
            prompt = f"""You are an API governance validator. Check if the following API specification violates this governance rule.

Governance Rule:
{rule_text}

API Features:
{chr(10).join(features)}

Analyze if there is a violation. Respond in JSON format:
{{
    "violated": true/false,
    "reason": "explanation if violated",
    "severity": "high/medium/low",
    "recommendation": "how to fix"
}}
"""
            
            try:
                response = await self.llm_client.generate_json(
                    prompt=prompt,
                    system_message="You are an API governance expert."
                )
                
                if response.get("violated"):
                    violations.append({
                        "rule": rule_text[:200] + "..." if len(rule_text) > 200 else rule_text,
                        "reason": response.get("reason"),
                        "severity": response.get("severity", "medium"),
                        "recommendation": response.get("recommendation"),
                        "rule_id": rule["id"]
                    })
            
            except Exception as e:
                logger.error(f"Error checking rule: {e}")
        
        return violations


def get_validator_service() -> GovernanceValidator:
    """Get validator service instance"""
    return GovernanceValidator()
