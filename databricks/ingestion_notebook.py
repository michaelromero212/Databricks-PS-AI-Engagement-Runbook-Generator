# Databricks notebook source
# MAGIC %md
# MAGIC # Ingestion Notebook
# MAGIC Reads uploaded files from DBFS and writes to Bronze Delta table with data quality validation.

# COMMAND ----------

# MAGIC %pip install python-docx

# COMMAND ----------

import os
import pandas as pd
from pyspark.sql.functions import current_timestamp, input_file_name, udf, col, lit
from pyspark.sql.types import StructType, StructField, StringType, BooleanType
from docx import Document

# COMMAND ----------

dbutils.widgets.text("input_path", "/dbfs/tmp/ps_ai_runbook_gen/uploads")
input_path = dbutils.widgets.get("input_path")

# COMMAND ----------

def read_file_content(path):
    if path.endswith(".txt") or path.endswith(".md") or path.endswith(".json") or path.endswith(".csv"):
        with open(path, "r") as f:
            return f.read()
    elif path.endswith(".docx"):
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    return ""

# COMMAND ----------

# P0-DE2: Data Quality Validation
def validate_document(content, filename):
    """
    Validate document content for quality issues.
    Returns tuple of (is_valid: bool, reason: str, quality_score: float)
    """
    if not content or not isinstance(content, str):
        return (False, "empty_or_invalid_content", 0.0)
    
    # Check minimum content length (meaningful content threshold)
    if len(content.strip()) < 50:
        return (False, "content_too_short", 0.1)
    
    # Check maximum content length (1MB text limit)
    if len(content) > 1_000_000:
        return (False, "content_too_large", 0.2)
    
    # Check for binary/garbage content (low letter ratio)
    letter_count = sum(c.isalpha() for c in content[:1000])
    if letter_count < 100 and len(content) > 200:
        return (False, "likely_binary_content", 0.1)
    
    # Basic quality scoring
    quality_score = 1.0
    
    # Penalize very short content
    if len(content) < 200:
        quality_score -= 0.3
    
    # Penalize if no common structure markers
    if not any(marker in content for marker in ['.', '\n', ',', ':']):
        quality_score -= 0.2
    
    return (True, "passed", max(0.0, quality_score))

# COMMAND ----------

# List files
files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(input_path.replace("dbfs:", "/dbfs")) for f in filenames]

data = []
validation_stats = {"passed": 0, "failed": 0, "reasons": []}

for f in files:
    try:
        content = read_file_content(f)
        filename = os.path.basename(f)
        
        # Apply validation
        is_valid, reason, quality_score = validate_document(content, filename)
        
        data.append({
            "path": f, 
            "content": content, 
            "file_type": f.split(".")[-1],
            "is_valid": is_valid,
            "validation_reason": reason,
            "quality_score": quality_score
        })
        
        if is_valid:
            validation_stats["passed"] += 1
        else:
            validation_stats["failed"] += 1
            validation_stats["reasons"].append(f"{filename}: {reason}")
            
    except Exception as e:
        print(f"Error reading {f}: {e}")
        data.append({
            "path": f,
            "content": "",
            "file_type": f.split(".")[-1],
            "is_valid": False,
            "validation_reason": f"read_error: {str(e)[:50]}",
            "quality_score": 0.0
        })
        validation_stats["failed"] += 1

# Print validation summary
print(f"📊 Data Quality Summary:")
print(f"   ✅ Passed: {validation_stats['passed']}")
print(f"   ❌ Failed: {validation_stats['failed']}")
if validation_stats["reasons"]:
    print(f"   ⚠️  Issues: {', '.join(validation_stats['reasons'][:5])}")

# COMMAND ----------

if not data:
    print("No data found")
    dbutils.notebook.exit("No data")

df = spark.createDataFrame(pd.DataFrame(data))
df = df.withColumn("ingestion_time", current_timestamp())

# Log quality metrics
valid_count = df.filter(col("is_valid") == True).count()
total_count = df.count()
print(f"✅ Ingested {total_count} documents ({valid_count} passed validation)")

# COMMAND ----------

# Write to Bronze (including validation metadata for downstream filtering)
df.write.format("delta").mode("overwrite").saveAsTable("bronze_engagement_docs")
print("Written to bronze_engagement_docs with quality metadata")

