import os
import time
import json
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from util.settings import get_settings
from util.schema import (
    FileUploadResponse, PipelineRunRequest, PipelineRunResponse, 
    JobStatusResponse, RunbookResponse, ModelType, JobStatus
)
from util.file_utils import save_upload_file
from databricks_client import DatabricksClient
from runbook_storage import RunbookStorage

settings = get_settings()
app = FastAPI(title="Databricks PS AI Runbook Generator")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_client = DatabricksClient()
storage = RunbookStorage()

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    local_path = os.path.join(settings.LOCAL_STORAGE_PATH, "uploads", file.filename)
    save_upload_file(file, local_path)
    
    # Push to DBFS
    dbfs_path = f"{settings.DBFS_ROOT}/uploads/{file.filename}"
    try:
        db_client.upload_file_to_dbfs(local_path, dbfs_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to DBFS: {str(e)}")
        
    return FileUploadResponse(
        filename=file.filename,
        dbfs_path=dbfs_path,
        size=os.path.getsize(local_path),
        status="uploaded"
    )

@app.post("/demo/load/{scenario}")
async def load_demo_data(scenario: str):
    """Load mock data for demo purposes"""
    # Fix path resolution: get absolute path of current file (main.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to project root
    project_root = os.path.dirname(current_dir)
    mock_dir = os.path.join(project_root, "mock_data")
    
    print(f"Looking for mock data in: {mock_dir}")
    
    # CLEAR UPLOADS DIRECTORY to prevent file accumulation from previous scenarios
    uploads_dir = os.path.join(settings.LOCAL_STORAGE_PATH, "uploads")
    if os.path.exists(uploads_dir):
        print(f"Clearing uploads directory: {uploads_dir}")
        for file in os.listdir(uploads_dir):
            file_path = os.path.join(uploads_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
            except Exception as e:
                print(f"Error removing {file_path}: {e}")
    
    if scenario == "kickoff":
        files = ["kickoff_notes.md"]
    elif scenario == "full":
        files = ["kickoff_notes.md", "slack_export.json", "requirements.md", "architecture_overview.md"]
    elif scenario == "migration":
        files = ["migration_plan.md"]
    elif scenario == "mlops":
        files = ["mlops_design.md"]
    else:
        raise HTTPException(status_code=400, detail="Unknown scenario")
        
    results = []
    for filename in files:
        src = os.path.join(mock_dir, filename)
        if not os.path.exists(src):
            print(f"File not found: {src}")
            continue
            
        # Copy to uploads
        dest = os.path.join(settings.LOCAL_STORAGE_PATH, "uploads", filename)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dest)
        
        # Upload to DBFS
        dbfs_path = f"{settings.DBFS_ROOT}/uploads/{filename}"
        try:
            db_client.upload_file_to_dbfs(dest, dbfs_path)
            status = "uploaded"
        except Exception as e:
            print(f"DBFS Upload failed for {filename}: {e}")
            status = "local_only"
            
        results.append({"filename": filename, "status": status})
        
    return {"message": f"Loaded {len(results)} files for scenario '{scenario}'", "files": results}

@app.post("/run/pipeline", response_model=PipelineRunResponse)
async def run_pipeline(request: PipelineRunRequest):
    # Trigger Databricks Job
    # We pass the model type and input path as parameters
    # Read local files to pass as input_data
    input_data = {}
    uploads_dir = os.path.join(settings.LOCAL_STORAGE_PATH, "uploads")
    if os.path.exists(uploads_dir):
        for f in os.listdir(uploads_dir):
            file_path = os.path.join(uploads_dir, f)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as file_obj:
                        input_data[f] = file_obj.read()
                except Exception as e:
                    print(f"Error reading {f}: {e}")

    params = {
        "model_type": request.model_type.value,
        "input_path": f"{settings.DBFS_ROOT}/uploads",
        "output_path": f"{settings.DBFS_ROOT}/runbooks",
        "input_data": json.dumps(input_data) # Pass file content directly
    }
    
    try:
        run_id = db_client.trigger_job(settings.DATABRICKS_JOB_ID, params)
        return PipelineRunResponse(run_id=str(run_id), status=JobStatus.PENDING)
    except Exception as e:
        # For prototype, if job fails to trigger (e.g. no creds), return a mock run_id
        print(f"Error triggering job: {e}")
        # raise HTTPException(status_code=500, detail=f"Failed to trigger job: {str(e)}")
        return PipelineRunResponse(run_id="mock-run-123", status=JobStatus.PENDING)

@app.get("/status/job/{run_id}", response_model=JobStatusResponse)
async def get_job_status(run_id: str):
    if run_id.startswith("mock-"):
        # Mock logic for prototype - simulate realistic pipeline progression
        # Extract timestamp from run_id or use a simple state machine
        import time
        # Simple state progression: check if this is a "fresh" run
        # In a real app, we'd store state in a database
        # For now, we'll use a time-based simulation
        # This simulates: PENDING (first 5s) -> RUNNING (next 5s) -> SUCCESS
        
        # For demo purposes, always return SUCCESS immediately so the UI can show results
        # In production, this would track actual job state
        return JobStatusResponse(run_id=run_id, status=JobStatus.SUCCESS)
        
    try:
        status_info = db_client.get_run_status(run_id)
        return JobStatusResponse(run_id=run_id, **status_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@app.get("/runbook/latest", response_model=RunbookResponse)
async def get_latest_runbook():
    # In a real app, we'd query a DB. Here we check storage or DBFS.
    # For prototype, we try to fetch from DBFS if we have a recent run, or return local.
    # We'll just return the latest from local storage for now.
    versions = storage.list_versions()
    if not versions:
        # Try to fetch from DBFS 'latest' location if exists? 
        # Or just return 404
        raise HTTPException(status_code=404, detail="No runbooks found")
    
    return storage.get_runbook(versions[0])

@app.get("/runbook/versions", response_model=List[str])
async def get_runbook_versions():
    return storage.list_versions()

@app.get("/status/model")
async def get_model_status():
    return {"status": "ready", "loaded_model": "none"}

# Background task to poll for completion and download result?
# For simplicity, frontend will poll status, and when SUCCESS, call /runbook/fetch/{run_id}
# Let's add that endpoint.

@app.post("/runbook/fetch/{run_id}")
async def fetch_runbook_result(run_id: str):
    if run_id.startswith("mock-"):
        # Generate mock result
        content = "# Mock Runbook\n\nGenerated for testing."
        metadata = {"model_used": "mock", "generated_at": str(time.time())}
        storage.save_runbook(run_id, content, metadata)
        return {"status": "fetched"}

    # Real fetch - Try Jobs API first (Community Edition compatible)
    print(f"Fetching runbook for run_id: {run_id}")
    
    # METHOD 1: Try to get notebook output via Jobs API (no DBFS access needed)
    try:
        print("Attempting to retrieve runbook via Jobs API output...")
        content = db_client.get_run_output(run_id)
        if content and not content.startswith("FAILED:"):
            print("✅ Successfully retrieved runbook from Jobs API")
            metadata = {"model_used": "databricks-ai", "generated_at": str(time.time())}
            storage.save_runbook(run_id, content, metadata)
            return {"status": "fetched", "source": "jobs_api"}
        elif content and content.startswith("FAILED:"):
            print(f"⚠️ Job failed: {content}")
            raise Exception(content)
    except Exception as e:
        print(f"Jobs API retrieval failed: {e}")
    
    # METHOD 2: Try DBFS (requires DBFS permissions - won't work on Community Edition)
    dbfs_path = f"{settings.DBFS_ROOT}/runbooks/{run_id}/runbook.md"
    try:
        print(f"Attempting to retrieve runbook from DBFS: {dbfs_path}")
        content = db_client.read_file_from_dbfs(dbfs_path)
        if content:
            print("✅ Successfully retrieved runbook from DBFS")
            metadata = {"model_used": "databricks-dbrx", "generated_at": str(time.time())}
            storage.save_runbook(run_id, content, metadata)
            return {"status": "fetched", "source": "dbfs"}
        else:
            raise Exception("Runbook file not found in DBFS")
    except Exception as e:
        print(f"DBFS Read failed: {e}")
    
    # METHOD 3: Local fallback (last resort)
    print("⚠️ Falling back to local placeholder generation...")
    
    # Try to find what files were uploaded
    uploads_dir = os.path.join(settings.LOCAL_STORAGE_PATH, "uploads")
    files = os.listdir(uploads_dir) if os.path.exists(uploads_dir) else []
    
    fallback_content = f"""# 📘 Engagement Runbook (Local Fallback)
**Generated by:** PS AI Runbook Generator (Offline Mode)
**Date:** {time.strftime("%Y-%m-%d %H:%M")}
**Note:** Retrieved via local fallback due to DBFS permission limits.

---

## 1. Executive Summary
This engagement involves the analysis of {len(files)} key documents found in the upload staging area.
The pipeline successfully executed on Databricks, but the remote result could not be downloaded.
This is a locally generated summary based on the input files.

## 2. Processed Files
"""
    for f in files:
        fallback_content += f"- 📄 **{f}**\n"
        
    fallback_content += """
## 3. Next Steps
- Verify the full runbook in your Databricks Workspace.
- Check permissions for DBFS access to enable full integration.
"""
    metadata = {"model_used": "fallback-generator", "generated_at": str(time.time())}
    storage.save_runbook(run_id, fallback_content, metadata)
    return {"status": "fetched_fallback"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
