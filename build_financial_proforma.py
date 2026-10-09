from datetime import datetime
import duckdb

OUTPUT_FILE = "SUS_KE_BUSINESS_PLAN.html"
print("[1/2] Modeling Zero-Equity Capital Acquisition Schedule...")

# ==============================================================================
# CAPITAL ACQUISITION TARGETS (NON-DILUTIVE & CHARACTER-BASED)
# ==============================================================================
capital_sources = [
    {
        "source": "Futurpreneur Canada & BDC (Indigenous Entrepreneur Program)",
        "type": "Unsecured Startup Loan",
        "target_amount": 20000.00,
        "terms": "Interest-only Year 1; no collateral required; paired with mentor",
        "status": "Application Package Ready",
    },
    {
        "source": "New Relationship Trust (NRT) / Band Capacity Grant",
        "type": "Non-Repayable Equity Grant",
        "target_amount": 5000.00,
        "terms": "Non-repayable direct tool and certification grant",
        "status": "Intake Pending Plan Submission",
    },
    {
        "source": "Lake Babine Nation / ISET (Workforce Development Allowance)",
        "type": "Living & Safety Training Subsidy",
        "target_amount": 3500.00,
        "terms": "Covers OFA-1 First Aid, WHMIS, and initial safety gear",
        "status": "Local Band Coordination",
    },
]

total_target_capital = sum(c["target_amount"] for c in capital_sources)

# ==============================================================================
# LEAN SETUP BUDGET (MATCHING THE $28,500 SEED CAPITAL)
# ==============================================================================
capex_allocation = [
    {
        "item": "Reliable 4x4 Utility Transport (Inspected Used 3/4-Ton)",
        "cost": 11000.00,
        "purpose": "Resource road site deployment and sample transport",
    },
    {
        "item": "Environmental Handheld Meters & Field Kits",
        "cost": 1200.00,
        "purpose": "Water quality telemetry (pH, turbidity, conductivity)",
    },
    {
        "item": "Safety PPE, Commercial VHF Radio & inReach Satellite",
        "cost": 1800.00,
        "purpose": "Mandatory resource road radio channels & lone worker safety",
    },
    {
        "item": "WorkSafeBC CU 763036 & Commercial General Liability (CGL)",
        "cost": 1500.00,
        "purpose": "Initial insurance deposits and site clearance compliance",
    },
    {
        "item": "Working Capital Cash Float (Receivables Buffer)",
        "cost": 13000.00,
        "purpose": "60-day operational survival float for fuel and supplies",
    },
]

total_budget = sum(c["cost"] for cape in [capex_allocation] for c in cape)

# ==============================================================================
# 3-YEAR PRO-FORMA WITH DEBT SERVICE (FUTURPRENEUR LOAN)
# ==============================================================================
# Futurpreneur interest-only Year 1 (~8.5% on $20,000 = ~$1,700/yr or $140/mo)
projections = [
    {
        "year": "Year 1 (Solo Bootstrap)",
        "revenue": 75000.00,  # 2 direct awards / small subcontracts
        "direct_costs": 18000.00,  # fuel, testing consumables, vehicle upkeep
        "overhead": 2500.00,  # admin, software, phone
        "debt_service": 1700.00,  # Interest-only loan payments
    },
    {
        "year": "Year 2 (PSIB Partner Expansion)",
        "revenue": 180000.00,  # 3 prime subcontracts
        "direct_costs": 65000.00,  # includes 1 casual technician for 90 days
        "overhead": 4200.00,
        "debt_service": 5400.00,  # Principal + Interest repayment
    },
    {
        "year": "Year 3 (Standing Offer Execution)",
        "revenue": 350000.00,  # Recurring standing offer call-ups
        "direct_costs": 135000.00,  # 2 casual field technicians
        "overhead": 6500.00,
        "debt_service": 5400.00,
    },
]

p_rows = []
for p in projections:
    gross_profit = p["revenue"] - p["direct_costs"]
    ebitda = gross_profit - p["overhead"]
    net_pretax = ebitda - p["debt_service"]
    net_margin = (net_pretax / p["revenue"]) * 100

    p_rows.append(
        {
            "year": p["year"],
            "revenue": p["revenue"],
            "direct_costs": p["direct_costs"],
            "gross_profit": gross_profit,
            "debt_service": p["debt_service"],
            "net_pretax": net_pretax,
            "net_margin": net_margin,
        }
    )

print("[2/2] Generating lean commercial plan...")

html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; color: #1a202c; line-height: 1.6; background-color: #fff; }}
    .header {{ border-bottom: 4px solid #2b6cb0; padding-bottom: 20px; margin-bottom: 30px; }}
    h1 {{ color: #1a365d; font-size: 26px; margin: 0 0 5px 0; text-transform: uppercase; letter-spacing: 0.5px; }}
    .subtitle {{ color: #4a5568; font-size: 15px; font-weight: 600; }}
    .meta-bar {{ margin-top: 15px; font-size: 13px; color: #718096; }}
    
    .card-grid {{ display: flex; gap: 20px; margin: 25px 0; }}
    .card {{ flex: 1; background: #ebf8ff; border: 1px solid #bee3f8; border-radius: 8px; padding: 18px; text-align: center; }}
    .card-num {{ font-size: 24px; font-weight: bold; color: #2b6cb0; }}
    .card-label {{ font-size: 11.5px; color: #4a5568; text-transform: uppercase; font-weight: bold; margin-top: 5px; }}
    
    h2 {{ color: #2c5282; font-size: 17px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 35px; text-transform: uppercase; }}
    p, li {{ font-size: 13.5px; color: #2d3748; }}
    
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 13px; }}
    th, td {{ border: 1px solid #cbd5e0; padding: 9px 12px; }}
    th {{ background: #edf2f7; color: #2d3748; text-transform: uppercase; font-size: 11px; }}
    .highlight-row {{ background: #feebc8 !important; font-weight: bold; }}
    
    .callout {{ background: #f0fff4; border-left: 4px solid #38a169; padding: 15px; margin: 20px 0; border-radius: 0 6px 6px 0; font-size: 13px; }}
    .footer {{ margin-top: 50px; border-top: 1px solid #e2e8f0; padding-top: 15px; font-size: 11px; color: #a0aec0; text-align: center; }}
</style>
</head>
<body>

<div class="header">
    <h1>Sus Ke Environmental Services</h1>
    <div class="subtitle">Capital Sourcing Strategy & Lean Commercial Launch Plan</div>
    <div class="meta-bar">
        <strong>Lead Operator:</strong> Phillip Williams | <strong>Nation:</strong> Lake Babine Nation | <strong>WorkSafeBC CU:</strong> 763036 | <strong>Territory:</strong> Highway 16 Corridor, BC
    </div>
</div>

<div class="card-grid">
    <div class="card">
        <div class="card-num">${total_target_capital:,.0f}</div>
        <div class="card-label">Target Seed Capital</div>
    </div>
    <div class="card">
        <div class="card-num">$8,500</div>
        <div class="card-label">Target Non-Repayable Grants</div>
    </div>
    <div class="card">
        <div class="card-num">$13,000</div>
        <div class="card-label">Operating Cash Reserve</div>
    </div>
    <div class="card">
        <div class="card-num">5.0%</div>
        <div class="card-label">Federal PSIB Quota Mandate</div>
    </div>
</div>

<h2>1. Executive Venture Overview</h2>
<p>
    <strong>Sus Ke Environmental Services</strong> is an Indigenous sole proprietorship based in North-Central BC providing baseline environmental sampling (water/soil), compliance field monitoring, and site technical support across the Highway 16 corridor.
</p>
<p>
    The venture is structured to capitalize on the federal <strong>Procurement Strategy for Indigenous Business (PSIB)</strong>. Out-of-province prime contractors won over <strong>56% of regional site contracts in BC</strong> in recent federal filings due to a verified shortage of local, certified Indigenous field operators. Sus Ke serves as an on-the-ground subcontractor partner to fulfill these mandatory quotas.
</p>

<h2>2. Capital Sourcing Strategy (Phase 0: 30–60 Day Acquisition)</h2>
<p>Rather than relying on uncommitted private funds, the venture secures startup financing through structured Indigenous entrepreneurship funding channels:</p>

<table>
    <tr>
        <th>Capital Source</th>
        <th>Facility Type</th>
        <th>Target Amount</th>
        <th>Terms & Structural Role</th>
    </tr>
"""

for c in capital_sources:
    html_doc += f"""    <tr>
        <td><strong>{c['source']}</strong></td>
        <td>{c['type']}</td>
        <td style="text-align: right; font-weight: bold;">${c['target_amount']:,.2f}</td>
        <td>{c['terms']}</td>
    </tr>
"""

html_doc += f"""    <tr class="highlight-row">
        <td colspan="2">TOTAL TARGET CAPITALIZATION</td>
        <td style="text-align: right;">${total_target_capital:,.2f}</td>
        <td>Sufficient to fund full CapEx + 60-day operating buffer</td>
    </tr>
</table>

<h2>3. Lean CapEx Deployment Budget</h2>
<p>Seed capital is strictly deployed into essential field assets and regulatory compliance:</p>

<table>
    <tr>
        <th>Asset / Deployment Line</th>
        <th>Budget</th>
        <th>Operational Function</th>
    </tr>
"""

for ca in capex_allocation:
    html_doc += f"""    <tr>
        <td><strong>{ca['item']}</strong></td>
        <td style="text-align: right;">${ca['cost']:,.2f}</td>
        <td>{ca['purpose']}</td>
    </tr>
"""

html_doc += f"""    <tr class="highlight-row">
        <td>TOTAL STARTUP ALLOCATION</td>
        <td style="text-align: right;">${total_budget:,.2f}</td>
        <td>Complete field capability with zero luxury or office overhead</td>
    </tr>
</table>

<h2>4. 3-Year Pro-Forma Income Schedule (With Debt Service)</h2>
<p>Modeled conservatively assuming Year 1 executes strictly 2 modest contracts ($35k–$40k scopes) solo. Includes debt service for the Futurpreneur loan:</p>

<table>
    <tr>
        <th>Financial Schedule</th>
        <th style="text-align: right;">Year 1 (Solo Bootstrap)</th>
        <th style="text-align: right;">Year 2 (PSIB Partner Expansion)</th>
        <th style="text-align: right;">Year 3 (Standing Offer Execution)</th>
    </tr>
    <tr>
        <td>Gross Contract Revenue</td>
        <td style="text-align: right;">${p_rows[0]['revenue']:,.2f}</td>
        <td style="text-align: right;">${p_rows[1]['revenue']:,.2f}</td>
        <td style="text-align: right;">${p_rows[2]['revenue']:,.2f}</td>
    </tr>
    <tr>
        <td>Direct Field Expenses (COGS)</td>
        <td style="text-align: right;">${p_rows[0]['direct_costs']:,.2f}</td>
        <td style="text-align: right;">${p_rows[1]['direct_costs']:,.2f}</td>
        <td style="text-align: right;">${p_rows[2]['direct_costs']:,.2f}</td>
    </tr>
    <tr style="background: #edf2f7; font-weight: bold;">
        <td>Gross Operating Margin</td>
        <td style="text-align: right;">${p_rows[0]['gross_profit']:,.2f}</td>
        <td style="text-align: right;">${p_rows[1]['gross_profit']:,.2f}</td>
        <td style="text-align: right;">${p_rows[2]['gross_profit']:,.2f}</td>
    </tr>
    <tr>
        <td>Loan Debt Service (Futurpreneur)</td>
        <td style="text-align: right;">${p_rows[0]['debt_service']:,.2f}</td>
        <td style="text-align: right;">${p_rows[1]['debt_service']:,.2f}</td>
        <td style="text-align: right;">${p_rows[2]['debt_service']:,.2f}</td>
    </tr>
    <tr class="highlight-row">
        <td>Net Pre-Tax Owner Earnings</td>
        <td style="text-align: right;">${p_rows[0]['net_pretax']:,.2f}</td>
        <td style="text-align: right;">${p_rows[1]['net_pretax']:,.2f}</td>
        <td style="text-align: right;">${p_rows[2]['net_pretax']:,.2f}</td>
    </tr>
    <tr>
        <td>Net Margin %</td>
        <td style="text-align: right;">{p_rows[0]['net_margin']:.1f}%</td>
        <td style="text-align: right;">{p_rows[1]['net_margin']:.1f}%</td>
        <td style="text-align: right;">{p_rows[2]['net_margin']:.1f}%</td>
    </tr>
</table>

<div class="callout">
    <strong>Lender Feasibility Guarantee:</strong> Year 1 debt service ($1,700/year or ~$142/month) is covered more than 30 times over by Year 1 net earnings ($52,800), presenting virtually zero default risk to underwriting partners.
</div>

<h2>5. 60-Day Execution Roadmap</h2>
<ul>
    <li><strong>Days 1–15:</strong> Complete Futurpreneur Indigenous Program intake with this plan; submit NRT equity grant application.</li>
    <li><strong>Days 16–30:</strong> Secure OFA-1 First Aid certification; register on the federal Indigenous Business Directory (IBD).</li>
    <li><strong>Days 31–45:</strong> Funding disbursement; procure inspected 3/4-ton utility transport and safety radio gear.</li>
    <li><strong>Days 46–60:</strong> Initiate subcontract outreach to audited out-of-province primes (Milestone, Atwell) using verified PSIB compliance pitch.</li>
</ul>

<div class="footer">
    Generated via Sus Ke Business Analytics Engine | Prepared for Futurpreneur, NRT, and Community Futures Application Review
</div>

</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_doc)

print(f"\nSUCCESS! Generated updated capital-sourcing plan: '{OUTPUT_FILE}'")