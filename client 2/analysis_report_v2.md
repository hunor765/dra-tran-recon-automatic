# Client 2 Reconciliation Analysis

## Executive Summary
- **GA4 Transactions**: 52127
- **Backend Transactions**: 84979
- **Matched**: 51768
- **Match Rate (vs Backend)**: 60.92%

## 1. Missing in GA4 Analysis
Transactions found in Backend but NOT in GA4: **33211**

### Breakdown by Status of Missing Orders
| Status | Count | Percentage |
|--------|-------|------------|
| canceled | 25733 | 77.5% |
| complete | 6794 | 20.5% |
| returnata | 466 | 1.4% |
| pending_payment | 115 | 0.3% |
| waiting_navision | 74 | 0.2% |
| pending | 25 | 0.1% |
| to_pay | 2 | 0.0% |
| waiting_tazz | 1 | 0.0% |
| redirected | 1 | 0.0% |

**Total Value of Missing Orders**: 97,156,550.24

## 2. Value Discrepancies (Matched Orders)
Orders with value discrepancy (> 1.0 unit): **8**

Top 10 Discrepancies:
| ID | Backend Value | GA4 Value | Diff |
|----|---------------|-----------|------|
| 369004992125 | 3124.98 | 6249.96 | -3124.98 |
| 369004976892 | 2072.99 | 4145.98 | -2072.99 |
| 369004976840 | 1974.98 | 3949.96 | -1974.98 |
| 369004991938 | 1873.99 | 3747.98 | -1873.99 |
| 369004991795 | 1773.99 | 3547.98 | -1773.99 |
| 369004977057 | 716.99 | 1433.98 | -716.99 |
| 369004992123 | 466.99 | 933.98 | -466.99 |
| 369004977139 | 213.99 | 427.98 | -213.99 |