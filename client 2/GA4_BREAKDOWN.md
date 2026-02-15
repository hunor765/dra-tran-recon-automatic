# 🕵️‍♀️ GA4 Breakdown: False Positives & Missing Data
**Date:** 2026-01-26

## 1. Canceled Orders FOUND in GA4 (False Positives)
**Total:** 5967 orders
**Impact:** These are Canceled orders that fired the 'Purchase' pixel. This inflates your revenue.

| Payment Method | Count (False Positives) | % of Total False Positives |
| :--- | :--- | :--- |
| Ridicare Magazin | 2981 | 50.0% |
| Card | 1139 | 19.1% |
| Numerar la livrare | 1123 | 18.8% |
| BTDirect | 280 | 4.7% |
| OP | 255 | 4.3% |
| Oney | 98 | 1.6% |
| Plata la locker | 86 | 1.4% |
| Tbi | 3 | 0.1% |
| LeanPay | 2 | 0.0% |

> **Insight:** If 'Card' or 'Oney' are high here, it means the user is redirected to the 'Thank You' page even if the payment failed/was canceled.

## 2. Orders NOT Found in GA4 (Missing Data)
**Total Missing (All Statuses):** 33211

### A. Missing 'Complete' Orders (Revenue Loss)
**Total Missing Valid Orders:** 6794
**Impact:** These are successful sales that GA4/GTM failed to capture.

| Payment Method | Count (Missing) | % of Total Missing Valid |
| :--- | :--- | :--- |
| Card | 2392 | 35.2% |
| Numerar la livrare | 1747 | 25.7% |
| Tbi | 1006 | 14.8% |
| OP | 537 | 7.9% |
| LeanPay | 369 | 5.4% |
| Ridicare Magazin | 328 | 4.8% |
| Oney | 241 | 3.5% |
| Plata la locker | 140 | 2.1% |
| BTDirect | 34 | 0.5% |

### B. Missing 'Canceled' Orders (Correct Behavior)
**Total Missing Canceled Orders:** 25733
(This is largely expected behavior - we generally don't want these in GA4).