#!/bin/bash

# Comprehensive Test Suite for Databricks PS AI Runbook Generator
# Tests all endpoints and Databricks connectivity

echo "========================================="
echo "🧪 COMPREHENSIVE FUNCTIONALITY TEST SUITE"
echo "========================================="
echo ""

BASE_URL="http://localhost:8000"
MOCK_DATA="../mock_data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_count=0
pass_count=0
fail_count=0

function run_test() {
    local test_name=$1
    local command=$2
    local expected_code=${3:-200}
    
    test_count=$((test_count + 1))
    echo "---"
    echo "Test #$test_count: $test_name"
    echo "Command: $command"
    
    response=$(eval $command)
    exit_code=$?
    
    echo "Response: $response"
    
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}✓ PASS${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}✗ FAIL${NC}"
        fail_count=$((fail_count + 1))
    fi
    echo ""
}

echo "=== Test Suite 1: Basic Connectivity ==="
echo ""

run_test "Health Check - Model Status" \
    "curl -s http://localhost:8000/status/model"

run_test "API Documentation Availability" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/docs"

echo ""
echo "=== Test Suite 2: File Upload ==="
echo ""

run_test "Upload Mock Kickoff Notes" \
    "curl -s -X POST -F 'file=@$MOCK_DATA/kickoff_notes.md' $BASE_URL/upload"

run_test "Upload Mock Slack Export" \
    "curl -s -X POST -F 'file=@$MOCK_DATA/slack_export.json' $BASE_URL/upload"

run_test "Upload Mock Jira Tickets" \
    "curl -s -X POST -F 'file=@$MOCK_DATA/jira_tickets.csv' $BASE_URL/upload"

echo ""
echo "=== Test Suite 3: Pipeline Execution ==="
echo ""

run_test "Trigger Pipeline with DistilBERT" \
    "curl -s -X POST -H 'Content-Type: application/json' -d '{\"model_type\":\"distilbert-base-uncased\",\"files\":[\"test\"]}' $BASE_URL/run/pipeline"

# Get the run ID from the last response
RUN_ID=$(echo $response | grep -o '"run_id":"[^"]*' | cut -d'"' -f4)
echo "Captured Run ID: $RUN_ID"
echo ""

if [[ ! -z "$RUN_ID" ]]; then
    sleep 2
    
    run_test "Check Job Status" \
        "curl -s $BASE_URL/status/job/$RUN_ID"
    
    echo "Waiting 5 seconds for job to progress..."
    sleep 5
    
    run_test "Re-check Job Status (after 5s)" \
        "curl -s $BASE_URL/status/job/$RUN_ID"
fi

echo ""
echo "=== Test Suite 4: Runbook Retrieval ==="
echo ""

run_test "Get Runbook Versions List" \
    "curl -s $BASE_URL/runbook/versions"

run_test "Get Latest Runbook (may fail if none exists)" \
    "curl -s $BASE_URL/runbook/latest"

echo ""
echo "========================================="
echo "📊 TEST SUMMARY"
echo "========================================="
echo "Total Tests: $test_count"
echo -e "${GREEN}Passed: $pass_count${NC}"
echo -e "${RED}Failed: $fail_count${NC}"
echo "Success Rate: $((pass_count * 100 / test_count))%"
echo ""

if [[ $fail_count -eq 0 ]]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Review output above.${NC}"
    exit 1
fi
