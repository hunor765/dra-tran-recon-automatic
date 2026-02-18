import pandas as pd
import numpy as np

# Load the datasets
print("=" * 80)
print("TRANSACTION RECONCILIATION ANALYSIS v2")
print("Ecommerce Backend vs GA4 Data")
print("=" * 80)

# Load ecommerce backend data
ecommerce = pd.read_csv("comenzi ultimele 3 luni.csv")
print(f"\n📊 Ecommerce Backend Dataset:")
print(f"   Columns: {list(ecommerce.columns)}")
print(f"   Total rows: {len(ecommerce):,}")

# Load GA4 data
ga4 = pd.read_csv("Free form 1 - Free form 1.csv")
print(f"\n📊 GA4 Dataset:")
print(f"   Columns: {list(ga4.columns)}")
print(f"   Total rows: {len(ga4):,}")

# Clean column names (remove trailing spaces)
ecommerce.columns = ecommerce.columns.str.strip()
ga4.columns = ga4.columns.str.strip()

# Debug: Check what the Transaction ID looks like
print("\n🔍 DEBUG - Transaction ID samples:")
print(f"   Ecommerce first 5: {ecommerce['transaction_id'].head().tolist()}")
print(f"   Ecommerce dtypes: {ecommerce['transaction_id'].dtype}")
print(f"   GA4 first 5: {ga4['Transaction ID'].head().tolist()}")
print(f"   GA4 dtypes: {ga4['Transaction ID'].dtype}")

# Check for the specific ID mentioned by user
test_id = 4161425
print(f"\n🔍 Looking for transaction {test_id}:")
print(f"   In ecommerce (as int): {(ecommerce['transaction_id'] == test_id).sum()}")
print(f"   In GA4 (as int): {(ga4['Transaction ID'] == test_id).sum()}")

# Remove the grand total row from GA4 (row 2 which has "Grand total")
# The issue is the second row has empty Date and "Grand total" text
ga4_clean = ga4.dropna(subset=['Date'])
ga4_clean = ga4_clean[ga4_clean['Date'] != '']

# Also handle if Transaction ID might have become float due to NaN
# Convert both to integer strings for proper matching
ecommerce['transaction_id_str'] = ecommerce['transaction_id'].astype(str)
ga4_clean['Transaction ID'] = pd.to_numeric(ga4_clean['Transaction ID'], errors='coerce')
ga4_clean = ga4_clean.dropna(subset=['Transaction ID'])
ga4_clean['transaction_id_str'] = ga4_clean['Transaction ID'].astype(int).astype(str)

print(f"\n📊 After cleaning GA4:")
print(f"   GA4 rows: {len(ga4_clean):,}")

# Convert values to numeric
ecommerce['value'] = pd.to_numeric(ecommerce['value'], errors='coerce')
ga4_clean['Total revenue'] = pd.to_numeric(ga4_clean['Total revenue'], errors='coerce')

print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

# Total transactions
ecom_transactions = len(ecommerce)
ga4_transactions = len(ga4_clean)
transaction_diff = ecom_transactions - ga4_transactions
transaction_diff_pct = (transaction_diff / ecom_transactions) * 100 if ecom_transactions > 0 else 0

print(f"\n📈 NUMBER OF TRANSACTIONS:")
print(f"   Ecommerce Backend: {ecom_transactions:,}")
print(f"   GA4:               {ga4_transactions:,}")
print(f"   Difference:        {transaction_diff:,} ({transaction_diff_pct:+.2f}%)")

# Total values
ecom_total_value = ecommerce['value'].sum()
ga4_total_value = ga4_clean['Total revenue'].sum()
value_diff = ecom_total_value - ga4_total_value
value_diff_pct = (value_diff / ecom_total_value) * 100 if ecom_total_value > 0 else 0

print(f"\n💰 TOTAL REVENUE:")
print(f"   Ecommerce Backend: {ecom_total_value:,.2f}")
print(f"   GA4:               {ga4_total_value:,.2f}")
print(f"   Difference:        {value_diff:,.2f} ({value_diff_pct:+.2f}%)")

# Average order value
ecom_aov = ecom_total_value / ecom_transactions if ecom_transactions > 0 else 0
ga4_aov = ga4_total_value / ga4_transactions if ga4_transactions > 0 else 0

print(f"\n📊 AVERAGE ORDER VALUE:")
print(f"   Ecommerce Backend: {ecom_aov:,.2f}")
print(f"   GA4:               {ga4_aov:,.2f}")

print("\n" + "=" * 80)
print("TRANSACTION MATCHING ANALYSIS")
print("=" * 80)

# Find matching and non-matching transactions using string IDs
ecom_ids = set(ecommerce['transaction_id_str'])
ga4_ids = set(ga4_clean['transaction_id_str'])

matching_ids = ecom_ids.intersection(ga4_ids)
ecom_only_ids = ecom_ids - ga4_ids
ga4_only_ids = ga4_ids - ecom_ids

print(f"\n🔗 MATCHING STATUS:")
print(f"   Transactions in BOTH systems:        {len(matching_ids):,}")
print(f"   Transactions ONLY in Ecommerce:      {len(ecom_only_ids):,}")
print(f"   Transactions ONLY in GA4:            {len(ga4_only_ids):,}")

# Calculate match rate
match_rate_ecom = (len(matching_ids) / len(ecom_ids)) * 100 if len(ecom_ids) > 0 else 0
match_rate_ga4 = (len(matching_ids) / len(ga4_ids)) * 100 if len(ga4_ids) > 0 else 0

print(f"\n📊 MATCH RATES:")
print(f"   % of Ecommerce orders found in GA4:  {match_rate_ecom:.2f}%")
print(f"   % of GA4 orders found in Ecommerce:  {match_rate_ga4:.2f}%")

# Analyze ecommerce-only transactions
ecom_only = ecommerce[ecommerce['transaction_id_str'].isin(ecom_only_ids)]
print(f"\n📦 ECOMMERCE-ONLY TRANSACTIONS:")
print(f"   Count: {len(ecom_only):,}")
print(f"   Total value: {ecom_only['value'].sum():,.2f}")

if 'order_status' in ecom_only.columns:
    status_breakdown = ecom_only.groupby('order_status').agg({
        'transaction_id': 'count',
        'value': 'sum'
    }).rename(columns={'transaction_id': 'Count', 'value': 'Total Value'})
    print(f"\n   Breakdown by Order Status:")
    for status, row in status_breakdown.iterrows():
        print(f"      {status}: {int(row['Count']):,} orders, {row['Total Value']:,.2f} value")

# GA4-only transactions
ga4_only = ga4_clean[ga4_clean['transaction_id_str'].isin(ga4_only_ids)]
print(f"\n🌐 GA4-ONLY TRANSACTIONS:")
print(f"   Count: {len(ga4_only):,}")
print(f"   Total value: {ga4_only['Total revenue'].sum():,.2f}")

print("\n" + "=" * 80)
print("VALUE COMPARISON FOR MATCHING TRANSACTIONS")
print("=" * 80)

# Create merged dataframe for matching transactions
matching_ecom = ecommerce[ecommerce['transaction_id_str'].isin(matching_ids)].copy()
matching_ga4 = ga4_clean[ga4_clean['transaction_id_str'].isin(matching_ids)].copy()

# Aggregate GA4 by transaction (in case of duplicates)
ga4_agg = matching_ga4.groupby('transaction_id_str').agg({
    'Total revenue': 'sum'
}).reset_index()

# Merge
merged = matching_ecom.merge(
    ga4_agg,
    on='transaction_id_str',
    how='inner'
)

merged['value_diff'] = merged['value'] - merged['Total revenue']
merged['value_diff_pct'] = (merged['value_diff'] / merged['value']) * 100

# Stats on value matches
exact_matches = len(merged[abs(merged['value_diff']) < 0.01])
close_matches = len(merged[(abs(merged['value_diff']) >= 0.01) & (abs(merged['value_diff']) < 1)])
with_discrepancy = len(merged[abs(merged['value_diff']) >= 1])

print(f"\n🎯 VALUE MATCHING (for {len(merged):,} matched transactions):")
print(f"   Exact matches (diff < 0.01):    {exact_matches:,} ({exact_matches/len(merged)*100:.1f}%)")
print(f"   Close matches (0.01-1):         {close_matches:,} ({close_matches/len(merged)*100:.1f}%)")
print(f"   With discrepancy (diff >= 1):   {with_discrepancy:,} ({with_discrepancy/len(merged)*100:.1f}%)")

if len(merged) > 0:
    total_ecom_matched = merged['value'].sum()
    total_ga4_matched = merged['Total revenue'].sum()
    total_value_diff = total_ecom_matched - total_ga4_matched
    
    print(f"\n💰 VALUE TOTALS FOR MATCHING TRANSACTIONS:")
    print(f"   Ecommerce value:  {total_ecom_matched:,.2f}")
    print(f"   GA4 value:        {total_ga4_matched:,.2f}")
    print(f"   Difference:       {total_value_diff:,.2f} ({total_value_diff/total_ecom_matched*100:+.2f}%)")

# Show biggest discrepancies
if with_discrepancy > 0:
    discrepancies = merged[abs(merged['value_diff']) >= 1].sort_values('value_diff', key=abs, ascending=False)
    print(f"\n⚠️  TOP 10 VALUE DISCREPANCIES:")
    print(f"   {'Transaction ID':<15} {'Ecommerce':>15} {'GA4':>15} {'Difference':>15}")
    print(f"   {'-'*60}")
    for _, row in discrepancies.head(10).iterrows():
        print(f"   {row['transaction_id_str']:<15} {row['value']:>15,.2f} {row['Total revenue']:>15,.2f} {row['value_diff']:>+15,.2f}")

print("\n" + "=" * 80)
print("ORDER STATUS ANALYSIS (Ecommerce)")
print("=" * 80)

if 'order_status' in ecommerce.columns:
    # Analysis by order status
    status_analysis = ecommerce.groupby('order_status').agg({
        'transaction_id': 'count',
        'value': 'sum'
    }).rename(columns={'transaction_id': 'Count', 'value': 'Total Value'})
    
    print(f"\n📋 ALL ORDERS BY STATUS:")
    for status, row in status_analysis.iterrows():
        pct = (row['Count'] / ecom_transactions) * 100
        print(f"   {status}: {int(row['Count']):,} orders ({pct:.1f}%), {row['Total Value']:,.2f} value")
    
    # For each status, check how many are in GA4
    print(f"\n📊 GA4 MATCH RATE BY ORDER STATUS:")
    for status in ecommerce['order_status'].unique():
        status_orders = ecommerce[ecommerce['order_status'] == status]
        status_in_ga4 = status_orders[status_orders['transaction_id_str'].isin(ga4_ids)]
        match_rate = (len(status_in_ga4) / len(status_orders)) * 100 if len(status_orders) > 0 else 0
        print(f"   {status}: {len(status_in_ga4):,}/{len(status_orders):,} matched ({match_rate:.1f}%)")

print("\n" + "=" * 80)
print("FINAL RECONCILIATION SUMMARY")
print("=" * 80)

# Calculate key metrics
delivered = ecommerce[ecommerce['order_status'] == 'Livrata'] if 'order_status' in ecommerce.columns else ecommerce
delivered_in_ga4 = delivered[delivered['transaction_id_str'].isin(ga4_ids)]

print(f"\n📊 DELIVERED ORDERS RECONCILIATION:")
print(f"   Total delivered orders:         {len(delivered):,}")
print(f"   Delivered orders in GA4:        {len(delivered_in_ga4):,}")
print(f"   Delivered orders NOT in GA4:    {len(delivered) - len(delivered_in_ga4):,}")
print(f"   GA4 capture rate for delivered: {len(delivered_in_ga4)/len(delivered)*100:.1f}%")

missing_delivered = delivered[~delivered['transaction_id_str'].isin(ga4_ids)]
print(f"\n💰 VALUE OF MISSING DELIVERED ORDERS:")
print(f"   Missing from GA4: {missing_delivered['value'].sum():,.2f}")

print("\n" + "=" * 80)
print("ROOT CAUSE ANALYSIS")
print("=" * 80)

print("""
📋 KEY FINDINGS:

1. 🔗 TRANSACTION MATCHING
   - IDs match between systems when compared correctly
   - Not all ecommerce transactions appear in GA4 (tracking gaps)
   - Not all GA4 transactions appear in ecommerce (possible duplicates/test transactions)

2. 📉 CANCELLED ORDERS
   - Large portion of ecommerce orders are cancelled (Anulata)
   - These may or may not appear in GA4 depending on when tracking fires
   - If tracking fires before order is paid/confirmed, cancelled orders appear in GA4

3. 💰 VALUE DIFFERENCES
   - Values may differ due to:
     • Tax/shipping calculation differences
     • Discount application timing
     • Currency rounding
     • Refunds/partial cancellations

4. 🚫 GA4 TRACKING GAPS
   - Ad blockers prevent ~15-30% of tracking
   - JavaScript errors can block tracking
   - Payment redirect flows may lose tracking
""")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
