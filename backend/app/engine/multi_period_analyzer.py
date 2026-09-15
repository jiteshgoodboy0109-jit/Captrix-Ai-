"""
Multi-Period & Multi-Year Financial Analysis Engine
Calculates Year-over-Year (YoY) Growth Rates, CAGR %, Multi-Year Margin Trends,
Balance Sheet & Capital Movements, Cash Flow Trajectory, Ratio Trends,
Significant Year-to-Year Shifts, and Directional Trend Classifications.
"""

from typing import Dict, Any, List, Optional
import math

def calculate_cagr(start_val: float | None, end_val: float | None, num_years: int) -> float | None:
    """Calculate Compound Annual Growth Rate (CAGR %) safely. Returns None if uncalculable or negative base."""
    if start_val is None or end_val is None or start_val <= 0 or end_val <= 0 or num_years <= 0:
        return None
    try:
        cagr = (math.pow(end_val / start_val, 1.0 / num_years) - 1.0) * 100.0
        return round(cagr, 2)
    except Exception:
        return None

def calculate_yoy(val1: float | None, val2: float | None) -> float | None:
    """Calculate Year-over-Year growth percentage safely."""
    if val1 is None or val2 is None or val1 == 0:
        return None
    return round(((val2 - val1) / abs(val1)) * 100.0, 2)

def classify_trend(metric_name: str, yoy: float | None) -> Dict[str, Any]:
    """Classify movement as IMPROVING, DETERIORATING, or STABLE with positive/negative tag."""
    if yoy is None:
        return {"status": "UNAVAILABLE", "is_positive": None, "label": "No Comparative Data"}
    
    # Metrics where an increase is generally positive
    higher_is_better = [
        "revenue", "gross_profit", "operating_profit", "ebit", "net_income", 
        "gross_margin", "operating_margin", "net_margin", "operating_cash_flow",
        "roe", "roa", "equity"
    ]
    # Metrics where a decrease is generally positive
    lower_is_better = [
        "cogs", "operating_expenses", "total_liabilities", "debt_to_equity",
        "debt_service", "interest_expense"
    ]

    metric_lower = metric_name.lower()
    is_higher_better = any(h in metric_lower for h in higher_is_better)
    is_lower_better = any(l in metric_lower for l in lower_is_better)

    if abs(yoy) < 1.0:
        return {"status": "STABLE", "is_positive": True, "label": f"Stable ({yoy:+.1f}%)"}

    if is_higher_better:
        if yoy > 0:
            return {"status": "IMPROVING", "is_positive": True, "label": f"Expanding ({yoy:+.1f}%)"}
        else:
            return {"status": "DETERIORATING", "is_positive": False, "label": f"Contracting ({yoy:+.1f}%)"}
    elif is_lower_better:
        if yoy < 0:
            return {"status": "IMPROVING", "is_positive": True, "label": f"Decreased ({yoy:+.1f}%)"}
        else:
            return {"status": "DETERIORATING", "is_positive": False, "label": f"Increased ({yoy:+.1f}%)"}
    else:
        # Neutral metrics (e.g. assets, current ratio within range)
        return {"status": "GROWTH" if yoy > 0 else "CONTRACTION", "is_positive": yoy > 0, "label": f"{yoy:+.1f}%"}

def generate_multi_period_analysis(statements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates comprehensive Multi-Year Comparative Financial Statements, YoY Growth Rates,
    CAGR %, Margin Evolution, Balance Sheet Movements, Cash Flow Trends, and Significant Anomaly Flags.
    """
    by_year = statements.get("by_year", {})
    years_sorted = sorted([y for y in by_year.keys() if y != "Current" and not y.startswith("FY")])
    if not years_sorted:
        years_sorted = sorted([y for y in by_year.keys() if y != "Current"])

    has_multi_year = len(years_sorted) >= 2

    if not by_year or not years_sorted:
        by_year = {"Current": statements}
        years_sorted = ["Current"]
        has_multi_year = False

    # Select up to 3 comparative periods
    if len(years_sorted) >= 3:
        y1, y2, y3 = years_sorted[-3], years_sorted[-2], years_sorted[-1]
    elif len(years_sorted) == 2:
        y1, y2, y3 = None, years_sorted[0], years_sorted[1]
    else:
        y1, y2, y3 = None, None, years_sorted[0]

    def _extract_yr(y: str | None) -> Dict[str, Any]:
        if y is None:
            return {}
        stmt = by_year.get(y, {})
        inc = stmt.get("income_statement", {})
        bs = stmt.get("balance_sheet", {})
        cf = stmt.get("cash_flow", {}) or stmt.get("cash_flow_statement", {})

        rev = inc.get("total_revenue", 0.0) or inc.get("revenue_from_operations", 0.0) or 0.0
        cogs = inc.get("cost_of_goods_sold")
        gp = inc.get("gross_profit")
        opex = inc.get("operating_expenses")
        ebit = inc.get("ebit") or inc.get("operating_income")
        pbt = inc.get("pbt") or inc.get("ebt")
        net = inc.get("net_income", 0.0) or 0.0

        assets = bs.get("total_assets")
        liab = bs.get("total_liabilities")
        eq_dict = bs.get("equity", {})
        equity = (eq_dict.get("total_equity") if isinstance(eq_dict, dict) else eq_dict) or 0.0

        curr_assets = bs.get("current_assets", {})
        ca = curr_assets.get("total_current_assets") if isinstance(curr_assets, dict) else None

        curr_liab = bs.get("current_liabilities", {})
        cl = curr_liab.get("total_current_liabilities") if isinstance(curr_liab, dict) else None

        nwc = (ca - cl) if (ca is not None and cl is not None) else None
        cr = round(ca / cl, 2) if (ca is not None and cl is not None and cl > 0) else None

        ocf = cf.get("operating_activities") or cf.get("operating_cash_flow")
        icf = cf.get("investing_activities") or cf.get("investing_cash_flow")
        fcf = cf.get("financing_activities") or cf.get("financing_cash_flow")
        net_cf = cf.get("net_change_in_cash") or cf.get("net_cash_flow")

        de = round(float(liab) / float(equity), 2) if (liab is not None and equity and float(equity) > 0) else None
        roa = round((float(net) / float(assets)) * 100.0, 2) if (assets and float(assets) > 0) else None
        roe = round((float(net) / float(equity)) * 100.0, 2) if (equity and float(equity) > 0) else None

        return {
            "period": y,
            "revenue": float(rev),
            "cogs": float(cogs) if cogs is not None else None,
            "gross_profit": float(gp) if gp is not None else None,
            "operating_expenses": float(opex) if opex is not None else None,
            "ebit": float(ebit) if ebit is not None else None,
            "pbt": float(pbt) if pbt is not None else None,
            "net_income": float(net),
            "total_assets": float(assets) if assets is not None else None,
            "total_liabilities": float(liab) if liab is not None else None,
            "total_equity": float(equity) if equity is not None else None,
            "current_assets": float(ca) if ca is not None else None,
            "current_liabilities": float(cl) if cl is not None else None,
            "net_working_capital": float(nwc) if nwc is not None else None,
            "current_ratio": cr,
            "debt_to_equity": de,
            "roa": roa,
            "roe": roe,
            "operating_cash_flow": float(ocf) if ocf is not None else None,
            "investing_cash_flow": float(icf) if icf is not None else None,
            "financing_cash_flow": float(fcf) if fcf is not None else None,
            "net_cash_flow": float(net_cf) if net_cf is not None else None,
        }

    d1 = _extract_yr(y1)
    d2 = _extract_yr(y2)
    d3 = _extract_yr(y3)

    # 1. Year-over-Year Growth & Directional Movements
    yoy_metrics = {}
    prior_d = d2 if y2 is not None else None
    latest_d = d3

    keys_to_track = [
        ("revenue", "Revenue from Operations"),
        ("cogs", "Cost of Goods Sold"),
        ("gross_profit", "Gross Profit"),
        ("operating_expenses", "Operating Expenses"),
        ("ebit", "Operating Profit (EBIT)"),
        ("pbt", "Profit Before Tax (PBT)"),
        ("net_income", "Net Income / Profit"),
        ("total_assets", "Total Assets"),
        ("total_liabilities", "Total Liabilities"),
        ("total_equity", "Total Shareholders' Equity"),
        ("net_working_capital", "Net Working Capital"),
        ("operating_cash_flow", "Operating Cash Flow"),
        ("current_ratio", "Current Ratio"),
        ("debt_to_equity", "Debt-to-Equity Ratio"),
        ("roe", "Return on Equity (ROE)")
    ]

    significant_changes = []
    
    if prior_d:
        for k, label in keys_to_track:
            v_prior = prior_d.get(k)
            v_latest = latest_d.get(k)
            growth = calculate_yoy(v_prior, v_latest)
            classification = classify_trend(k, growth)
            yoy_metrics[f"{k}_yoy"] = growth
            yoy_metrics[f"{k}_trend"] = classification

            # Identify significant changes (> 25% or material shift)
            if growth is not None and abs(growth) >= 25.0:
                severity = "HIGH" if abs(growth) >= 50.0 else "MEDIUM"
                direction = "increased" if growth > 0 else "declined"
                significant_changes.append({
                    "metric": label,
                    "prior_value": v_prior,
                    "latest_value": v_latest,
                    "change_pct": growth,
                    "severity": severity,
                    "classification": classification["status"],
                    "description": f"{label} {direction} by {abs(growth):.1f}% from {v_prior:,.2f} to {v_latest:,.2f} between FY{prior_d['period']} and FY{latest_d['period']}."
                })
    else:
        for k, label in keys_to_track:
            yoy_metrics[f"{k}_yoy"] = None
            yoy_metrics[f"{k}_trend"] = {"status": "SINGLE_PERIOD", "is_positive": None, "label": "Single Period Available"}

    # 2. Multi-Period CAGR Metrics
    num_years = 2 if y1 is not None else 1
    rev_cagr = calculate_cagr(d1.get("revenue"), d3.get("revenue"), num_years) if y1 is not None else None
    net_cagr = calculate_cagr(d1.get("net_income"), d3.get("net_income"), num_years) if y1 is not None else None
    gp_cagr = calculate_cagr(d1.get("gross_profit"), d3.get("gross_profit"), num_years) if y1 is not None else None
    assets_cagr = calculate_cagr(d1.get("total_assets"), d3.get("total_assets"), num_years) if y1 is not None else None

    # 3. Margin & Ratio Trend History
    margin_trends = []
    ratio_trends = []
    periods_active = [d for d in [d1, d2, d3] if d]

    for d in periods_active:
        p = d["period"]
        r = d.get("revenue") or 0.0
        gp = d.get("gross_profit")
        ebit = d.get("ebit")
        net = d.get("net_income") or 0.0
        
        gm = round((gp / r) * 100.0, 2) if (r > 0 and gp is not None) else None
        om = round((ebit / r) * 100.0, 2) if (r > 0 and ebit is not None) else None
        nm = round((net / r) * 100.0, 2) if r > 0 else None

        margin_trends.append({
            "period": f"FY{p}" if str(p) != "Current" else "Current",
            "gross_margin": gm,
            "operating_margin": om,
            "net_margin": nm
        })

        ratio_trends.append({
            "period": f"FY{p}" if str(p) != "Current" else "Current",
            "current_ratio": d.get("current_ratio"),
            "debt_to_equity": d.get("debt_to_equity"),
            "return_on_equity": d.get("roe"),
            "return_on_assets": d.get("roa")
        })

    # 4. Comparative Income Statement & Balance Sheet Tables
    def _tbl_row(label: str, k: str) -> Dict[str, Any]:
        row: Dict[str, Any] = {"metric": label}
        if d1: row[f"fy_{d1['period']}"] = d1.get(k)
        if d2: row[f"fy_{d2['period']}"] = d2.get(k)
        if d3: row[f"fy_{d3['period']}"] = d3.get(k)
        row["yoy_growth_pct"] = yoy_metrics.get(f"{k}_yoy")
        row["trend_status"] = yoy_metrics.get(f"{k}_trend", {}).get("status")
        return row

    comparative_income_statement = [
        _tbl_row("Revenue from Operations", "revenue"),
        _tbl_row("Cost of Goods Sold (COGS)", "cogs"),
        _tbl_row("Gross Profit", "gross_profit"),
        _tbl_row("Operating Expenses", "operating_expenses"),
        _tbl_row("Operating Profit (EBIT)", "ebit"),
        _tbl_row("Profit Before Tax (PBT)", "pbt"),
        _tbl_row("Net Income / Profit", "net_income")
    ]

    comparative_balance_sheet = [
        _tbl_row("Total Assets", "total_assets"),
        _tbl_row("Current Assets", "current_assets"),
        _tbl_row("Current Liabilities", "current_liabilities"),
        _tbl_row("Net Working Capital", "net_working_capital"),
        _tbl_row("Total Liabilities", "total_liabilities"),
        _tbl_row("Shareholders' Equity", "total_equity")
    ]

    comparative_cash_flow = [
        _tbl_row("Cash Flow from Operating Activities", "operating_cash_flow"),
        _tbl_row("Cash Flow from Investing Activities", "investing_cash_flow"),
        _tbl_row("Cash Flow from Financing Activities", "financing_cash_flow"),
        _tbl_row("Net Change in Cash & Cash Equivalents", "net_cash_flow")
    ]

    # AI Trajectory Commentary
    if has_multi_year and prior_d:
        rev_g = yoy_metrics.get("revenue_yoy") or 0.0
        net_g = yoy_metrics.get("net_income_yoy") or 0.0
        cr_latest = latest_d.get("current_ratio")
        cr_str = f"Current Ratio of {cr_latest:.2f}x" if cr_latest is not None else "Current Ratio unavailable"
        cagr_text = f" and 3-year revenue CAGR of {rev_cagr:.1f}%" if rev_cagr is not None else ""
        
        ai_trajectory = (
            f"Multi-year comparative analysis between FY{prior_d['period']} and FY{latest_d['period']} reveals "
            f"YoY revenue growth of {rev_g:+.1f}%{cagr_text} alongside YoY net income movement of {net_g:+.1f}%. "
            f"The company maintains a latest {cr_str}. A total of {len(significant_changes)} significant year-over-year shifts "
            f"were identified across primary financial line items."
        )
    else:
        ai_trajectory = (
            f"Single-period financial statements parsed for FY{latest_d.get('period', 'Current')}. "
            f"Multi-year comparative historical schedules were not reported in the source workbook. "
            f"All single-period metrics are evaluated strictly on available ending balances."
        )

    return {
        "is_multi_year": has_multi_year,
        "periods_analyzed": [d["period"] for d in periods_active],
        "latest_period": latest_d.get("period", "Current"),
        "prior_period": prior_d.get("period") if prior_d else None,
        "cagr_metrics": {
            "revenue_cagr": rev_cagr,
            "net_income_cagr": net_cagr,
            "gross_profit_cagr": gp_cagr,
            "assets_cagr": assets_cagr
        },
        "yoy_growth": yoy_metrics,
        "significant_changes": significant_changes,
        "comparative_income_statement": comparative_income_statement,
        "comparative_balance_sheet": comparative_balance_sheet,
        "comparative_cash_flow": comparative_cash_flow,
        "margin_trends": margin_trends,
        "ratio_trends": ratio_trends,
        "ai_trajectory": ai_trajectory
    }
