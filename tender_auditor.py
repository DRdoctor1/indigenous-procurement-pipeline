import os
import duckdb
import polars as pl
import requests

# Live CanadaBuys endpoint for all OPEN/ACTIVE tenders
FEED_URL = "https://canadabuys.canada.ca/opendata/pub/openTenderNotice-ouvertAvisAppelOffres.csv"
LOCAL_CSV = "active_tenders_live.csv"
LOCAL_PARQUET = "active_tenders.parquet"

print("Step 1: Downloading active CanadaBuys tenders feed...")
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
}

try:
    response = requests.get(FEED_URL, headers=headers, timeout=60)
    response.raise_for_status()

    # Save raw CSV locally
    with open(LOCAL_CSV, "wb") as f:
        f.write(response.content)
    print(
        f"Downloaded live tender snapshot ({len(response.content) / 1024:.1f} KB)."
    )

except Exception as e:
    print(f"Failed to download feed: {e}")
    exit(1)

# Step 2: Ingest with Polars & convert to Parquet for fast querying
print("Step 2: Processing into Parquet format...")
try:
    # Read CSV defensively (handling ragged lines and encoding)
    df = pl.read_csv(
        LOCAL_CSV, ignore_errors=True, truncate_ragged_lines=True
    )
    df.write_parquet(LOCAL_PARQUET)
    print(f"Cached {len(df)} active tenders into {LOCAL_PARQUET}")
except Exception as e:
    print(f"Polars conversion failed: {e}")
    exit(1)

# Step 3: Targeted Regional Opportunity Query
print("Running Targeted Opportunity Filter (BC / Operations / Site)...")

con = duckdb.connect()

query = f"""
SELECT 
    "title-titre-eng" AS title,
    "contractingEntityName-nomEntitContractante-eng" AS buyer,
    "regionsOfDelivery-regionsLivraison-eng" AS delivery_region,
    "tenderClosingDate-appelOffresDateCloture" AS closing_date,
    "noticeURL-URLavis-eng" AS rfp_url
FROM '{LOCAL_PARQUET}'
WHERE 
    -- 1. REGIONAL FILTER: British Columbia or Canada-wide
    (
        "regionsOfDelivery-regionsLivraison-eng" ILIKE '%British Columbia%' 
        OR "regionsOfDelivery-regionsLivraison-eng" ILIKE '%Canada%'
    )
    -- 2. OPERATIONAL / RESOURCE / SITE WORK FILTER
    AND (
        "title-titre-eng" ILIKE '%forest%'
        OR "title-titre-eng" ILIKE '%tree%'
        OR "title-titre-eng" ILIKE '%clearing%'
        OR "title-titre-eng" ILIKE '%site%'
        OR "title-titre-eng" ILIKE '%camp%'
        OR "title-titre-eng" ILIKE '%environ%'
        OR "title-titre-eng" ILIKE '%mine%'
        OR "title-titre-eng" ILIKE '%waste%'
        OR "title-titre-eng" ILIKE '%fuel%'
        OR "title-titre-eng" ILIKE '%road%'
        OR "title-titre-eng" ILIKE '%drilling%'
        OR "tenderDescription-descriptionAppelOffres-eng" ILIKE '%environmental monitoring%'
        OR "tenderDescription-descriptionAppelOffres-eng" ILIKE '%site maintenance%'
    )
ORDER BY closing_date ASC;
"""

matches = con.execute(query).fetchall()

print(f"\n=======================================================")
print(
    f" FOUND {len(matches)} LIVE OPERATIONAL OPPORTUNITIES IN BC / CANADA"
)
print(f"=======================================================\n")

for m in matches:
    print(f"TITLE:    {m[0]}")
    print(f"BUYER:    {m[1]}")
    print(f"REGION:   {m[2]}")
    print(f"CLOSES:   {m[3]}")
    print(f"URL:      {m[4]}")
    print("-" * 70)