from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from enum import Enum

class ModelType(str, Enum):
    DATABRICKS_DBRX = "dbrx-instruct"
    HF_DISTILBERT = "distilbert-base-uncased"
    HF_MINILM = "sentence-transformers/all-MiniLM-L6-v2"


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    TERMINATED = "TERMINATED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    INTERNAL_ERROR = "INTERNAL_ERROR"

class FileUploadResponse(BaseModel):
    filename: str
    dbfs_path: str
    size: int
    status: str

class PipelineRunRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    model_type: ModelType
    files: List[str]

class PipelineRunResponse(BaseModel):
    run_id: str
    status: JobStatus
    dashboard_url: Optional[str] = None

class JobStatusResponse(BaseModel):
    run_id: str
    status: JobStatus
    state_message: Optional[str] = None
    start_time: Optional[int] = None

class RunbookResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    run_id: str
    markdown_content: str
    metadata: Dict[str, Any]
    model_used: str
    generated_at: str
