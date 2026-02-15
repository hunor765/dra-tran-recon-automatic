import pandas as pd

try:
    df = pd.read_excel("client 2/tranzactii-cu-status .xlsx")
    print("Columns:", df.columns.tolist())
    print("\nFirst 3 rows:")
    print(df.head(3))
except Exception as e:
    print(f"Error reading Excel: {e}")
