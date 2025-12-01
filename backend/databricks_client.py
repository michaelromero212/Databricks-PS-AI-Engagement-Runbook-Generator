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
        
        For multi-task jobs, this retrieves output from the 'generation' task.
        """
        # First, try direct output (works for single-task jobs)
        url = f"{self.host}/api/2.1/jobs/runs/get-output?run_id={run_id}"
        response = requests.get(url, headers=self.headers, timeout=10)
        
        # If this is a multi-task job, we'll get a 400 error
        if response.status_code == 400:
            error_data = response.json()
            if 'INVALID_PARAMETER_VALUE' in error_data.get('error_code', ''):
                # This is a multi-task job - get the task runs
                print(f"Multi-task job detected. Finding 'generation' task...")
                return self._get_task_output(run_id, 'generation')
            else:
                response.raise_for_status()
        
        response.raise_for_status()
        
        # Single-task job - get output directly
        output_data = response.json()
        
        # Check if there's a notebook output result
        if 'notebook_output' in output_data:
            result = output_data['notebook_output'].get('result', '')
            return result
        
        # Fallback to error if present
        if 'error' in output_data:
            raise Exception(f"Job run failed: {output_data.get('error')}")
            
        return None
    
    def _get_task_output(self, parent_run_id: str, task_key: str) -> str:
        """
        Get output from a specific task within a multi-task job.
        
        Args:
            parent_run_id: The parent job run ID
            task_key: The key of the task to retrieve output from (e.g., 'generation')
        
        Returns:
            The notebook output from the specified task
        """
        # Get the run details to find task runs
        url = f"{self.host}/api/2.1/jobs/runs/get?run_id={parent_run_id}"
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        run_data = response.json()
        
        # Find the task with the matching key
        tasks = run_data.get('tasks', [])
        task_run_id = None
        
        for task in tasks:
            if task.get('task_key') == task_key:
                task_run_id = task.get('run_id')
                break
        
        if not task_run_id:
            available_tasks = [t.get('task_key') for t in tasks]
            raise Exception(f"Task '{task_key}' not found. Available tasks: {available_tasks}")
        
        print(f"Found task '{task_key}' with run_id: {task_run_id}")
        
        # Get output from the specific task run
        url = f"{self.host}/api/2.1/jobs/runs/get-output?run_id={task_run_id}"
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        output_data = response.json()
        
        if 'notebook_output' in output_data:
            result = output_data['notebook_output'].get('result', '')
            return result
        
        if 'error' in output_data:
            raise Exception(f"Task '{task_key}' failed: {output_data.get('error')}")
        
        return None
