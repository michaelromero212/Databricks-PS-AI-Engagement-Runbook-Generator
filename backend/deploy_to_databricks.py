import os
import json
import base64
import requests
from dotenv import load_dotenv

# Load env vars
load_dotenv()

HOST = os.getenv("DATABRICKS_HOST")
TOKEN = os.getenv("DATABRICKS_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

NOTEBOOKS_DIR = "../databricks"
TARGET_DIR = "/Shared/PS_AI_Runbook_Gen"

def import_notebook(local_path, target_path):
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")
    
    data = {
        "path": target_path,
        "content": content,
        "language": "PYTHON",
        "overwrite": True,
        "format": "SOURCE"
    }
    
    resp = requests.post(f"{HOST}/api/2.0/workspace/import", headers=HEADERS, json=data)
    if resp.status_code != 200:
        print(f"Error importing {target_path}: {resp.text}")
        return False
    print(f"Imported {target_path}")
    return True

def create_job():
    # Load job json template
    with open(os.path.join(NOTEBOOKS_DIR, "job.json"), "r") as f:
        job_spec = json.load(f)
    
    # Update notebook paths
    for task in job_spec["tasks"]:
        filename = task["notebook_task"]["notebook_path"].split("/")[-1]
        task["notebook_task"]["notebook_path"] = f"{TARGET_DIR}/{filename}"
        
        # Ensure cluster config is valid for Community Edition (if applicable)
        # For CE, we often need to use an existing cluster or a very specific new cluster config.
        # The template uses a new cluster. Let's hope it works or we might need to ask user for an existing cluster ID.
        # However, 'new_cluster' is often restricted in CE.
        # Strategy: Try to create with new_cluster. If fails, we might need to warn user.
        # Actually, for CE, 'new_cluster' usually works but with limited node types.
        # Let's stick to the template but ensure node_type_id is generic if possible, or keep as is.
        
    resp = requests.post(f"{HOST}/api/2.1/jobs/create", headers=HEADERS, json=job_spec)
    if resp.status_code != 200:
        print(f"Error creating job: {resp.text}")
        return None
    
    job_id = resp.json().get("job_id")
    print(f"Created Job with ID: {job_id}")
    return job_id

def main():
    print(f"Deploying to {HOST}...")
    
    # 1. Create Directory
    requests.post(f"{HOST}/api/2.0/workspace/mkdirs", headers=HEADERS, json={"path": TARGET_DIR})
    
    # 2. Import Notebooks
    notebooks = [
        "ingestion_notebook.py",
        "nlp_notebook.py",
        "embeddings_notebook.py",
        "runbook_generator_notebook.py"
    ]
    
    for nb in notebooks:
        if not import_notebook(os.path.join(NOTEBOOKS_DIR, nb), f"{TARGET_DIR}/{nb.replace('.py', '')}"):
            return

    # 3. Create Job
    job_id = create_job()
    
    if job_id:
        # Update .env
        with open(".env", "r") as f:
            lines = f.readlines()
        
        with open(".env", "w") as f:
            for line in lines:
                if line.startswith("DATABRICKS_JOB_ID="):
                    f.write(f"DATABRICKS_JOB_ID={job_id}\n")
                else:
                    f.write(line)
        print("Updated .env with Job ID")

if __name__ == "__main__":
    main()
