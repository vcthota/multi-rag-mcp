"""
Test API Governance Validator
Validates a sample API specification against governance rules from vector DB
"""
import asyncio
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# Sample API Spec with some violations
SAMPLE_API_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Orders API",
        "version": "1.0.0",
        "description": "API for managing orders"
    },
    "paths": {
        "/createOrder": {  # VIOLATION: Using verb in URI
            "post": {
                "summary": "Create a new order",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "orderId": {"type": "string"},
                                    "amount": {"type": "number"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {  # VIOLATION: Should be 201 for resource creation
                        "description": "Order created"
                    }
                }
            }
        },
        "/getUserDetails/{id}": {  # VIOLATION: Using verb and camelCase
            "get": {
                "summary": "Get user details",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Success"
                    }
                }
            }
        }
    }
    # VIOLATION: Missing security schemes
    # VIOLATION: No error model defined
    # VIOLATION: No pagination support
}

# Good API Spec for comparison
GOOD_API_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Orders API",
        "version": "1.0.0",
        "description": "API for managing orders"
    },
    "paths": {
        "/api/v1/orders": {
            "get": {
                "summary": "List all orders",
                "parameters": [
                    {
                        "name": "page",
                        "in": "query",
                        "schema": {"type": "integer", "default": 1}
                    },
                    {
                        "name": "size",
                        "in": "query",
                        "schema": {"type": "integer", "default": 20}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "data": {"type": "array"},
                                        "meta": {"type": "object"},
                                        "links": {"type": "object"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {"$ref": "#/components/responses/BadRequest"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                    "500": {"$ref": "#/components/responses/InternalError"}
                }
            },
            "post": {
                "summary": "Create a new order",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/OrderCreate"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Order created",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Order"}
                            }
                        }
                    },
                    "400": {"$ref": "#/components/responses/BadRequest"},
                    "401": {"$ref": "#/components/responses/Unauthorized"}
                }
            }
        },
        "/api/v1/orders/{orderId}": {
            "get": {
                "summary": "Get order by ID",
                "parameters": [
                    {
                        "name": "orderId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Order"}
                            }
                        }
                    },
                    "404": {"$ref": "#/components/responses/NotFound"}
                }
            }
        }
    },
    "components": {
        "schemas": {
            "Order": {
                "type": "object",
                "properties": {
                    "orderId": {"type": "string"},
                    "amount": {"type": "number"},
                    "status": {"type": "string"}
                }
            },
            "OrderCreate": {
                "type": "object",
                "required": ["amount"],
                "properties": {
                    "amount": {"type": "number"},
                    "customerId": {"type": "string"}
                }
            },
            "Error": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "message": {"type": "string"},
                    "details": {"type": "string"},
                    "traceId": {"type": "string"}
                }
            }
        },
        "responses": {
            "BadRequest": {
                "description": "Bad request",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                }
            },
            "Unauthorized": {
                "description": "Unauthorized",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                }
            },
            "NotFound": {
                "description": "Resource not found",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                }
            },
            "InternalError": {
                "description": "Internal server error",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                }
            }
        },
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    },
    "security": [
        {"bearerAuth": []}
    ]
}


async def test_validation(spec: dict, spec_name: str):
    """Test validation for a given API spec"""
    
    logger.info("=" * 100)
    logger.info(f"TESTING: {spec_name}")
    logger.info("=" * 100)
    
    try:
        from src.services.api_governance.validator import get_validator_service
        
        # Get validator
        validator = get_validator_service()
        
        # Convert spec to JSON string
        spec_json = json.dumps(spec, indent=2)
        
        # Validate
        result = await validator.validate_spec(spec_json, spec_format="json")
        
        # Display results
        print("\n" + "=" * 100)
        print(f"VALIDATION RESULTS: {spec_name}")
        print("=" * 100)
        print(f"Valid: {result['valid']}")
        print(f"Compliance Score: {result['compliance_score']:.2f}%")
        print(f"Rules Checked: {result['rules_checked']}")
        print(f"Features Analyzed: {result['features_analyzed']}")
        print(f"Violations Found: {len(result['violations'])}")
        
        if result['violations']:
            print("\n" + "-" * 100)
            print("VIOLATIONS DETAILS:")
            print("-" * 100)
            
            for violation in result['violations']:
                print(f"\n[Violation #{violation.get('violation_number', '?')}]")
                print(f"Severity: {violation['severity'].upper()}")
                print(f"Rule: {violation['rule']}")
                print(f"Details: {violation['details']}")
                print(f"Recommendation: {violation['recommendation']}")
                if violation.get('examples'):
                    print(f"Example: {violation['examples']}")
                print("-" * 100)
        else:
            print("\n✅ No violations found! API spec is compliant with governance rules.")
        
        print("=" * 100 + "\n")
        
        return result
        
    except Exception as e:
        logger.error(f"Validation test failed: {e}", exc_info=True)
        raise


async def main():
    """Run validation tests"""
    
    print("\n" + "=" * 100)
    print("API GOVERNANCE VALIDATION TEST")
    print("=" * 100)
    print("\nThis test will validate two API specifications:")
    print("1. BAD API Spec - Contains multiple violations")
    print("2. GOOD API Spec - Follows all governance rules")
    print("=" * 100 + "\n")
    
    # Test 1: Bad API Spec (with violations)
    print("\n>>> TEST 1: Validating BAD API Spec (Expected: Multiple violations)")
    bad_result = await test_validation(SAMPLE_API_SPEC, "BAD API Spec")
    
    # Test 2: Good API Spec (compliant)
    print("\n>>> TEST 2: Validating GOOD API Spec (Expected: No violations)")
    good_result = await test_validation(GOOD_API_SPEC, "GOOD API Spec")
    
    # Summary
    print("\n" + "=" * 100)
    print("VALIDATION TEST SUMMARY")
    print("=" * 100)
    print(f"BAD Spec Compliance: {bad_result['compliance_score']:.2f}% | Violations: {len(bad_result['violations'])}")
    print(f"GOOD Spec Compliance: {good_result['compliance_score']:.2f}% | Violations: {len(good_result['violations'])}")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
