"""
Test UI validation through API endpoint
"""
import asyncio
import httpx
import json

async def test_validation():
    """Test the validation endpoint that UI uses"""
    
    api_url = "http://localhost:8000"
    
    # Test spec
    test_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0"
        },
        "paths": {
            "/createUser": {
                "post": {
                    "summary": "Create user",
                    "responses": {
                        "200": {
                            "description": "Success"
                        }
                    }
                }
            }
        }
    }
    
    spec_content = json.dumps(test_spec)
    
    print("=" * 80)
    print("Testing API Validation Endpoint")
    print("=" * 80)
    
    url = f"{api_url}/api/v1/governance/validate"
    
    payload = {
        "spec_content": spec_content,
        "spec_format": "json"
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            print(f"\n📤 Sending request to: {url}")
            print(f"📝 Spec content length: {len(spec_content)} characters\n")
            
            response = await client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"✅ Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n" + "=" * 80)
                print("VALIDATION RESULTS")
                print("=" * 80)
                
                print(f"\n📊 Valid: {result['valid']}")
                print(f"📊 Compliance Score: {result['compliance_score'] * 100:.1f}%")
                print(f"📊 Rules Checked: {result['rules_checked']}")
                print(f"📊 Violations Found: {len(result['violations'])}")
                print(f"📊 Features Analyzed: {result['features_analyzed']}")
                
                if result['violations']:
                    print(f"\n❌ VIOLATIONS:")
                    print("-" * 80)
                    for v in result['violations']:
                        print(f"\n{v['violation_number']}. [{v['severity'].upper()}] {v['rule']}")
                        print(f"   Details: {v['details']}")
                        print(f"   Recommendation: {v['recommendation']}")
                
                print("\n" + "=" * 80)
                print("✅ TEST PASSED - Validation endpoint working correctly!")
                print("=" * 80)
                
                return True
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_validation())
    exit(0 if success else 1)
