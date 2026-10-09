import duckdb
import polars as pl
import requests


def fetch_government_data(search_query: str, limit: int = 50) -> pl.DataFrame:
    """Fetches live datasets dynamically based on user query and limit."""
    url = "https://open.canada.ca/data/en/api/3/action/package_search"

    params = {"q": search_query, "rows": limit}

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }

    try:
        # Timeout increased to 30s to handle slow government servers
        print(f"Connecting to Canada Open Data for '{search_query}'...")
        response = requests.get(url, params=params, headers=headers, timeout=30)
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

    return pl.DataFrame(clean_records)
# --- EXECUTION HARNESS ---

df = fetch_government_data("indigenous", limit=20)

if not df.is_empty():
    df.write_parquet("procurement_cache.parquet")
    print(
        f"Successfully cached {len(df)} records to procurement_cache.parquet"
    )

    con = duckdb.connect()

    # The SQL query searching specifically for keywords inside the cached data
    query = """
    SELECT 
        department,
        title
    FROM 'procurement_cache.parquet'
    WHERE title ILIKE '%Assessment%' OR title ILIKE '%Recruitment%';
    """

    print("\n--- SPECIFIC BUSINESS OPPORTUNITY / TOPIC RECORDS ---")
    results = con.execute(query).fetchall()

    for row in results:
        print(f"[{row[0]}] -> {row[1]}")
else:
    print("Extraction yielded no rows. Parquet file not modified.")