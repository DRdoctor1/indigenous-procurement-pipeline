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

# Step 3: Generate Prime Contractor Partnership Leads
print(
    "[3/3] Generating Lead Sheet of Out-of-Province Prime Contractors winning in BC...\n"
)
con = duckdb.connect()

query = f"""
SELECT 
    "supplierLegalName-nomLegalFournisseur-eng" AS prime_contractor,
    "supplierAddressProvince-fournisseurAdresseProvince-eng" AS headquarter_province,
    COUNT(*) AS contracts_won_in_bc,
    ROUND(SUM("totalContractValue-valeurTotaleContrat"), 2) AS total_bc_revenue,
    STRING_AGG("title-titre-eng", ' | ') AS project_titles
FROM '{LOCAL_PARQUET}'
WHERE 
    (
        "regionsOfDelivery-regionsLivraison-eng" ILIKE '%British Columbia%' 
        OR "regionsOfDelivery-regionsLivraison-eng" ILIKE '%BC%'
    )
    AND "supplierAddressProvince-fournisseurAdresseProvince-eng" NOT ILIKE '%British Columbia%'
    AND "supplierAddressProvince-fournisseurAdresseProvince-eng" IS NOT NULL
    AND "totalContractValue-valeurTotaleContrat" > 20000
GROUP BY prime_contractor, headquarter_province
ORDER BY total_bc_revenue DESC;
"""

df_leads = con.execute(query).fetch_df()

print("=" * 110)
print(f" PRIME CONTRACTORS FOR INDIGENOUS PARTNERSHIPS ({len(df_leads)} Found)")
print("=" * 110)

for idx, r in df_leads.iterrows():
    print(f"\nPRIME:   {r['prime_contractor']} (HQ: {r['headquarter_province']})")
    print(f"REVENUE: ${r['total_bc_revenue']:,.2f} across {r['contracts_won_in_bc']} project(s)")
    print(f"SCOPES:  {r['project_titles'][:120]}...")
    print("-" * 110)

# Save the lead sheet to CSV
df_leads.to_csv("PRIME_CONTRACTOR_LEAD_SHEET.csv", index=False)
print(
    "\nSaved full lead list to 'PRIME_CONTRACTOR_LEAD_SHEET.csv' in your project folder."
)