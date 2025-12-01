# 📘 Databricks PS AI Engagement Runbook Generator

> An intelligent automation tool that transforms Professional Services engagement artifacts into comprehensive, AI-generated runbooks using Databricks workflows, designed for **Databricks Community Edition compatibility**.

---

## 🎯 Project Overview

This application automates the creation of Professional Services engagement runbooks by analyzing project documentation using AI. Built with a modern web stack and integrated with Databricks, it demonstrates end-to-end data processing, NLP analysis, and intelligent document generation—all orchestrated through the Databricks platform.

### What Does It Do?

- **Smart Document Analysis**: Ingests kickoff notes, Slack conversations, Jira tickets, and architecture diagrams
- **AI-Powered Insights**: Uses NLP models to extract key technologies, risks, dates, and deliverables
- **Automated Runbook Generation**: Creates professional, markdown-formatted engagement runbooks
- **Real-Time Processing**: Live pipeline status tracking with visual feedback
- **Community Edition Ready**: Fully functional on Databricks free tier with DBFS bypass architecture

---

## 🏆 Why This Matters for Databricks Professional Services

### Business Value
1. **Time Savings**: Reduces runbook creation time from hours to minutes
2. **Consistency**: Ensures standardized documentation across all engagements
3. **Knowledge Capture**: Automatically extracts and structures tribal knowledge from conversations
4. **Scalability**: Handles multiple concurrent engagement analyses

###Technical Differentiation
- **Databricks-Native**: Showcases real-world usage of Jobs API, multi-task workflows, and notebook orchestration
- **Community Edition Compatible**: Innovative DBFS bypass technique using job parameters instead of file storage
- **Production-Ready Patterns**: Demonstrates proper error handling, timeout management, and fallback strategies
- **Modern Stack**: React + FastAPI + Databricks = Enterprise-grade architecture

---

## 🖼️ Application Screenshots

### 1. Dashboard View - Scenario Selection
![Dashboard Initial View](docs/images/01_dashboard_view.png)

**What You're Seeing**: The main dashboard presents four pre-configured demo scenarios:
- **Scenario A (Kickoff Notes Only)**: Minimal input for quick test
- **Scenario B (Full Engagement)**: Complete artifact set (Slack, Jira, architecture docs)
- **Scenario C (Hadoop Migration)**: Specialized migration project context
- **Scenario D (MLOps Design)**: ML platform architecture focus

The clean UI shows Databricks connectivity status and pipeline execution steps in the left sidebar.

---

### 2. Data Loading Confirmation
![Scenario Loaded](docs/images/02_scenario_loaded.png)

**What You're Seeing**: After selecting a scenario, the system loads the corresponding files and displays confirmation:
- **File Count**: "Successfully loaded 1 files. Ready to generate."
- **Status Indicator**: Green confirmation message
- **Ready State**: Generate Runbook button is now active

**Behind the Scenes**: The backend reads files from `mock_data/`, serializes them to JSON, and prepares them as job parameters (bypassing DBFS write requirements for Community Edition).

---

### 3. Pipeline Execution in Progress
![Pipeline Running](docs/images/03_pipeline_running.png)

**What You're Seeing**: Real-time pipeline status visualization:
- **Run ID Badge**: Unique identifier for this job execution (e.g., `Run ID: 962308258988139`)
- **Status Badge**: Shows "RUNNING" in blue
- **Sidebar Indicators**: Visual progress through 4 pipeline stages:
  - Ingestion ✓
  - NLP Analysis (active, pulsing indicator)
  - Embeddings
  - Generation
- **Content Area**: "Starting pipeline..." message with loading animation

**Performance Note**: On Databricks Community Edition, this typically takes **90-120 seconds** due to cluster cold start and limited compute resources.

---

### 4. Generated Runbook Display
![Runbook Generated](docs/images/04_runbook_output.png)

**What You're Seeing**: The final AI-generated runbook rendered in markdown:
- **SUCCESS status badge** (green)
- **Professional formatting** with headers, bullet points, and emojis
- **Executive Summary** highlighting analyzed documents count
- **Processed Files** list showing input artifacts
- **Next Steps** and recommendations

**Output Quality**: The runbook includes extracted technologies (Databricks,Spark, MLflow), identified risks, timeline information, and structured action items—all generated from analyzing the input documents.

---

## 🏗️ Architecture & Tech Stack

### Frontend (React + TypeScript)
- **Framework**: Vite + React 18
- **Styling**: TailwindCSS for modern, responsive UI
- **State Management**: React hooks for pipeline status tracking
- **Markdown Rendering**: `marked.js` for runbook display
- **File**: `test_ui.html` (standalone demo) or full React app in `frontend/`

### Backend (Python + FastAPI)
- **API Framework**: FastAPI 0.104+ (async, high-performance)
- **Databricks Integration**: Custom client for Jobs API 2.1
- **File Handling**: Multi-part uploads, local storage management
- **Environment**: Pydantic settings for configuration
- **Key Innovation**: Direct input parameter passing to bypass DBFS restrictions

### Databricks Pipeline (4-Stage Workflow)
```
┌──────────────┐
│  Ingestion   │  Read input files, validate structure
└──────┬───────┘
       ↓
┌──────────────┐
│ NLP Analysis │  Extract entities, dates, technologies
└──────┬───────┘
       ↓
┌──────────────┐
│  Embeddings  │  Generate semantic vectors (future: similarity search)
└──────┬───────┘
       ↓
┌──────────────────┐
│ Runbook Generator│  Template-based markdown generation
└──────────────────┘
```

**Notebooks Locations**: `/Workspace/Shared/PS_AI_Runbook_Gen/`
- `ingestion_notebook.py`
- `nlp_notebook.py`
- `embeddings_notebook.py`
- `runbook_generator_notebook.py`

---

## 🔌 Databricks Integration Deep Dive

### Jobs API 2.1 Usage
```python
# Trigger job with parameters
run_id = client.trigger_job(
    job_id=DATABRICKS_JOB_ID,
    params={
        "model_type": "distilbert-base-uncased",
        "input_data": json.dumps({"file.md": "content..."})  # DBFS bypass!
    }
)

# Poll for status
status = client.get_run_status(run_id)  # PENDING → RUNNING → SUCCESS

# Retrieve output (Community Edition compatible!)
runbook = client.get_run_output(task_run_id)  # From dbutils.notebook.exit()
```

### Community Edition Workaround
**Problem**: Community Edition tokens lack DBFS write permissions.

**Solution**: 
1. **Backend**: Serializes file content to JSON string parameter
2. **Notebook**: Parses `input_data` widget instead of reading from DBFS
3. **Output**: Returns via `dbutils.notebook.exit()` instead of writing files
4. **Retrieval**: Backend fetches from `/api/2.1/jobs/runs/get-output`

**Result**: ✅ Full functionality without requiring DBFS access!

---

## 🚀 Quick Start Guide

### Prerequisites
- **Databricks Account**: Community Edition (free) or Standard
- **Python 3.8+** and **pip**
- **(Optional) Node.js 18+** for React frontend

### 1. Databricks Setup (5 minutes)

**Upload Notebooks:**
1. Navigate to Databricks Workspace → `/Workspace/Shared/`
2. Create folder: `PS_AI_Runbook_Gen`
3. Import all 4 notebooks from `databricks/` folder

**Create Job:**
1. Go to **Workflows** → **Create Job**
2. Add 4 tasks in sequence:
   - Task 1: "ingestion" → `ingestion_notebook`
   - Task 2: "nlp_processing" → `nlp_notebook` (depends on Task 1)
   - Task 3: "embeddings" → `embeddings_notebook` (depends on Task 2)
   - Task 4: "generation" → `runbook_generator_notebook` (depends on Task 3)
3. Configure cluster: **Single Node** or any Community Edition compatible cluster
4. **Save job** and copy the **Job ID** from URL

**Get API Token:**
- User Settings → Developer → Access Tokens → Generate New Token

### 2. Backend Setup (2 minutes)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "DATABRICKS_HOST=https://community.cloud.databricks.com" > .env
echo "DATABRICKS_TOKEN=dapi..." >> .env  # Your token
echo "DATABRICKS_JOB_ID=123456" >> .env  # Your job ID

# Start server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Launch Application

**Option A: Standalone HTML (Fastest)**
```bash
# Just open in browser
open test_ui.html
```

**Option B: Full React App**
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### 4. Demo Workflow

1. **Select Scenario**: Click "Kickoff Notes Only" card
2. **Wait for Load**: ~10-12 seconds (DBFS timeout is normal)
3. **Generate**: Click "Generate Runbook" button
4. **Monitor**: Watch sidebar indicators (90-120 sec on free tier)
5. **View Results**: AI-generated runbook appears on SUCCESS

---

## 📊 Performance Benchmarks

| Metric | Community Edition | Standard Workspace |
|--------|-------------------|-------------------|
| Cluster Cold Start | ~30-45 seconds | ~15-20 seconds |
| Data Loading | ~10 seconds | ~2 seconds |
| Pipeline Execution | 90-120 seconds | 40-60 seconds |
| **Total Time** | **~2 minutes** | **~1 minute** |

**Optimization Tips**:
- Keep cluster running during demos (auto-terminates after 2h idle)
- Pre-warm by running a test job before presentation
- Use "Single Node" cluster for fastest startup

---

## 🛠️ Project Structure

```
Databricks-PS-AI-Engagement-Runbook-Generator/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── databricks_client.py    # Jobs API integration
│   ├── runbook_storage.py      # Local file management
│   └── util/
│       ├── settings.py          # Environment configuration
│       └── schema.py            # Pydantic models
├── databricks/
│   ├── ingestion_notebook.py
│   ├── nlp_notebook.py
│   ├── embeddings_notebook.py
│   └── runbook_generator_notebook.py
├── frontend/                    # React application
│   └── src/
│       ├── components/          # UI components
│       └── lib/                 # API client
├── mock_data/                   # Demo scenarios
│   ├── kickoff_notes.md
│   ├── slack_export.json
│   ├── jira_tickets.csv
│   └── architecture_overview.md
└── test_ui.html                 # Standalone demo
```

---

## 🎓 Key Learnings & Technical Highlights

### For Hiring Managers
This project demonstrates:
- **End-to-End Ownership**: From UI design to cloud orchestration
- **Problem Solving**: Creative DBFS bypass solution for Community Edition
- **Production Thinking**: Timeout handling, error recovery, fallback strategies
- **Modern Stack Proficiency**: React, FastAPI, Databricks, TypeScript

### For Technical Reviewers
Notable implementations:
- **Async/Await Patterns**: FastAPI background tasks for job polling
- **API Design**: RESTful endpoints with proper status codes
- **State Management**: Frontend handles PENDING → RUNNING → SUCCESS transitions
- **Error Boundaries**: Graceful degradation when APIs fail
- **Type Safety**: Pydantic models for request/response validation

---

## 🐛 Troubleshooting

### "Internal Server Error" on Pipeline Trigger
**Cause**: Missing environment variables  
**Fix**: Verify `.env` file has all 3 variables set correctly

### "DBFS permission limits" or Timeout Messages
**Status**: ✅ **This is normal!** The app works via Jobs API bypass  
**Action**: None needed—system will proceed automatically

### Job Stuck in "RUNNING" for >5 minutes
**Cause**: Cluster terminated or library installation failed  
**Fix**: Check Databricks Job Run logs, restart cluster if needed

### "Local Fallback" Runbook Appears
**Cause**: Frontend `fetchRunbook()` issue (known bug in `test_ui.html`)  
**Workaround**: Use backend API directly: `curl http://localhost:8000/runbook/latest`  
**Status**: Fix pending in next version

---

## 📝 License

This project is a demonstration/portfolio piece. Feel free to reference architecture patterns, but please credit if used in production.

---

## 👤 Author

**Michael Romero**  
*Aspiring Databricks Professional Services Engineer*

📧 Contact: [your-email@example.com]  
🔗 LinkedIn: [your-linkedin-url]  
💼 Portfolio: [your-portfolio-url]

---

## 🙏 Acknowledgments

- **Databricks Community Edition** for providing free access to platform capabilities
- **HuggingFace** for open-source NLP models
- **FastAPI** and **React** communities for excellent documentation

---

**Built with ❤️ to showcase Databricks platform expertise and full-stack engineering capabilities.**
