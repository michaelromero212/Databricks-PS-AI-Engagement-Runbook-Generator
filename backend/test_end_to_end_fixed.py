#!/usr/bin/env python3
"""
End-to-end test:
1. Trigger a new job run
2. Wait for completion
3. Retrieve the runbook using the fixed client
"""
import sys
sys.path.insert(0, '/Users/michaelromero/Documents/Databricks-PS-AI-Engagement-Runbook-Generator/backend')

from databricks_client import DatabricksClient
from util.settings import get_settings
import time
import json

settings = get_settings()
client = DatabricksClient()

print("=" * 70)
print("END-TO-END RUNBOOK GENERATION TEST")
print("=" * 70)

# Step 1: Trigger new job
print("\n📤 STEP 1: Triggering new job run...")

# Create test input data
test_input = {
    "test_file.md": """# Test Engagement
    
This is a test engagement using Databricks, Spark, and MLflow.
The project started in 2024 and involves migrating from Hadoop to Databricks.
"""
}

params = {
    "model_type": "distilbert-base-uncased",
    "input_path": f"{settings.DBFS_ROOT}/uploads",
    "output_path": f"{settings.DBFS_ROOT}/runbooks",
    "input_data": json.dumps(test_input)
}

try:
    run_id = client.trigger_job(settings.DATABRICKS_JOB_ID, params)
    print(f"✅ Job triggered successfully!")
    print(f"   Run ID: {run_id}")
except Exception as e:
    print(f"❌ Failed to trigger job: {e}")
    exit(1)

# Step 2: Wait for completion
print(f"\n⏳ STEP 2: Waiting for job to complete...")
max_wait = 300  # 5 minutes
wait_time = 0
poll_interval = 10

while wait_time < max_wait:
    try:
        status_info = client.get_run_status(run_id)
        status = status_info['status']
        
        print(f"   [{wait_time}s] Status: {status.value}")
        
        if status.value in ['SUCCESS', 'FAILED', 'TERMINATED', 'INTERNAL_ERROR']:
            if status.value == 'SUCCESS':
                print(f"\n✅ Job completed successfully!")
                break
            else:
                print(f"\n❌ Job failed with status: {status.value}")
                print(f"   Message: {status_info.get('state_message', 'N/A')}")
                exit(1)
        
        time.sleep(poll_interval)
        wait_time += poll_interval
        
    except Exception as e:
        print(f"   Error checking status: {e}")
        time.sleep(poll_interval)
        wait_time += poll_interval

if wait_time >= max_wait:
    print(f"\n⚠️  Timeout waiting for job completion (waited {max_wait}s)")
    exit(1)

# Step 3: Retrieve runbook
print(f"\n📥 STEP 3: Retrieving runbook output...")
try:
    runbook = client.get_run_output(run_id)
    
    if runbook:
        print("✅ Runbook retrieved successfully!")
        print("\n" + "=" * 70)
        print("GENERATED RUNBOOK:")
        print("=" * 70)
        print(runbook)
        print("=" * 70)
        print(f"\n✅✅✅ END-TO-END TEST PASSED! ✅✅✅")
        print(f"The runbook was successfully generated and retrieved from Databricks!")
        print("=" * 70)
    else:
        print("❌ No runbook content returned")
        exit(1)
        
except Exception as e:
    print(f"❌ Failed to retrieve runbook: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
