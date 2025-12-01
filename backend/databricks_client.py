import requests
import json
from util.settings import get_settings
from util.schema import JobStatus

settings = get_settings()

class DatabricksClient:
    def __init__(self):
        self.host = settings.DATABRICKS_HOST
        self.token = settings.DATABRICKS_TOKEN
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def trigger_job(self, job_id: str, params: dict = None) -> str:
        url = f"{self.host}/api/2.1/jobs/run-now"
        data = {"job_id": job_id}
        if params:
            data["notebook_params"] = params
        
        response = requests.post(url, headers=self.headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json().get("run_id")

    def get_run_status(self, run_id: str) -> dict:
        url = f"{self.host}/api/2.1/jobs/runs/get?run_id={run_id}"
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        state = response.json().get("state", {})
        
        life_cycle_state = state.get("life_cycle_state")
        result_state = state.get("result_state")
        
        status = JobStatus.PENDING
        if life_cycle_state in ["PENDING", "RUNNING", "TERMINATING"]:
            status = JobStatus.RUNNING
        elif life_cycle_state == "TERMINATED":
            if result_state == "SUCCESS":
                status = JobStatus.SUCCESS
            elif result_state == "FAILED":
                status = JobStatus.FAILED
            else:
                status = JobStatus.TERMINATED
        elif life_cycle_state == "SKIPPED":
            status = JobStatus.SKIPPED
        elif life_cycle_state == "INTERNAL_ERROR":
            status = JobStatus.INTERNAL_ERROR
            
        return {
            "status": status,
            "state_message": state.get("state_message", ""),
            "start_time": response.json().get("start_time")
        }

    def upload_file_to_dbfs(self, local_path: str, dbfs_path: str):
        # DBFS API 2.0
        # 1. Create handle
        create_url = f"{self.host}/api/2.0/dbfs/create"
        create_data = {"path": dbfs_path, "overwrite": True}
        resp = requests.post(create_url, headers=self.headers, json=create_data, timeout=10)
        resp.raise_for_status()
        handle = resp.json().get("handle")
        
        # 2. Add block
        add_url = f"{self.host}/api/2.0/dbfs/add-block"
        with open(local_path, "rb") as f:
            while True:
                chunk = f.read(1024 * 1024) # 1MB chunks
                if not chunk:
                    break
                import base64
                data = base64.b64encode(chunk).decode()
                requests.post(add_url, headers=self.headers, json={"handle": handle, "data": data}, timeout=30)
        
        # 3. Close
        close_url = f"{self.host}/api/2.0/dbfs/close"
        requests.post(close_url, headers=self.headers, json={"handle": handle}, timeout=10)

    def read_file_from_dbfs(self, dbfs_path: str) -> str:
        url = f"{self.host}/api/2.0/dbfs/read?path={dbfs_path}"
        response = requests.get(url, headers=self.headers, timeout=10)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json().get("data")
        import base64
        return base64.b64decode(data).decode('utf-8')

    def get_run_output(self, run_id: str) -> str:
        """
        Get notebook output from a completed job run.
        This works with Community Edition tokens that lack DBFS access.
        Returns the value passed to dbutils.notebook.exit() in the notebook.
        """
        url = f"{self.host}/api/2.1/jobs/runs/get-output?run_id={run_id}"
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        
        # The notebook output is in the 'notebook_output' field
        output_data = response.json()
        
        # Check if there's a notebook output result
        if 'notebook_output' in output_data:
            result = output_data['notebook_output'].get('result', '')
            return result
        
        # Fallback to error if present
        if 'error' in output_data:
            raise Exception(f"Job run failed: {output_data.get('error')}")
            
        return None
