# Backend Integration Reference

## Exact Field Mappings

### WooCommerce → DRA Backend

**API Endpoint Used:**
```
GET https://your-store.com/wp-json/wc/v3/orders
```

**Fields Extracted:**

| WooCommerce Field | DRA Field | Example |
|-------------------|-----------|---------|
| `order.id` | `clean_id` | "12345" |
| `order.total` | `value` | 149.99 |
| `order.status` | `status` | "completed" |
| `order.payment_method` | `payment_method` | "stripe" |

**Sample WooCommerce Response:**
```json
{
  "id": 12345,
  "status": "completed",
  "total": "149.99",
  "payment_method": "stripe",
  "date_created": "2026-01-15T10:30:00"
}
```

**Required WooCommerce API Permissions:**
- `read` access to orders

---

### GA4 → DRA Backend

**API Used:** Google Analytics Data API v1beta

**Fields Extracted:**

| GA4 Dimension/Metric | DRA Field | Example |
|---------------------|-----------|---------|
| `transactionId` | `clean_id` | "12345" |
| `purchaseRevenue` | `value` | 149.99 |
| `date` | `date` | "2026-01-15" |
| `browser` | `browser` | "Chrome" |
| `deviceCategory` | `device` | "desktop" |

**GA4 Query Configuration:**
```python
request = RunReportRequest(
    property=f"properties/{property_id}",
    dimensions=[
        Dimension(name="transactionId"),
        Dimension(name="date"),
        Dimension(name="browser"),
        Dimension(name="deviceCategory"),
    ],
    metrics=[
        Metric(name="purchaseRevenue"),
    ],
    date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
)
```

**Required GA4 Setup:**
1. Ecommerce tracking enabled in GA4
2. `purchase` events firing correctly
3. `transaction_id` parameter set on purchase events

---

## Reconciliation Algorithm

### Step 1: Data Normalization

```python
# WooCommerce DataFrame
df_backend = pd.DataFrame([
    {"clean_id": "12345", "value": 149.99, "status": "completed"},
    {"clean_id": "12346", "value": 89.50, "status": "completed"},
])

# GA4 DataFrame
df_ga4 = pd.DataFrame([
    {"clean_id": "12345", "value": 149.99, "browser": "Chrome"},
    {"clean_id": "12347", "value": 200.00, "browser": "Safari"},
])
```

### Step 2: Set Matching

```python
backend_ids = set(df_backend['clean_id'])  # {"12345", "12346"}
ga4_ids = set(df_ga4['clean_id'])          # {"12345", "12347"}

# Intersection (matched)
matched = backend_ids & ga4_ids            # {"12345"}

# Backend only (missing from GA4 - TRACKING GAPS!)
missing_from_ga4 = backend_ids - ga4_ids   # {"12346"}

# GA4 only (phantoms/duplicates)
phantoms = ga4_ids - backend_ids           # {"12347"}
```

### Step 3: Metrics Calculation

```python
match_rate = len(matched) / len(backend_ids) * 100  # 50%

missing_value = df_backend[
    df_backend['clean_id'].isin(missing_from_ga4)
]['value'].sum()  # 89.50
```

---

## Where Data Flows

### 1. Connector Config Storage

**Database Table:** `connectors`

```sql
CREATE TABLE connectors (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    type VARCHAR(50),  -- 'ga4', 'woocommerce', 'shopify'
    config_json TEXT,  -- ENCRYPTED credentials
    is_active BOOLEAN
);
```

**Example Config (encrypted):**
```json
// WooCommerce
{
  "url": "https://store.com",
  "consumer_key": "ck_...",
  "consumer_secret": "cs_..."
}

// GA4
{
  "property_id": "123456789",
  "credentials_json": "{...service account...}"
}
```

### 2. Job Execution Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Admin/User  │────►│   POST /api  │────►│   Backend    │
│  Clicks Run  │     │  /jobs/run/1 │     │   Creates    │
└──────────────┘     └──────────────┘     │   Job Record │
                                          └──────┬───────┘
                                                 │
                    ┌────────────────────────────┘
                    ▼
            ┌──────────────┐
            │  Fetch Data  │
            │  - GA4       │
            │  - WooCommerce│
            └──────┬───────┘
                   │
                   ▼
            ┌──────────────┐
            │  Reconcile   │
            │  - Match IDs │
            │  - Compare   │
            └──────┬───────┘
                   │
                   ▼
            ┌──────────────┐
            │ Store Results│◄────── JSON in job.result_summary
            └──────────────┘
```

### 3. Results Storage

**Database Table:** `jobs`

```sql
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    client_id INTEGER,
    status VARCHAR(50),  -- 'pending', 'running', 'completed', 'failed'
    result_summary JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

**Example Result Summary:**
```json
{
  "match_rate": 86.4,
  "total_backend_value": 10000.00,
  "total_ga4_value": 9500.00,
  "missing_count": 50,
  "missing_ids": ["12346", "12347", "12348"],
  "missing_value": 500.00
}
```

---

## Code Locations for Customization

### To Modify Data Fetching:

**File:** `backend/core/ingestors/woocommerce.py`
```python
# Line 55-61: Extract additional fields
for order in page_orders:
    orders.append({
        "clean_id": str(order.get("id")),
        "value": float(order.get("total", 0)),
        "status": order.get("status"),
        "payment_method": order.get("payment_method"),
        # ADD CUSTOM FIELDS HERE:
        "customer_id": order.get("customer_id"),
        "currency": order.get("currency"),
    })
```

**File:** `backend/core/ingestors/google_analytics.py`
```python
# Line 45-53: Add more dimensions
request = RunReportRequest(
    property=f"properties/{self.property_id}",
    dimensions=[
        Dimension(name="transactionId"),
        Dimension(name="date"),
        # ADD CUSTOM DIMENSIONS:
        Dimension(name="sessionSource"),  # Traffic source
        Dimension(name="sessionMedium"),  # Medium
    ],
    ...
)
```

### To Modify Reconciliation Logic:

**File:** `backend/api/v1/endpoints/jobs.py`
```python
# Line 52-58: Current matching logic
common = set(df_ga4['clean_id']) & set(df_backend['clean_id'])
missing_ids = set(df_backend['clean_id']) - set(df_ga4['clean_id'])

# ADD CUSTOM LOGIC HERE:
# - Value comparison
# - Status filtering
# - Date range checks
```

---

## Testing API Connections

### Test WooCommerce (cURL)
```bash
curl -u "ck_xxxxx:cs_xxxxx" \
  "https://your-store.com/wp-json/wc/v3/orders?per_page=1"
```

### Test GA4 (Python)
```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient

client = BetaAnalyticsDataClient.from_service_account_file("key.json")
# If this works without error, credentials are valid
```

---

## Common Issues & Solutions

### Issue: Transaction IDs Don't Match

**Cause:** WooCommerce and GA4 use different ID formats
- WooCommerce: `12345`
- GA4: `#12345` or `Order-12345`

**Solution:** Normalize IDs in ingestors:
```python
# In woocommerce.py
clean_id = str(order.get("id"))

# In google_analytics.py  
clean_id = row.dimension_values[0].value.replace("#", "").replace("Order-", "")
```

### Issue: Timezone Mismatch

**Cause:** Orders at midnight appear on different days

**Solution:** Convert to store timezone:
```python
# Add timezone handling in ingestors
from datetime import timezone
df['date'] = df['date'].dt.tz_convert('Europe/Bucharest')
```

### Issue: Refunded Orders

**Cause:** Refunds change order totals

**Solution:** Handle refund status:
```python
if order.get("status") == "refunded":
    value = float(order.get("refunded_total", 0))
else:
    value = float(order.get("total", 0))
```

---

## Environment Variables

**Backend** (`.env`):
```
DATABASE_URL=postgresql://...
ENCRYPTION_KEY=your-fernet-key
```

**Frontend** (`.env.local`):
```
NEXT_PUBLIC_SUPABASE_URL=https://...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_API_URL=http://localhost:8000
```
