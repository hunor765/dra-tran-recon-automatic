# 💳 Payment Method vs. Order Status Analysis
**Date:** 2026-01-26

## 1. Overview (Top Payment Methods)
Total orders by payment method:
| metoda_plata                |   Total |
|:----------------------------|--------:|
| Card                        |   33199 |
| Numerar la livrare          |   21587 |
| Oney                        |    8873 |
| Numerar sau card in magazin |    7187 |
| LeanPay                     |    5207 |
| Tbi                         |    3579 |
| BTDirect                    |    2080 |
| Plata la locker             |    1950 |
| OP                          |    1317 |

## 2. Status Distribution Details
How does each payment method perform? (Row Percentages)
| Method                      |   Total Orders | complete (%)   | canceled (%)   | returnata (%)   | waiting_navision (%)   | pending (%)   |
|:----------------------------|---------------:|:---------------|:---------------|:----------------|:-----------------------|:--------------|
| Card                        |          33199 | 21575 (65.0%)  | 10417 (31.4%)  | 1012 (3.0%)     | 135 (0.4%)             | 11 (0.0%)     |
| Numerar la livrare          |          21587 | 18140 (84.0%)  | 1292 (6.0%)    | 2036 (9.4%)     | 93 (0.4%)              | 18 (0.1%)     |
| Oney                        |           8873 | 1783 (20.1%)   | 6989 (78.8%)   | 87 (1.0%)       | 10 (0.1%)              | 0 (0.0%)      |
| Numerar sau card in magazin |           7187 | 3682 (51.2%)   | 3274 (45.6%)   | 137 (1.9%)      | 93 (1.3%)              | 1 (0.0%)      |
| LeanPay                     |           5207 | 369 (7.1%)     | 4812 (92.4%)   | 20 (0.4%)       | 3 (0.1%)               | 1 (0.0%)      |
| Tbi                         |           3579 | 1006 (28.1%)   | 2488 (69.5%)   | 37 (1.0%)       | 3 (0.1%)               | 1 (0.0%)      |
| BTDirect                    |           2080 | 79 (3.8%)      | 1973 (94.9%)   | 4 (0.2%)        | 0 (0.0%)               | 0 (0.0%)      |
| Plata la locker             |           1950 | 1597 (81.9%)   | 96 (4.9%)      | 249 (12.8%)     | 5 (0.3%)               | 3 (0.2%)      |
| OP                          |           1317 | 791 (60.1%)    | 359 (27.3%)    | 37 (2.8%)       | 8 (0.6%)               | 121 (9.2%)    |

## 3. Deep Dive: Problematic Gateways

### Tbi
- **canceled**: 2488 orders (69.5%)
- **complete**: 1006 orders (28.1%)
- **pending_payment**: 44 orders (1.2%)
- **returnata**: 37 orders (1.0%)
- **waiting_navision**: 3 orders (0.1%)
- **pending**: 1 orders (0.0%)
> ⚠️ **High Cancellation Rate:** Over 70% of Tbi orders are canceled. This strongly suggests a UX issue or technical failure during the approval process.

### LeanPay
- **canceled**: 4812 orders (92.4%)
- **complete**: 369 orders (7.1%)
- **returnata**: 20 orders (0.4%)
- **waiting_navision**: 3 orders (0.1%)
- **pending**: 1 orders (0.0%)
- **pending_payment**: 1 orders (0.0%)
- **waiting_tazz**: 1 orders (0.0%)
> ⚠️ **High Cancellation Rate:** Over 92% of LeanPay orders are canceled. This strongly suggests a UX issue or technical failure during the approval process.

### OP
- **complete**: 791 orders (60.1%)
- **canceled**: 359 orders (27.3%)
- **pending**: 121 orders (9.2%)
- **returnata**: 37 orders (2.8%)
- **waiting_navision**: 8 orders (0.6%)
- **redirected**: 1 orders (0.1%)

### Oney
- **canceled**: 6989 orders (78.8%)
- **complete**: 1783 orders (20.1%)
- **returnata**: 87 orders (1.0%)
- **waiting_navision**: 10 orders (0.1%)
- **pending_payment**: 4 orders (0.0%)
> ⚠️ **High Cancellation Rate:** Over 79% of Oney orders are canceled. This strongly suggests a UX issue or technical failure during the approval process.

### BTDirect
- **canceled**: 1973 orders (94.9%)
- **complete**: 79 orders (3.8%)
- **pending_payment**: 24 orders (1.2%)
- **returnata**: 4 orders (0.2%)
> ⚠️ **High Cancellation Rate:** Over 95% of BTDirect orders are canceled. This strongly suggests a UX issue or technical failure during the approval process.

## 4. Key Insights
- **Card vs Cash Reliability:** 'Card' payments have a cancellation rate of **31.4%**, whereas 'Numerar la livrare' (Cash on Delivery) is **6.0%**.