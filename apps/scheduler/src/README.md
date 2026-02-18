# DRA Transaction Reconciliation Ultra (MVP)

## Overview
This is the automated version of the Transaction Reconciliation tool. Unlike the Manual version (Phase 0), this tool connects directly to data sources to perform scheduled audits.

## Data Sources
1. **Google Analytics 4 (GA4)**:
   - Source: Google Analytics Data API (v1beta)
   - Method: `runReport` request
   - Key Dimensions: `transactionId`, `date`, `browser`, `deviceCategory`
   - Key Metrics: `purchaseRevenue`

2. **Ecommerce Backend**:
   - Source: REST API / SQL Database / CSV Feed (URL)
   - Method: Periodic fetch
   - Key Fields: `order_id`, `total_price`, `status`, `payment_method`

## Architecture
- **`ingest.py`**: Connectors for GA4 and Backend APIs.
- **`reconcile.py`**: The core matching logic (reused from Phase 0).
- **`report.py`**: Generates email summaries and PDF reports.
- **`scheduler.py`**: Runs the job daily (CRON or simple loop).

## Setup
1. Place `credentials.json` (Service Account) in root.
2. Configure `config.yaml` with API endpoints and keys.
3. Run `python main.py`.
