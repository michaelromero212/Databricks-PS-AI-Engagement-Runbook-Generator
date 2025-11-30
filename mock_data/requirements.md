# Functional Requirements Specification
## Project: Retail Lakehouse Migration

### 1. Data Ingestion
- **REQ-001:** System must ingest POS transaction data every 15 minutes.
- **REQ-002:** System must handle late-arriving data up to 3 days.
- **REQ-003:** All PII data (credit card, email) must be masked at ingestion.

### 2. Data Processing
- **REQ-004:** Daily aggregation jobs must complete by 6 AM EST.
- **REQ-005:** Currency conversion must use the daily spot rate from the Finance API.

### 3. Governance & Security
- **REQ-006:** Row-level security must be implemented based on 'Region' column.
- **REQ-007:** Only the 'Finance' group can access the 'margin' column.

### 4. Performance
- **REQ-008:** Dashboard queries must return in under 2 seconds for 95% of requests.
- **REQ-009:** The system must scale to support 50 concurrent users.
