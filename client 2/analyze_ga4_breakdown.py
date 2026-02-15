import pandas as pd
import os

def analyze_ga4_breakdown():
    print("Loading data for GA4 Breakdown Analysis...")
    
    ga4_path = "client 2/ga4_exportv2 - Free form 1.csv"
    backend_path = "client 2/tranzactii-cu-status .xlsx"
    
    # Load & Clean
    df_ga4 = pd.read_csv(ga4_path)
    df_ga4 = df_ga4[df_ga4['Transaction ID'].notna()]
    df_ga4 = df_ga4[df_ga4['Transaction ID'] != '(not set)']
    df_ga4['Transaction ID'] = df_ga4['Transaction ID'].astype(str).str.strip()
    
    df_backend = pd.read_excel(backend_path)
    df_backend['increment_id'] = df_backend['increment_id'].astype(str).str.strip()
    df_backend['metoda_plata'] = df_backend['metoda_plata'].replace('Numerar sau card in magazin', 'Ridicare Magazin').fillna('Unknown')
    
    # Sets
    ga4_ids = set(df_ga4['Transaction ID'])
    
    # --- Analysis 1: Canceled Orders FOUND in GA4 (False Positives) ---
    # Which payment methods falsely report success?
    
    df_canceled = df_backend[df_backend['status'] == 'canceled']
    df_canceled_in_ga4 = df_canceled[df_canceled['increment_id'].isin(ga4_ids)]
    
    print(f"Total Canceled in Backend: {len(df_canceled)}")
    print(f"Canceled WE FOUND in GA4: {len(df_canceled_in_ga4)}")
    
    breakdown_canceled_in_ga4 = df_canceled_in_ga4['metoda_plata'].value_counts()
    
    # --- Analysis 2: Orders NOT found in GA4 (Missing) ---
    # Specifically Valid (Complete) orders vs All Missing
    
    df_missing = df_backend[~df_backend['increment_id'].isin(ga4_ids)]
    
    # A. All missing (Context)
    breakdown_all_missing = df_missing['metoda_plata'].value_counts()
    
    # B. Valid (Complete) missing (Revenue Loss)
    df_missing_valid = df_missing[df_missing['status'] == 'complete']
    breakdown_valid_missing = df_missing_valid['metoda_plata'].value_counts()
    
    
    # --- Report Generation ---
    report = []
    report.append("# 🕵️‍♀️ GA4 Breakdown: False Positives & Missing Data")
    report.append(f"**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    
    report.append("\n## 1. Canceled Orders FOUND in GA4 (False Positives)")
    report.append(f"**Total:** {len(df_canceled_in_ga4)} orders")
    report.append("**Impact:** These are Canceled orders that fired the 'Purchase' pixel. This inflates your revenue.")
    
    report.append("\n| Payment Method | Count (False Positives) | % of Total False Positives |")
    report.append("| :--- | :--- | :--- |")
    for method, count in breakdown_canceled_in_ga4.items():
        pct = count / len(df_canceled_in_ga4) * 100
        report.append(f"| {method} | {count} | {pct:.1f}% |")
        
    report.append("\n> **Insight:** If 'Card' or 'Oney' are high here, it means the user is redirected to the 'Thank You' page even if the payment failed/was canceled.")

    report.append("\n## 2. Orders NOT Found in GA4 (Missing Data)")
    report.append(f"**Total Missing (All Statuses):** {len(df_missing)}")
    
    report.append("\n### A. Missing 'Complete' Orders (Revenue Loss)")
    report.append(f"**Total Missing Valid Orders:** {len(df_missing_valid)}")
    report.append("**Impact:** These are successful sales that GA4/GTM failed to capture.")
    
    report.append("\n| Payment Method | Count (Missing) | % of Total Missing Valid |")
    report.append("| :--- | :--- | :--- |")
    for method, count in breakdown_valid_missing.items():
        pct = count / len(df_missing_valid) * 100
        report.append(f"| {method} | {count} | {pct:.1f}% |")
        
    report.append("\n### B. Missing 'Canceled' Orders (Correct Behavior)")
    # We expect canceled orders to be missing.
    df_missing_canceled = df_missing[df_missing['status'] == 'canceled']
    report.append(f"**Total Missing Canceled Orders:** {len(df_missing_canceled)}")
    report.append("(This is largely expected behavior - we generally don't want these in GA4).")
    
    
    with open("client 2/GA4_BREAKDOWN.md", "w") as f:
        f.write("\n".join(report))
        
    print("Report generated: client 2/GA4_BREAKDOWN.md")

if __name__ == "__main__":
    analyze_ga4_breakdown()
