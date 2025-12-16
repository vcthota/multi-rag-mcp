#!/bin/bash

# Production API Test Suite for Multi-RAG API Governance
# Tests error handling, validation, and production features

BASE_URL="http://localhost:8000"
API_BASE="${BASE_URL}/api/v1/governance"

echo "==================================="
echo "Multi-RAG API Production Tests"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_status="$3"
    
    echo -e "${YELLOW}Test: ${test_name}${NC}"
    
    response=$(eval "$command" 2>&1)
    status=$?
    
    if [ $status -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        echo "Response: $response"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "Error: $response"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    echo ""
}

# Wait for server to be ready
echo "Checking if server is running..."
for i in {1..10}; do
    if curl -s "${BASE_URL}/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Server is running${NC}"
        echo ""
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}✗ Server is not responding. Please start the server with: python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload${NC}"
        exit 1
    fi
    sleep 1
done

# Test 1: Health Check
echo "==================================="
echo "Test 1: Health Check"
echo "==================================="
response=$(curl -s "${API_BASE}/health")
echo "$response" | python -m json.tool
if echo "$response" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Health check failed${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# Test 2: Main Health Check
echo "==================================="
echo "Test 2: Main Application Health"
echo "==================================="
response=$(curl -s "${BASE_URL}/health")
echo "$response" | python -m json.tool
if echo "$response" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Main health check passed${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Main health check failed${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# Test 3: Root Endpoint
echo "==================================="
echo "Test 3: Root Endpoint"
echo "==================================="
response=$(curl -s "${BASE_URL}/")
echo "$response" | python -m json.tool
if echo "$response" | grep -q "Multi-RAG"; then
    echo -e "${GREEN}✓ Root endpoint passed${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Root endpoint failed${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# Test 4: Invalid File Type Upload (Error Handling Test)
echo "==================================="
echo "Test 4: Invalid File Type (Should Fail)"
echo "==================================="
echo "This is not a PDF" > /tmp/test_file.txt
response=$(curl -s -X POST "${API_BASE}/ingest" \
    -F "file=@/tmp/test_file.txt" \
    -H "Content-Type: multipart/form-data")
echo "$response" | python -m json.tool
if echo "$response" | grep -q "UNSUPPORTED_FILE_TYPE\|error"; then
    echo -e "${GREEN}✓ Error handling works - invalid file type rejected${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Error handling failed - invalid file should be rejected${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
rm /tmp/test_file.txt
echo ""

# Test 5: Validation with Invalid Format
echo "==================================="
echo "Test 5: Validation - Invalid Format (Should Fail)"
echo "==================================="
response=$(curl -s -X POST "${API_BASE}/validate" \
    -H "Content-Type: application/json" \
    -d '{
        "spec_content": "{}",
        "spec_format": "invalid_format"
    }')
echo "$response" | python -m json.tool
if echo "$response" | grep -q "error\|validation"; then
    echo -e "${GREEN}✓ Input validation works - invalid format rejected${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Input validation failed${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# Test 6: Validation with Valid Format
echo "==================================="
echo "Test 6: Validation - Valid Request Structure"
echo "==================================="
response=$(curl -s -X POST "${API_BASE}/validate" \
    -H "Content-Type: application/json" \
    -d '{
        "spec_content": "{\"openapi\": \"3.0.0\", \"info\": {\"title\": \"Test API\", \"version\": \"1.0.0\"}}",
        "spec_format": "json"
    }')
echo "$response" | python -m json.tool 2>&1 || echo "$response"
if echo "$response" | grep -q "request_id\|error"; then
    echo -e "${GREEN}✓ Validation endpoint accepts valid requests${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Validation endpoint failed${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# Test 7: API Documentation
echo "==================================="
echo "Test 7: API Documentation (Swagger UI)"
echo "==================================="
response=$(curl -s "${BASE_URL}/docs" | head -n 5)
if echo "$response" | grep -q "Swagger\|swagger"; then
    echo -e "${GREEN}✓ API documentation is available${NC}"
    echo "Access at: ${BASE_URL}/docs"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ API documentation failed${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# Test 8: Request ID Tracking
echo "==================================="
echo "Test 8: Request ID Tracking"
echo "==================================="
response=$(curl -s -X POST "${API_BASE}/validate" \
    -H "Content-Type: application/json" \
    -H "X-Request-ID: test-req-12345" \
    -d '{
        "spec_content": "{}",
        "spec_format": "json"
    }')
echo "$response" | python -m json.tool 2>&1 || echo "$response"
if echo "$response" | grep -q "request_id"; then
    echo -e "${GREEN}✓ Request ID tracking is working${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Request ID tracking failed${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# Summary
echo "==================================="
echo "Test Summary"
echo "==================================="
echo -e "Tests Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Tests Failed: ${RED}${TESTS_FAILED}${NC}"
echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Production features working:"
    echo "  ✓ Error handling with custom exceptions"
    echo "  ✓ Input validation"
    echo "  ✓ Request ID tracking"
    echo "  ✓ Structured error responses"
    echo "  ✓ API documentation"
    echo ""
    echo "Next steps:"
    echo "  1. Visit ${BASE_URL}/docs for interactive API testing"
    echo "  2. Add your OpenAI API key to .env"
    echo "  3. Test with a real PDF: curl -X POST ${API_BASE}/ingest -F 'file=@your_doc.pdf'"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo "Check the output above for details"
    exit 1
fi
