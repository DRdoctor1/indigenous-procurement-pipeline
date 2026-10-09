import duckdb
import polars as pl
import requests

FEED_URL = "https://canadabuys.canada.ca/opendata/pub/openTenderNotice-ouvertAvisAppelOffres.csv"
LOCAL_CSV = "active_tenders_live.csv"
LOCAL_PARQUET = "active_tenders.parquet"

# --- STEP 1: DEFENSIVE INGESTION ---
print("[1/3] Downloading live CanadaBuys procurement feed...")
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
}

try:
    response = requests.get(FEED_URL, headers=headers, timeout=60)
    response.raise_for_status()
    with open(LOCAL_CSV, "wb") as f:
        f.write(response.content)
    print(f" -> Download complete ({len(response.content) / 1024:.1f} KB).")
except Exception as e:
    print(f"Network Extraction Failed: {e}")
    exit(1)

# --- STEP 2: PARQUET CACHE LAYER ---
print("[2/3] Writing clean binary Parquet table...")
try:
    df = pl.read_csv(LOCAL_CSV, ignore_errors=True, truncate_ragged_lines=True)
    df.write_parquet(LOCAL_PARQUET)
    print(f" -> Successfully cached {len(df)} active federal notices.")
except Exception as e:
    print(f"Parquet conversion failed: {e}")
    exit(1)

# --- STEP 3: ANALYTICAL SQL AUDITOR ---
print(
    "[3/3] Running SQL Audit for Site Services, Forestry, Mining & Indigenous Mandates...\n"
)
con = duckdb.connect()

query = f"""
WITH regional_ops AS (
    SELECT 
        "title-titre-eng" AS title,
        "contractingEntityName-nomEntitContractante-eng" AS buyer,
        "regionsOfDelivery-regionsLivraison-eng" AS region,
        "tenderClosingDate-appelOffresDateCloture" AS closing_date,
        "noticeURL-URLavis-eng" AS bid_url,
        "tenderDescription-descriptionAppelOffres-eng" AS description,
        -- SQL CASE EXPRESSION: Categorize Indigenous Mandate Type
        CASE 
            WHEN "tenderDescription-descriptionAppelOffres-eng" ILIKE '%Procurement Strategy for Indigenous Business%'
                 OR "tenderDescription-descriptionAppelOffres-eng" ILIKE '%PSIB%'
                 OR "tenderDescription-descriptionAppelOffres-eng" ILIKE '%indigenous set-aside%'
                 OR "tenderDescription-descriptionAppelOffres-eng" ILIKE '%aboriginal set-aside%'
            THEN 'DIRECT_PSIB_MANDATE'
            ELSE 'GENERAL_COMMERCIAL_LEVERAGE'
        END AS mandate_category
    FROM '{LOCAL_PARQUET}'
    WHERE 
        -- Target British Columbia or National standing offers
        (
            "regionsOfDelivery-regionsLivraison-eng" ILIKE '%British Columbia%' 
            OR "regionsOfDelivery-regionsLivraison-eng" ILIKE '%Canada%'
        )
        -- Target Physical Operations / Site Services / Resources
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
            OR "title-titre-eng" ILIKE '%excavat%'
            OR "title-titre-eng" ILIKE '%civil%'
            OR "tenderDescription-descriptionAppelOffres-eng" ILIKE '%site services%'
            OR "tenderDescription-descriptionAppelOffres-eng" ILIKE '%environmental monitoring%'
        )
)
SELECT 
    mandate_category,
    title,
    buyer,
    closing_date,
    COALESCE(bid_url, 'Check CanadaBuys Portal directly') AS url
FROM regional_ops
ORDER BY mandate_category ASC, closing_date ASC;
"""

results = con.execute(query).fetchall()

print(f"{'='*90}")
print(f" TARGETED BC & NATIONAL PROCUREMENT REPORT ({len(results)} Matches Found)")
print(f"{'='*90}\n")

for r in results:
    tag = r[0]
    title = r[1]
    buyer = r[2]
    closing = r[3]
    url = r[4]

    print(f"[{tag}]")
    print(f"Opportunity : {title}")
    print(f"Agency      : {buyer}")
    print(f"Closing Date: {closing}")
    print(f"Bid Link    : {url}")
    print("-" * 90)