"""
API Governance Service - Correction Engine
Automatically corrects API specification violations
"""
from typing import Dict, Any, List
import logging
import json

from src.core.rag_engine.llm_client import get_llm_client
from src.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GovernanceCorrector:
    """API governance correction engine"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
    
    async def correct_violations(
        self,
        spec_content: str,
        violations: List[Dict[str, Any]],
        spec_format: str = "json"
    ) -> Dict[str, Any]:
        """Automatically correct violations in API specification"""
        
        logger.info(f"Correcting {len(violations)} violations")
        
        if not violations:
            return {
                "corrected": False,
                "original_spec": spec_content,
                "corrected_spec": spec_content,
                "changes": [],
                "message": "No violations to correct"
            }
        
        try:
            # Build correction prompt
            violations_text = self._format_violations(violations)
            
            prompt = f"""You are an API governance expert. Fix the following API specification to resolve all governance violations.

Original API Specification ({spec_format}):
```{spec_format}
{spec_content}
```

Violations to Fix:
{violations_text}

Instructions:
1. Analyze each violation carefully
2. Apply the recommended fixes to the specification
3. Ensure the output is valid {spec_format}
4. Maintain all existing functionality while fixing violations
5. Add comments explaining what was changed

Respond in JSON format:
{{
    "corrected_spec": "the full corrected specification",
    "changes_made": [
        {{
            "violation": "which violation was fixed",
            "change": "what was changed",
            "location": "where in the spec"
        }}
    ]
}}
"""
            
            response = await self.llm_client.generate_json(
                prompt=prompt,
                system_message="You are an expert at API governance and OpenAPI/Swagger specifications.",
                temperature=0.3,  # Lower temperature for more consistent corrections
                max_tokens=4000
            )
            
            corrected_spec = response.get("corrected_spec", spec_content)
            changes = response.get("changes_made", [])
            
            # Convert corrected_spec to string if it's a dict
            if isinstance(corrected_spec, dict):
                corrected_spec = json.dumps(corrected_spec, indent=2)
            
            # Validate the corrected spec is valid JSON/YAML
            if spec_format.lower() == "json":
                json.loads(corrected_spec)
            
            logger.info(f"Applied {len(changes)} corrections")
            
            return {
                "corrected": True,
                "original_spec": spec_content,
                "corrected_spec": corrected_spec,
                "changes": changes,
                "violations_fixed": len(violations)
            }
        
        except Exception as e:
            logger.error(f"Error correcting violations: {e}")
            raise
    
    def _format_violations(self, violations: List[Dict[str, Any]]) -> str:
        """Format violations for prompt"""
        
        formatted = []
        for i, violation in enumerate(violations, 1):
            formatted.append(f"""
Violation {i}:
- Severity: {violation.get('severity', 'unknown')}
- Issue: {violation.get('reason', 'No reason provided')}
- Recommendation: {violation.get('recommendation', 'No recommendation')}
- Rule: {violation.get('rule', 'N/A')}
""")
        
        return "\n".join(formatted)
    
    async def suggest_improvements(
        self,
        spec_content: str,
        spec_format: str = "json"
    ) -> List[Dict[str, Any]]:
        """Suggest improvements beyond compliance"""
        
        prompt = f"""Analyze this API specification and suggest improvements for:
- Security best practices
- Documentation completeness
- Error handling
- Versioning strategy
- Performance considerations

API Specification:
```{spec_format}
{spec_content[:2000]}  # First 2000 chars for context
```

Provide 3-5 actionable suggestions in JSON format:
{{
    "suggestions": [
        {{
            "category": "security/documentation/error-handling/etc",
            "suggestion": "what to improve",
            "benefit": "why this helps",
            "priority": "high/medium/low"
        }}
    ]
}}
"""
        
        try:
            response = await self.llm_client.generate_json(
                prompt=prompt,
                system_message="You are an API design expert.",
                temperature=0.5
            )
            
            return response.get("suggestions", [])
        
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []


def get_corrector_service() -> GovernanceCorrector:
    """Get corrector service instance"""
    return GovernanceCorrector()
