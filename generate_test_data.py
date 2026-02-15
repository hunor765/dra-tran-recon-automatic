import pandas as pd
import random
import os

# Paths
base_dir = "/Users/lazarhunor/.gemini/antigravity/playground/dynamic-pioneer/client 2"
backend_file = os.path.join(base_dir, "datarevolt-tranzactii.xlsx")
ga4_file = os.path.join(base_dir, "ga4_exportv2 - Free form 1.csv")

output_dir = "/Users/lazarhunor/.gemini/antigravity/playground/dynamic-pioneer/test_data"
os.makedirs(output_dir, exist_ok=True)

# 1. Enrich Backend Data
print(f"Reading Backend: {backend_file}")
df_backend = pd.read_excel(backend_file)

statuses = ["completed", "completed", "completed", "pending", "failed", "cancelled", "returned"]
df_backend["order_status"] = [random.choice(statuses) for _ in range(len(df_backend))]

backend_out = os.path.join(output_dir, "backend_enriched.csv")
df_backend.to_csv(backend_out, index=False)
print(f"Saved enriched backend to: {backend_out}")

# 2. Enrich GA4 Data
print(f"Reading GA4: {ga4_file}")
df_ga4 = pd.read_csv(ga4_file, skiprows=6) # Skipping header metadata lines standard in GA4 exports

browsers = ["Chrome", "Chrome", "Chrome", "Safari", "Safari", "Firefox", "Edge"]
devices = ["mobile", "mobile", "desktop", "desktop", "tablet"]

df_ga4["browser"] = [random.choice(browsers) for _ in range(len(df_ga4))]
df_ga4["device_category"] = [random.choice(devices) for _ in range(len(df_ga4))]

ga4_out = os.path.join(output_dir, "ga4_enriched.csv")
df_ga4.to_csv(ga4_out, index=False)
print(f"Saved enriched GA4 to: {ga4_out}")
