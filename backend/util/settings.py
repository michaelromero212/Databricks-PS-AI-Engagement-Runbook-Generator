import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABRICKS_HOST: str = os.getenv("DATABRICKS_HOST", "")
    DATABRICKS_TOKEN: str = os.getenv("DATABRICKS_TOKEN", "")
    DATABRICKS_JOB_ID: str = os.getenv("DATABRICKS_JOB_ID", "")
    DBFS_ROOT: str = "/dbfs/tmp/ps_ai_runbook_gen"
    LOCAL_STORAGE_PATH: str = "./data_storage"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
