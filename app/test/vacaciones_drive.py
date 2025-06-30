import pandas as pd

sheet_id = "17MfMq1GnBTLPI3uFVfzgqCx91Y1JEh6qtyGKqKPj3mo"
gid = "0"  # Asume que es la primera hoja

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

df = pd.read_csv(url)
print(df.head())
