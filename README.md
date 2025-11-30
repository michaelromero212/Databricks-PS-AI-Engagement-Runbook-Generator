# Databricks PS AI Engagement Runbook Generator

A complete end-to-end prototype for generating Professional Services engagement runbooks using AI, designed to work within the constraints of the Databricks Free Trial / Community Edition.

## 🚀 Features
- **React Frontend**: Modern, responsive UI with drag-and-drop uploads, pipeline controls, and markdown rendering.
- **FastAPI Backend**: Handles file uploads, triggers Databricks jobs, and manages runbook state.
- **Databricks Integration**: Uses the Jobs API 2.1 to orchestrate a multi-task workflow (Ingestion -> NLP -> Embeddings -> Generation).
- **AI-Powered**: Leverages free HuggingFace models and lightweight LLMs compatible with small clusters.
- **Mock Data**: Includes realistic sample artifacts (Kickoff notes, Slack exports, Jira tickets) for demonstration.

## 📋 Prerequisites
- **Databricks Community Edition** (or Standard) account.
- **Python 3.9+** installed locally.
- **Node.js 18+** installed locally.
- **Databricks CLI** (optional but recommended).

## 🛠️ Installation & Setup

### 1. Databricks Setup
1. **Create DBFS Directories**:
   In your Databricks notebook or using CLI:
   ```python
   dbutils.fs.mkdirs("/tmp/ps_ai_runbook_gen/uploads")
   dbutils.fs.mkdirs("/tmp/ps_ai_runbook_gen/runbooks")
   ```

2. **Import Notebooks**:
   - Go to your Databricks Workspace.
   - Click **Import** and select the files from the `databricks/` folder in this repo:
     - `ingestion_notebook.py`
     - `nlp_notebook.py`
     - `embeddings_notebook.py`
     - `runbook_generator_notebook.py`

3. **Create the Job**:
   - Go to **Workflows** -> **Create Job**.
   - Create a multi-task job matching the structure in `databricks/job.json`.
   - **Task 1: Ingestion**: Points to `ingestion_notebook`.
   - **Task 2: NLP**: Depends on Ingestion, points to `nlp_notebook`.
   - **Task 3: Embeddings**: Depends on NLP, points to `embeddings_notebook`.
   - **Task 4: Generation**: Depends on Embeddings, points to `runbook_generator_notebook`.
   - **Cluster**: Use a "Shared" or "Single Node" cluster (Free tier limit: 1 driver, 0 workers usually, or small instance). Ensure it has access to PyPI to install `transformers`, `sentence-transformers`, `python-docx`.
   - **Copy the Job ID** from the URL (e.g., `.../jobs/123456`).

4. **Generate Access Token**:
   - User Settings -> Developer -> Access Tokens -> Generate New Token.
   - Copy the token.

### 2. Backend Setup
1. Navigate to `backend/`:
   ```bash
   cd backend
   ```
2. Create virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configure `.env`:
   Create a `.env` file in `backend/` with:
   ```ini
   DATABRICKS_HOST=https://community.cloud.databricks.com
   DATABRICKS_TOKEN=dapi...your_token_here...
   DATABRICKS_JOB_ID=123456
   ```
4. Run the server:
   ```bash
   python main.py
   ```
   Server runs at `http://localhost:8000`.

### 3. Frontend Setup
1. Navigate to `frontend/`:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   App runs at `http://localhost:5173`.

## 🏃‍♂️ How to Demo
1. **Open the Web App** at `http://localhost:5173`.
2. **Upload Files**: Drag and drop the files from `mock_data/` (e.g., `kickoff_notes.md`, `slack_export.json`).
3. **Select Model**: Choose "HuggingFace DistilBERT" (fastest for demo).
4. **Run Pipeline**: Click "Run Pipeline".
   - The status bar will show "PENDING" then "RUNNING".
   - In Databricks, you can show the Job Run starting.
5. **View Results**:
   - Once the job completes (approx 2-3 mins on free tier), the status changes to "SUCCESS".
   - Click "Refresh Status" if needed.
   - The generated runbook will appear in the viewer.
6. **Diff View**: Click "Compare Versions" to see the side-by-side view (simulated).

## ⚠️ Free Tier Limitations & Troubleshooting
- **Cluster Startup**: Community Edition clusters terminate after inactivity. Ensure your cluster is ON before running the demo.
- **Library Installation**: The first run might be slow as it installs `transformers` and `torch`.
- **Memory Errors**: If the job fails with OOM, try reducing the input text size in the notebooks (logic already includes truncation).
- **API Rate Limits**: The backend polls status every 5 seconds. If you hit limits, increase the interval in `App.tsx`.

## 📁 Repository Structure
- `frontend/`: React application source code.
- `backend/`: FastAPI server and Databricks client.
- `databricks/`: Python notebooks for the ETL/AI pipeline.
- `mock_data/`: Sample files for testing.
