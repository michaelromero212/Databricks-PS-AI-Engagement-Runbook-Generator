import os
import time
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

@app.post("/run/pipeline", response_model=PipelineRunResponse)
async def run_pipeline(request: PipelineRunRequest):
    # Trigger Databricks Job
    # We pass the model type and input path as parameters
    params = {
        "model_type": request.model_type.value,
        "input_path": f"{settings.DBFS_ROOT}/uploads",
        "output_path": f"{settings.DBFS_ROOT}/runbooks"
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
        # Mock logic for prototype
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

    # Real fetch
    # The job writes to {settings.DBFS_ROOT}/runbooks/{run_id}/runbook.md
    dbfs_path = f"{settings.DBFS_ROOT}/runbooks/{run_id}/runbook.md"
    try:
        content = db_client.read_file_from_dbfs(dbfs_path)
        if content:
            metadata = {"model_used": "databricks-dbrx", "generated_at": str(time.time())} # simplified
            storage.save_runbook(run_id, content, metadata)
            return {"status": "fetched"}
        else:
            raise HTTPException(status_code=404, detail="Runbook file not found in DBFS")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch from DBFS: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
