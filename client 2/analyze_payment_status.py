import pandas as pd

def analyze_status_vs_payment():
    print("Loading data for Status vs Payment Analysis...")
    
    backend_path = "client 2/tranzactii-cu-status .xlsx"
    df = pd.read_excel(backend_path)
    
    # Clean up
    df['metoda_plata'] = df['metoda_plata'].fillna('Unknown')
    df['status'] = df['status'].fillna('Unknown')
    
    # 1. Cross-Tabulation (Counts)
    crosstab = pd.crosstab(df['metoda_plata'], df['status'])
    
    # 2. Row Percentages (Status distribution per Payment Method)
    # e.g., For "Tbi", X% are complete, Y% are canceled.
    row_pct = pd.crosstab(df['metoda_plata'], df['status'], normalize='index') * 100
    
    # 3. Focus on the "Problematic" Gateways found earlier
    problem_gateways = ['Tbi', 'LeanPay', 'OP', 'Oney', 'BTDirect']
    
    report = []
    report.append("# 💳 Payment Method vs. Order Status Analysis")
    report.append(f"**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    report.append("\n## 1. Overview (Top Payment Methods)")
    
    # Sort by total volume
    crosstab['Total'] = crosstab.sum(axis=1)
    crosstab = crosstab.sort_values('Total', ascending=False)
    
    top_methods = crosstab.head(10)
    report.append("Total orders by payment method:")
    report.append(top_methods[['Total']].to_markdown())
    
    report.append("\n## 2. Status Distribution Details")
    report.append("How does each payment method perform? (Row Percentages)")
    
    # Generate a clean markdown table for the top 5 statuses
    top_statuses = df['status'].value_counts().head(5).index.tolist()
    
    # Create summary table
    summary_data = []
    for method in crosstab.index:
        row = {'Method': method, 'Total Orders': crosstab.loc[method, 'Total']}
        for status in top_statuses:
            count = crosstab.loc[method, status] if status in crosstab.columns else 0
            pct = row_pct.loc[method, status] if status in row_pct.columns else 0
            row[f"{status} (%)"] = f"{count} ({pct:.1f}%)"
        summary_data.append(row)
        
    df_summary = pd.DataFrame(summary_data)
    report.append(df_summary.to_markdown(index=False))

    report.append("\n## 3. Deep Dive: Problematic Gateways")
    
    for gw in problem_gateways:
        if gw in row_pct.index:
            report.append(f"\n### {gw}")
            # Get the row
            dist = row_pct.loc[gw].sort_values(ascending=False)
            dist = dist[dist > 0] # Only show non-zero
            
            for status, pct in dist.items():
                count = crosstab.loc[gw, status]
                report.append(f"- **{status}**: {count} orders ({pct:.1f}%)")
                
            # Insight logic
            cancel_rate = row_pct.loc[gw, 'canceled'] if 'canceled' in row_pct.columns else 0
            complete_rate = row_pct.loc[gw, 'complete'] if 'complete' in row_pct.columns else 0
            
            if cancel_rate > 50:
                report.append(f"> ⚠️ **High Cancellation Rate:** Over {cancel_rate:.0f}% of {gw} orders are canceled. This strongly suggests a UX issue or technical failure during the approval process.")
            elif complete_rate > 90:
                 report.append(f"> ✅ **High Completion Rate:** {gw} has a healthy completion rate, making the earlier tracking failure (100% missing in GA4) purely a tracking implementation issue, not a business logic one.")

    report.append("\n## 4. Key Insights")
    
    # Insight 1: Card Cancellations vs Cash
    card_cancel = row_pct.loc['Card', 'canceled'] if 'Card' in row_pct.index else 0
    cash_cancel = row_pct.loc['Numerar la livrare', 'canceled'] if 'Numerar la livrare' in row_pct.index else 0
    
    report.append(f"- **Card vs Cash Reliability:** 'Card' payments have a cancellation rate of **{card_cancel:.1f}%**, whereas 'Numerar la livrare' (Cash on Delivery) is **{cash_cancel:.1f}%**.")
    
    # Insight 2: The "Tbi" Anomaly
    # if Tbi was 100% missing in GA4 but has high 'complete' here, it proves the tracking pixel is 100% broken.
    
    with open("client 2/PAYMENT_STATUS_RELATION.md", "w") as f:
        f.write("\n".join(report))
        
    print("Report generated: client 2/PAYMENT_STATUS_RELATION.md")

if __name__ == "__main__":
    analyze_status_vs_payment()
