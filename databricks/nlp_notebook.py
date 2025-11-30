# Databricks notebook source
# MAGIC %md
# MAGIC # NLP Processing Notebook
# MAGIC Extracts entities using lightweight text processing and writes to Silver Delta table.

# COMMAND ----------

# MAGIC %pip install spacy

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import pandas as pd
from pyspark.sql.functions import udf, col, lit
from pyspark.sql.types import StringType, ArrayType
import re

# COMMAND ----------

# Load Bronze
try:
    bronze_df = spark.table("bronze_engagement_docs")
    print(f"Loaded {bronze_df.count()} documents from bronze_engagement_docs")
except Exception as e:
    print(f"Error loading bronze table: {e}")
    dbutils.notebook.exit("FAILED: Could not load bronze table")

# COMMAND ----------

# Lightweight entity extraction using regex patterns (no heavy ML models)
def extract_entities_simple(text):
    """Extract entities using regex patterns - lightweight and fast"""
    if not text or not isinstance(text, str):
        return []
    
    entities = []
    
    # Extract dates (simple pattern)
    dates = re.findall(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}', text)
    entities.extend([f"DATE: {d}" for d in dates[:5]])
    
    # Extract emails
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    entities.extend([f"EMAIL: {e}" for e in emails[:3]])
    
    # Extract capitalized phrases (likely names/orgs)
    names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text[:2000])
    entities.extend([f"PERSON: {n}" for n in names[:5]])
    
    # Extract key terms
    keywords = ['Databricks', 'AWS', 'Azure', 'Delta Lake', 'Spark', 'Unity Catalog', 
                'ML', 'AI', 'ETL', 'SQL', 'Python', 'Scala']
    found_keywords = [kw for kw in keywords if kw.lower() in text.lower()]
    entities.extend([f"TECH: {k}" for k in found_keywords[:5]])
    
    return entities[:20]  # Limit to 20 entities

extract_udf = udf(extract_entities_simple, ArrayType(StringType()))

# COMMAND ----------

# Apply simple NLP
try:
    silver_df = bronze_df.withColumn("entities", extract_udf(col("content")))
    silver_df = silver_df.withColumn("processing_status", lit("success"))
    print(f"Successfully processed {silver_df.count()} documents")
except Exception as e:
    print(f"Error during entity extraction: {e}")
    # Create error-state dataframe
    silver_df = bronze_df.withColumn("entities", lit([]))
    silver_df = silver_df.withColumn("processing_status", lit("failed"))

# COMMAND ----------

# Write to Silver
try:
    silver_df.write.format("delta").mode("overwrite").saveAsTable("silver_engagement_enriched")
    print("✅ Written to silver_engagement_enriched")
except Exception as e:
    print(f"❌ Error writing to silver table: {e}")
    dbutils.notebook.exit("FAILED: Could not write to silver table")
