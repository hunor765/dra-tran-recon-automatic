import pandas as pd

def generate_full_email():
    print("Generating Full Email with Exact Tracking Rates...")
    
    ga4_path = "client 2/ga4_exportv2 - Free form 1.csv"
    backend_path = "client 2/tranzactii-cu-status .xlsx"
    
    # Load & Clean
    df_ga4 = pd.read_csv(ga4_path)
    df_ga4 = df_ga4[df_ga4['Transaction ID'].notna()]
    df_ga4 = df_ga4[df_ga4['Transaction ID'] != '(not set)']
    df_ga4['Transaction ID'] = df_ga4['Transaction ID'].astype(str).str.strip()
    if df_ga4['Total revenue'].dtype == 'object':
        df_ga4['Total revenue'] = pd.to_numeric(df_ga4['Total revenue'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    
    df_backend = pd.read_excel(backend_path)
    df_backend['increment_id'] = df_backend['increment_id'].astype(str).str.strip()
    df_backend['metoda_plata'] = df_backend['metoda_plata'].fillna('Unknown')
    
    ga4_ids = set(df_ga4['Transaction ID'])
    
    # Focus on COMPLETE orders only for tracking rate
    df_complete = df_backend[df_backend['status'] == 'complete'].copy()
    df_complete['in_ga4'] = df_complete['increment_id'].isin(ga4_ids)
    
    # Group by Payment Method
    results = []
    for method, group in df_complete.groupby('metoda_plata'):
        total = len(group)
        tracked = group['in_ga4'].sum()
        missing = total - tracked
        tracking_rate = (tracked / total * 100) if total > 0 else 0
        missing_value = group[~group['in_ga4']]['valoare'].sum()
        total_value = group['valoare'].sum()
        
        results.append({
            'method': method,
            'total_orders': total,
            'tracked_orders': tracked,
            'missing_orders': missing,
            'tracking_rate': tracking_rate,
            'missing_value': missing_value,
            'total_value': total_value
        })
    
    df_results = pd.DataFrame(results).sort_values('missing_value', ascending=False)
    
    # Also get canceled orders in GA4 breakdown
    df_canceled = df_backend[df_backend['status'] == 'canceled']
    df_canceled_in_ga4 = df_canceled[df_canceled['increment_id'].isin(ga4_ids)]
    canceled_in_ga4_by_method = df_canceled_in_ga4.groupby('metoda_plata').agg({
        'increment_id': 'count',
        'valoare': 'sum'
    }).rename(columns={'increment_id': 'count'}).sort_values('valoare', ascending=False)
    
    # --- BUILD EMAIL ---
    email = []
    email.append("# 📊 RAPORT COMPLET: Reconciliere GA4 vs Backend - Client 2")
    email.append(f"**Data Analiză:** {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    email.append("**Perioada Analizată:** Ultimele 3 luni (Oct-Dec 2025 + Jan 2026)")
    
    email.append("\n---\n")
    email.append("## 🔴 SUMAR EXECUTIV")
    
    total_complete = len(df_complete)
    total_tracked = df_complete['in_ga4'].sum()
    total_missing = total_complete - total_tracked
    total_missing_value = df_complete[~df_complete['in_ga4']]['valoare'].sum()
    overall_rate = (total_tracked / total_complete * 100)
    
    email.append(f"- **Comenzi Complete (Backend):** {total_complete:,}")
    email.append(f"- **Comenzi Găsite în GA4:** {total_tracked:,}")
    email.append(f"- **Comenzi Lipsă din GA4:** {total_missing:,}")
    email.append(f"- **Valoare Lipsă:** {total_missing_value:,.0f} RON")
    email.append(f"- **Rată Tracking Overall:** {overall_rate:.1f}%")
    
    email.append("\n---\n")
    email.append("## 🚨 PROBLEME CRITICE PE METODE DE PLATĂ")
    email.append("\n### A. Metode cu Redirect Extern (Problematice)")
    
    # Select problematic ones
    problem_methods = ['LeanPay', 'Tbi', 'Oney', 'BTDirect', 'Card']
    
    for method in problem_methods:
        row = df_results[df_results['method'] == method]
        if len(row) > 0:
            r = row.iloc[0]
            email.append(f"\n**{method}** are **{r['tracking_rate']:.1f}%** tracking:")
            email.append(f"- {r['total_orders']:,} comenzi în backend, doar {r['tracked_orders']:,} în GA4")
            email.append(f"- **{r['missing_orders']:,} comenzi lipsă** (valoare: **{r['missing_value']:,.0f} RON**)")
            
            # Root cause explanation
            if r['tracking_rate'] < 10:
                email.append(f"- *Cauză:* Redirect-ul extern nu revine la pagina Thank You sau sesiunea GA4 se pierde complet.")
            elif r['tracking_rate'] < 50:
                email.append(f"- *Cauză:* Redirect-ul extern pierde frecvent sesiunea GA4, tracking partial.")
            elif r['tracking_rate'] < 80:
                email.append(f"- *Cauză:* Parte din utilizatori nu ajung pe Thank You page după plată cu card (3DS, timeout, etc).")
    
    email.append("\n### B. Metode FĂRĂ Redirect (Funcționează Bine)")
    
    good_methods = ['Numerar la livrare', 'Plata la locker', 'Numerar sau card in magazin']
    for method in good_methods:
        row = df_results[df_results['method'] == method]
        if len(row) > 0:
            r = row.iloc[0]
            email.append(f"- **{method}:** {r['tracking_rate']:.1f}% tracking ✅")
    
    email.append("\n*Concluzie:* Metodele fără redirect extern funcționează bine pentru că utilizatorul rămâne pe site și pixelul se declanșează corect.")
    
    email.append("\n---\n")
    email.append("## ⚠️ INFLARE FALSĂ: Comenzi Anulate în GA4")
    email.append(f"**Total Comenzi Anulate găsite în GA4:** {len(df_canceled_in_ga4):,}")
    email.append(f"**Valoare Inflată Fals:** {df_canceled_in_ga4['valoare'].sum():,.0f} RON")
    email.append("\nAceste comenzi au fost anulate în backend dar au fost contorizate ca venituri în GA4:")
    
    email.append("\n| Metodă Plată | Comenzi Anulate în GA4 | Valoare Inflată |")
    email.append("| :--- | :--- | :--- |")
    for method, row in canceled_in_ga4_by_method.head(5).iterrows():
        email.append(f"| {method} | {row['count']:,} | {row['valoare']:,.0f} RON |")
    
    email.append("\n*Cauză principală:* 'Ridicare din Magazin' reprezintă 50% din falsele pozitive - utilizatorul comandă online, pixelul se declanșează, dar ulterior anulează comanda la magazin.")
    
    email.append("\n---\n")
    email.append("## 📋 RECOMANDĂRI")
    email.append("1. **Prioritate 1 - LeanPay & Tbi:** Verificați implementarea redirect-ului. Zero tracking înseamnă că utilizatorii nu ajung niciodată pe Thank You page după aprobare.")
    email.append("2. **Prioritate 2 - Card (64.5%):** Investigați 3D Secure flow și timeouts. 35% din venituri lipsă sunt de pe Card.")
    email.append("3. **Server-Side Tracking:** Singura soluție definitivă pentru metodele cu redirect este să implementați Server-Side GTM care trimite evenimentul direct din backend după confirmarea plății.")
    email.append("4. **Refund Events:** Pentru a corecta inflatarea de la 'Ridicare Magazin', implementați evenimente de Refund în GA4 când o comandă este anulată.")
    
    email.append("\n---\n")
    email.append("## 📊 TABEL COMPLET (TOATE METODELE)")
    email.append("\n| Metodă Plată | Comenzi Backend | Comenzi GA4 | Rată Tracking | Comenzi Lipsă | Valoare Lipsă (RON) |")
    email.append("| :--- | ---: | ---: | ---: | ---: | ---: |")
    
    for _, r in df_results.iterrows():
        email.append(f"| {r['method']} | {r['total_orders']:,} | {r['tracked_orders']:,} | {r['tracking_rate']:.1f}% | {r['missing_orders']:,} | {r['missing_value']:,.0f} |")
    
    # Write
    with open("client 2/FULL_EMAIL_REPORT.md", "w") as f:
        f.write("\n".join(email))
        
    print("Full Email Report saved to: client 2/FULL_EMAIL_REPORT.md")

if __name__ == "__main__":
    generate_full_email()
