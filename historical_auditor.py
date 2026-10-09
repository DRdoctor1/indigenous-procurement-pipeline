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

print(
    "[3/3] Auditing historical awards strictly within Northern BC / Hwy 16 Corridor...\n"
)
con = duckdb.connect()

query = f"""
SELECT 
    "title-titre-eng" AS title,
    "totalContractValue-valeurTotaleContrat" AS value,
    "supplierLegalName-nomLegalFournisseur-eng" AS winner,
    "supplierAddressCity-fournisseurAdresseVille-eng" AS winner_city,
    "supplierAddressProvince-fournisseurAdresseProvince-eng" AS winner_province,
    "contractingEntityName-nomEntitContractante-eng" AS buyer,
    "contractAwardDate-dateAttributionContrat" AS award_date
FROM '{LOCAL_PARQUET}'
WHERE 
    -- 1. Scan delivery text, titles, or descriptions for your home territory
    (
        "regionsOfDelivery-regionsLivraison-eng" ILIKE '%Burns Lake%'
        OR "regionsOfDelivery-regionsLivraison-eng" ILIKE '%Smithers%'
        OR "regionsOfDelivery-regionsLivraison-eng" ILIKE '%Prince George%'
        OR "regionsOfDelivery-regionsLivraison-eng" ILIKE '%Vanderhoof%'
        OR "regionsOfDelivery-regionsLivraison-eng" ILIKE '%Houston%'
        OR "regionsOfDelivery-regionsLivraison-eng" ILIKE '%Babine%'
        OR "title-titre-eng" ILIKE '%Burns Lake%'
        OR "title-titre-eng" ILIKE '%Smithers%'
        OR "title-titre-eng" ILIKE '%Prince George%'
        OR "title-titre-eng" ILIKE '%Vanderhoof%'
        OR "title-titre-eng" ILIKE '%Houston%'
        OR "title-titre-eng" ILIKE '%Babine%'
        OR "tenderDescription-descriptionAppelOffres-eng" ILIKE '%Burns Lake%'
        OR "tenderDescription-descriptionAppelOffres-eng" ILIKE '%Smithers%'
        OR "tenderDescription-descriptionAppelOffres-eng" ILIKE '%Prince George%'
    )
ORDER BY value DESC;
"""

local_matches = con.execute(query).fetch_df()

print("=" * 100)
print(
    f" HYPER-LOCAL NORTHERN BC / HWY 16 OPPORTUNITIES ({len(local_matches)} Found)"
)
print("=" * 100)

if not local_matches.empty:
    for idx, r in local_matches.iterrows():
        print(f"${r['value']:,.2f} | {r['title'][:70]}")
        print(
            f"   Winner: {r['winner']} ({r['winner_city']}, {r['winner_province']})"
        )
        print(f"   Buyer:  {r['buyer']} | Date: {r['award_date']}")
        print("-" * 100)
else:
    print(
        "Zero direct federal procurement awards tagged explicitly with local town names in this period."
    )