# Databricks notebook source
# MAGIC %md
# MAGIC # Embeddings Generation Notebook
# MAGIC Creates simple feature vectors from the enriched data (lightweight approach for free tier).

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import pandas as pd
from pyspark.sql.functions import udf, col, lit, length, size
from pyspark.sql.types import ArrayType, FloatType
import hashlib

# COMMAND ----------

# Load Silver
try:
    silver_df = spark.table("silver_engagement_enriched")
    print(f"Loaded {silver_df.count()} documents from silver_engagement_enriched")
except Exception as e:
    print(f"Error loading silver table: {e}")
    dbutils.notebook.exit("FAILED: Could not load silver table")

# COMMAND ----------

# Lightweight embedding generation using simple hashing and feature extraction
# This avoids loading large sentence-transformer models which crash on serverless
def create_simple_embedding(text):
    """
    Generate a simple 128-dimensional vector from text without ML models.
    Uses text features like character distribution, length, etc.
    """
    if not text or not isinstance(text, str):
        return [0.0] * 128
    
    # Normalize text
    text = text.lower()[:5000]
    
    # Create 128-dim vector
    embedding = []
    
    # 1. Character distribution (first 26 dims: a-z frequency)
    char_freq = [0.0] * 26
    for char in text:
        if 'a' <= char <= 'z':
            char_freq[ord(char) - ord('a')] += 1
    # Normalize
    total_chars = sum(char_freq) or 1
    char_freq = [f / total_chars for f in char_freq]
    embedding.extend(char_freq)
    
    # 2. Statistical features (next 20 dims)
    embedding.append(float(len(text)) / 10000.0)  # Length
    embedding.append(float(text.count(' ')) / (len(text) or 1))  # Space density
    embedding.append(float(text.count('.')) / (len(text) or 1))  # Sentence markers
    embedding.append(float(text.count(',')) / (len(text) or 1))  # Comma density
    embedding.append(float(sum(c.isupper() for c in text)) / (len(text) or 1))  # Uppercase ratio
    
    # Add more simple features
    embedding.append(float(text.count('databricks')))
    embedding.append(float(text.count('aws')))
    embedding.append(float(text.count('azure')))
    embedding.append(float(text.count('ml') + text.count('ai')))
    embedding.append(float(text.count('data')))
    embedding.append(float(text.count('sql')))
    embedding.append(float(text.count('python')))
    embedding.append(float(text.count('spark')))
    embedding.append(float(text.count('delta')))
    embedding.append(float(text.count('table')))
    embedding.append(float(text.count('cluster')))
    embedding.append(float(text.count('job')))
    embedding.append(float(text.count('notebook')))
    embedding.append(float(text.count('pipeline')))
    embedding.append(float(text.count('workflow')))
    
    # 3. Hash-based features (remaining 82 dims)
    # Use different hash functions for variety
    for i in range(82):
        hash_val = int(hashlib.md5((text + str(i)).encode()).hexdigest(), 16)
        embedding.append((hash_val % 1000) / 1000.0)
    
    return embedding[:128]  # Ensure exactly 128 dimensions

embedding_udf = udf(create_simple_embedding, ArrayType(FloatType()))

# COMMAND ----------

# Generate embeddings
try:
    gold_df = silver_df.withColumn("embedding", embedding_udf(col("content")))
    gold_df = gold_df.withColumn("embedding_dim", lit(128))
    gold_df = gold_df.withColumn("embedding_method", lit("simple_hash_features"))
    print(f"Successfully generated embeddings for {gold_df.count()} documents")
except Exception as e:
    print(f"Error during embedding generation: {e}")
    dbutils.notebook.exit("FAILED: Could not generate embeddings")

# COMMAND ----------

# Write to Gold
try:
    gold_df.write.format("delta").mode("overwrite").saveAsTable("gold_engagement_vectors")
    print("✅ Written to gold_engagement_vectors")
except Exception as e:
    print(f"❌ Error writing to gold table: {e}")
    dbutils.notebook.exit("FAILED: Could not write to gold table")
