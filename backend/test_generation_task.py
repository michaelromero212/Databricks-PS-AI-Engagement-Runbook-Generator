#!/usr/bin/env python3
"""
Test getting output from the generation task specifically
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("DATABRICKS_HOST")
TOKEN = os.getenv("DATABRICKS_TOKEN")

headers = {"Authorization": f"Bearer {TOKEN}"}

# The generation task run ID from the previous test
task_run_id = "444642917064789"

print("=" * 60)
print(f"TESTING OUTPUT FROM GENERATION TASK: {task_run_id}")
print("=" * 60)

try:
    resp = requests.get(
        f"{HOST}/api/2.1/jobs/runs/get-output?run_id={task_run_id}",
        headers=headers,
        timeout=10
    )
    
    if resp.status_code != 200:
        print(f"❌ HTTP {resp.status_code}: {resp.text}")
        exit(1)
        
    resp.raise_for_status()
    output_data = resp.json()
    
    print("✅ Successfully retrieved output!")
    
    if 'notebook_output' in output_data:
        notebook_output = output_data['notebook_output']
        if 'result' in notebook_output:
            result = notebook_output['result']
            print(f"\n✅ Runbook content retrieved (length: {len(result)} chars)")
            print("\n" + "=" * 60)
            print("RUNBOOK PREVIEW:")
            print("=" * 60)
            print(result[:500])
            print("...")
            print(result[-200:])
            print("=" * 60)
            print("\n✅ SUCCESS! We can retrieve the runbook from the generation task!")
        else:
            print(f"\n⚠️  'result' not in notebook_output. Keys: {list(notebook_output.keys())}")
    else:
        print("\n❌ No notebook_output in response")
        print(json.dumps(output_data, indent=2)[:500])
        
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
