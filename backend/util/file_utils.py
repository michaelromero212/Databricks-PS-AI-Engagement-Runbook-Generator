import os
import shutil
from typing import List
from fastapi import UploadFile
from .settings import get_settings

settings = get_settings()

def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    try:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return destination
    finally:
        upload_file.file.close()

def list_files(directory: str) -> List[str]:
    if not os.path.exists(directory):
        return []
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
