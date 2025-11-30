import requests
import os
import json
from dotenv import load_dotenv

# Load env vars
load_dotenv()

HOST = os.getenv("DATABRICKS_HOST")
TOKEN = os.getenv("DATABRICKS_TOKEN")
JOB_ID = os.getenv("DATABRICKS_JOB_ID")

print(f"Testing connection to: {HOST}")
print(f"Job ID: {JOB_ID}")
print("-" * 50)

headers = {"Authorization": f"Bearer {TOKEN}"}

def test_token():
    print("\n1. Testing Token & Host Connectivity (List Jobs)...")
    try:
        resp = requests.get(f"{HOST}/api/2.1/jobs/list?limit=1", headers=headers, timeout=10)
        if resp.status_code == 200:
            print("✅ SUCCESS: Connected to Databricks API.")
            return True
        elif resp.status_code == 403:
            print("❌ FAILED: 403 Forbidden. Token is invalid or expired.")
        elif resp.status_code == 401:
            print("❌ FAILED: 401 Unauthorized. Token is missing or invalid.")
        else:
            print(f"❌ FAILED: Status {resp.status_code}. {resp.text}")
    except Exception as e:
        print(f"❌ FAILED: Connection error. {str(e)}")
    return False

def test_job():
    print("\n2. Testing Job Access...")
    if not JOB_ID:
        print("❌ FAILED: No Job ID configured.")
        return False
        
    try:
        resp = requests.get(f"{HOST}/api/2.1/jobs/get?job_id={JOB_ID}", headers=headers, timeout=10)
        if resp.status_code == 200:
            job_data = resp.json()
            print(f"✅ SUCCESS: Found Job '{job_data.get('settings', {}).get('name', 'Unknown')}'.")
            return True
        elif resp.status_code == 404:
            print(f"❌ FAILED: Job ID {JOB_ID} not found.")
        else:
            print(f"❌ FAILED: Status {resp.status_code}. {resp.text}")
    except Exception as e:
        print(f"❌ FAILED: Connection error. {str(e)}")
    return False

def test_dbfs():
    print("\n3. Testing DBFS Write Permissions...")
    try:
        # Try to create a dummy directory
        data = {"path": "/dbfs/tmp/connection_test_dir"}
        resp = requests.post(f"{HOST}/api/2.0/dbfs/mkdirs", headers=headers, json=data, timeout=10)
        if resp.status_code == 200:
            print("✅ SUCCESS: DBFS Write permission confirmed.")
        elif resp.status_code == 403:
            print("⚠️ WARNING: 403 Forbidden. Token lacks DBFS write permissions.")
            print("   (This is expected for some tokens, but limits file upload capability)")
        else:
            print(f"❌ FAILED: Status {resp.status_code}. {resp.text}")
    except Exception as e:
        print(f"❌ FAILED: Connection error. {str(e)}")

def check_recent_runs():
    print("\n4. Checking Recent Job Runs...")
    try:
        resp = requests.get(f"{HOST}/api/2.1/jobs/runs/list?job_id={JOB_ID}&limit=3", headers=headers, timeout=10)
        if resp.status_code == 200:
            runs = resp.json().get('runs', [])
            if not runs:
                print("ℹ️  No runs found for this job.")
            for run in runs:
                state = run.get('state', {})
                status = state.get('life_cycle_state')
                result = state.get('result_state', 'N/A')
                print(f"   - Run {run.get('run_id')}: {status} ({result})")
        else:
            print(f"❌ FAILED: Could not list runs. {resp.text}")
    except Exception as e:
        print(f"❌ FAILED: Connection error. {str(e)}")

if __name__ == "__main__":
    if test_token():
        test_job()
        test_dbfs()
        check_recent_runs()
    print("\n" + "=" * 50)
