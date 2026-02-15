import pandas as pd
import os

def run_analysis():
    print("Loading data...")
    
    # Paths
    ga4_path = "client 2/ga4_exportv2 - Free form 1.csv"
    backend_path = "client 2/tranzactii-cu-status .xlsx"
    
    # Load GA4
    df_ga4 = pd.read_csv(ga4_path)
    # Basic cleaning
    df_ga4 = df_ga4[df_ga4['Transaction ID'].notna()]
    df_ga4['Transaction ID'] = df_ga4['Transaction ID'].astype(str).str.strip()
    # Handle '(not set)' if present
    df_ga4 = df_ga4[df_ga4['Transaction ID'] != '(not set)']
    
    # Clean Revenue (remove commas if any)
    if df_ga4['Total revenue'].dtype == 'object':
        df_ga4['Total revenue'] = pd.to_numeric(df_ga4['Total revenue'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

    # Load Backend
    df_backend = pd.read_excel(backend_path)
    df_backend['increment_id'] = df_backend['increment_id'].astype(str).str.strip()
    
    # --- Reconciliation Logic ---
    
    ga4_ids = set(df_ga4['Transaction ID'])
    backend_ids = set(df_backend['increment_id'])
    
    common_ids = ga4_ids.intersection(backend_ids)
    missing_in_ga4 = backend_ids - ga4_ids
    missing_in_backend = ga4_ids - backend_ids
    
    print(f"Total GA4 Transactions: {len(ga4_ids)}")
    print(f"Total Backend Transactions: {len(backend_ids)}")
    print(f"Matched: {len(common_ids)}")
    print(f"Missing in GA4: {len(missing_in_ga4)}")
    print(f"Missing in Backend: {len(missing_in_backend)}")
    
    # --- Analysis of Missing in GA4 ---
    
    report = []
    report.append("# Client 2 Reconciliation Analysis")
    report.append("\n## Executive Summary")
    report.append(f"- **GA4 Transactions**: {len(ga4_ids)}")
    report.append(f"- **Backend Transactions**: {len(backend_ids)}")
    report.append(f"- **Matched**: {len(common_ids)}")
    report.append(f"- **Match Rate (vs Backend)**: {len(common_ids)/len(backend_ids)*100:.2f}%")
    
    report.append("\n## 1. Missing in GA4 Analysis")
    report.append(f"Transactions found in Backend but NOT in GA4: **{len(missing_in_ga4)}**")
    
    if len(missing_in_ga4) > 0:
        missing_orders = df_backend[df_backend['increment_id'].isin(missing_in_ga4)]
        
        # Breakdown by Status
        status_counts = missing_orders['status'].value_counts()
        report.append("\n### Breakdown by Status of Missing Orders")
        report.append("| Status | Count | Percentage |")
        report.append("|--------|-------|------------|")
        for status, count in status_counts.items():
            pct = count / len(missing_orders) * 100
            report.append(f"| {status} | {count} | {pct:.1f}% |")
            
        # Value of missing orders
        total_missing_val = missing_orders['valoare'].sum()
        report.append(f"\n**Total Value of Missing Orders**: {total_missing_val:,.2f}")

    # --- Analysis of Discrepancies (Value) ---
    
    report.append("\n## 2. Value Discrepancies (Matched Orders)")
    
    matched_backend = df_backend[df_backend['increment_id'].isin(common_ids)].set_index('increment_id')
    matched_ga4 = df_ga4[df_ga4['Transaction ID'].isin(common_ids)].set_index('Transaction ID')
    
    # Join on index
    combined = matched_backend.join(matched_ga4, lsuffix='_backend', rsuffix='_ga4')
    
    # Calculate diff
    combined['diff'] = combined['valoare'] - combined['Total revenue']
    combined['diff_abs'] = combined['diff'].abs()
    
    # Threshold for "significant" discrepancy (e.g., > 1.0)
    significant_diffs = combined[combined['diff_abs'] > 1.0]
    
    report.append(f"Orders with value discrepancy (> 1.0 unit): **{len(significant_diffs)}**")
    
    if len(significant_diffs) > 0:
        report.append("\nTop 10 Discrepancies:")
        report.append("| ID | Backend Value | GA4 Value | Diff |")
        report.append("|----|---------------|-----------|------|")
        
        top_diffs = significant_diffs.sort_values('diff_abs', ascending=False).head(10)
        for id, row in top_diffs.iterrows():
            report.append(f"| {id} | {row['valoare']:.2f} | {row['Total revenue']:.2f} | {row['diff']:.2f} |")

    # Save Report
    output_path = "client 2/analysis_report_v2.md"
    with open(output_path, "w") as f:
        f.write("\n".join(report))
        
    print(f"Analysis complete. Report saved to {output_path}")

if __name__ == "__main__":
    run_analysis()
