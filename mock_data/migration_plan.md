# Legacy Hadoop to Databricks Migration Plan

## 1. Executive Summary
The goal of this engagement is to migrate the existing on-premise Hadoop (Cloudera) data lake to Databricks on AWS. This includes migrating 500TB of HDFS data, converting Hive tables to Delta Lake, and refactoring 200+ Oozie workflows to Databricks Workflows.

## 2. Current State
- **Platform:** Cloudera CDP 7.1
- **Storage:** HDFS (500TB)
- **Compute:** YARN, Hive, Spark 2.4
- **Orchestration:** Oozie
- **Key Pain Points:** High maintenance costs, lack of scalability, inability to support modern AI workloads.

## 3. Target State
- **Platform:** Databricks E2 Architecture on AWS
- **Storage:** S3 (Delta Lake)
- **Compute:** Databricks Jobs & SQL Warehouses
- **Orchestration:** Databricks Workflows
- **Governance:** Unity Catalog

## 4. Migration Strategy
### Phase 1: Foundation
- Setup AWS VPC and S3 buckets.
- Deploy Databricks workspace using Terraform.
- Configure Unity Catalog metastore.

### Phase 2: Data Migration
- Use Databricks Autoloader or DistCp to move HDFS data to S3.
- Convert Parquet/Avro data to Delta Lake format.
- `CONVERT TO DELTA` for existing external tables.

### Phase 3: Code Refactoring
- Rewrite HiveQL to Spark SQL.
- Convert Oozie XML to Databricks Asset Bundles (DABs).
- Upgrade Spark 2.4 code to Spark 3.5.

## 5. Risks
- **Data Consistency:** Ensuring data parity between HDFS and S3 during cutover.
- **Performance:** Tuning Spark jobs for cloud object storage vs HDFS.
- **Skill Gap:** Team needs training on Unity Catalog and Delta Lake best practices.
