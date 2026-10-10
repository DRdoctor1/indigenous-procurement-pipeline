from datetime import datetime

OUTPUT_FILE = "SUS_KE_FIRE_OPS_PLAN.html"
print("[1/2] Compiling Wildland Fire & Fuel Mitigation Commercial Pro-Forma...")

# CAPITAL STRUCTURE
target_capital = 28500.00
futurpreneur_loan = 20000.00
grants_training = 8500.00  # NRT + Band ISET / Safety gear subsidy

# LEAN SETUP ASSETS (WILDFIRE & FIELD BRUSHING FOCUS)
startup_assets = [
    {
        "item": "Inspected 4x4 3/4-Ton Crew/Utility Truck",
        "cost": 11000.00,
        "function": "BCWS Equipment Call-Out Registry eligible transport & tool haulage",
    },
    {
        "item": "Pro Brush Saw / Chainsaw Kit + Safety Chaps & Field Tools",
        "cost": 2200.00,
        "function": "Manual fuel mitigation, danger tree clearing, spacing & brushing",
    },
    {
        "item": "VHF Commercial Radio & Garmin inReach Satellite Unit",
        "function": "Mandatory BCWS fireline communications & resource road safety",
        "cost": 1800.00,
    },
    {
        "item": "WorkSafeBC CU 763036 & Commercial General Liability (CGL)",
        "function": "Mandatory provincial contract clearance & site access compliance",
        "cost": 1500.00,
    },
    {
        "item": "Liquid Working Capital Reserve (Fuel, Float & Contingency)",
        "function": "Guaranteed 45-day operational cash cushion for government invoice cycles",
        "cost": 12000.00,
    },
]

total_capex = sum(a["cost"] for a in startup_assets)

# 3-YEAR REVENUE MODEL (SUMMER CALL-OUTS + FALL/WINTER FUEL CONTRACTS)
# Year 1: 45 days BCWS fireline call-out/standby + 1 modest local fuel/brushing contract ($35k)
# Year 2: 60 days fireline call-out + 1 BCTS Babine fuel contract ($90k)
# Year 3: Multi-crew deployment across regional district
projections = [
    {
        "year": "Year 1 (Solo Bootstrap)",
        "fire_season_rev": 42500.00,  # 45 days @ ~$944/day (truck + operator tariff)
        "fall_winter_contracts": 38000.00,  # 1 local fuel mitigation / brushing scope
        "total_revenue": 80500.00,
        "direct_costs": 19500.00,  # fuel, saw maintenance, chains, PPE, insurance
        "debt_service": 1700.00,  # ~$142/mo interest-only loan
    },
    {
        "year": "Year 2 (Crew Expansion)",
        "fire_season_rev": 75000.00,  # 2-person crew deployed on active calls
        "fall_winter_contracts": 95000.00,  # BCTS Babine fuel mitigation / spacing tender
        "total_revenue": 170000.00,
        "direct_costs": 62000.00,  # includes on-call saw assistant wages
        "debt_service": 5400.00,  # P+I repayment
    },
    {
        "year": "Year 3 (Multi-Unit Contractor)",
        "fire_season_rev": 135000.00,  # 2 trucks registered with BCWS Northwest Centre
        "fall_winter_contracts": 185000.00,  # 2 major ministry fuel reduction packages
        "total_revenue": 320000.00,
        "direct_costs": 125000.00,
        "debt_service": 5400.00,
    },
]

p_rows = []
for p in projections:
    gross_margin = p["total_revenue"] - p["direct_costs"]
    net_pretax = gross_margin - p["debt_service"]
    net_pct = (net_pretax / p["total_revenue"]) * 100
    p_rows.append(
        {
            "year": p["year"],
            "total_revenue": p["total_revenue"],
            "direct_costs": p["direct_costs"],
            "gross_margin": gross_margin,
            "debt_service": p["debt_service"],
            "net_pretax": net_pretax,
            "net_pct": net_pct,
        }
    )

print("[2/2] Generating executive pitch document...")

html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 30px; color: #1a202c; line-height: 1.5; background-color: #fff; }}
    .header {{ border-bottom: 4px solid #c53030; padding-bottom: 15px; margin-bottom: 20px; }}
    h1 {{ color: #742a2a; font-size: 26px; margin: 0; text-transform: uppercase; letter-spacing: 0.5px; }}
    .subtitle {{ color: #c53030; font-size: 15px; font-weight: bold; margin-top: 3px; }}
    .meta-bar {{ margin-top: 10px; font-size: 12px; color: #4a5568; background: #fff5f5; padding: 8px 12px; border-radius: 4px; border-left: 4px solid #e53e3e; }}
    
    .pitch-box {{ background: #fffaf0; border: 2px solid #dd6b20; border-radius: 8px; padding: 18px; margin: 20px 0; }}
    .pitch-title {{ color: #9c4221; font-size: 14px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }}
    .pitch-grid {{ display: flex; gap: 15px; }}
    .pitch-col {{ flex: 1; border-right: 1px solid #ecc94b; padding-right: 15px; font-size: 12.5px; }}
    .pitch-col:last-child {{ border-right: none; padding-right: 0; }}
    .pitch-lead {{ font-weight: bold; color: #7b341e; margin-bottom: 4px; display: block; }}
    
    .card-grid {{ display: flex; gap: 15px; margin: 20px 0; }}
    .card {{ flex: 1; background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px; text-align: center; }}
    .card-num {{ font-size: 22px; font-weight: bold; color: #c53030; }}
    .card-label {{ font-size: 11px; color: #4a5568; text-transform: uppercase; font-weight: bold; margin-top: 4px; }}
    
    h2 {{ color: #742a2a; font-size: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-top: 25px; text-transform: uppercase; }}
    p, li {{ font-size: 12.5px; color: #2d3748; }}
    
    table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 12px; }}
    th, td {{ border: 1px solid #cbd5e0; padding: 8px 10px; }}
    th {{ background: #edf2f7; color: #2d3748; text-transform: uppercase; font-size: 10.5px; }}
    .highlight-row {{ background: #feebc8 !important; font-weight: bold; }}
    
    .callout {{ background: #f0fff4; border-left: 4px solid #38a169; padding: 12px; margin: 15px 0; border-radius: 0 4px 4px 0; font-size: 12px; }}
    .footer {{ margin-top: 35px; border-top: 1px solid #e2e8f0; padding-top: 10px; font-size: 10.5px; color: #a0aec0; text-align: center; }}
</style>
</head>
<body>

<div class="header">
    <h1>Sus Ke Field & Emergency Operations</h1>
    <div class="subtitle">Commercial Wildland Fire, Fuel Mitigation & Civil Support Venture</div>
    <div class="meta-bar">
        <strong>Lead Operator:</strong> Phillip Williams | <strong>Affiliation:</strong> Lake Babine Nation | <strong>Operational Background:</strong> 3 Years Type 3 Wildland Firefighter | <strong>WorkSafeBC:</strong> Active CU 763036 | <strong>Base:</strong> Bulkley-Nechako / Hwy 16
    </div>
</div>

<div class="pitch-box">
    <div class="pitch-title">Executive 60-Second Lender & Investor Memo</div>
    <div class="pitch-grid">
        <div class="pitch-col">
            <span class="pitch-lead">1. Operational Proof & Qualifications</span>
            Lead operator brings <strong>3 verified seasons of active Type 3 Wildland Firefighting experience</strong> with live provincial tickets (S-100, S-290, radio, saw safety). Zero theoretical startup risk—proven field capability under extreme pressure.
        </div>
        <div class="pitch-col">
            <span class="pitch-lead">2. Dual Counter-Cyclical Revenue</span>
            • <strong>Summer (May–Aug):</strong> BC Wildfire Service (BCWS) equipment/operator tariff call-outs ($600–$950/day). Priority dispatch for local Indigenous contractors.<br>
            • <strong>Fall/Winter (Sep–Mar):</strong> BCTS & Ministry of Forests fuel reduction, danger tree spacing & FSR roadside brushing ($80k–$140k tenders).
        </div>
        <div class="pitch-col">
            <span class="pitch-lead">3. Debt Protection & Capital Defense</span>
            <strong>$20,000 loan request</strong> carries an interest-only service of just <strong>$142/month</strong> in Year 1. Covered <strong>34x over</strong> by Year 1 net cash ($59,300). Backed by <strong>$12,000 in liquid operating reserve</strong> to float Net-30/60 government pay cycles.
        </div>
    </div>
</div>

<div class="card-grid">
    <div class="card">
        <div class="card-num">${target_capital:,.0f}</div>
        <div class="card-label">Total Seed Capital</div>
    </div>
    <div class="card">
        <div class="card-num">3 Seasons</div>
        <div class="card-label">Type 3 Fireline Experience</div>
    </div>
    <div class="card">
        <div class="card-num">${startup_assets[4]['cost']:,.0f}</div>
        <div class="card-label">Operating Cash Reserve</div>
    </div>
    <div class="card">
        <div class="card-num">> 34x</div>
        <div class="card-label">Debt Service Coverage (DSCR)</div>
    </div>
</div>

<h2>1. Capital Deployment Budget</h2>
<table>
    <tr>
        <th>Asset / Deployment Line</th>
        <th style="text-align: right;">Budget Allocation</th>
        <th>Operational Purpose</th>
    </tr>
"""

for a in startup_assets:
    html_content += f"""    <tr>
        <td><strong>{a['item']}</strong></td>
        <td style="text-align: right; font-weight: bold;">${a['cost']:,.2f}</td>
        <td>{a['function']}</td>
    </tr>
"""

html_content += f"""    <tr class="highlight-row">
        <td>TOTAL SEED DEPLOYMENT</td>
        <td style="text-align: right;">${total_capex:,.2f}</td>
        <td>Complete field capability with zero debt-burdened heavy machinery</td>
    </tr>
</table>

<h2>2. 3-Year Counter-Cyclical Pro-Forma Income Schedule</h2>
<table>
    <tr>
        <th>Financial Schedule</th>
        <th style="text-align: right;">Year 1 (Solo Operator)</th>
        <th style="text-align: right;">Year 2 (Crew Expansion)</th>
        <th style="text-align: right;">Year 3 (Multi-Unit Contractor)</th>
    </tr>
    <tr>
        <td>Summer Fireline Call-Out Revenue (BCWS)</td>
        <td style="text-align: right;">${projections[0]['fire_season_rev']:,.2f}</td>
        <td style="text-align: right;">${projections[1]['fire_season_rev']:,.2f}</td>
        <td style="text-align: right;">${projections[2]['fire_season_rev']:,.2f}</td>
    </tr>
    <tr>
        <td>Fall/Winter Fuel Reduction & Brushing Contracts</td>
        <td style="text-align: right;">${projections[0]['fall_winter_contracts']:,.2f}</td>
        <td style="text-align: right;">${projections[1]['fall_winter_contracts']:,.2f}</td>
        <td style="text-align: right;">${projections[2]['fall_winter_contracts']:,.2f}</td>
    </tr>
    <tr style="background: #edf2f7; font-weight: bold;">
        <td>Total Annual Gross Revenue</td>
        <td style="text-align: right;">${p_rows[0]['total_revenue']:,.2f}</td>
        <td style="text-align: right;">${p_rows[1]['total_revenue']:,.2f}</td>
        <td style="text-align: right;">${p_rows[2]['total_revenue']:,.2f}</td>
    </tr>
    <tr>
        <td>Direct Field Expenses (Fuel, Saw Maintenance, Gear, CGL)</td>
        <td style="text-align: right;">${p_rows[0]['direct_costs']:,.2f}</td>
        <td style="text-align: right;">${p_rows[1]['direct_costs']:,.2f}</td>
        <td style="text-align: right;">${p_rows[2]['direct_costs']:,.2f}</td>
    </tr>
    <tr style="font-weight: bold;">
        <td>Gross Operating Margin</td>
        <td style="text-align: right;">${p_rows[0]['gross_margin']:,.2f}</td>
        <td style="text-align: right;">${p_rows[1]['gross_margin']:,.2f}</td>
        <td style="text-align: right;">${p_rows[2]['gross_margin']:,.2f}</td>
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
        <td style="text-align: right;">{p_rows[0]['net_pct']:.1f}%</td>
        <td style="text-align: right;">{p_rows[1]['net_pct']:.1f}%</td>
        <td style="text-align: right;">{p_rows[2]['net_pct']:.1f}%</td>
    </tr>
</table>

<div class="callout">
    <strong>Underwriting Guarantee:</strong> The business is not dependent on speculative marketing. Summer tariffs are set by provincial hire agreements, and winter fuel mitigation is funded through Community Resiliency Investment (CRI) and BCTS tenders already audited in the local Babine operating area.
</div>

<h2>3. Proprietary Technical Leverage</h2>
<p>
    Unlike conventional local field contractors who rely on word-of-mouth and manual bid discovery, Sus Ke operates an <strong>automated algorithmic procurement monitor (Python/DuckDB)</strong> that scans the BC Data Catalogue and CanadaBuys weekly. This ensures immediate notification of closing tenders 10–14 days ahead of open regional awareness.
</p>

<div class="footer">
    Compiled via Sus Ke Business Analytics Engine | Prepared for Futurpreneur, BDC, and Indigenous Capital Corporation Review
</div>

</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\nSUCCESS! Generated Wildland Fire & Fuel Plan: '{OUTPUT_FILE}'")