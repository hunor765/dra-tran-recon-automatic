import pandas as pd
import numpy as np

# Load the datasets
print("=" * 80)
print("TRANSACTION RECONCILIATION ANALYSIS")
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

# Remove the grand total row from GA4 (row with no Date)
ga4 = ga4[ga4['Date'].notna() & (ga4['Date'] != '')]
# Also remove the row containing "Grand total" if it exists
if 'Grand total' in ga4['Total revenue'].values:
    ga4 = ga4[ga4['Total revenue'] != 'Grand total']

# Convert transaction IDs to string for comparison
ecommerce['transaction_id'] = ecommerce['transaction_id'].astype(str)
ga4['Transaction ID'] = ga4['Transaction ID'].astype(str)

# Convert values to numeric
ecommerce['value'] = pd.to_numeric(ecommerce['value'], errors='coerce')
ga4['Total revenue'] = pd.to_numeric(ga4['Total revenue'], errors='coerce')

print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

# Total transactions
ecom_transactions = len(ecommerce)
ga4_transactions = len(ga4)
transaction_diff = ecom_transactions - ga4_transactions
transaction_diff_pct = (transaction_diff / ecom_transactions) * 100 if ecom_transactions > 0 else 0

print(f"\n📈 NUMBER OF TRANSACTIONS:")
print(f"   Ecommerce Backend: {ecom_transactions:,}")
print(f"   GA4:               {ga4_transactions:,}")
print(f"   Difference:        {transaction_diff:,} ({transaction_diff_pct:+.2f}%)")

# Total values
ecom_total_value = ecommerce['value'].sum()
ga4_total_value = ga4['Total revenue'].sum()
value_diff = ecom_total_value - ga4_total_value
value_diff_pct = (value_diff / ecom_total_value) * 100 if ecom_total_value > 0 else 0

print(f"\n💰 TOTAL REVENUE:")
print(f"   Ecommerce Backend: {ecom_total_value:,.2f}")
print(f"   GA4:               {ga4_total_value:,.2f}")
print(f"   Difference:        {value_diff:,.2f} ({value_diff_pct:+.2f}%)")

# Average order value
ecom_aov = ecom_total_value / ecom_transactions if ecom_transactions > 0 else 0
ga4_aov = ga4_total_value / ga4_transactions if ga4_transactions > 0 else 0
aov_diff = ecom_aov - ga4_aov
aov_diff_pct = (aov_diff / ecom_aov) * 100 if ecom_aov > 0 else 0

print(f"\n📊 AVERAGE ORDER VALUE:")
print(f"   Ecommerce Backend: {ecom_aov:,.2f}")
print(f"   GA4:               {ga4_aov:,.2f}")
print(f"   Difference:        {aov_diff:,.2f} ({aov_diff_pct:+.2f}%)")

print("\n" + "=" * 80)
print("TRANSACTION MATCHING ANALYSIS")
print("=" * 80)

# Find matching and non-matching transactions
ecom_ids = set(ecommerce['transaction_id'])
ga4_ids = set(ga4['Transaction ID'])

matching_ids = ecom_ids.intersection(ga4_ids)
ecom_only_ids = ecom_ids - ga4_ids
ga4_only_ids = ga4_ids - ecom_ids

print(f"\n🔗 MATCHING STATUS:")
print(f"   Transactions in BOTH systems:        {len(matching_ids):,}")
print(f"   Transactions ONLY in Ecommerce:      {len(ecom_only_ids):,}")
print(f"   Transactions ONLY in GA4:            {len(ga4_only_ids):,}")

# Analyze ecommerce-only transactions
ecom_only = ecommerce[ecommerce['transaction_id'].isin(ecom_only_ids)]
print(f"\n📦 ECOMMERCE-ONLY TRANSACTIONS BREAKDOWN:")
print(f"   Total value of unmatched ecommerce orders: {ecom_only['value'].sum():,.2f}")

if 'order_status' in ecom_only.columns:
    status_breakdown = ecom_only.groupby('order_status').agg({
        'transaction_id': 'count',
        'value': 'sum'
    }).rename(columns={'transaction_id': 'Count', 'value': 'Total Value'})
    print(f"\n   Breakdown by Order Status:")
    for status, row in status_breakdown.iterrows():
        print(f"      {status}: {row['Count']:,} orders, {row['Total Value']:,.2f} value")

# GA4-only transactions
ga4_only = ga4[ga4['Transaction ID'].isin(ga4_only_ids)]
print(f"\n🌐 GA4-ONLY TRANSACTIONS:")
print(f"   Total value of unmatched GA4 transactions: {ga4_only['Total revenue'].sum():,.2f}")
print(f"   Count: {len(ga4_only):,}")

print("\n" + "=" * 80)
print("VALUE DISCREPANCY ANALYSIS (Matching Transactions)")
print("=" * 80)

# Compare values for matching transactions
matching_ecom = ecommerce[ecommerce['transaction_id'].isin(matching_ids)].copy()
matching_ga4 = ga4[ga4['Transaction ID'].isin(matching_ids)].copy()

# Create a merged dataframe for comparison
merged = matching_ecom.merge(
    matching_ga4[['Transaction ID', 'Total revenue']],
    left_on='transaction_id',
    right_on='Transaction ID',
    how='inner'
)

merged['value_diff'] = merged['value'] - merged['Total revenue']
merged['value_diff_pct'] = (merged['value_diff'] / merged['value']) * 100

# Count exact matches vs discrepancies
exact_matches = len(merged[abs(merged['value_diff']) < 0.01])
with_discrepancy = len(merged[abs(merged['value_diff']) >= 0.01])

print(f"\n🎯 VALUE MATCHING (for matched transactions):")
print(f"   Exact value matches (diff < 0.01): {exact_matches:,}")
print(f"   With value discrepancy:            {with_discrepancy:,}")

if with_discrepancy > 0:
    discrepancies = merged[abs(merged['value_diff']) >= 0.01]
    print(f"\n   Total value discrepancy: {discrepancies['value_diff'].sum():,.2f}")
    print(f"   Average discrepancy:     {discrepancies['value_diff'].mean():,.2f}")
    print(f"   Max positive diff:       {discrepancies['value_diff'].max():,.2f}")
    print(f"   Max negative diff:       {discrepancies['value_diff'].min():,.2f}")

print("\n" + "=" * 80)
print("ECOMMERCE ORDER STATUS ANALYSIS")
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
        print(f"   {status}: {row['Count']:,} orders ({pct:.1f}%), {row['Total Value']:,.2f} value")
    
    # Check if cancelled/cancelled orders might explain differences
    if 'Anulata' in status_analysis.index:
        cancelled = ecommerce[ecommerce['order_status'] == 'Anulata']
        cancelled_in_ga4 = cancelled[cancelled['transaction_id'].isin(ga4_ids)]
        cancelled_not_in_ga4 = cancelled[~cancelled['transaction_id'].isin(ga4_ids)]
        
        print(f"\n❌ CANCELLED ORDERS (Anulata) TRACKING:")
        print(f"   Total cancelled:                {len(cancelled):,}")
        print(f"   Cancelled found in GA4:         {len(cancelled_in_ga4):,}")
        print(f"   Cancelled NOT in GA4:           {len(cancelled_not_in_ga4):,}")
    
    # Delivered orders analysis
    if 'Livrata' in status_analysis.index:
        delivered = ecommerce[ecommerce['order_status'] == 'Livrata']
        delivered_total = delivered['value'].sum()
        print(f"\n✅ DELIVERED ORDERS (Livrata):")
        print(f"   Total delivered orders:         {len(delivered):,}")
        print(f"   Total delivered value:          {delivered_total:,.2f}")

print("\n" + "=" * 80)
print("ROOT CAUSE ANALYSIS")
print("=" * 80)

print("""
📋 COMMON REASONS FOR DISCREPANCIES BETWEEN ECOMMERCE BACKEND AND GA4:

1. 🚫 AD BLOCKERS & TRACKING PREVENTION
   - Users with ad blockers prevent GA4 tracking from firing
   - Safari's ITP (Intelligent Tracking Prevention) blocks cookies
   - Estimated impact: 10-30% of transactions can be missed

2. 📉 CANCELLED ORDERS
   - Orders placed but later cancelled may or may not be tracked in GA4
   - GA4 tracks at checkout completion, backend tracks full lifecycle
   - Your cancelled orders (Anulata) account for a significant portion

3. 🔄 JAVASCRIPT ERRORS / PAGE LOAD ISSUES
   - GA4 tracking fires on JavaScript events
   - If page doesn't fully load or JavaScript errors occur, tracking fails
   - Network issues can prevent tracking beacon from sending

4. 💰 VALUE CALCULATION DIFFERENCES
   - GA4 may use different value calculations (before/after discounts, tax, shipping)
   - Currency conversions or rounding differences
   - Enhanced Ecommerce vs standard tracking configurations

5. 🕐 TIMING / ATTRIBUTION DIFFERENCES
   - GA4 uses session-based attribution
   - Orders completed at midnight might fall on different dates
   - Timezone differences between systems

6. 🔗 TRANSACTION ID DUPLICATES / MODIFICATIONS
   - Same transaction ID fired multiple times in GA4
   - Order modifications that change transaction details

7. 📱 CROSS-DEVICE / CROSS-BROWSER ISSUES
   - Users starting on one device, completing on another
   - GA4 may not properly attribute the transaction

8. 🔒 PAYMENT PROVIDER REDIRECTS
   - Users completing payment on external sites
   - Return-to-site tracking may fail for some payment methods
""")

# Calculate what percentage of the gap is explained by cancelled orders
if 'order_status' in ecommerce.columns:
    delivered_ecom = ecommerce[ecommerce['order_status'] == 'Livrata']
    delivered_value = delivered_ecom['value'].sum()
    delivered_count = len(delivered_ecom)
    
    print("\n" + "=" * 80)
    print("ADJUSTED COMPARISON (Delivered Orders Only)")
    print("=" * 80)
    
    print(f"\n📊 COMPARING DELIVERED ORDERS vs GA4:")
    print(f"   Delivered (Ecommerce): {delivered_count:,} orders, {delivered_value:,.2f} value")
    print(f"   GA4 Total:             {ga4_transactions:,} orders, {ga4_total_value:,.2f} value")
    
    adjusted_tx_diff = delivered_count - ga4_transactions
    adjusted_tx_diff_pct = (adjusted_tx_diff / delivered_count) * 100 if delivered_count > 0 else 0
    adjusted_val_diff = delivered_value - ga4_total_value
    adjusted_val_diff_pct = (adjusted_val_diff / delivered_value) * 100 if delivered_value > 0 else 0
    
    print(f"\n   Transaction difference: {adjusted_tx_diff:,} ({adjusted_tx_diff_pct:+.2f}%)")
    print(f"   Value difference:       {adjusted_val_diff:,.2f} ({adjusted_val_diff_pct:+.2f}%)")

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

print("""
✅ RECOMMENDED ACTIONS:

1. 📊 IMPLEMENT SERVER-SIDE TRACKING
   - Use Measurement Protocol to send transactions server-side
   - This bypasses ad blockers and JavaScript issues
   - Can achieve near 100% tracking accuracy

2. 🔄 SET UP REGULAR RECONCILIATION
   - Monthly comparison of backend vs GA4 data
   - Track the discrepancy rate over time
   - Alert if discrepancy exceeds threshold

3. 💡 IMPROVE ECOMMERCE TRACKING IMPLEMENTATION
   - Ensure purchase event fires reliably on thank-you page
   - Consider firing on payment provider callback
   - Implement backup tracking via Google Tag Manager

4. 📈 USE CONVERSION ADJUSTMENT FACTORS
   - Calculate average discrepancy rate
   - Apply correction factor to GA4 reports
   - Document methodology for stakeholders

5. 🔍 AUDIT HIGH-VALUE DISCREPANCIES
   - Manually review large transactions that don't match
   - Identify patterns in missing transactions
   - Fix specific issues in tracking implementation
""")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
