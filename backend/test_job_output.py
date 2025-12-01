#!/usr/bin/env python3
"""
Test script to check if we can retrieve job output from the most recent run.
This will help diagnose why the fallback mode is triggering.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("DATABRICKS_HOST")
TOKEN = os.getenv("DATABRICKS_TOKEN")
JOB_ID = os.getenv("DATABRICKS_JOB_ID")

headers = {"Authorization": f"Bearer {TOKEN}"}

print("=" * 60)
print("TESTING JOB OUTPUT RETRIEVAL")
print("=" * 60)

# Step 1: Get the most recent run for this job
print(f"\n1. Getting most recent run for Job ID: {JOB_ID}")
try:
    resp = requests.get(
        f"{HOST}/api/2.1/jobs/runs/list?job_id={JOB_ID}&limit=1", 
        headers=headers, 
        timeout=10
    )
    resp.raise_for_status()
    runs = resp.json().get('runs', [])
    
    if not runs:
        print("❌ No runs found for this job")
        exit(1)
        
    latest_run = runs[0]
    run_id = latest_run.get('run_id')
    state = latest_run.get('state', {})
    print(f"✅ Found run: {run_id}")
    print(f"   Status: {state.get('life_cycle_state')} / {state.get('result_state', 'N/A')}")
    
except Exception as e:
    print(f"❌ Failed to get runs: {e}")
    exit(1)

# Step 2: Try to get the output of this run
print(f"\n2. Attempting to retrieve output for run: {run_id}")
try:
    resp = requests.get(
        f"{HOST}/api/2.1/jobs/runs/get-output?run_id={run_id}",
        headers=headers,
        timeout=10
    )
    if resp.status_code != 200:
        print(f"❌ HTTP {resp.status_code}: {resp.text}")
    resp.raise_for_status()
    output_data = resp.json()
    
    print("✅ Successfully called get-output API")
    print(f"\n📋 Response structure:")
    for key in output_data.keys():
        print(f"   - {key}")
    
    # Check for notebook output
    if 'notebook_output' in output_data:
        notebook_output = output_data['notebook_output']
        print(f"\n📓 Notebook Output found:")
        print(f"   Keys: {list(notebook_output.keys())}")
        
        if 'result' in notebook_output:
            result = notebook_output['result']
            result_preview = result[:200] if len(result) > 200 else result
            print(f"\n✅ RESULT FOUND (length: {len(result)} chars)")
            print(f"   Preview: {result_preview}...")
            print("\n" + "=" * 60)
            print("✅ SUCCESS! The backend SHOULD be able to retrieve this output.")
            print("=" * 60)
        else:
            print("\n⚠️  'result' key not found in notebook_output")
            print(f"   Available keys: {list(notebook_output.keys())}")
    else:
        print("\n❌ No 'notebook_output' in response")
        
    # Check for errors
    if 'error' in output_data:
        print(f"\n❌ Error in output: {output_data['error']}")
        
    # Show full output for debugging
    print(f"\n🔍 Full Response (truncated):")
    import json
    print(json.dumps(output_data, indent=2)[:1000])
    
except Exception as e:
    print(f"❌ Failed to get output: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
