import duckdb
import polars as pl
import requests

# Official CanadaBuys Contract History Feed (Fiscal Year 2024-2025 awards)
AWARDS_FEED_URL = "https://canadabuys.canada.ca/opendata/pub/2024-2025-contractHistory-contratsOctroyes.csv"
LOCAL_CSV = "contract_history_2024_2025.csv"
LOCAL_PARQUET = "contract_history.parquet"

print("[1/3] Downloading federal historical contract awards feed...")
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
}

try:
    response = requests.get(AWARDS_FEED_URL, headers=headers, timeout=90)
    response.raise_for_status()
    with open(LOCAL_CSV, "wb") as f:
        f.write(response.content)
    print(
        f" -> Download complete ({len(response.content) / (1024*1024):.2f} MB)."
    )
except Exception as e:
    print(f"Extraction failed: {e}")
    exit(1)

print("[2/3] Converting historical awards to binary Parquet table...")
try:
    # Read defensively: allow jagged lines and UTF-8 encoding
    df = pl.read_csv(
        LOCAL_CSV,
        ignore_errors=True,
        truncate_ragged_lines=True,
        infer_schema_length=10000,
    )
    df.write_parquet(LOCAL_PARQUET)
    print(f" -> Successfully cached {len(df):,} contract awards into Parquet.")
except Exception as e:
    print(f"Parquet conversion failed: {e}")
    exit(1)

# Step 3: Find accessible, winnable contract sizes won by out-of-province vendors
print(
    "[3/3] Isolating entry-level site service contracts (< $500k) won by outsiders...\n"
)
con = duckdb.connect()

query = f"""
SELECT 
    "title-titre-eng" AS title,
    "totalContractValue-valeurTotaleContrat" AS value,
    "supplierLegalName-nomLegalFournisseur-eng" AS winner,
    "supplierAddressProvince-fournisseurAdresseProvince-eng" AS winner_location,
    "contractAwardDate-dateAttributionContrat" AS award_date
FROM '{LOCAL_PARQUET}'
WHERE 
    (
        "regionsOfDelivery-regionsLivraison-eng" ILIKE '%British Columbia%' 
        OR "regionsOfDelivery-regionsLivraison-eng" ILIKE '%BC%'
    )
    AND (
        "title-titre-eng" ILIKE '%forest%'
        OR "title-titre-eng" ILIKE '%tree%'
        OR "title-titre-eng" ILIKE '%clearing%'
        OR "title-titre-eng" ILIKE '%site%'
        OR "title-titre-eng" ILIKE '%camp%'
        OR "title-titre-eng" ILIKE '%environ%'
        OR "title-titre-eng" ILIKE '%waste%'
        OR "title-titre-eng" ILIKE '%fuel%'
        OR "title-titre-eng" ILIKE '%water%'
        OR "title-titre-eng" ILIKE '%sampling%'
        OR "title-titre-eng" ILIKE '%inspect%'
    )
    -- Sole-proprietorship target range: Under $500,000
    AND "totalContractValue-valeurTotaleContrat" BETWEEN 15000 AND 500000
ORDER BY value DESC;
"""

df_matches = con.execute(query).fetch_df()

print("=" * 110)
print(f" ACCESSIBLE ENTRY-LEVEL OPPORTUNITIES ({len(df_matches)} Found)")
print("=" * 110)

for idx, r in df_matches.iterrows():
    print(f"${r['value']:,.2f} | {r['title'][:70]}")
    print(f"   Winner: {r['winner']} ({r['winner_location']}) | Date: {r['award_date']}")
    print("-" * 110)