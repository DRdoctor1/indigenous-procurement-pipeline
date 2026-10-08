import duckdb
import polars as pl
import requests


def fetch_government_data(search_query: str, limit: int = 50) -> pl.DataFrame:
    """Fetches live datasets dynamically based on user query and limit."""
    url = "https://open.canada.ca/data/en/api/3/action/package_search"

    # TODO 1: Assign 'search_query' and 'limit' to the dictionary keys below
    params = {"q": search_query, "rows": limit}

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Network Extraction Failed: {e}")
        return pl.DataFrame()

    packages = payload.get("result", {}).get("results", [])

    clean_records = []
    for pkg in packages:
        title = pkg.get("title", "No Title")
        org = pkg.get("organization")
        org_title = (
            org.get("title", "Independent / Unknown")
            if org
            else "Independent / Unknown"
        )
        dataset_id = pkg.get("id", "No ID")

        clean_records.append(
            {"id": dataset_id, "department": org_title, "title": str(title).strip()}
        )

    # Convert the list of records to a Polars DataFrame
    return pl.DataFrame(clean_records)


# --- EXECUTION HARNESS ---

# Call the function here and store the result in 'df'
df = fetch_government_data("forestry mining water indigenous", limit=30)

# ANALYTICAL SQL (DuckDB)
con = duckdb.connect()
query = """
SELECT 
    department,
    COUNT(id) AS records_found
FROM df
GROUP BY department
ORDER BY records_found DESC;
"""

print(f"\n--- SQL RESULTS ---")
results = con.execute(query).fetchall()
for row in results:
    print(f"Count: {row[1]} | Department: {row[0]}")