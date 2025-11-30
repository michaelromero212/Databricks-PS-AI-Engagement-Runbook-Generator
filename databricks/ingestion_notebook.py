# Databricks notebook source
# MAGIC %md
# MAGIC # Ingestion Notebook
# MAGIC Reads uploaded files from DBFS and writes to Bronze Delta table.

# COMMAND ----------

# MAGIC %pip install python-docx

# COMMAND ----------

import os
import pandas as pd
from pyspark.sql.functions import current_timestamp, input_file_name
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

# List files
files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(input_path.replace("dbfs:", "/dbfs")) for f in filenames]

data = []
for f in files:
    try:
        content = read_file_content(f)
        data.append({"path": f, "content": content, "file_type": f.split(".")[-1]})
    except Exception as e:
        print(f"Error reading {f}: {e}")

# COMMAND ----------

if not data:
    print("No data found")
    dbutils.notebook.exit("No data")

df = spark.createDataFrame(pd.DataFrame(data))
df = df.withColumn("ingestion_time", current_timestamp())

# COMMAND ----------

# Write to Bronze
df.write.format("delta").mode("overwrite").saveAsTable("bronze_engagement_docs")
print("Written to bronze_engagement_docs")
