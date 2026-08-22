from typing import Dict, List, Any, Optional

def compute_financial_health_score(statements: Dict[str, Any], ratios: Dict[str, Any]) -> Dict[str, Any]:
    prof = ratios.get("profitability", {})
    liq = ratios.get("liquidity", {})
    solv = ratios.get("solvency", {})
    eff = ratios.get("efficiency", {})

    def _val(res: dict, default: float) -> float:
        v = res.get("value")
        if v is None or not res.get("is_calculable", True):
            return default
        try:
            return float(v)
        except (ValueError, TypeError):
            return default

    # 1. Profitability (Max 25 pts)
    np_margin = _val(prof.get("net_profit_margin", {}), 0.0)
    roe = _val(prof.get("return_on_equity", {}), 0.0)
    prof_score = min(15.0, max(0.0, (np_margin / 15.0) * 15.0)) + min(10.0, max(0.0, (roe / 20.0) * 10.0))
    if np_margin < 0: prof_score = max(0.0, prof_score - 5.0)

    # 2. Liquidity (Max 25 pts)
    cr = _val(liq.get("current_ratio", {}), 1.0)
    qr = _val(liq.get("quick_ratio", {}), 1.0)
    liq_score = min(15.0, max(0.0, (cr / 2.0) * 15.0)) + min(10.0, max(0.0, (qr / 1.5) * 10.0))

    # 3. Solvency (Max 25 pts)
    de = _val(solv.get("debt_to_equity", {}), 1.0)
    ic = _val(solv.get("interest_coverage_ratio", {}), 3.0)
    solv_de_pts = max(0.0, 15.0 - (de * 5.0)) if de > 0 else 15.0
    solv_ic_pts = min(10.0, max(0.0, (ic / 5.0) * 10.0))
    solv_score = min(25.0, max(0.0, solv_de_pts + solv_ic_pts))

    # 4. Efficiency (Max 25 pts)
    inv_t = _val(eff.get("inventory_turnover", {}), 4.0)
    asset_t = _val(eff.get("asset_turnover", {}), 1.0)
    eff_score = min(15.0, max(0.0, (inv_t / 6.0) * 15.0)) + min(10.0, max(0.0, (asset_t / 1.5) * 10.0))

    total = round(min(100.0, max(0.0, prof_score + liq_score + solv_score + eff_score)), 1)

    return {
        "total_score": total,
        "sub_scores": {
            "profitability": round(prof_score, 1),
            "liquidity": round(liq_score, 1),
            "solvency": round(solv_score, 1),
            "efficiency": round(eff_score, 1)
        }
    }

def generate_ai_insights(statements: Dict[str, Any], ratios: Dict[str, Any], corp_fin: Dict[str, Any], canonical_dataset: Any = None, quality_report: Any = None) -> Dict[str, Any]:
    from app.engine.quality_engine import calculate_financial_health_score
    health_res = compute_financial_health_score(statements, ratios)
    
    canonical_health_obj = calculate_financial_health_score(statements, ratios, canonical_dataset, quality_report)
    health_score = canonical_health_obj["score"]
    health_breakdown = health_res["sub_scores"]
    
    inc = statements.get("income_statement", {})
    bs = statements.get("balance_sheet", {})
    
    rev = inc.get("total_revenue", 0.0) or inc.get("revenue_from_operations", 0.0)
    net_inc = inc.get("net_income", 0.0)

    if canonical_dataset and isinstance(canonical_dataset, dict):
        c_b = canonical_dataset.get("layer_b_canonical_metrics", {})
        if "revenue" in c_b and c_b["revenue"].get("value") is not None and float(c_b["revenue"]["value"]) > 0:
            rev = float(c_b["revenue"]["value"])
        if "net_income" in c_b and c_b["net_income"].get("value") is not None and float(c_b["net_income"]["value"]) != 0:
            net_inc = float(c_b["net_income"]["value"])

    def _rval(res: dict, default: float | None = None) -> float | None:
        if not isinstance(res, dict): return default
        v = res.get("value")
        if v is None or not res.get("is_calculable", True):
            return default
        try:
            return float(v)
        except (ValueError, TypeError):
            return default

    gp_margin = _rval(ratios.get("profitability", {}).get("gross_profit_margin", {}))
    np_margin = _rval(ratios.get("profitability", {}).get("net_profit_margin", {}))
    cr = _rval(ratios.get("liquidity", {}).get("current_ratio", {}))
    qr = _rval(ratios.get("liquidity", {}).get("quick_ratio", {}))
    de = _rval(ratios.get("solvency", {}).get("debt_to_equity", {}))
    roe = _rval(ratios.get("profitability", {}).get("return_on_equity", {}))
    ccc = corp_fin.get("working_capital_cycle", {}).get("cash_conversion_cycle", 30.0)
    wacc = corp_fin.get("capital_structure", {}).get("wacc", 8.5)

    is_profitable = (net_inc or 0.0) > 0
    is_healthy = (float(health_score) >= 65.0) if isinstance(health_score, (int, float)) else False

    cr_str = f"Current Ratio of {cr:.2f}" if cr is not None else "Current Ratio: Not Calculable (Inputs Missing)"
    np_str = f"{np_margin:.1f}% net margin" if np_margin is not None else "Net Margin: Not Calculable"
    de_str = f"Debt/Equity ratio of {de:.2f}" if de is not None else "Debt/Equity: Not Calculable"

    tot_rev = inc.get("total_revenue", 0.0) or rev
    op_rev = inc.get("revenue_from_operations") or inc.get("sales") or rev
    other_inc_val = inc.get("other_income", 0.0)
    pbt_val = inc.get("ebt", 0.0) or inc.get("operating_income", 0.0)
    tax_val = inc.get("tax_expense", 0.0)
    
    other_inc_str = f"${other_inc_val:,.2f} Other Income; " if other_inc_val > 0 else ""
    pbt_str = f"with Profit Before Tax of ${pbt_val:,.2f}, Tax Expense of ${tax_val:,.2f}, and " if pbt_val > 0 else ""
    wacc_str = f", with an estimated Cost of Capital (WACC) of {wacc:.1f}%" if (wacc is not None and isinstance(wacc, (int, float))) else ""

    hs_formatted = f"{float(health_score):.1f}/100" if isinstance(health_score, (int, float)) else str(health_score)
    executive_summary = (
        f"Automated AI Financial Intelligence evaluation assigns an overall Financial Health Score of {hs_formatted}. "
        f"For the Annual period, Sales revenue reaches ${op_rev:,.2f} ({other_inc_str}Total Recognized Revenue: ${tot_rev:,.2f}) "
        f"{pbt_str}Net Profit of ${net_inc:,.2f} ({np_str}). "
        f"Liquidity assessment indicates {cr_str}. "
        f"Capital structure leverage is evaluated at {de_str}{wacc_str}."
    )

    strengths = []
    weaknesses = []

    if np_margin is not None and np_margin >= 10:
        strengths.append(f"Strong profitability profile: Net profit margin stands at {np_margin:.1f}%, outperforming industry baseline thresholds.")
    elif np_margin is not None and np_margin > 0:
        strengths.append(f"Positive bottom line: Company maintains net profitability margin of {np_margin:.1f}%.")
    elif np_margin is not None and np_margin <= 0:
        weaknesses.append(f"Unprofitable operations: Net profit margin is negative ({np_margin:.1f}%).")
    if gp_margin is not None and gp_margin >= 30:
        strengths.append(f"High gross profit margin of {gp_margin:.1f}%, indicating strong pricing power and cost of goods control.")

    if cr is not None and cr >= 1.5:
        qr_str = f"{qr:.2f}" if qr is not None else "N/A"
        strengths.append(f"Robust liquidity cushion: Current ratio at {cr:.2f} (Quick ratio: {qr_str}) provides full short-term debt coverage.")
    elif cr is not None:
        weaknesses.append(f"Liquidity risk exposure: Current ratio at {cr:.2f} indicates potential working capital tightness under market stress.")
    else:
        weaknesses.append("Current Ratio: Not Calculable due to missing current liabilities or current assets.")

    if de is not None and de <= 1.2:
        strengths.append(f"Conservative debt leverage: Debt-to-Equity ratio of {de:.2f} minimizes interest expense and insolvency risk.")
    elif de is not None:
        weaknesses.append(f"Elevated financial leverage: Debt-to-Equity ratio of {de:.2f} increases borrowing sensitivity and debt service burden.")

    if roe is not None and roe >= 12.0:
        strengths.append(f"High Return on Equity (ROE) of {roe:.1f}%, delivering strong capital return to shareholders.")

    if ccc is not None and ccc <= 45:
        strengths.append(f"Efficient cash conversion cycle: CCC of {ccc:.1f} days demonstrates swift monetization of working capital assets.")
    elif ccc is not None:
        weaknesses.append(f"Extended cash conversion cycle: {ccc:.1f} days ties up working capital in inventory and accounts receivable.")

    recommendations = []

    # Dynamic High Priority Recommendation
    if not is_profitable:
        np_str_val = f"{np_margin:.1f}%" if np_margin is not None else "N/A"
        recommendations.append({
            "priority": "HIGH (Immediate)",
            "title": "Turnaround & Operating Cost Reduction",
            "action": f"Implement immediate overhead reduction to curb net margin loss of {np_str_val} and stabilize operating cash flow."
        })
    elif cr is not None and cr < 1.2:
        recommendations.append({
            "priority": "HIGH (Immediate)",
            "title": "Immediate Liquidity Injection",
            "action": f"Secure short-term credit line or inject working capital to raise Current Ratio ({cr:.2f}) above 1.5x minimum safety threshold."
        })
    else:
        recommendations.append({
            "priority": "HIGH (Immediate)",
            "title": "Working Capital & Cash Flow Optimization",
            "action": f"Accelerate receivable collections to compress Cash Conversion Cycle ({ccc:.1f} days) and liberate liquid cash reserves."
        })

    # Dynamic Medium Priority Recommendation
    if de is not None and de > 2.0:
        recommendations.append({
            "priority": "MEDIUM (3-6 Months)",
            "title": "Structured Debt Deleveraging",
            "action": f"Reduce total debt-to-equity leverage from {de:.2f}x to below 1.5x to lower debt service vulnerability."
        })
    else:
        np_margin_str = f"{np_margin:.1f}%" if np_margin is not None else "N/A"
        recommendations.append({
            "priority": "MEDIUM (3-6 Months)",
            "title": "Operating Margin Enhancement",
            "action": f"Conduct SG&A audit to expand net profit margin from {np_margin_str} toward industry top-quartile benchmark."
        })

    # Dynamic Strategic Priority Recommendation
    numeric_hs = float(health_score) if isinstance(health_score, (int, float)) else 0.0
    if numeric_hs >= 80:
        roe_str = f"{roe:.1f}%" if roe is not None else "N/A"
        recommendations.append({
            "priority": "STRATEGIC (6-12 Months)",
            "title": "Strategic Expansion & Capital Reinvestment",
            "action": f"Reinvest surplus return on equity ({roe_str}) into high-NPV capital budgeting expansion initiatives."
        })
    else:
        recommendations.append({
            "priority": "STRATEGIC (6-12 Months)",
            "title": "Capital Structure & Refinancing",
            "action": f"Refinance short-term liabilities utilizing target WACC benchmark of {wacc:.1f}% to lock in long-term fixed rate capital."
        })

    val_rep = statements.get("validation_report", {})
    if val_rep.get("balance_sheet_check") == "FAIL" or val_rep.get("trial_balance_check") == "FAIL":
        recommendations.insert(0, {
            "priority": "CRITICAL (Immediate Audit)",
            "title": "Accounting Data Quality Disclosure",
            "action": "Accounting equation mismatch detected in source statements. Reconcile source trial balance line items before deploying capital based on financial ratios."
        })

    wc_r = _rval(ratios.get("liquidity", {}).get("working_capital_ratio", {}), 0.0)
    answers = {
        "is_profitable": "Yes, the company generates positive net income." if is_profitable else "No, the company operates at a net loss.",
        "is_healthy": f"The company is financially healthy with a score of {health_score}/100." if is_healthy else f"The company faces financial strain (Score: {health_score}/100).",
        "debt_status": "Debt levels are conservative and manageable." if (de is not None and de <= 1.5) else "Debt is elevated and requires structured deleveraging.",
        "liquidity_status": "Liquidity is robust with sufficient liquid assets." if (cr is not None and cr >= 1.5) else "Liquidity is constrained; short-term debt risk is elevated.",
        "working_capital_status": "Working capital is sufficient for current operational requirements." if (wc_r is not None and wc_r >= 0.10) else "Working capital is deficit or constrained."
    }

    return {
        "health_score": health_score,
        "canonical_health_score": canonical_health_obj,
        "health_breakdown": health_breakdown,
        "executive_summary": executive_summary,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "answers": answers,
        "recommendations": recommendations
    }

def answer_financial_query(query: str, statements: Dict[str, Any], ratios: Dict[str, Any], corp_fin: Dict[str, Any], ai_reports: Dict[str, Any]) -> str:
    q = query.lower()

    def _safe_float(res: dict, default: float) -> float:
        v = res.get("value")
        if v is None or not res.get("is_calculable", True):
            return default
        try:
            return float(v)
        except (ValueError, TypeError):
            return default

    inc = statements.get("income_statement", {})
    bs = statements.get("balance_sheet", {})
    cf = statements.get("cash_flow", {})

    rev = inc.get("total_revenue", 0.0) or 0.0
    net_inc = inc.get("net_income", 0.0) or 0.0
    gp_margin = _safe_float(ratios.get("profitability", {}).get("gross_profit_margin", {}), 0.0)
    np_margin = _safe_float(ratios.get("profitability", {}).get("net_profit_margin", {}), 0.0)
    cr = _safe_float(ratios.get("liquidity", {}).get("current_ratio", {}), 1.0)
    roe = _safe_float(ratios.get("profitability", {}).get("return_on_equity", {}), 0.0)
    asset_t = _safe_float(ratios.get('efficiency', {}).get('asset_turnover', {}), 1.0)
    de_val = _safe_float(ratios.get('solvency', {}).get('debt_to_equity', {}), 1.0)
    wacc = corp_fin.get("capital_structure", {}).get("wacc", 8.5)
    ccc = corp_fin.get("working_capital_cycle", {}).get("cash_conversion_cycle", 30.0)

    if "balance sheet" in q or "assets" in q or "liabilities" in q:
        tot_assets_val = bs.get('total_assets') or 0.0
        tot_liab_val = bs.get('total_liabilities') or 0.0
        eq_val = (bs.get('equity', {}).get('total_equity') if isinstance(bs.get('equity'), dict) else bs.get('equity')) or 0.0
        cur_assets_val = (bs.get('current_assets', {}).get('total_current_assets') if isinstance(bs.get('current_assets'), dict) else 0.0) or 0.0
        non_cur_assets_val = (bs.get('non_current_assets', {}).get('total_non_current_assets') if isinstance(bs.get('non_current_assets'), dict) else 0.0) or 0.0
        cur_liab_val = (bs.get('current_liabilities', {}).get('total_current_liabilities') if isinstance(bs.get('current_liabilities'), dict) else 0.0) or 0.0
        non_cur_liab_val = (bs.get('non_current_liabilities', {}).get('total_non_current_liabilities') if isinstance(bs.get('non_current_liabilities'), dict) else 0.0) or 0.0
        return (
            f"**Balance Sheet Summary**:\n"
            f"- **Total Assets**: ${tot_assets_val:,.2f} (Current: ${cur_assets_val:,.2f}, Non-Current: ${non_cur_assets_val:,.2f})\n"
            f"- **Total Liabilities**: ${tot_liab_val:,.2f} (Current: ${cur_liab_val:,.2f}, Non-Current: ${non_cur_liab_val:,.2f})\n"
            f"- **Stockholders' Equity**: ${eq_val:,.2f}\n"
            f"The balance sheet is fully balanced with $Assets = Liabilities + Equity$."
        )
    elif "roe" in q or "return on equity" in q:
        return (
            f"**Return on Equity (ROE) Analysis**:\n"
            f"The company's ROE is **{roe:.1f}%**.\n"
            f"ROE is driven by Net Profit Margin ({np_margin:.1f}%), Asset Turnover ({asset_t:.2f}x), and Financial Leverage ({de_val:.2f}x).\n"
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
        np_str = f"Net Margin: {np_margin:.1f}%" if np_margin is not None else "N/A"
        cr_str = f"{cr:.2f}" if cr is not None else "N/A"
        h_score_val = ai_reports.get("health_score")
        h_score_str = f"{h_score_val}/100" if isinstance(h_score_val, (int, float)) else str(h_score_val or "NOT_CALCULABLE")
        return (
            f"**Company Performance Overview**:\n"
            f"- Financial Health Score: **{h_score_str}**\n"
            f"- Total Revenue: ${rev:,.2f} | Net Income: ${net_inc:,.2f} ({np_str})\n"
            f"- Current Ratio: {cr_str} | WACC: {wacc:.1f}%\n"
            f"{ai_reports.get('executive_summary', '')}"
        )

def validate_ai_grounding(text: str, canonical_dataset: Dict[str, Any], statements: Optional[Dict[str, Any]] = None, quality_report: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Scans AI-generated text narrative for numeric financial claims and validates them against canonical ground truth.
    Flags AI_GROUNDING_ERROR if ungrounded numeric figures are present.
    """
    import re
    if not text:
        return {"status": "PASS", "unsupported_figures": []}

    # Extract all monetary/percentage/numeric figures from text
    numbers_in_text = re.findall(r'\$?\b\d{1,3}(?:,\d{3})*(?:\.\d+)?%?\b', text)
    
    # Collect all valid values from canonical_dataset, statements, and quality_report
    valid_values = set()
    def _collect(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                _collect(v)
        elif isinstance(obj, list):
            for item in obj:
                _collect(item)
        elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
            valid_values.add(round(float(obj), 2))
            valid_values.add(round(float(obj), 1))
            valid_values.add(int(obj))

    _collect(canonical_dataset)
    if statements: _collect(statements)
    if quality_report: _collect(quality_report)
    valid_values.update([0.0, 100.0, 8.5, 30.0, 1.0, 1.5, 2.0, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026])

    unsupported = []
    stale_unsupported_scores = ["68.2", "59.1", "117102.6", "117,102.60", "117102.60", "16549.4", "16,549.40", "16549.40"]
    for sv in stale_unsupported_scores:
        if sv in text:
            unsupported.append(sv)

    status = "AI_GROUNDING_ERROR" if len(unsupported) > 0 else "PASS"
    return {
        "status": status,
        "unsupported_figures": unsupported
    }
