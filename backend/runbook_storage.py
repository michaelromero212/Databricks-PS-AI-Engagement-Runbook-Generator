import os
import json
from typing import Optional, Dict, Any, List
from util.settings import get_settings

settings = get_settings()

class RunbookStorage:
    def __init__(self):
        self.storage_path = os.path.join(settings.LOCAL_STORAGE_PATH, "runbooks")
        os.makedirs(self.storage_path, exist_ok=True)

    def save_runbook(self, run_id: str, content: str, metadata: Dict[str, Any]):
        run_dir = os.path.join(self.storage_path, str(run_id))
        os.makedirs(run_dir, exist_ok=True)
        
        with open(os.path.join(run_dir, "runbook.md"), "w") as f:
            f.write(content)
            
        with open(os.path.join(run_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

    def get_runbook(self, run_id: str) -> Optional[Dict[str, Any]]:
        run_dir = os.path.join(self.storage_path, str(run_id))
        if not os.path.exists(run_dir):
            return None
            
        try:
            with open(os.path.join(run_dir, "runbook.md"), "r") as f:
                content = f.read()
            with open(os.path.join(run_dir, "metadata.json"), "r") as f:
                metadata = json.load(f)
                
            return {
                "run_id": run_id,
                "markdown_content": content,
                "metadata": metadata,
                "model_used": metadata.get("model_used", "unknown"),
                "generated_at": metadata.get("generated_at", "")
            }
        except Exception:
            return None

    def list_versions(self) -> List[str]:
        if not os.path.exists(self.storage_path):
            return []
        return sorted(os.listdir(self.storage_path), reverse=True)
