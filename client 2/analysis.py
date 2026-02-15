import pandas as pd

# Load files
print("Loading files...")
ga4 = pd.read_csv('ga4_exportv2 - Free form 1.csv')
excel = pd.read_excel('datarevolt-tranzactii.xlsx')

# Clean IDs
excel['clean_id'] = excel['increment_id'].astype(str).str.replace('-1', '').str.strip()
ga4['clean_id'] = ga4['Transaction ID'].astype(str).str.strip()
ga4_ids = set(ga4['clean_id'].tolist())

print("=" * 80)
print("PAYMENT METHOD TRACKING ANALYSIS")
print("=" * 80)

results = []
for pm in excel['metoda_plata'].unique():
    pm_df = excel[excel['metoda_plata'] == pm]
    total = len(pm_df)
    in_ga4 = len(pm_df[pm_df['clean_id'].isin(ga4_ids)])
    missing = total - in_ga4
    rate = in_ga4 / total * 100 if total > 0 else 0
    value_total = pm_df['valoare'].sum()
    value_in_ga4 = pm_df[pm_df['clean_id'].isin(ga4_ids)]['valoare'].sum()
    results.append((pm, total, in_ga4, missing, rate, value_total, value_in_ga4))

# Sort by rate ascending (worst first)
results.sort(key=lambda x: x[4])

print(f"\n{'Payment Method':<25} {'Total':>8} {'In GA4':>8} {'Missing':>8} {'Rate':>7} {'Value Lost':>15}")
print("-" * 80)
for pm, total, in_ga4, missing, rate, val_total, val_ga4 in results:
    val_lost = val_total - val_ga4
    print(f"{pm:<25} {total:>8,} {in_ga4:>8,} {missing:>8,} {rate:>6.1f}% {val_lost:>15,.0f}")

print("\n" + "=" * 80)
print("SHIPPING METHOD TRACKING ANALYSIS")
print("=" * 80)

results2 = []
for sm in excel['metoda_livrare'].unique():
    sm_df = excel[excel['metoda_livrare'] == sm]
    total = len(sm_df)
    in_ga4 = len(sm_df[sm_df['clean_id'].isin(ga4_ids)])
    rate = in_ga4 / total * 100 if total > 0 else 0
    results2.append((sm, total, in_ga4, rate))

results2.sort(key=lambda x: x[3])
print(f"\n{'Shipping Method':<25} {'Total':>10} {'In GA4':>10} {'Rate':>8}")
print("-" * 55)
for sm, total, in_ga4, rate in results2:
    print(f"{sm:<25} {total:>10,} {in_ga4:>10,} {rate:>7.1f}%")

print("\n" + "=" * 80)
print("CROSS-ANALYSIS: Payment x Shipping")
print("=" * 80)

# For each payment method, show tracking rate by shipping
for pm in ['Oney', 'LeanPay', 'Tbi', 'BTDirect', 'Card', 'Numerar la livrare']:
    pm_df = excel[excel['metoda_plata'] == pm]
    if len(pm_df) == 0:
        continue
    print(f"\n{pm}:")
    for sm in pm_df['metoda_livrare'].unique():
        sm_df = pm_df[pm_df['metoda_livrare'] == sm]
        total = len(sm_df)
        in_ga4 = len(sm_df[sm_df['clean_id'].isin(ga4_ids)])
        rate = in_ga4 / total * 100 if total > 0 else 0
        if total >= 10:
            print(f"   {sm:<25} {total:>6,} orders, {rate:>5.1f}% in GA4")

print("\nDone!")
