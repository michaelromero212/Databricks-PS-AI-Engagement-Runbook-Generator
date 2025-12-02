const API_BASE = 'http://localhost:8000';

export interface FileUploadResponse {
    filename: string;
    dbfs_path: string;
    size: number;
    status: string;
}

export interface PipelineRunResponse {
    run_id: string;
    status: string;
}

export interface JobStatusResponse {
    run_id: string;
    status: string;
    state_message?: string;
    start_time?: number;
}

export interface RunbookResponse {
    run_id: string;
    markdown_content: string;
    metadata: any;
    model_used: string;
    generated_at: string;
}

export const api = {
    uploadFile: async (file: File): Promise<FileUploadResponse> => {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData,
        });
        if (!res.ok) throw new Error('Upload failed');
        return res.json();
    },

    runPipeline: async (modelType: string, files: string[]): Promise<PipelineRunResponse> => {
        const res = await fetch(`${API_BASE}/run/pipeline`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_type: modelType, files }),
        });
        if (!res.ok) throw new Error('Pipeline trigger failed');
        return res.json();
    },

    getJobStatus: async (runId: string): Promise<JobStatusResponse> => {
        const res = await fetch(`${API_BASE}/status/job/${runId}`);
        if (!res.ok) throw new Error('Status check failed');
        return res.json();
    },

    fetchRunbook: async (runId: string): Promise<void> => {
        const res = await fetch(`${API_BASE}/runbook/fetch/${runId}`, { method: 'POST' });
        if (!res.ok) throw new Error('Fetch runbook failed');
    },

    getLatestRunbook: async (): Promise<RunbookResponse> => {
        const res = await fetch(`${API_BASE}/runbook/latest`);
        if (!res.ok) throw new Error('Get runbook failed');
        return res.json();
    },

    getRunbook: async (runId: string): Promise<RunbookResponse> => {
        const res = await fetch(`${API_BASE}/runbook/${runId}`);
        if (!res.ok) throw new Error('Get runbook failed');
        return res.json();
    },

    loadDemoScenario: async (scenario: string): Promise<any> => {
        const res = await fetch(`${API_BASE}/demo/load/${scenario}`, { method: 'POST' });
        if (!res.ok) throw new Error('Demo load failed');
        return res.json();
    }
};
