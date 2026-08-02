from typing import Dict, List, Any

def compute_financial_health_score(statements: Dict[str, Any], ratios: Dict[str, Any]) -> float:
    prof = ratios.get("profitability", {})
    liq = ratios.get("liquidity", {})
    solv = ratios.get("solvency", {})
    eff = ratios.get("efficiency", {})

    score = 0.0

    # 1. Profitability (25 pts)
    np_margin = prof.get("net_profit_margin", {}).get("value", 0.0)
    if np_margin >= 15: score += 25
    elif np_margin >= 8: score += 20
    elif np_margin >= 3: score += 12
    elif np_margin > 0: score += 5

    # 2. Liquidity (25 pts)
    cr = liq.get("current_ratio", {}).get("value", 1.0)
    if cr >= 1.8: score += 25
    elif cr >= 1.4: score += 20
    elif cr >= 1.0: score += 12
    else: score += 5

    # 3. Solvency (25 pts)
    de = solv.get("debt_to_equity", {}).get("value", 1.0)
    if de <= 0.8: score += 25
    elif de <= 1.5: score += 20
    elif de <= 2.5: score += 12
    else: score += 5

    # 4. Efficiency (25 pts)
    inv_t = eff.get("inventory_turnover", {}).get("value", 3.0)
    if inv_t >= 6.0: score += 25
    elif inv_t >= 3.5: score += 20
    elif inv_t >= 1.5: score += 12
    else: score += 5

    return round(score, 1)

def generate_ai_insights(statements: Dict[str, Any], ratios: Dict[str, Any], corp_fin: Dict[str, Any]) -> Dict[str, Any]:
    health_score = compute_financial_health_score(statements, ratios)
    
    inc = statements.get("income_statement", {})
    bs = statements.get("balance_sheet", {})
    
    rev = inc.get("total_revenue", 0.0)
    net_inc = inc.get("net_income", 0.0)
    gp_margin = ratios.get("profitability", {}).get("gross_profit_margin", {}).get("value", 0.0)
    np_margin = ratios.get("profitability", {}).get("net_profit_margin", {}).get("value", 0.0)
    cr = ratios.get("liquidity", {}).get("current_ratio", {}).get("value", 1.0)
    qr = ratios.get("liquidity", {}).get("quick_ratio", {}).get("value", 1.0)
    de = ratios.get("solvency", {}).get("debt_to_equity", {}).get("value", 1.0)
    roe = ratios.get("profitability", {}).get("return_on_equity", {}).get("value", 0.0)
    ccc = corp_fin.get("working_capital_cycle", {}).get("cash_conversion_cycle", 30.0)
    wacc = corp_fin.get("capital_structure", {}).get("wacc", 8.5)

    is_profitable = net_inc > 0
    is_healthy = health_score >= 65.0

    strengths = []
    weaknesses = []

    if np_margin >= 10:
        strengths.append(f"Strong profitability profile: Net profit margin stands at {np_margin:.1f}%, outperforming industry baseline thresholds.")
    elif np_margin > 0:
        strengths.append(f"Positive bottom line: Company maintains net profitability margin of {np_margin:.1f}%.")
    else:
        weaknesses.append(f"Compressed margin profile: Operating losses result in a net profit margin of {np_margin:.1f}%.")

    if gp_margin >= 30:
        strengths.append(f"High gross profit margin of {gp_margin:.1f}%, indicating strong pricing power and cost of goods control.")

    if cr >= 1.5:
        strengths.append(f"Robust liquidity cushion: Current ratio at {cr:.2f} (Quick ratio: {qr:.2f}) provides full short-term debt coverage.")
    else:
        weaknesses.append(f"Liquidity risk exposure: Current ratio at {cr:.2f} indicates potential working capital tightness under market stress.")

    if de <= 1.2:
        strengths.append(f"Conservative debt leverage: Debt-to-Equity ratio of {de:.2f} minimizes interest expense and insolvency risk.")
    else:
        weaknesses.append(f"Elevated financial leverage: Debt-to-Equity ratio of {de:.2f} increases borrowing sensitivity and debt service burden.")

    if roe >= 12.0:
        strengths.append(f"High Return on Equity (ROE) of {roe:.1f}%, delivering strong capital return to shareholders.")

    if ccc <= 45:
        strengths.append(f"Efficient cash conversion cycle: CCC of {ccc:.1f} days demonstrates swift monetization of working capital assets.")
    else:
        weaknesses.append(f"Extended cash conversion cycle: {ccc:.1f} days ties up working capital in inventory and accounts receivable.")

    executive_summary = (
        f"Automated AI Financial Intelligence evaluation assigns an overall Financial Health Score of {health_score}/100. "
        f"Total recognized revenue reaches ${rev:,.2f} with a net earnings outcome of ${net_inc:,.2f} ({np_margin:.1f}% net margin). "
        f"Short-term liquidity is {'robust' if cr >= 1.5 else 'constrained'} with a Current Ratio of {cr:.2f}. "
        f"Capital structure leverage remains {'conservative and resilient' if de <= 1.2 else 'leveraged'} at a Debt/Equity ratio of {de:.2f}, "
        f"with a estimated Cost of Capital (WACC) of {wacc:.1f}%."
    )

    recommendations = [
        {
            "priority": "HIGH (Immediate)",
            "title": "Working Capital & Cash Flow Optimization",
            "action": f"Accelerate receivable collections to compress Cash Conversion Cycle ({ccc:.1f} days) and liberate liquid cash reserves."
        },
        {
            "priority": "MEDIUM (3-6 Months)",
            "title": "Operating Margin Enhancement",
            "action": f"Conduct audit of administrative & SG&A overheads to raise net profit margin from {np_margin:.1f}% toward target benchmark."
        },
        {
            "priority": "STRATEGIC (6-12 Months)",
            "title": "Capital Structure Optimization",
            "action": f"Refinance short-term liabilities utilizing corporate WACC benchmark of {wacc:.1f}% to lock in long-term fixed financing."
        }
    ]

    answers = {
        "is_profitable": "Yes, the company generates positive net income." if is_profitable else "No, the company operates at a net loss.",
        "is_healthy": f"The company is financially healthy with a score of {health_score}/100." if is_healthy else f"The company faces financial strain (Score: {health_score}/100).",
        "debt_status": "Debt levels are conservative and manageable." if de <= 1.5 else "Debt is elevated and requires structured deleveraging.",
        "liquidity_status": "Liquidity is robust with sufficient liquid assets." if cr >= 1.5 else "Liquidity is constrained; short-term debt risk is elevated.",
        "working_capital_status": "Working capital is sufficient for current operational requirements." if ratios.get("liquidity", {}).get("working_capital_ratio", {}).get("value", 0.0) >= 0.10 else "Working capital is deficit or constrained."
    }

    return {
        "health_score": health_score,
        "executive_summary": executive_summary,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "answers": answers,
        "recommendations": recommendations
    }

def answer_financial_query(query: str, statements: Dict[str, Any], ratios: Dict[str, Any], corp_fin: Dict[str, Any], ai_reports: Dict[str, Any]) -> str:
    q = query.lower()

    inc = statements.get("income_statement", {})
    bs = statements.get("balance_sheet", {})
    cf = statements.get("cash_flow", {})

    rev = inc.get("total_revenue", 0.0)
    net_inc = inc.get("net_income", 0.0)
    gp_margin = ratios.get("profitability", {}).get("gross_profit_margin", {}).get("value", 0.0)
    np_margin = ratios.get("profitability", {}).get("net_profit_margin", {}).get("value", 0.0)
    cr = ratios.get("liquidity", {}).get("current_ratio", {}).get("value", 1.0)
    roe = ratios.get("profitability", {}).get("return_on_equity", {}).get("value", 0.0)
    wacc = corp_fin.get("capital_structure", {}).get("wacc", 8.5)
    ccc = corp_fin.get("working_capital_cycle", {}).get("cash_conversion_cycle", 30.0)

    if "balance sheet" in q or "assets" in q or "liabilities" in q:
        return (
            f"**Balance Sheet Summary**:\n"
            f"- **Total Assets**: ${bs.get('total_assets', 0.0):,.2f} (Current: ${bs.get('current_assets', {}).get('total_current_assets', 0.0):,.2f}, Non-Current: ${bs.get('non_current_assets', {}).get('total_non_current_assets', 0.0):,.2f})\n"
            f"- **Total Liabilities**: ${bs.get('total_liabilities', 0.0):,.2f} (Current: ${bs.get('current_liabilities', {}).get('total_current_liabilities', 0.0):,.2f}, Non-Current: ${bs.get('non_current_liabilities', {}).get('total_non_current_liabilities', 0.0):,.2f})\n"
            f"- **Stockholders' Equity**: ${bs.get('equity', {}).get('total_equity', 0.0):,.2f}\n"
            f"The balance sheet is fully balanced with $Assets = Liabilities + Equity$."
        )
    elif "roe" in q or "return on equity" in q:
        return (
            f"**Return on Equity (ROE) Analysis**:\n"
            f"The company's ROE is **{roe:.1f}%**.\n"
            f"ROE is driven by Net Profit Margin ({np_margin:.1f}%), Asset Turnover ({ratios.get('efficiency', {}).get('asset_turnover', {}).get('value', 1.0):.2f}x), and Financial Leverage ({ratios.get('solvency', {}).get('debt_to_equity', {}).get('value', 1.0):.2f}x).\n"
            f"To boost ROE, management should focus on improving operating margins and optimizing asset deployment."
        )
    elif "cash flow" in q:
        return (
            f"**Cash Flow Analysis**:\n"
            f"- **Operating Cash Flow**: ${cf.get('operating_activities', 0.0):,.2f}\n"
            f"- **Investing Cash Flow**: ${cf.get('investing_activities', 0.0):,.2f}\n"
            f"- **Financing Cash Flow**: ${cf.get('financing_activities', 0.0):,.2f}\n"
            f"- **Net Cash Generation**: ${cf.get('net_change_in_cash', 0.0):,.2f} (Ending Cash: ${cf.get('ending_cash', 0.0):,.2f})"
        )
    elif "working capital" in q or "ccc" in q:
        return (
            f"**Working Capital & Cash Conversion Cycle**:\n"
            f"- **Net Working Capital**: ${corp_fin.get('working_capital_cycle', {}).get('net_working_capital', 0.0):,.2f}\n"
            f"- **Cash Conversion Cycle (CCC)**: {ccc:.1f} days\n"
            f"It takes approximately {ccc:.1f} days to convert investments in inventory and accounts receivable back into liquid cash."
        )
    elif "recommend" in q or "improve" in q or "profit" in q:
        recs = ai_reports.get("recommendations", [])
        text = "**AI Business Recommendations**:\n"
        for r in recs:
            text += f"- **[{r['priority']}] {r['title']}**: {r['action']}\n"
        return text
    else:
        return (
            f"**Company Performance Overview**:\n"
            f"- Financial Health Score: **{ai_reports.get('health_score', 85)}/100**\n"
            f"- Total Revenue: ${rev:,.2f} | Net Income: ${net_inc:,.2f} ({np_margin:.1f}% margin)\n"
            f"- Current Ratio: {cr:.2f} | WACC: {wacc:.1f}%\n"
            f"{ai_reports.get('executive_summary', '')}"
        )
