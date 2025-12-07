# Databricks notebook source
# MAGIC %md
# MAGIC # Runbook Generator Notebook
# MAGIC Generates the final runbook markdown using a template-based approach (reliable for free tier).

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import os
import pandas as pd
import datetime
import uuid

# COMMAND ----------

dbutils.widgets.text("output_path", "/dbfs/tmp/ps_ai_runbook_gen/runbooks")
dbutils.widgets.text("model_type", "distilbert-base-uncased")
dbutils.widgets.text("input_data", "") # New widget for direct JSON input

output_path = dbutils.widgets.get("output_path")
model_type = dbutils.widgets.get("model_type")
input_data_json = dbutils.widgets.get("input_data")

# COMMAND ----------

import json

# Load Data (Priority: Direct Input > Gold Table)
docs = []

if input_data_json and input_data_json.strip():
    print("Using direct input data (Bypassing DBFS/Gold Table)")
    try:
        input_files = json.loads(input_data_json)
        # Convert to expected format for the rest of the notebook
        for filename, content in input_files.items():
            # Simple entity extraction simulation for direct input
            entities = []
            if "TECH:" in content:
                # Extract tech from content if simulated
                pass 
            
            # For now, we just pass the raw content. 
            # In a real app, we'd run the NLP here or expect pre-processed entities.
            # To make the existing logic work, we'll simulate some entities based on keywords
            if "hadoop" in content.lower(): entities.append("TECH: Hadoop")
            if "hive" in content.lower(): entities.append("TECH: Hive")
            if "spark" in content.lower(): entities.append("TECH: Spark")
            if "databricks" in content.lower(): entities.append("TECH: Databricks")
            if "mlflow" in content.lower(): entities.append("TECH: MLflow")
            if "2024" in content: entities.append("DATE: 2024-01-01") # Mock date
            
            docs.append({
                "path": f"dbfs:/uploads/{filename}", 
                "content": content,
                "entities": entities
            })
        print(f"Loaded {len(docs)} documents from direct input")
    except Exception as e:
        print(f"Error parsing input_data: {e}")
        dbutils.notebook.exit(f"FAILED: Error parsing input data - {str(e)}")

else:
    # Fallback to loading Gold Data (Original Logic)
    try:
        df = spark.table("gold_engagement_vectors")
        docs = df.collect()
        print(f"Loaded {len(docs)} documents from Gold Table")
    except Exception as e:
        print(f"Error loading gold table: {e}")
        # If we are here, it means no input data AND no gold table. 
        # For Community Edition, this is likely fatal if we expected DBFS to work.
        # But we can return a helpful error.
        dbutils.notebook.exit("FAILED: No input data provided and could not load gold table")

# COMMAND ----------

# Extract aggregated insights
all_entities = []
tech_stack = set()
risks = []
dates = []

for row in docs:
    if row['entities']:
        for entity in row['entities']:
            all_entities.append(entity)
            if "TECH:" in entity:
                tech_stack.add(entity.replace("TECH: ", ""))
            if "DATE:" in entity:
                dates.append(entity.replace("DATE: ", ""))

# Simple "AI" Logic for Executive Summary
doc_count = len(docs)
tech_summary = ", ".join(list(tech_stack)[:5]) if tech_stack else "Standard Databricks Stack"

executive_summary = f"""
This engagement involves the analysis of {doc_count} key documents. 
The primary technology stack identified includes **{tech_summary}**. 
The engagement is currently in the planning/execution phase with key milestones identified in the attached schedule.
"""

# COMMAND ----------

# MLflow Experiment Tracking (P0-DB2)
# Track each runbook generation run for observability
import mlflow

try:
    # Set experiment - creates if doesn't exist
    mlflow.set_experiment("/Shared/PS_AI_Runbook_Gen/experiments")
    
    with mlflow.start_run(run_name=f"runbook_gen_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        # Log parameters
        mlflow.log_param("model_type", model_type)
        mlflow.log_param("doc_count", doc_count)
        mlflow.log_param("input_mode", "direct_input" if input_data_json else "gold_table")
        
        # Log tech stack as a comma-separated param (limited to 250 chars)
        tech_list = list(tech_stack)[:10]
        mlflow.log_param("tech_stack", ", ".join(tech_list) if tech_list else "none_detected")
        
        # Log metrics
        mlflow.log_metric("entities_extracted", len(all_entities))
        mlflow.log_metric("unique_technologies", len(tech_stack))
        mlflow.log_metric("dates_found", len(dates))
        
        # Tag for easy filtering
        mlflow.set_tag("pipeline_stage", "generation")
        mlflow.set_tag("experiment_type", "runbook_generation")
        
        print(f"✅ MLflow run logged to experiment: /Shared/PS_AI_Runbook_Gen/experiments")
        print(f"   - Documents: {doc_count}, Entities: {len(all_entities)}, Technologies: {len(tech_stack)}")
        
except Exception as e:
    # MLflow tracking should not block runbook generation
    print(f"⚠️ MLflow tracking skipped (optional): {e}")

# COMMAND ----------

# Generate Professional Runbook Markdown
# Enhanced formatting for better readability and professional appearance

# Calculate additional metrics for the runbook
file_types = {}
for row in docs:
    ext = row['path'].split('.')[-1].lower()
    file_types[ext] = file_types.get(ext, 0) + 1

file_type_summary = ", ".join([f"{count} {ext.upper()}" for ext, count in file_types.items()])

# Determine engagement type based on content analysis
engagement_type = "General Engagement"
if any("migration" in str(row.get('content', '')).lower() for row in docs):
    engagement_type = "Migration Project"
elif any("mlops" in str(row.get('content', '')).lower() or "mlflow" in str(row.get('content', '')).lower() for row in docs):
    engagement_type = "MLOps Implementation"
elif any("hadoop" in str(row.get('content', '')).lower() or "hive" in str(row.get('content', '')).lower() for row in docs):
    engagement_type = "Hadoop/Hive Migration"

# Build the enhanced runbook
markdown_output = f"""# 📘 Professional Services Engagement Runbook

> **Generated by:** PS AI Runbook Generator  
> **Model:** `{model_type}`  
> **Generated:** {datetime.datetime.now().strftime("%B %d, %Y at %H:%M")}

---

## 📋 Engagement Metadata

| Property | Value |
|----------|-------|
| **Engagement Type** | {engagement_type} |
| **Documents Analyzed** | {doc_count} |
| **File Types** | {file_type_summary} |
| **Technologies Detected** | {len(tech_stack)} |
| **Status** | 🟡 DRAFT |

---

## 1️⃣ Executive Summary

{executive_summary.strip()}

### Key Highlights
"""

# Add key highlights based on what was found
if tech_stack:
    markdown_output += f"- **Technology Stack:** {', '.join(list(tech_stack)[:5])}\n"
if dates:
    markdown_output += f"- **Key Dates Identified:** {len(dates)} milestone(s) found\n"
markdown_output += f"- **Document Coverage:** {doc_count} source document(s) analyzed\n"

markdown_output += """
---

## 2️⃣ Source Documents

The following documents were ingested and analyzed:

| Document | Type | Status |
|----------|------|--------|
"""

for row in docs:
    filename = row['path'].split('/')[-1]
    file_ext = filename.split('.')[-1].upper()
    markdown_output += f"| 📄 {filename} | {file_ext} | ✅ Processed |\n"

markdown_output += """
---

## 3️⃣ Technical Architecture

### Identified Technologies
"""

if tech_stack:
    markdown_output += "\n| Technology | Category | Notes |\n|------------|----------|-------|\n"
    for tech in tech_stack:
        category = "Platform" if tech in ["Databricks", "AWS", "Azure", "GCP"] else "Framework" if tech in ["Spark", "MLflow", "Delta Lake"] else "Tool"
        markdown_output += f"| ✅ **{tech}** | {category} | Detected in source documents |\n"
else:
    markdown_output += "\n> ⚠️ No specific technologies were explicitly detected. Manual review recommended.\n"

markdown_output += """
### Architecture Recommendations

Based on the analysis, consider the following architectural patterns:

1. **Data Ingestion Layer**
   - Unity Catalog for centralized governance
   - Delta Lake for reliable data storage
   - Auto Loader for incremental file processing

2. **Processing Layer**
   - Databricks Jobs for orchestration
   - Structured Streaming for real-time needs
   - Photon acceleration for performance

3. **Serving Layer**
   - SQL Warehouses for BI/Analytics
   - Model Serving for ML endpoints
   - Feature Store for ML features

---

## 4️⃣ Risk Assessment

### Identified Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Data quality dependencies | 🟡 Medium | Implement data validation in Bronze layer |
| Timeline constraints | 🟡 Medium | Establish milestone checkpoints |
| Resource availability | 🟢 Low | Define backup personnel |

### Assumptions

- ✅ All provided documents are current and organization-approved
- ✅ Stakeholders have reviewed initial scope
- ✅ Development environment access is available

---

## 5️⃣ Timeline & Milestones

"""

if dates:
    markdown_output += "### Key Dates Extracted\n\n"
    for i, date in enumerate(dates, 1):
        markdown_output += f"- **Milestone {i}:** {date}\n"
else:
    markdown_output += "> 📅 No specific dates were extracted from the documents. Please add key milestones manually.\n"

markdown_output += """
### Recommended Phases

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Discovery | 1-2 weeks | Requirements, Architecture Design |
| Development | 4-6 weeks | MVP, Integration Testing |
| Deployment | 1-2 weeks | Production Release, Documentation |
| Hypercare | 2-4 weeks | Support, Optimization |

---

## 6️⃣ Next Steps

### Immediate Actions (Week 1)
1. [ ] Review and validate the extracted technical stack
2. [ ] Confirm key dates and milestones with stakeholders
3. [ ] Schedule kickoff meeting with all parties

### Short-term Actions (Weeks 2-4)
4. [ ] Complete detailed architecture design
5. [ ] Set up development environment
6. [ ] Begin implementation sprint 1

---

## 📎 Appendix

### Document Processing Summary

```
Total Documents: {doc_count}
Entities Extracted: {len(all_entities)}
Technologies Found: {len(tech_stack)}
Dates Identified: {len(dates)}
```

### Generation Details

- **Pipeline:** PS AI Runbook Generator
- **Model Used:** {model_type}
- **Timestamp:** {datetime.datetime.now().isoformat()}

---

*This runbook was automatically generated by the Databricks Professional Services AI Tooling Prototype. Please review and customize before distribution.*
"""

# COMMAND ----------

# Return output via dbutils.notebook.exit (Works for Community Edition)
# DBFS write is optional and skipped if using direct input to avoid permission issues

if input_data_json and input_data_json.strip():
    # Direct input mode: Skip DBFS write, only return via notebook.exit
    print(f"✅ Runbook generated (length: {len(markdown_output)} chars)")
    print("Returning runbook via notebook.exit (Direct Input Mode - DBFS write skipped)")
    dbutils.notebook.exit(markdown_output)
else:
    # Gold table mode: Try DBFS write
    try:
        # Get Run ID from context if available, else generate one
        try:
            context = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
            run_id = str(context.jobId().get()) if context.jobId().isDefined() else str(uuid.uuid4())
        except:
            run_id = str(uuid.uuid4())
            
        print(f"Writing runbook for Run ID: {run_id}")

        # Create directory
        # Handle DBFS path correctly
        if output_path.startswith("dbfs:"):
            local_output_path = output_path.replace("dbfs:", "/dbfs")
        else:
            local_output_path = output_path
            
        final_dir = os.path.join(local_output_path, run_id)
        os.makedirs(final_dir, exist_ok=True)
        
        file_path = os.path.join(final_dir, "runbook.md")
        with open(file_path, "w") as f:
            f.write(markdown_output)
        
        print(f"✅ Runbook successfully written to {file_path}")
        
        # IMPORTANT: Return the runbook content as notebook output
        # This allows retrieval via Jobs API even without DBFS access (Community Edition compatible)
        dbutils.notebook.exit(markdown_output)
        
    except Exception as e:
        print(f"❌ Error writing runbook: {e}")
        # Still return the content even if DBFS write fails
        dbutils.notebook.exit(markdown_output)

