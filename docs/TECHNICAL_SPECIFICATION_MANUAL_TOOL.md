# DRA Transaction Reconciliation (Manual) - Technical Specification

## 1. Overview
This document describes the technical implementation and analysis logic of the **DRA Transaction Reconciliation Tool (Manual Version)**, located in `dra-tran-recon-manual_backup`.

**Objective**: To replicate the "Tri-Phase Reconciliation" logic in other applications or languages.

## 2. Core Analysis Logic (`backend/main.py`)

The heart of the application is the `/analyze` endpoint. It processes two datasets (GA4 and Backend) using Pandas.

### 2.1. Input Data Requirements
*   **GA4 Export**: CSV/Excel containing Transaction ID, Value, Date, Browser, Device.
*   **Backend Export**: CSV/Excel containing Order ID, Value, Date, Payment Method, Shipping Method, Status.

### 2.2. Phase 1: Data Normalization (Pre-processing)

Before comparing, both datasets undergo strict cleaning:

1.  **Transaction IDs**:
    *   **GA4**: Converted to string, stripped of whitespace.
    *   **Backend**: Converted to string, **removes '-1' suffix** (specific constraint), stripped of whitespace.
2.  **Values**:
    *   Converted to numeric (float), non-numeric coerced to NaN, then filled with 0.

```python
# Pseudo-code
ga4['clean_id'] = ga4[id_col].str.strip()
backend['clean_id'] = backend[id_col].str.replace('-1', '').str.strip()
```

### 2.3. Phase 2: Set-Theoretic Matching

We use Set Difference to classify transactions into three buckets:

1.  **Common (Matched)**: $ID \in A \cap B$
2.  **Backend Only (Missing in GA4)**: $ID \in A \setminus B$
3.  **GA4 Only (Phantoms)**: $ID \in B \setminus A$

#### Value Comparison (for Matched IDs only)
*   **Aggregation**: GA4 transactions are grouped by ID and summed (to handle duplicate hits for the same ID).
*   **Difference Calculation**: `Diff = BackendValue - GA4Value`
*   **Exact Match Definition**: `abs(Diff) < 1.0` (Allows for minor rounding/currency differences).

### 2.4. Phase 3: Dimensional Analysis

The tool calculates "Tracking Rate" breakdown by specific dimensions to find root causes.

**Formula**:
$$ MatchRate \% = \frac{\text{Count of IDs in Dimension present in GA4}}{\text{Total Count of IDs in Dimension}} \times 100 $$

**Dimensions Analyzed**:
1.  **Payment Method**: Identifies if specific gateways (e.g., PayPal, Stripe) are failing to redirect back to the "Thank You" page.
    *   *Logic*: Group Backend IDs by Payment Method -> Check intersection with GA4 IDs.
2.  **Shipping Method**: Checks if specific logical flows (e.g., "Store Pickup" vs "Courier") affect tracking.
3.  **Order Status**: Helps filter out legitimate gaps (e.g., "Cancelled" orders should not be in GA4).
4.  **Tech Stack (Browser/Device)**: Analyzes the *Matched* subset to see if specific browsers (e.g., Safari/iPhone) are under-represented relative to market share (indicating ITP issues).

### 2.5. Phase 4: Temporal Analysis (Daily Evolution)

*   **Logic**: Parses backend dates.
*   **Grouping**: Groups transactions by Day (YYYY-MM-DD).
*   **Metric**: Calculates `MatchRate` per day.
*   **Purpose**: Detects specific days where tracking code might have been broken (e.g., a bad deploy on Friday).

## 3. Heuristic Recommendations Engine

The system automatically generates recommendations based on thresholds:

| Trigger | Severity | Recommendation |
| :--- | :--- | :--- |
| **Payment Method Rate = 0%** | **CRITICAL** | "Implement server-side tracking immediately." (Likely redirect failure) |
| **Payment Method Rate < 50%** | **HIGH** | "Review redirect flows and cross-domain tracking." |
| **Overall Match Rate < 80%** | **MEDIUM** | "Consider Measurement Protocol." |

## 4. API Specification

### Endpoints
*   `POST /upload/ga4`: Multipart upload (CSV/XLSX). Returns preview.
*   `POST /upload/backend`: Multipart upload (CSV/XLSX). Returns preview.
*   `POST /analyze`: JSON Body with Column Mapping. Returns complex JSON analysis.
*   `POST /report/pdf`: Generates PDF report based on analysis.

### Data Model (`AnalysisResult`)
```json
{
  "summary": { "match_rate": 95.5, ... },
  "payment_analysis": [ { "method": "PayPal", "rate": 20.0, "missing": 50 } ],
  "recommendations": [ ... ]
}
```
