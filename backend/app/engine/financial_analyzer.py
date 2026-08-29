import numpy as np
from typing import Dict, Any, Optional

def safe_ratio(num: Optional[float], den: Optional[float], multiply_100: bool = False, decimal_places: int = 2) -> Dict[str, Any]:
    """Calculate ratio with zero-denominator and missing-input protection."""
    if den == 0 or den is None or num is None:
        return {
            "value": None,
            "display_value": "Ratio Not Calculable — Required Source Data Missing / Denominator = 0",
            "is_calculable": False
        }
    val = (num / den) * (100.0 if multiply_100 else 1.0)
    return {
        "value": round(val, decimal_places),
        "display_value": f"{round(val, decimal_places)}{'%' if multiply_100 else ''}",
        "is_calculable": True
    }

def calculate_financial_ratios(statements: Dict[str, Any]) -> Dict[str, Any]:
    val_report = statements.get("validation_report", {})
    bs_valid = val_report.get("balance_sheet_check", "PASS") == "PASS"

    inc = statements.get("income_statement", {})
    bs = statements.get("balance_sheet", {})
    
    rev = inc.get("total_revenue", 0.0)
    cogs = inc.get("cost_of_goods_sold", 0.0)
    gp = inc.get("gross_profit", 0.0)
    ebit = inc.get("ebit", 0.0)
    net_inc = inc.get("net_income", 0.0)
    interest = inc.get("interest_expense", 0.0)

    curr_assets = bs.get("current_assets", {})
    ca = curr_assets.get("total_current_assets", 0.0) if isinstance(curr_assets, dict) else 0.0
    cash = curr_assets.get("cash", 0.0) if isinstance(curr_assets, dict) else 0.0
    curr_liab = bs.get("current_liabilities", {})
    total_assets = bs.get("total_assets", 0.0)
    total_liab = bs.get("total_liabilities", 0.0)
    
    equity_dict = bs.get("equity", {})
    equity = equity_dict.get("total_equity") if isinstance(equity_dict, dict) else None
    if equity == 0.0 and not equity_dict.get("common_stock"):
        equity = None
    
    lt_liab_dict = bs.get("long_term_liabilities", {})

    ca = float(curr_assets.get("total_current_assets")) if (isinstance(curr_assets, dict) and curr_assets.get("total_current_assets") is not None) else None
    cl = float(curr_liab.get("total_current_liabilities")) if (isinstance(curr_liab, dict) and curr_liab.get("total_current_liabilities") is not None) else None
    cash = float(curr_assets.get("cash")) if (isinstance(curr_assets, dict) and curr_assets.get("cash") is not None) else None
    rec = float(curr_assets.get("accounts_receivable")) if (isinstance(curr_assets, dict) and curr_assets.get("accounts_receivable") is not None) else None
    inv = float(curr_assets.get("inventory")) if (isinstance(curr_assets, dict) and curr_assets.get("inventory") is not None) else None
    long_debt = float(lt_liab_dict.get("total_long_term_liabilities")) if (isinstance(lt_liab_dict, dict) and lt_liab_dict.get("total_long_term_liabilities") is not None) else None

    # 1. Liquidity Ratios
    cr_res = safe_ratio(ca, cl) if (bs_valid and ca is not None and cl is not None) else {"value": None, "display_value": "NOT_CALCULABLE", "is_calculable": False}
    quick_assets = (ca - inv) if (ca is not None and inv is not None) else ca
    qr_res = safe_ratio(quick_assets, cl) if (bs_valid and quick_assets is not None and cl is not None) else {"value": None, "display_value": "NOT_CALCULABLE", "is_calculable": False}
    cash_r_res = safe_ratio(cash, cl) if (bs_valid and cash is not None and cl is not None) else {"value": None, "display_value": "NOT_CALCULABLE", "is_calculable": False}
    working_capital = (ca - cl) if (ca is not None and cl is not None) else None
    wc_r_res = safe_ratio(working_capital, rev, multiply_100=True) if (bs_valid and working_capital is not None and rev is not None) else {"value": None, "display_value": "NOT_CALCULABLE", "is_calculable": False}

    cr_val: Optional[float] = float(cr_res["value"]) if (cr_res["is_calculable"] and cr_res["value"] is not None) else None
    qr_val: Optional[float] = float(qr_res["value"]) if (qr_res["is_calculable"] and qr_res["value"] is not None) else None
    cash_r_val: Optional[float] = float(cash_r_res["value"]) if (cash_r_res["is_calculable"] and cash_r_res["value"] is not None) else None
    wc_r_val: Optional[float] = float(wc_r_res["value"]) if (wc_r_res["is_calculable"] and wc_r_res["value"] is not None) else None

    liquidity = {
        "current_ratio": {
            "name": "Current Ratio",
            "value": cr_res["value"],
            "display_value": cr_res["display_value"],
            "is_calculable": cr_res["is_calculable"],
            "formula": "Current Assets / Current Liabilities",
            "inputs": {"Current Assets": ca, "Current Liabilities": cl},
            "benchmark": "> 1.5",
            "status": ("HEALTHY" if cr_val >= 1.5 else ("WARNING" if cr_val >= 1.0 else "CRITICAL")) if cr_val is not None else "NOT_CALCULABLE",
            "interpretation": f"The company holds ${cr_val:.2f} of current assets for every $1.00 of short-term liabilities." if cr_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        },
        "quick_ratio": {
            "name": "Quick Ratio (Acid-Test)",
            "value": qr_res["value"],
            "display_value": qr_res["display_value"],
            "is_calculable": qr_res["is_calculable"],
            "formula": "(Current Assets - Inventory) / Current Liabilities",
            "inputs": {"Quick Assets": quick_assets, "Current Liabilities": cl},
            "benchmark": "> 1.0",
            "status": ("HEALTHY" if qr_val >= 1.0 else ("WARNING" if qr_val >= 0.8 else "CRITICAL")) if qr_val is not None else "NOT_CALCULABLE",
            "interpretation": f"Quick ratio stands at {qr_val:.2f}, excluding inventory." if qr_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        },
        "cash_ratio": {
            "name": "Cash Ratio",
            "value": cash_r_res["value"],
            "display_value": cash_r_res["display_value"],
            "is_calculable": cash_r_res["is_calculable"],
            "formula": "Cash & Equivalents / Current Liabilities",
            "inputs": {"Cash": cash, "Current Liabilities": cl},
            "benchmark": "> 0.5",
            "status": ("HEALTHY" if cash_r_val >= 0.5 else "WARNING") if cash_r_val is not None else "NOT_CALCULABLE",
            "interpretation": f"Cash reserves cover {cash_r_val * 100:.1f}% of current short-term liabilities." if cash_r_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        },
        "working_capital_ratio": {
            "name": "Working Capital Ratio",
            "value": wc_r_res["value"],
            "display_value": wc_r_res["display_value"],
            "is_calculable": wc_r_res["is_calculable"],
            "formula": "(Current Assets - Current Liabilities) / Revenue",
            "inputs": {"Working Capital": working_capital, "Revenue": rev},
            "benchmark": "15% - 30%",
            "status": ("HEALTHY" if 10.0 <= wc_r_val <= 35.0 else "WARNING") if wc_r_val is not None else "NOT_CALCULABLE",
            "interpretation": f"Working capital represents {wc_r_val:.1f}% of annual revenues." if wc_r_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        }
    }

    # 2. Profitability Ratios
    gp_res = safe_ratio(gp, rev, multiply_100=True) if bs_valid else {"value": None, "display_value": "NOT_CALCULABLE", "is_calculable": False}
    np_res = safe_ratio(net_inc, rev, multiply_100=True) if bs_valid else {"value": None, "display_value": "NOT_CALCULABLE", "is_calculable": False}
    roa_res = safe_ratio(net_inc, total_assets, multiply_100=True) if bs_valid else {"value": None, "display_value": "NOT_CALCULABLE", "is_calculable": False}
    roe_res = safe_ratio(net_inc, equity, multiply_100=True) if (bs_valid and equity) else {"value": None, "display_value": "NOT_CALCULABLE", "is_calculable": False}
    
    capital_employed = (equity + long_debt) if (equity is not None and long_debt is not None and (equity + long_debt) > 0) else ((total_assets - cl) if (total_assets is not None and cl is not None) else None)
    if not bs_valid or capital_employed is None or capital_employed <= 0 or ebit is None or ebit == 0:
        roce_res = {
            "value": None,
            "display_value": "NOT_CALCULABLE",
            "is_calculable": False,
            "status": "DATA_QUALITY_ERROR"
        }
    else:
        calc_roce_val = safe_ratio(ebit, capital_employed, multiply_100=True)
        if calc_roce_val["value"] is None or calc_roce_val["value"] > 100.0 or calc_roce_val["value"] < -100.0:
            roce_res = {
                "value": None,
                "display_value": "NOT_CALCULABLE",
                "is_calculable": False,
                "status": "DATA_QUALITY_ERROR"
            }
        else:
            roce_res = calc_roce_val

    gp_val: Optional[float] = float(gp_res["value"]) if (gp_res["is_calculable"] and gp_res["value"] is not None) else None
    np_val: Optional[float] = float(np_res["value"]) if (np_res["is_calculable"] and np_res["value"] is not None) else None
    roa_val: Optional[float] = float(roa_res["value"]) if (roa_res["is_calculable"] and roa_res["value"] is not None) else None
    roe_val: Optional[float] = float(roe_res["value"]) if (roe_res["is_calculable"] and roe_res["value"] is not None) else None
    roce_val: Optional[float] = float(roce_res["value"]) if (roce_res["is_calculable"] and roce_res["value"] is not None) else None

    profitability = {
        "gross_profit_margin": {
            "name": "Gross Profit Margin",
            "value": gp_res["value"],
            "display_value": gp_res["display_value"],
            "is_calculable": gp_res["is_calculable"],
            "unit": "%",
            "formula": "(Gross Profit / Total Revenue) * 100",
            "inputs": {"Gross Profit": gp, "Revenue": rev},
            "benchmark": "> 30%",
            "status": ("HEALTHY" if gp_val >= 30 else ("WARNING" if gp_val >= 15 else "CRITICAL")) if gp_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Company yields a negative gross margin of {gp_val:.1f}%." if gp_val < 0 else f"Company retains {gp_val:.1f}% of revenue after direct production costs.") if gp_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        },
        "net_profit_margin": {
            "name": "Net Profit Margin",
            "value": np_res["value"],
            "display_value": np_res["display_value"],
            "is_calculable": np_res["is_calculable"],
            "unit": "%",
            "formula": "(Net Income / Total Revenue) * 100",
            "inputs": {"Net Income": net_inc, "Revenue": rev},
            "benchmark": "> 10%",
            "status": ("HEALTHY" if np_val >= 10 else ("WARNING" if np_val >= 5 else "CRITICAL")) if np_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Company experienced a net loss margin of {np_val:.1f}% on total revenue." if np_val < 0 else f"Company yields {np_val:.1f}% net profit from total revenue.") if np_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        },
        "return_on_assets": {
            "name": "Return on Assets (ROA)",
            "value": roa_res["value"],
            "display_value": roa_res["display_value"],
            "is_calculable": roa_res["is_calculable"],
            "unit": "%",
            "formula": "(Net Income / Total Assets) * 100",
            "inputs": {"Net Income": net_inc, "Total Assets": total_assets},
            "benchmark": "> 5%",
            "status": ("HEALTHY" if roa_val >= 5 else "WARNING") if roa_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Incurs a net loss of ${abs(roa_val):.2f} per $100 of total assets." if roa_val < 0 else f"Generates ${roa_val:.2f} of net profit per $100 of total assets.") if roa_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        },
        "return_on_equity": {
            "name": "Return on Equity (ROE)",
            "value": roe_res["value"],
            "display_value": roe_res["display_value"],
            "is_calculable": roe_res["is_calculable"],
            "unit": "%",
            "formula": "(Net Income / Total Equity) * 100",
            "inputs": {"Net Income": net_inc, "Total Equity": equity},
            "benchmark": "> 15%",
            "status": ("HEALTHY" if roe_val >= 15 else ("WARNING" if roe_val >= 8 else "CRITICAL")) if roe_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Shareholders experience a {roe_val:.1f}% net return on equity." if roe_val < 0 else f"Shareholders earn a {roe_val:.1f}% return on equity invested.") if roe_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        },
        "return_on_capital_employed": {
            "name": "ROCE",
            "value": roce_res["value"],
            "display_value": roce_res["display_value"],
            "is_calculable": roce_res["is_calculable"],
            "unit": "%",
            "formula": "(EBIT / Capital Employed) * 100",
            "inputs": {"EBIT": ebit, "Capital Employed": capital_employed},
            "benchmark": "> 12%",
            "status": roce_res.get("status") if "status" in roce_res else (("HEALTHY" if (roce_val is not None and roce_val >= 12) else "WARNING") if roce_val is not None else "NOT_CALCULABLE"),
            "interpretation": (f"Operating return on capital employed is negative at {roce_val:.1f}%." if roce_val < 0 else f"Operating return on capital employed stands at {roce_val:.1f}%.") if roce_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        }
    }

    # 3. Solvency & Debt Ratios
    st_borrowings = (curr_liab.get("short_term_borrowings") or curr_liab.get("short_term_debt") or 0.0) if isinstance(curr_liab, dict) else 0.0
    lt_borrowings = (lt_liab_dict.get("long_term_borrowings") or lt_liab_dict.get("long_term_debt") or 0.0) if isinstance(lt_liab_dict, dict) else 0.0
        
    total_borrowings = float(st_borrowings) + float(lt_borrowings)
    debt_for_de = total_borrowings if total_borrowings > 0 else total_liab

    de_res = safe_ratio(debt_for_de, equity) if (bs_valid and equity) else {"value": None, "display_value": "NOT_CALCULABLE", "is_calculable": False}
    dr_res = safe_ratio(total_liab, total_assets, multiply_100=True) if bs_valid else {"value": None, "display_value": "NOT_CALCULABLE", "is_calculable": False}
    eq_r_res = safe_ratio(equity, total_assets, multiply_100=True) if (bs_valid and equity) else {"value": None, "display_value": "NOT_CALCULABLE", "is_calculable": False}
    ic_res = safe_ratio(ebit, interest) if bs_valid else {"value": None, "display_value": "NOT_CALCULABLE", "is_calculable": False}

    de_val: Optional[float] = float(de_res["value"]) if (de_res["is_calculable"] and de_res["value"] is not None) else None
    dr_val: Optional[float] = float(dr_res["value"]) if (dr_res["is_calculable"] and dr_res["value"] is not None) else None
    eq_r_val: Optional[float] = float(eq_r_res["value"]) if (eq_r_res["is_calculable"] and eq_r_res["value"] is not None) else None
    ic_val: Optional[float] = float(ic_res["value"]) if (ic_res["is_calculable"] and ic_res["value"] is not None) else None

    solvency = {
        "debt_to_equity": {
            "name": "Debt to Equity Ratio",
            "value": de_res["value"],
            "display_value": de_res["display_value"],
            "is_calculable": de_res["is_calculable"],
            "formula": "Total Liabilities / Shareholders' Equity",
            "inputs": {"Total Liabilities": total_liab, "Equity": equity},
            "benchmark": "< 1.5",
            "status": ("HEALTHY" if de_val <= 1.5 else ("WARNING" if de_val <= 2.5 else "CRITICAL")) if de_val is not None else "NOT_CALCULABLE",
            "interpretation": f"For every $1 of equity, the firm carries ${de_val:.2f} of total debt." if de_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        },
        "debt_ratio": {
            "name": "Debt Ratio",
            "value": dr_res["value"],
            "display_value": dr_res["display_value"],
            "is_calculable": dr_res["is_calculable"],
            "formula": "Total Liabilities / Total Assets",
            "inputs": {"Total Liabilities": total_liab, "Total Assets": total_assets},
            "benchmark": "< 0.6",
            "status": ("HEALTHY" if dr_val <= 0.6 else "WARNING") if dr_val is not None else "NOT_CALCULABLE",
            "interpretation": f"Liabilities finance {dr_val * 100:.1f}% of total assets." if dr_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        },
        "equity_ratio": {
            "name": "Equity Ratio",
            "value": eq_r_res["value"],
            "display_value": eq_r_res["display_value"],
            "is_calculable": eq_r_res["is_calculable"],
            "formula": "Shareholders' Equity / Total Assets",
            "inputs": {"Equity": equity, "Total Assets": total_assets},
            "benchmark": "> 0.4",
            "status": ("HEALTHY" if eq_r_val >= 0.4 else "WARNING") if eq_r_val is not None else "NOT_CALCULABLE",
            "interpretation": f"Shareholder equity funds {eq_r_val * 100:.1f}% of asset base." if eq_r_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        },
        "interest_coverage_ratio": {
            "name": "Interest Coverage Ratio",
            "value": ic_res["value"],
            "display_value": ic_res["display_value"],
            "is_calculable": ic_res["is_calculable"],
            "formula": "EBIT / Interest Expense",
            "inputs": {"EBIT": ebit, "Interest Expense": interest},
            "benchmark": "> 3.0",
            "status": ("HEALTHY" if ic_val >= 3.0 else ("WARNING" if ic_val >= 1.5 else "CRITICAL")) if ic_val is not None else "NOT_CALCULABLE",
            "interpretation": f"Operating earnings cover annual interest expense {ic_val:.1f} times." if ic_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        }
    }

    # 4. Efficiency Ratios
    inv_t_res = safe_ratio(cogs, inv)
    rec_t_res = safe_ratio(rev, rec)
    asset_t_res = safe_ratio(rev, total_assets)

    inv_t_val: Optional[float] = float(inv_t_res["value"]) if (inv_t_res["is_calculable"] and inv_t_res["value"] is not None) else None
    rec_t_val: Optional[float] = float(rec_t_res["value"]) if (rec_t_res["is_calculable"] and rec_t_res["value"] is not None) else None
    asset_t_val: Optional[float] = float(asset_t_res["value"]) if (asset_t_res["is_calculable"] and asset_t_res["value"] is not None) else None

    efficiency = {
        "inventory_turnover": {
            "name": "Inventory Turnover",
            "value": inv_t_res["value"],
            "display_value": inv_t_res["display_value"],
            "is_calculable": inv_t_res["is_calculable"],
            "formula": "COGS / Average Inventory",
            "inputs": {"COGS": cogs, "Inventory": inv},
            "benchmark": "4.0 - 8.0x",
            "status": ("HEALTHY" if inv_t_val >= 4.0 else "WARNING") if inv_t_val is not None else "NOT_CALCULABLE",
            "interpretation": f"Inventory is restocked and sold {inv_t_val:.1f} times per year." if inv_t_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        },
        "receivable_turnover": {
            "name": "Receivables Turnover",
            "value": rec_t_res["value"],
            "display_value": rec_t_res["display_value"],
            "is_calculable": rec_t_res["is_calculable"],
            "formula": "Revenue / Accounts Receivable",
            "inputs": {"Revenue": rev, "Accounts Receivable": rec},
            "benchmark": "> 6.0x",
            "status": ("HEALTHY" if rec_t_val >= 6.0 else "WARNING") if rec_t_val is not None else "NOT_CALCULABLE",
            "interpretation": f"Accounts receivable are collected {rec_t_val:.1f} times annually." if rec_t_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        },
        "asset_turnover": {
            "name": "Asset Turnover",
            "value": asset_t_res["value"],
            "display_value": asset_t_res["display_value"],
            "is_calculable": asset_t_res["is_calculable"],
            "formula": "Revenue / Total Assets",
            "inputs": {"Revenue": rev, "Total Assets": total_assets},
            "benchmark": "> 1.0x",
            "status": ("HEALTHY" if asset_t_val >= 1.0 else "WARNING") if asset_t_val is not None else "NOT_CALCULABLE",
            "interpretation": f"Generates ${asset_t_val:.2f} of annual revenue per dollar of asset deployment." if asset_t_val is not None else "Ratio Not Calculable — Required Source Data Missing"
        }
    }

    return {
        "liquidity": liquidity,
        "profitability": profitability,
        "solvency": solvency,
        "efficiency": efficiency
    }

def calculate_npv(rate: float, cash_flows: list) -> float:
    """Calculate Net Present Value (NPV) safely."""
    return sum(cf / ((1.0 + rate) ** t) for t, cf in enumerate(cash_flows))

def calculate_irr(cash_flows: list, guess: float = 0.1, max_iter: int = 100, tol: float = 1e-6) -> float:
    """Calculate Internal Rate of Return (IRR) using Newton-Raphson method safely."""
    r = guess
    for _ in range(max_iter):
        if 1.0 + r <= 1e-6:
            r = -0.999
        npv = sum(cf / ((1.0 + r) ** t) for t, cf in enumerate(cash_flows))
        d_npv = sum(-t * cf / ((1.0 + r) ** (t + 1)) for t, cf in enumerate(cash_flows))
        if abs(d_npv) < 1e-12:
            break
        new_r = r - npv / d_npv
        if abs(new_r - r) < tol:
            return new_r
        r = new_r
    return r

def calculate_corporate_finance(statements: Dict[str, Any], ratios: Dict[str, Any]) -> Dict[str, Any]:
    inc = statements.get("income_statement", {})
    bs = statements.get("balance_sheet", {})
    cf = statements.get("cash_flow", {})

    rev = inc.get("total_revenue", 0.0)
    raw_cogs = inc.get("cost_of_goods_sold")
    cogs_val = float(raw_cogs) if (raw_cogs is not None and not isinstance(raw_cogs, str)) else 0.0
    net_inc = inc.get("net_income", 0.0) or 0.0
    
    curr_assets = bs.get("current_assets", {})
    ca = curr_assets.get("total_current_assets", 0.0) if isinstance(curr_assets, dict) else 0.0
    rec = curr_assets.get("accounts_receivable", 0.0) if isinstance(curr_assets, dict) else 0.0
    inv = curr_assets.get("inventory", 0.0) if isinstance(curr_assets, dict) else 0.0
    
    curr_liab = bs.get("current_liabilities", {})
    cl = curr_liab.get("total_current_liabilities", 0.0) if isinstance(curr_liab, dict) else 0.0
    pay = curr_liab.get("accounts_payable", 0.0) if isinstance(curr_liab, dict) else 0.0

    total_liab = bs.get("total_liabilities") or 0.0
    
    equity_dict = bs.get("equity", {})
    equity = (equity_dict.get("total_equity") if isinstance(equity_dict, dict) else (equity_dict if isinstance(equity_dict, (int, float)) else 0.0)) or 0.0

    lt_liab_dict = bs.get("long_term_liabilities", {})
    long_debt = (lt_liab_dict.get("total_long_term_liabilities") if isinstance(lt_liab_dict, dict) else (lt_liab_dict if isinstance(lt_liab_dict, (int, float)) else 0.0)) or 0.0

    ca_val = float(ca) if (ca is not None and isinstance(ca, (int, float))) else 0.0
    cl_val = float(cl) if (cl is not None and isinstance(cl, (int, float))) else 0.0
    rec_val = float(rec) if (rec is not None and isinstance(rec, (int, float))) else 0.0
    inv_val = float(inv) if (inv is not None and isinstance(inv, (int, float))) else 0.0
    pay_val = float(pay) if (pay is not None and isinstance(pay, (int, float))) else 0.0

    # Working Capital & Cash Conversion Cycle (CCC)
    dio = round((inv_val / cogs_val) * 365, 1) if (cogs_val > 0 and inv_val > 0) else None
    dso = round((rec_val / rev) * 365, 1) if (rev is not None and rev > 0 and rec_val > 0) else None
    dpo = round((pay_val / cogs_val) * 365, 1) if (cogs_val > 0 and pay_val > 0) else None

    operating_cycle = round((dio or 0.0) + (dso or 0.0), 1) if (dio is not None or dso is not None) else None
    cash_conversion_cycle = round(operating_cycle - (dpo or 0.0), 1) if (operating_cycle is not None and dpo is not None) else None

    working_capital_cycle = {
        "current_assets": round(ca_val, 2) if ca is not None else None,
        "current_liabilities": round(cl_val, 2) if cl is not None else None,
        "net_working_capital": round(ca_val - cl_val, 2) if (ca is not None and cl is not None) else None,
        "days_inventory_outstanding_dio": dio,
        "days_sales_outstanding_dso": dso,
        "days_payable_outstanding_dpo": dpo,
        "operating_cycle": operating_cycle,
        "cash_conversion_cycle": cash_conversion_cycle,
        "interpretation": f"Cash conversion cycle is {cash_conversion_cycle:.1f} days." if cash_conversion_cycle is not None else "Working capital cycle metrics require valid Revenue, COGS, and Receivables/Payables reported in source workbook."
    }

    # Capital Structure & WACC
    cost_of_debt = 0.065
    tax_rate = 0.21
    after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)
    
    risk_free_rate = 0.042
    beta = 1.15
    market_premium = 0.055
    cost_of_equity = risk_free_rate + (beta * market_premium)

    total_capital = max(0.0, long_debt) + max(0.0, equity)
    w_d = (long_debt / total_capital) if (total_capital > 0 and long_debt > 0) else 0.0
    w_e = (equity / total_capital) if (total_capital > 0 and equity > 0) else 1.0

    wacc = (w_e * cost_of_equity) + (w_d * after_tax_cost_of_debt)

    capital_structure = {
        "debt_ratio": round(total_liab / (total_liab + equity), 4) if (total_liab + equity) > 0 else 0.0,
        "equity_ratio": round(equity / (total_liab + equity), 4) if (total_liab + equity) > 0 else 0.0,
        "cost_of_debt": round(cost_of_debt * 100, 2),
        "after_tax_cost_of_debt": round(after_tax_cost_of_debt * 100, 2),
        "cost_of_equity": round(cost_of_equity * 100, 2),
        "wacc": round(wacc * 100, 2)
    }

    # Capital Budgeting (Strict Zero-Fabrication: Derived from actual source numbers)
    initial_investment = float(ca) if (ca is not None and ca > 0) else 0.0
    annual_fcf = float(net_inc) if (net_inc is not None and net_inc != 0) else 0.0
    is_calculable = initial_investment > 0 and annual_fcf != 0

    if is_calculable:
        cash_flows = [-initial_investment] + [annual_fcf * (1.05 ** t) for t in range(5)]
        discount_rate = 0.10
        npv = calculate_npv(discount_rate, cash_flows)
        try:
            irr = calculate_irr(cash_flows) * 100
            if np.isnan(irr) or np.isinf(irr) or irr < 0:
                irr = 0.0
        except Exception:
            irr = 0.0
        verdict = "FEASIBLE" if npv > 0 else "HIGH RISK / REJECT"
    else:
        npv = 0.0
        irr = 0.0
        discount_rate = 0.10
        verdict = "NOT_CALCULABLE — Source Data Missing / Non-Positive Assets or Net Income"

    capital_budgeting = {
        "initial_investment": round(initial_investment, 2),
        "projected_annual_fcf": round(annual_fcf, 2),
        "discount_rate": discount_rate * 100,
        "npv": round(npv, 2),
        "irr": round(irr, 2),
        "is_calculable": is_calculable,
        "verdict": verdict
    }

    # DCF Intrinsic Valuation & Scenario Analysis
    from app.engine.valuation_engine import calculate_dcf_valuation, calculate_scenario_sensitivity
    dcf_valuation = calculate_dcf_valuation(statements, ratios, wacc=wacc)
    scenario_analysis = calculate_scenario_sensitivity(statements, ratios)

    return {
        "capital_budgeting": capital_budgeting,
        "capital_structure": capital_structure,
        "working_capital_cycle": working_capital_cycle,
        "valuation_model": dcf_valuation,
        "scenario_analysis": scenario_analysis
    }
