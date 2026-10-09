import duckdb
import polars as pl

# ==============================================================================
# CANADIAN SME BENCHMARKS (ISED / STATSCAN NAICS 541620 & 562910 FIELD BENCHMARKS)
# For Northern Small Operators (< $500k Annual Revenue)
# ==============================================================================

BENCHMARKS = {
    "fuel_and_vehicle_pct": 0.12,  # 12% of revenue goes to fuel, tires, truck maintenance
    "insurance_and_legal_pct": 0.04,  # 4% goes to CGL, WorkSafeBC, environmental liability
    "field_supplies_and_testing_pct": 0.08,  # 8% to lab assay fees, PPE, disposable sampling kits
    "casual_labor_pct": 0.35,  # 35% paid to on-call casual day-rate tech (when needed)
    "tax_reserve_pct": 0.15,  # 15% withheld for federal/provincial corporate taxes
    "target_net_profit_pct": 0.26,  # 26% net margin for efficient solo operators
}

# STARTING CAPITAL POSITION
STARTING_EQUITY = 35000.00

# INITIAL SETUP CAPEX (ONE-TIME COSTS)
SETUP_CAPEX = {
    "used_utility_4x4_deposit": 12000.00,
    "initial_safety_ppe_gear": 2500.00,
    "basic_sampling_meters": 2000.00,
    "incorporation_ibd_legal": 1500.00,
    "annual_insurance_prepay": 3000.00,
}

total_capex = sum(SETUP_CAPEX.values())
available_working_capital = STARTING_EQUITY - total_capex

print(f"{'='*80}")
print(f"FINANCIAL POSITION AT STARTUP")
print(f"{'='*80}")
print(f"Starting Cash Injection        : ${STARTING_EQUITY:,.2f}")
print(f"Initial CapEx Setup Costs      : ${total_capex:,.2f}")
print(
    f"Remaining Cash Reserve (Buffer): ${available_working_capital:,.2f}\n"
)

# ==============================================================================
# CONTRACT SIMULATION ENGINE (SCENARIOS: $40k, $80k, $150k Subcontracts)
# ==============================================================================

scenarios = [
    {
        "contract_name": "Tier 1: Direct-Award Water/Soil Sampling Scope",
        "contract_value": 40000.00,
        "estimated_days": 30,
        "requires_second_hand": False,  # You work solo
    },
    {
        "contract_name": "Tier 2: Prime Subcontract (Milestone/Atwell PSIB Scope)",
        "contract_value": 85000.00,
        "estimated_days": 60,
        "requires_second_hand": True,  # 1 helper hired on-call
    },
    {
        "contract_name": "Tier 3: Multi-Month Remediation & Site Standby",
        "contract_value": 150000.00,
        "estimated_days": 110,
        "requires_second_hand": True,  # 1 helper hired on-call
    },
]

financial_models = []

for sc in scenarios:
    rev = sc["contract_value"]
    days = sc["estimated_days"]

    # Calculate variable direct costs
    fuel_exp = rev * BENCHMARKS["fuel_and_vehicle_pct"]
    supplies_exp = rev * BENCHMARKS["field_supplies_and_testing_pct"]
    insurance_allotment = rev * BENCHMARKS["insurance_and_legal_pct"]

    # Labor cost: Solo means you keep it; Second hand means day-rate helper
    if sc["requires_second_hand"]:
        # $320/day for casual field tech (8 hrs @ $40/hr)
        helper_labor = days * 320.00
    else:
        helper_labor = 0.00

    total_direct_costs = (
        fuel_exp + supplies_exp + insurance_allotment + helper_labor
    )
    gross_operating_profit = rev - total_direct_costs
    tax_withholding = gross_operating_profit * BENCHMARKS["tax_reserve_pct"]
    net_cash_earned = gross_operating_profit - tax_withholding

    # Maximum cash required to float before receiving invoice payment (Day 0 to Day 60)
    # Floating 60 days of fuel, supplies, and helper payroll
    float_required_60_days = total_direct_costs * (60.0 / max(days, 60))

    financial_models.append(
        {
            "scenario": sc["contract_name"],
            "contract_value": rev,
            "field_days": days,
            "fuel_vehicle": fuel_exp,
            "field_supplies": supplies_exp,
            "helper_labor": helper_labor,
            "total_operating_costs": total_direct_costs,
            "net_cash_takehome": net_cash_earned,
            "peak_cash_float_needed": float_required_60_days,
            "is_funded_by_cash_reserve": float_required_60_days
            <= available_working_capital,
        }
    )

df_sim = pl.DataFrame(financial_models)

# Run SQL analytics over the simulation
con = duckdb.connect()

query = """
SELECT 
    scenario,
    contract_value AS revenue,
    total_operating_costs AS total_costs,
    ROUND(net_cash_takehome, 2) AS net_profit,
    ROUND((net_cash_takehome / contract_value) * 100, 1) AS net_margin_pct,
    ROUND(peak_cash_float_needed, 2) AS max_cash_float_needed,
    CASE 
        WHEN is_funded_by_cash_reserve THEN 'SAFE (Fully Covered by $14k Reserve)'
        ELSE 'RISK (Requires Working Capital Line from ANTCO)'
    END AS failsafe_status
FROM df_sim;
"""

results = con.execute(query).fetch_df()

print(f"{'='*80}")
print("FINANCIAL FEASIBILITY & CASH-FLOW FAILSAFE AUDIT")
print(f"{'='*80}\n")

for idx, r in results.iterrows():
    print(f"CONTRACT: {r['scenario']}")
    print(f" -> Revenue           : ${r['revenue']:,.2f}")
    print(f" -> Total Field Costs : ${r['total_costs']:,.2f}")
    print(
        f" -> Net Take-Home     : ${r['net_profit']:,.2f} ({r['net_margin_pct']}% Margin)"
    )
    print(f" -> 60-Day Cash Float : ${r['max_cash_float_needed']:,.2f}")
    print(f" -> FAILSAFE STATUS   : {r['failsafe_status']}")
    print("-" * 80)