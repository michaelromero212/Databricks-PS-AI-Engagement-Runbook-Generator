#!/usr/bin/env python3
"""
Test script to get task run details
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("DATABRICKS_HOST")
TOKEN = os.getenv("DATABRICKS_TOKEN")
JOB_ID = os.getenv("DATABRICKS_JOB_ID")

headers = {"Authorization": f"Bearer {TOKEN}"}

print("=" * 60)
print("GETTING TASK RUN DETAILS")
print("=" * 60)

# Get the most recent run
resp = requests.get(
    f"{HOST}/api/2.1/jobs/runs/list?job_id={JOB_ID}&limit=1", 
    headers=headers, 
    timeout=10
)
resp.raise_for_status()
runs = resp.json().get('runs', [])
run_id = runs[0].get('run_id')

print(f"\nRun ID: {run_id}")

# Get run details
resp = requests.get(
    f"{HOST}/api/2.1/jobs/runs/get?run_id={run_id}",
    headers=headers,
    timeout=10
)
resp.raise_for_status()
run_data = resp.json()

print("\n📋 Run Structure:")
print(json.dumps(run_data, indent=2)[:2000])

# Check for tasks
if 'tasks' in run_data:
    print(f"\n✅ Found {len(run_data['tasks'])} tasks:")
    for task in run_data['tasks']:
        task_key = task.get('task_key')
        run_id = task.get('run_id')
        state = task.get('state', {})
        print(f"  - Task: {task_key}")
        print(f"    Run ID: {run_id}")
        print(f"    State: {state.get('result_state', 'N/A')}")
