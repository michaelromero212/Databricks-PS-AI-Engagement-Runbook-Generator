#!/bin/bash

echo "========================================="
echo "🧪 END-TO-END DASHBOARD TEST"
echo "Testing with Mock Data"
echo "========================================="
echo ""

BASE_URL="http://localhost:8000"
MOCK_DIR="../mock_data"

echo "=== Phase 1: Upload Mock Data Files ==="
echo ""

FILES=("kickoff_notes.md" "slack_export.json" "jira_tickets.csv" "requirements.md" "architecture_overview.md")

for file in "${FILES[@]}"; do
    echo "📤 Uploading: $file"
    response=$(curl -s -X POST -F "file=@$MOCK_DIR/$file" $BASE_URL/upload)
    echo "Response: $response"
    echo ""
done

echo ""
echo "=== Phase 2: Trigger Pipeline ==="
echo ""

echo "🚀 Triggering Databricks job with DistilBERT model..."
pipeline_response=$(curl -s -X POST -H "Content-Type: application/json" \
    -d '{"model_type":"distilbert-base-uncased","files":["kickoff_notes.md","slack_export.json"]}' \
    $BASE_URL/run/pipeline)

echo "$pipeline_response"
RUN_ID=$(echo $pipeline_response | grep -o '"run_id":"[^"]*' | cut -d'"' -f4)
echo ""
echo "📋 Job Run ID: $RUN_ID"
echo ""

if [[ -z "$RUN_ID" ]]; then
    echo "❌ Failed to get Run ID!"
    exit 1
fi

echo ""
echo "=== Phase 3: Monitor Job Execution ==="
echo ""

for i in {1..20}; do
    sleep 10
    echo "⏱️  Check #$i (${i}0 seconds elapsed)..."
    
    status_response=$(curl -s $BASE_URL/status/job/$RUN_ID)
    status=$(echo $status_response | grep -o '"status":"[^"]*' | cut -d'"' -f4)
    
    echo "   Status: $status"
    
    if [[ "$status" == "SUCCESS" ]]; then
        echo ""
        echo "✅ Job completed successfully!"
        break
    elif [[ "$status" == "FAILED" ]] || [[ "$status" == "INTERNAL_ERROR" ]]; then
        echo ""
        echo "❌ Job failed with status: $status"
        echo "Full response: $status_response"
        exit 1
    fi
done

echo ""
echo "=== Phase 4: Fetch Generated Runbook ==="
echo ""

echo "📥 Fetching runbook from DBFS..."
fetch_response=$(curl -s -X POST $BASE_URL/runbook/fetch/$RUN_ID)
echo "Fetch response: $fetch_response"
echo ""

sleep 2

echo "📖 Getting latest runbook..."
runbook_response=$(curl -s $BASE_URL/runbook/latest)

if echo "$runbook_response" | grep -q "markdown_content"; then
    echo "✅ Runbook retrieved successfully!"
    echo ""
    echo "Runbook Preview (first 500 chars):"
    echo "$runbook_response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['markdown_content'][:500])"
    echo ""
    echo "Model used: $(echo "$runbook_response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['model_used'])")"
else
    echo "⚠️  Could not retrieve runbook"
    echo "Response: $runbook_response"
fi

echo ""
echo "=== Phase 5: Verify All Endpoints ==="
echo ""

echo "✓ Health check..."
curl -s $BASE_URL/status/model | python3 -m json.tool

echo ""
echo "✓ Runbook versions..."
curl -s $BASE_URL/runbook/versions | python3 -m json.tool

echo ""
echo "========================================="
echo "✅ END-TO-END TEST COMPLETE"
echo "========================================="
