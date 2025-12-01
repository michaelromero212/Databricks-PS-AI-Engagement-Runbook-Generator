#!/usr/bin/env python3
"""
Test the fixed databricks_client.get_run_output method
"""
import sys
sys.path.insert(0, '/Users/michaelromero/Documents/Databricks-PS-AI-Engagement-Runbook-Generator/backend')

from databricks_client import DatabricksClient
import os
import requests
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("TESTING FIXED get_run_output METHOD")
print("=" * 60)

# Get the latest run ID
HOST = os.getenv("DATABRICKS_HOST")
TOKEN = os.getenv("DATABRICKS_TOKEN")
JOB_ID = os.getenv("DATABRICKS_JOB_ID")
headers = {"Authorization": f"Bearer {TOKEN}"}

resp = requests.get(
    f"{HOST}/api/2.1/jobs/runs/list?job_id={JOB_ID}&limit=1", 
    headers=headers, 
    timeout=10
)
resp.raise_for_status()
runs = resp.json().get('runs', [])
parent_run_id = runs[0].get('run_id')

print(f"\nTesting with parent run_id: {parent_run_id}\n")

# Test the fixed method
client = DatabricksClient()
try:
    output = client.get_run_output(parent_run_id)
    
    if output:
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Runbook retrieved successfully!")
        print("=" * 60)
        print(f"\nRunbook length: {len(output)} chars")
        print("\nPreview:")
        print(output[:300])
        print("...")
        print(output[-200:])
        print("\n" + "=" * 60)
    else:
        print("❌ No output returned")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
