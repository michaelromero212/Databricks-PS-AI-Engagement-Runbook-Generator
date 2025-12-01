import os
import requests
import json
from dotenv import load_dotenv

# Load env before importing client
load_dotenv('backend/.env')

print(f"DEBUG: DATABRICKS_HOST from env: {os.getenv('DATABRICKS_HOST')}")

from backend.databricks_client import DatabricksClient

client = DatabricksClient()
run_id = "827872674628066" # Latest test run with DBFS bypass

print(f"--- Debugging Run ID: {run_id} ---")

print("\n1. Getting Job Run Details...")
try:
    # Get full run info to see tasks
    url = f"{client.host}/api/2.1/jobs/runs/get?run_id={run_id}"
    resp = requests.get(url, headers=client.headers)
    full_status = resp.json()
    
    print("\nTasks found:")
    generation_run_id = None
    
    for task in full_status.get('tasks', []):
        t_key = task.get('task_key')
        t_id = task.get('run_id')
        t_state = task.get('state', {}).get('life_cycle_state')
        print(f"- Task Key: {t_key}, Run ID: {t_id}, State: {t_state}")
        
        if t_key == 'generation':
            generation_run_id = t_id

    if generation_run_id:
        print(f"\n-> FOUND GENERATION RUN ID: {generation_run_id}")
        print(f"Checking output for Generation Task Run ID: {generation_run_id}...")
        
        output = client.get_run_output(str(generation_run_id))
        if output:
            print(f"  -> SUCCESS! Output length: {len(output)}")
            print(f"  -> Preview: {output[:200]}...")
        else:
            print("  -> FAILURE: Output is None or empty")
            
            # Check raw output for generation task
            print("  -> Checking raw API output for this task...")
            url = f"{client.host}/api/2.1/jobs/runs/get-output?run_id={generation_run_id}"
            resp = requests.get(url, headers=client.headers)
            print(f"  -> Status: {resp.status_code}")
            print(f"  -> Keys: {resp.json().keys()}")
            if 'error' in resp.json():
                print(f"  -> Error: {resp.json()['error']}")
            if 'notebook_output' in resp.json():
                print(f"  -> Notebook Output: {resp.json()['notebook_output']}")
    else:
        print("\n-> FAILURE: Could not find 'generation' task in job run.")

except Exception as e:
    print(f"Error: {e}")
