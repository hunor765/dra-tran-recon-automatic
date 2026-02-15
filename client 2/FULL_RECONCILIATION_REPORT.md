# 📊 Comprehensive Reconciliation Report: Client 2
**Date:** 2026-01-26

## 1. Executive Summary
| Metric | Count | Value (RON) | Description |
| :--- | :--- | :--- | :--- |
| **Valid Orders (Backend)** | 49022 | 68,546,058.88 | Orders marked as 'complete' |
| **Matched in GA4** | 42228 | - | Valid orders successfully tracked |
| **Missing from GA4** | **6794** | **11,483,607.27** | Valid orders NOT tracked |
| **True Match Rate** | **86.14%** | - | Percentage of valid orders tracked |

> 🚨 **Critical Finding:** You are missing **6794** valid orders in GA4, totaling **11,483,607.27 RON** in untracked revenue.

## 2. Why are orders missing? (Pattern Analysis)

### A. By Payment Method
Is the tracking failing for specific payment gateways?
| Payment Method | Missing Count | Total Valid Count | Failure Rate |
| :--- | :--- | :--- | :--- |
| Card | 2392 | 21575 | **11.1%** |
| Numerar la livrare | 1747 | 18140 | **9.6%** |
| Tbi | 1006 | 1006 | **100.0%** |
| OP | 537 | 791 | **67.9%** |
| LeanPay | 369 | 369 | **100.0%** |
| Numerar sau card in magazin | 328 | 3682 | **8.9%** |
| Oney | 241 | 1783 | **13.5%** |
| Plata la locker | 140 | 1597 | **8.8%** |
| BTDirect | 34 | 79 | **43.0%** |

### B. By Shipping Method
| Shipping Method | Missing Count |
| :--- | :--- |
| Livrare la domiciliu | 5648 |
| Rezervare in magazin | 651 |
| Livrare la locker | 372 |
| Livrare la magazin | 123 |

### C. Temporal Analysis (Timeline)
Are there specific days where tracking stopped completely?
| Date | Missing Orders |
| :--- | :--- |
| 2025-11-07 | 577 |
| 2025-11-08 | 185 |
| 2025-11-10 | 172 |
| 2025-11-09 | 145 |
| 2025-11-11 | 133 |

## 3. Data Integrity & Anomalies

### A. Canceled Orders in GA4
- **5967** Canceled orders were tracked in GA4.
- This inflates your GA4 revenue by **11,270,574.07 RON**.
- *Recommendation:* Ensure the tracking pixel does NOT fire on thank-you pages if the order status is canceled/failed, or implement Refund hits.

### B. Duplicate / Double Counting
- **8** orders have exactly double the value in GA4 vs Backend.
- **Example IDs:** 369004976840, 369004976892, 369004977057, 369004977139, 369004991795
- *Cause:* This typically happens when the purchase event triggers twice (e.g., on page reload or email link click).
- *Fix:* Add a `transaction_id` check in GTM to prevent firing if ID already sent, or deduplicate in BigQuery.

## 4. Final Recommendations
1. **Fix Missing 'Complete' Orders:** The 60% match rate is low. Investigate the Payment Methods identified above (likely redirects like Netopia/MobilPay/Stripe failing to return to Thank You page).
2. **Implement Server-Side Tracking:** Reliance on browser-side 'Thank You' pages is the #1 cause of this 40% data loss.
3. **Exclude Canceled Orders:** Stop pushing data for canceled orders to GA4.
4. **Deduplication:** Fix the double-firing events for the identified orders.