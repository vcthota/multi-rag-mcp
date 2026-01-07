"""
Test API Governance Corrector
Tests the automatic correction of API specification violations
"""
import asyncio
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# Bad API Spec with violations
BAD_API_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Orders API",
        "version": "1.0.0"
    },
    "paths": {
        "/createOrder": {  # VIOLATION: verb in URI
            "post": {
                "summary": "Create order",
                "responses": {
                    "200": {  # VIOLATION: should be 201
                        "description": "Success"
                    }
                }
            }
        },
        "/getUserDetails/{id}": {  # VIOLATION: verb + camelCase
            "get": {
                "summary": "Get user",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {"description": "Success"}
                }
            }
        }
    }
}


# Sample violations from validator
SAMPLE_VIOLATIONS = [
    {
        "violation_number": 1,
        "rule": "URI Naming Standards",
        "details": "The endpoint '/createOrder' uses a verb. API endpoints should be named using nouns.",
        "severity": "high",
        "recommendation": "Rename '/createOrder' to '/orders' to follow RESTful naming conventions.",
        "examples": "POST /orders"
    },
    {
        "violation_number": 2,
        "rule": "HTTP Status Codes",
        "details": "POST endpoint returns 200 instead of 201 for resource creation.",
        "severity": "medium",
        "recommendation": "Change response status code to 201 (Created) for resource creation.",
        "examples": '"201": { "description": "Order created" }'
    },
    {
        "violation_number": 3,
        "rule": "URI Naming Standards",
        "details": "The endpoint '/getUserDetails/{id}' uses a verb and camelCase.",
        "severity": "high",
        "recommendation": "Rename '/getUserDetails/{id}' to '/users/{id}' using lowercase with hyphens.",
        "examples": "GET /users/{id}"
    }
]


async def test_corrector():
    """Test the corrector service"""
    
    print("\n" + "=" * 100)
    print("API GOVERNANCE CORRECTOR TEST")
    print("=" * 100)
    
    try:
        from src.services.api_governance.corrector import get_corrector_service
        
        # Get corrector service
        corrector = get_corrector_service()
        
        # Convert spec to JSON string
        spec_json = json.dumps(BAD_API_SPEC, indent=2)
        
        print("\n📝 ORIGINAL API SPECIFICATION (WITH VIOLATIONS):")
        print("-" * 100)
        print(spec_json)
        print("-" * 100)
        
        print("\n🔍 VIOLATIONS TO FIX:")
        print("-" * 100)
        for v in SAMPLE_VIOLATIONS:
            print(f"\n{v['violation_number']}. [{v['severity'].upper()}] {v['rule']}")
            print(f"   Problem: {v['details']}")
            print(f"   Fix: {v['recommendation']}")
        print("-" * 100)
        
        print("\n🔧 APPLYING AUTOMATIC CORRECTIONS...")
        print("Please wait, this may take 20-30 seconds...\n")
        
        # Apply corrections
        result = await corrector.correct_violations(
            spec_content=spec_json,
            violations=SAMPLE_VIOLATIONS,
            spec_format="json"
        )
        
        print("\n" + "=" * 100)
        print("CORRECTION RESULTS")
        print("=" * 100)
        
        print(f"\nCorrected: {result['corrected']}")
        print(f"Violations Fixed: {result.get('violations_fixed', 0)}")
        print(f"Changes Made: {len(result.get('changes', []))}")
        
        # Display changes
        if result.get('changes'):
            print("\n📋 CHANGES MADE:")
            print("-" * 100)
            for i, change in enumerate(result['changes'], 1):
                print(f"\n{i}. Violation Fixed: {change.get('violation', 'N/A')}")
                print(f"   Change: {change.get('change', 'N/A')}")
                print(f"   Location: {change.get('location', 'N/A')}")
            print("-" * 100)
        
        # Display corrected spec
        print("\n✅ CORRECTED API SPECIFICATION:")
        print("-" * 100)
        corrected_spec = result.get('corrected_spec', '')
        
        # Try to format it nicely
        try:
            corrected_obj = json.loads(corrected_spec)
            print(json.dumps(corrected_obj, indent=2))
        except:
            print(corrected_spec)
        print("-" * 100)
        
        # Compare before and after
        print("\n📊 COMPARISON:")
        print("-" * 100)
        print(f"Original Length: {len(spec_json)} characters")
        print(f"Corrected Length: {len(corrected_spec)} characters")
        
        # Check specific fixes
        print("\n🔍 VERIFICATION:")
        if '/orders' in corrected_spec and '/createOrder' not in corrected_spec:
            print("✅ Fixed: /createOrder → /orders")
        else:
            print("❌ Not fixed: /createOrder still present")
        
        if '/users/' in corrected_spec and '/getUserDetails/' not in corrected_spec:
            print("✅ Fixed: /getUserDetails/{id} → /users/{id}")
        else:
            print("❌ Not fixed: /getUserDetails still present")
        
        if '"201"' in corrected_spec:
            print("✅ Fixed: Status code changed to 201")
        else:
            print("❌ Not fixed: Status code still 200")
        
        print("-" * 100)
        
        # Test suggestions feature
        print("\n\n" + "=" * 100)
        print("TESTING IMPROVEMENT SUGGESTIONS")
        print("=" * 100)
        
        print("\n🔍 Generating improvement suggestions...")
        suggestions = await corrector.suggest_improvements(
            spec_content=corrected_spec,
            spec_format="json"
        )
        
        if suggestions:
            print(f"\n💡 FOUND {len(suggestions)} SUGGESTIONS:")
            print("-" * 100)
            for i, suggestion in enumerate(suggestions, 1):
                print(f"\n{i}. [{suggestion.get('priority', 'medium').upper()}] {suggestion.get('category', 'N/A')}")
                print(f"   Suggestion: {suggestion.get('suggestion', 'N/A')}")
                print(f"   Benefit: {suggestion.get('benefit', 'N/A')}")
            print("-" * 100)
        else:
            print("\n⚠️ No suggestions generated")
        
        print("\n" + "=" * 100)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 100)
        
        return result
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n❌ ERROR: {e}")
        raise


async def main():
    """Run the corrector test"""
    try:
        await test_corrector()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
