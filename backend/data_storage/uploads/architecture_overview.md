# Architecture Overview

## Current State (Legacy)
- **Compute:** On-premise Hadoop Cluster (Hortonworks), 50 nodes.
- **Storage:** HDFS, approx 50TB.
- **Orchestration:** Oozie workflows.
- **Consumption:** Tableau connected via Hive JDBC (slow).

## Future State (Databricks Lakehouse)
- **Cloud Provider:** AWS
- **Storage:** S3 (Delta Lake format)
    - Bronze: Raw ingestion (JSON/CSV)
    - Silver: Cleaned, Enriched, masked PII
    - Gold: Aggregated business level tables
- **Compute:** Databricks Jobs Clusters (Photon enabled)
- **Orchestration:** Databricks Workflows
- **Governance:** Unity Catalog
- **Consumption:** Databricks SQL Serverless for Tableau & PowerBI

## Integration Points
- **Source:** Kafka (Sales), Oracle (Inventory), Salesforce (CRM)
- **Identity:** Okta SSO integration
