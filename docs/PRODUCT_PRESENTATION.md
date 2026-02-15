# DRA Transaction Reconciliation Platform - Product Presentation Guide

## 1. Introduction (1 Minute)
**Objective**: unified platform for reconciling E-commerce backend data with Google Analytics 4 (GA4) to ensure data integrity and accurate reporting.

**The Problem**:
- Discrepancies between "Reality" (Backend Orders) and "Tracking" (GA4).
- Causes: Ad blockers, cancelled orders, payment redirects, client-side errors.
- Impact: Inaccurate marketing ROAS, mistrust in data.

**The Solution**: A hybrid approach.
1. **Manual Tool**: For deep-dive, visual auditing and manual correction by humans.
2. **Automated Analysis**: For daily monitoring and red-flag alerting.

---

## 2. The Manual Reconciliation Tool (3 Minutes)
*(Ref: `dra-tran-recon-manual`)*

**Target Audience**: Finance Managers, Data Analysts.

**Key Features**:
*   **Drag-and-Drop Interface**: Upload `Backend.csv` and `GA4.csv` directly in the browser.
*   **Visual Dashboard**:
    *   Big Number Metrics: Total Revenue Match %, Transaction Count Gap.
    *   Trend Charts: Daily discrepancies visualised.
*   **Interactive Reconciliation Table**:
    *   **Green Rows**: Perfect matches (Id + Value).
    *   **Yellow Rows**: Value mismatches (e.g., Tax differences).
    *   **Red Rows**: Missing transactions (The "Ghost" orders).
*   **Actionable Exports**: Download "Missing Orders" report to upload to GA4 via Measurement Protocol.

**Tech Stack**:
*   **Frontend**: Next.js 14, Tailwind CSS (Modern, clean UI).
*   **Backend**: FastAPI, Pandas (Fast processing of large CSVs).
*   **State**: Local processing (Privacy focused) or Supabase (Cloud persistence).

---

## 3. The Core Analysis Logic (2 Minutes)
*(Ref: `reconciliation_analysis.py`)*

The "Brain" behind the tools. How we analyze the gap:

1.  **Data Harmonization**:
    *   Standardizing Date formats (YYYY-MM-DD).
    *   Cleaning Transaction IDs (trimming prefixes like `#`).
2.  **Matching Algorithm**:
    *   `Intersection`: IDs present in both.
    *   `Set Difference`: IDs in A but not B (and vice versa).
3.  **Value Comparison**:
    *   Checks for `abs(diff) < 0.01` to account for floating point rounding.
    *   Identifies specific "Tax/Shipping" related discrepancies.
4.  **Status breakdown**:
    *   Splits gaps by Order Status (e.g., "Cancelled", "Refunded") to isolate legitimate exclusions.

---

## 4. The "Ultra" Automated Tool (3 Minutes)
*(Ref: `dra-tran-recon-ultra`)*

**Target Audience**: CTOs, Automated Reporting Systems.

**Workflow**:
1.  **Ingest**: Connectors fetch live data via APIs (not CSV files).
    *   *Source A*: WooCommerce/Shopify API.
    *   *Source B*: Google Analytics Data API (BetaAnalyticsDataClient).
2.  **Process**: Runs the Core Analysis Logic nightly.
3.  **Report**:
    *   Sends an HTML Email Summary to stakeholders.
    *   Alerts if Discrepancy > 5%.

**Benefits**:
*   "Set and Forget".
*   Proactive detection of tracking failures (e.g., if a deploy breaks the DataLayer).

---

## 5. Technical Methodology & Algorithm (Q&A Prep)

**Q: "What is the algorithm behind the reconciliation?"**

**A: The "Tri-Phase Reconciliation Protocol"**

Our methodology follows a strict three-phase process designed to handle the messy reality of disjointed data sources.

### Phase 1: Data Normalization (The "Common Language")
Before matching, we force both datasets into a standardized schema.
*   **ID Normalization**: We treat all Transaction IDs as strings and strip whitespace/prefixes (e.g., `#1001` becomes `1001`).
*   **Temporal Alignment**: Timestamps are converted to `YYYY-MM-DD` and aligned to the shop's local timezone to fix "Midnight Drift" (where an order at 23:59 appears next day in GA4).
*   **Floating Point Hygiene**: All currency values are processed using strict decimal precision, not standard floating point, to prevent `0.0000001` mismatches.

### Phase 2: Set-Theoretic Matching (The Core Algorithm)
We use a **Set Theory** approach rather than simple iteration, which makes the tool O(n) efficient even for millions of rows.
1.  **The Intersection ($\cap$)**: IDs present in **both** sets. We then apply a `value_delta` check. If `abs(BackendValue - GA4Value) > 0.01`, it's flagged as a "Value Mismatch" (often Tax/Shipping).
2.  **The Backend Difference ($A - B$)**: The "Ghosts". These are real money orders missing from analytics. We segment these by **Order Status** (Cancelled vs. Paid) to filter out noise.
3.  **The GA4 Difference ($B - A$)**: The "Phantoms". Duplicate transactions or test orders that don't exist in the backend.

### Phase 3: Root Cause Heuristics
The system doesn't just say "Mismatch"; it attempts to classify *why* using heuristic logic:
*   *Is the missing order Status = Cancelled?* -> **Legitimate Exclusion**.
*   *Is the browser Safari?* -> **ITP/Cookie Blocking**.
*   *Is the value difference exactly 19%?* -> **VAT Exclusion Error**.

---

## 6. Q&A / Next Steps
