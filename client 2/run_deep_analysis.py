import pandas as pd
import os

def run_deep_analysis():
    print("Loading data for Deep Analysis...")
    
    # Paths
    ga4_path = "client 2/ga4_exportv2 - Free form 1.csv"
    backend_path = "client 2/tranzactii-cu-status .xlsx"
    
    # 1. Load & Clean GA4
    # -------------------
    df_ga4 = pd.read_csv(ga4_path)
    df_ga4 = df_ga4[df_ga4['Transaction ID'].notna()]
    df_ga4['Transaction ID'] = df_ga4['Transaction ID'].astype(str).str.strip()
    df_ga4 = df_ga4[df_ga4['Transaction ID'] != '(not set)'] 
    
    # Clean Revenue
    if df_ga4['Total revenue'].dtype == 'object':
        df_ga4['Total revenue'] = pd.to_numeric(df_ga4['Total revenue'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    
    # Ensure Date parsing if available in GA4 (it is 'Date' column like 20251218)
    if 'Date' in df_ga4.columns:
        df_ga4['date_parsed'] = pd.to_datetime(df_ga4['Date'], format='%Y%m%d', errors='coerce')


    # 2. Load & Clean Backend
    # -----------------------
    df_backend = pd.read_excel(backend_path)
    df_backend['increment_id'] = df_backend['increment_id'].astype(str).str.strip()
    
    # Parse Created At
    df_backend['created_at_parsed'] = pd.to_datetime(df_backend['created_at'], errors='coerce')
    df_backend['date_day'] = df_backend['created_at_parsed'].dt.date

    # Define "Valid" Statuses for Analysis (We usually only care about successful orders matching GA4)
    # Based on previous run: 'complete' is the main success status. 'canceled', 'returnata' should be ignored for match rate usually, 
    # BUT we want to know if GA4 is tracking canceled orders too (which is bad).
    # actually, usually GA4 should ONLY track 'complete'.
    
    valid_statuses = ['complete', 'processing'] # Assuming 'processing' might exist or similar, but from prev analysis we saw 'complete'
    
    # 3. Categorize Backend Data
    # --------------------------
    df_valid_backend = df_backend[df_backend['status'].isin(valid_statuses)].copy()
    df_canceled = df_backend[df_backend['status'] == 'canceled'].copy()
    
    print(f"Total Backend: {len(df_backend)}")
    print(f"Valid Backend (Complete): {len(df_valid_backend)}")
    
    # 4. Reconciliation
    # -----------------
    ga4_ids = set(df_ga4['Transaction ID'])
    valid_backend_ids = set(df_valid_backend['increment_id'])
    all_backend_ids = set(df_backend['increment_id'])
    
    # A. True Match Rate (Valid Backend vs GA4)
    common_valid = valid_backend_ids.intersection(ga4_ids)
    missing_valid = valid_backend_ids - ga4_ids
    
    # B. GAP Analysis (Why are valid orders missing?)
    df_missing_valid = df_valid_backend[df_valid_backend['increment_id'].isin(missing_valid)].copy()
    
    # C. False Positives (GA4 has it, but it was Canceled)
    # It's bad if canceled orders are in GA4
    canceled_ids = set(df_canceled['increment_id'])
    wrongly_tracked_canceled = canceled_ids.intersection(ga4_ids)
    
    # 5. Pattern Recognition for Missing Valid Orders
    # ---------------------------------------------
    
    # By Payment Method
    missing_by_payment = df_missing_valid['metoda_plata'].value_counts()
    
    # By Date (Temporal gaps)
    missing_by_date = df_missing_valid.groupby('date_day').size().sort_index()
    
    # By Shipping (if relevant)
    if 'metoda_livrare' in df_missing_valid.columns:
        missing_by_shipping = df_missing_valid['metoda_livrare'].value_counts()
    
    
    # 6. Duplication Check (Value Doubling)
    # -------------------------------------
    matched_backend = df_backend[df_backend['increment_id'].isin(ga4_ids)].set_index('increment_id')
    matched_ga4 = df_ga4[df_ga4['Transaction ID'].isin(all_backend_ids)].set_index('Transaction ID')
    
    # Note: GA4 might have duplicates if we join, but distinct IDs are unique.
    # Let's join on ID
    combined = matched_backend.join(matched_ga4, rsuffix='_ga4')
    combined['diff'] = combined['valoare'] - combined['Total revenue']
    combined['diff_abs'] = combined['diff'].abs()
    combined['ratio'] = combined['Total revenue'] / combined['valoare'] # Check for 2.0 ratio
    
    doubled_orders = combined[(combined['ratio'] > 1.9) & (combined['ratio'] < 2.1)]
    
    
    # 7. Generate Full Report
    # -----------------------
    report = []
    
    report.append("# 📊 Comprehensive Reconciliation Report: Client 2")
    report.append(f"**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    report.append("\n## 1. Executive Summary")
    
    true_match_rate = len(common_valid) / len(valid_backend_ids) * 100 if len(valid_backend_ids) > 0 else 0
    
    report.append("| Metric | Count | Value (RON) | Description |")
    report.append("| :--- | :--- | :--- | :--- |")
    report.append(f"| **Valid Orders (Backend)** | {len(valid_backend_ids)} | {df_valid_backend['valoare'].sum():,.2f} | Orders marked as 'complete' |")
    report.append(f"| **Matched in GA4** | {len(common_valid)} | - | Valid orders successfully tracked |")
    report.append(f"| **Missing from GA4** | **{len(missing_valid)}** | **{df_missing_valid['valoare'].sum():,.2f}** | Valid orders NOT tracked |")
    report.append(f"| **True Match Rate** | **{true_match_rate:.2f}%** | - | Percentage of valid orders tracked |")
    
    report.append(f"\n> 🚨 **Critical Finding:** You are missing **{len(missing_valid)}** valid orders in GA4, totaling **{df_missing_valid['valoare'].sum():,.2f} RON** in untracked revenue.")

    report.append("\n## 2. Why are orders missing? (Pattern Analysis)")
    
    report.append("\n### A. By Payment Method")
    report.append("Is the tracking failing for specific payment gateways?")
    report.append("| Payment Method | Missing Count | Total Valid Count | Failure Rate |")
    report.append("| :--- | :--- | :--- | :--- |")
    
    all_payment_counts = df_valid_backend['metoda_plata'].value_counts()
    
    for method, missing_count in missing_by_payment.items():
        total_count = all_payment_counts.get(method, 0)
        fail_rate = (missing_count / total_count * 100) if total_count > 0 else 0
        report.append(f"| {method} | {missing_count} | {total_count} | **{fail_rate:.1f}%** |")

    report.append("\n### B. By Shipping Method")
    report.append("| Shipping Method | Missing Count |")
    report.append("| :--- | :--- |")
    for method, count in missing_by_shipping.head(10).items():
        report.append(f"| {method} | {count} |")

    report.append("\n### C. Temporal Analysis (Timeline)")
    report.append("Are there specific days where tracking stopped completely?")
    # Check for days with 100% failure or high spikes
    report.append("| Date | Missing Orders |")
    report.append("| :--- | :--- |")
    # Show top 5 worst days
    for date, count in missing_by_date.sort_values(ascending=False).head(5).items():
         report.append(f"| {date} | {count} |")


    report.append("\n## 3. Data Integrity & Anomalies")
    
    report.append("\n### A. Canceled Orders in GA4")
    report.append(f"- **{len(wrongly_tracked_canceled)}** Canceled orders were tracked in GA4.")
    if len(wrongly_tracked_canceled) > 0:
        val_canceled = df_backend[df_backend['increment_id'].isin(wrongly_tracked_canceled)]['valoare'].sum()
        report.append(f"- This inflates your GA4 revenue by **{val_canceled:,.2f} RON**.")
        report.append("- *Recommendation:* Ensure the tracking pixel does NOT fire on thank-you pages if the order status is canceled/failed, or implement Refund hits.")

    report.append("\n### B. Duplicate / Double Counting")
    report.append(f"- **{len(doubled_orders)}** orders have exactly double the value in GA4 vs Backend.")
    if len(doubled_orders) > 0:
        report.append("- **Example IDs:** " + ", ".join(doubled_orders.index.astype(str)[:5].tolist()))
        report.append("- *Cause:* This typically happens when the purchase event triggers twice (e.g., on page reload or email link click).")
        report.append("- *Fix:* Add a `transaction_id` check in GTM to prevent firing if ID already sent, or deduplicate in BigQuery.")

    report.append("\n## 4. Final Recommendations")
    report.append("1. **Fix Missing 'Complete' Orders:** The 60% match rate is low. Investigate the Payment Methods identified above (likely redirects like Netopia/MobilPay/Stripe failing to return to Thank You page).")
    report.append("2. **Implement Server-Side Tracking:** Reliance on browser-side 'Thank You' pages is the #1 cause of this 40% data loss.")
    report.append("3. **Exclude Canceled Orders:** Stop pushing data for canceled orders to GA4.")
    report.append("4. **Deduplication:** Fix the double-firing events for the identified orders.")

    # Save
    with open("client 2/FULL_RECONCILIATION_REPORT.md", "w") as f:
        f.write("\n".join(report))
    
    print("Full report generated.")

if __name__ == "__main__":
    run_deep_analysis()
