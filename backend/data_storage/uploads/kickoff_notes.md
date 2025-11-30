# Project Kickoff Notes - Global Retailer Migration

**Date:** 2024-03-15
**Attendees:** 
- Sarah Chen (Databricks SA)
- Mike Ross (Client Lead)
- Jessica Pearson (Client DE)

## Agenda
1. Project Scope
2. Current Architecture
3. Success Criteria
4. Timeline

## Key Discussion Points
- **Scope:** Migration of on-prem Hadoop cluster to Databricks on AWS.
- **Data Volume:** Approx 50TB of historical sales data.
- **Pain Points:** 
    - Current nightly jobs take 14 hours, missing SLAs.
    - No ability to run ad-hoc queries during the day.
    - Data quality issues in the 'customer' table.
- **Goals:**
    - Reduce ETL runtime to < 4 hours.
    - Enable real-time dashboarding for executive team.
    - Implement Unity Catalog for governance.

## Action Items
- [ ] Mike to provide AWS cross-account role ARN.
- [ ] Sarah to share reference architecture for "Lakehouse for Retail".
- [ ] Jessica to export sample DDLs from Hive.

## Risks
- Network connectivity between on-prem and VPC might delay initial load.
- Legacy UDFs in Java might need rewriting in PySpark.
