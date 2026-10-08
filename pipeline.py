import duckdb
import polars as pl
import requests

# 1. LIVE DATA SOURCE: Canadian Open Government API
URL = "https://open.canada.ca/data/en/api/3/action/package_search"
params = {"q": "indigenous", "rows": 10}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print("Fetching live government records...")
try:
    response = requests.get(URL, params=params, headers=headers, timeout=10)
    print(f"HTTP Status Code: {response.status_code}")
    response.raise_for_status()
    payload = response.json()
except requests.exceptions.RequestException as e:
    print(f"Network Extraction Failed: {e}")
    exit(1)

# Extract records defensively
packages = payload.get("result", {}).get("results", [])
print(f"Successfully retrieved {len(packages)} live records.")

# 2. SANITIZATION & TRANSFORMATION (Python)
clean_records = []
for pkg in packages:
    title = pkg.get("title", "No Title")
    org = pkg.get("organization")
    org_title = org.get("title", "Independent / Unknown") if org else "Independent / Unknown"
    dataset_id = pkg.get("id", "No ID")

    clean_records.append(
        {"id": dataset_id, "department": org_title, "title": str(title).strip()}
    )

# 3. TABULAR CONVERSION (Polars -> DuckDB)
# Polars formats the raw list into a strict tabular memory structure
df = pl.DataFrame(clean_records)

# 4. ANALYTICAL SQL (DuckDB)
con = duckdb.connect()

query = """
SELECT 
    department,
    COUNT(id) AS records_found
FROM df
GROUP BY department
ORDER BY records_found DESC;
"""

print("\n--- LIVE RESULTS (AGGREGATED BY DEPT) ---")
results = con.execute(query).fetchall()

for row in results:
    print(f"Count: {row[1]} | Department: {row[0]}")