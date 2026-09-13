"""
Centralized Deterministic Financial Ratio Engine Module
Provides a single source of truth for all financial ratio definitions, formulas,
constituent input tracking, and reproducibility verification across Captrix.
Enforces zero-fabrication: LLM is never the authority for arithmetic.
"""

from typing import Dict, Any, Optional
import math


def safe_div(num: Optional[float], den: Optional[float], multiply_100: bool = False, decimal_places: int = 2) -> Dict[str, Any]:
    """Calculate ratio safely with zero/null denominator protection."""
    if den is None or den == 0 or num is None:
        return {
            "value": None,
            "display_value": "Ratio Not Calculable — Required Source Data Missing / Denominator = 0",
            "is_calculable": False,
            "reason": "Denominator is zero, missing, or numerator is null"
        }
    val = (float(num) / float(den)) * (100.0 if multiply_100 else 1.0)
    rounded = round(val, decimal_places)
    return {
        "value": rounded,
        "display_value": f"{rounded}{'%' if multiply_100 else 'x'}",
        "is_calculable": True,
        "reason": None
    }


def verify_ratio_reproducibility(num: Optional[float], den: Optional[float], value: Optional[float], multiply_100: bool = False, tol: float = 0.02) -> bool:
    """Verifies that the reported ratio value can be reproduced directly from displayed inputs."""
    if value is None or den is None or den == 0 or num is None:
        return True
    expected = (float(num) / float(den)) * (100.0 if multiply_100 else 1.0)
    return abs(expected - float(value)) <= tol


class RatioEngine:
    """
    Centralized, deterministic ratio engine.
    Every ratio strictly links:
      - Displayed Formula
      - Constituent Inputs (source fields & values)
      - Explicit Accounting Definition
      - Deterministic Calculation
      - Reproducibility Verification
    """

    @staticmethod
    def calculate_all_ratios(statements: Dict[str, Any]) -> Dict[str, Any]:
        val_report = statements.get("validation_report", {})
        bs_valid = val_report.get("balance_sheet_check", "PASS") != "FAIL"

        inc = statements.get("income_statement", {})
        bs = statements.get("balance_sheet", {})

        # 1. Income Statement Line Items (Preserving exact reported values)
        rev = inc.get("total_revenue") or inc.get("revenue_from_operations") or inc.get("sales")
        rev = float(rev) if rev is not None else None
        
        cogs = inc.get("cost_of_goods_sold") or inc.get("cogs")
        cogs = float(cogs) if cogs is not None else None
        
        gp = inc.get("gross_profit")
        gp = float(gp) if gp is not None else None
        
        ebit = inc.get("ebit") or inc.get("operating_income") or inc.get("profit_from_operations")
        ebit = float(ebit) if ebit is not None else None
        
        net_inc = inc.get("net_income") or inc.get("net_profit")
        net_inc = float(net_inc) if net_inc is not None else None
        
        interest = inc.get("interest_expense") or inc.get("finance_costs")
        interest = float(interest) if interest is not None else None

        # 2. Balance Sheet Line Items
        curr_assets = bs.get("current_assets", {}) if isinstance(bs.get("current_assets"), dict) else {}
        ca = curr_assets.get("total_current_assets")
        ca = float(ca) if ca is not None else None
        
        cash = curr_assets.get("cash")
        cash = float(cash) if cash is not None else None
        
        rec = curr_assets.get("accounts_receivable") or curr_assets.get("trade_receivables")
        rec = float(rec) if rec is not None else None
        
        inv = curr_assets.get("inventory") or curr_assets.get("inventories")
        inv = float(inv) if inv is not None else None

        curr_liab = bs.get("current_liabilities", {}) if isinstance(bs.get("current_liabilities"), dict) else {}
        cl = curr_liab.get("total_current_liabilities")
        cl = float(cl) if cl is not None else None

        total_assets = bs.get("total_assets")
        total_assets = float(total_assets) if total_assets is not None else None

        total_liab = bs.get("total_liabilities")
        total_liab = float(total_liab) if total_liab is not None else None

        equity_dict = bs.get("equity", {}) if isinstance(bs.get("equity"), dict) else {}
        equity = equity_dict.get("total_equity")
        if equity is None and isinstance(bs.get("total_equity"), (int, float)):
            equity = bs.get("total_equity")
        equity = float(equity) if equity is not None else None

        lt_liab_dict = bs.get("long_term_liabilities") or bs.get("non_current_liabilities") or {}
        lt_liab_dict = lt_liab_dict if isinstance(lt_liab_dict, dict) else {}
        long_debt = lt_liab_dict.get("long_term_debt") or lt_liab_dict.get("long_term_borrowings") or lt_liab_dict.get("total_long_term_liabilities")
        long_debt = float(long_debt) if long_debt is not None else None

        st_debt = curr_liab.get("short_term_debt") or curr_liab.get("short_term_borrowings")
        st_debt = float(st_debt) if st_debt is not None else None

        total_debt = ((st_debt or 0.0) + (long_debt or 0.0)) if (st_debt is not None or long_debt is not None) else None

        # =========================================================================
        # 1. LIQUIDITY RATIOS
        # =========================================================================
        liquidity = {}

        # 1.1 Current Ratio
        cr_calc = safe_div(ca, cl) if (bs_valid and ca is not None and cl is not None) else safe_div(None, None)
        cr_val = cr_calc["value"]
        liquidity["current_ratio"] = {
            "name": "Current Ratio",
            "category": "liquidity",
            "value": cr_val,
            "display_value": f"{cr_val:.2f}x" if cr_val is not None else "NOT_CALCULABLE",
            "unit": "x",
            "is_calculable": cr_calc["is_calculable"],
            "formula": "Current Assets / Current Liabilities",
            "inputs": {
                "Current Assets": ca,
                "Current Liabilities": cl
            },
            "definition_used": "Standard Short-Term Liquidity Ratio: Measures ability to cover short-term obligations with short-term assets.",
            "benchmark": "> 1.5x (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if cr_val >= 1.5 else ("WARNING" if cr_val >= 1.0 else "CRITICAL")) if cr_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"The enterprise holds {cr_val:.2f}x of current assets for every 1.00 of current liabilities." if cr_val is not None else "Not calculable: Current Assets or Current Liabilities missing in source schedules."),
            "reproducible": verify_ratio_reproducibility(ca, cl, cr_val)
        }

        # 1.2 Quick Ratio (Acid-Test)
        quick_assets = (ca - inv) if (ca is not None and inv is not None) else ca
        qr_calc = safe_div(quick_assets, cl) if (bs_valid and quick_assets is not None and cl is not None) else safe_div(None, None)
        qr_val = qr_calc["value"]
        liquidity["quick_ratio"] = {
            "name": "Quick Ratio (Acid-Test)",
            "category": "liquidity",
            "value": qr_val,
            "display_value": f"{qr_val:.2f}x" if qr_val is not None else "NOT_CALCULABLE",
            "unit": "x",
            "is_calculable": qr_calc["is_calculable"],
            "formula": "(Current Assets - Inventory) / Current Liabilities",
            "inputs": {
                "Current Assets": ca,
                "Inventory": inv,
                "Liquid Quick Assets": quick_assets,
                "Current Liabilities": cl
            },
            "definition_used": "Acid-Test Ratio: Excludes inventory to assess immediate liquidity buffer against short-term debt.",
            "benchmark": "> 1.0x (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if qr_val >= 1.0 else ("WARNING" if qr_val >= 0.8 else "CRITICAL")) if qr_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Liquid quick assets cover {qr_val:.2f}x of current short-term liabilities excluding inventory." if qr_val is not None else "Not calculable: Current Assets or Current Liabilities missing in source schedules."),
            "reproducible": verify_ratio_reproducibility(quick_assets, cl, qr_val)
        }

        # 1.3 Cash Ratio
        cash_calc = safe_div(cash, cl) if (bs_valid and cash is not None and cl is not None) else safe_div(None, None)
        cash_val = cash_calc["value"]
        liquidity["cash_ratio"] = {
            "name": "Cash Ratio",
            "category": "liquidity",
            "value": cash_val,
            "display_value": f"{cash_val:.2f}x" if cash_val is not None else "NOT_CALCULABLE",
            "unit": "x",
            "is_calculable": cash_calc["is_calculable"],
            "formula": "Cash & Cash Equivalents / Current Liabilities",
            "inputs": {
                "Cash & Cash Equivalents": cash,
                "Current Liabilities": cl
            },
            "definition_used": "Most conservative liquidity metric: Evaluates direct cash reserves against immediate liabilities.",
            "benchmark": "> 0.5x (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if cash_val >= 0.5 else ("WARNING" if cash_val >= 0.2 else "CRITICAL")) if cash_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Cash reserves cover {cash_val * 100:.1f}% of current short-term obligations." if cash_val is not None else "Not calculable: Cash or Current Liabilities missing in source schedules."),
            "reproducible": verify_ratio_reproducibility(cash, cl, cash_val)
        }

        # 1.4 Net Working Capital to Revenue (Formerly mislabeled as Working Capital Ratio)
        nwc = (ca - cl) if (ca is not None and cl is not None) else None
        nwc_rev_calc = safe_div(nwc, rev, multiply_100=True) if (bs_valid and nwc is not None and rev is not None) else safe_div(None, None)
        nwc_rev_val = nwc_rev_calc["value"]
        liquidity["working_capital_ratio"] = {
            "name": "Net Working Capital to Revenue",
            "canonical_name": "net_working_capital_to_revenue",
            "category": "liquidity",
            "value": nwc_rev_val,
            "display_value": f"{nwc_rev_val:.1f}%" if nwc_rev_val is not None else "NOT_CALCULABLE",
            "unit": "%",
            "is_calculable": nwc_rev_calc["is_calculable"],
            "formula": "(Net Working Capital / Revenue) * 100",
            "inputs": {
                "Current Assets": ca,
                "Current Liabilities": cl,
                "Net Working Capital": nwc,
                "Revenue": rev
            },
            "definition_used": "Working Capital Intensity: Measures net working capital requirement as a percentage of annual sales.",
            "benchmark": "10.0% - 25.0% (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if (nwc_rev_val is not None and 10.0 <= nwc_rev_val <= 30.0) else ("WARNING" if (nwc_rev_val is not None and nwc_rev_val > 0) else "CRITICAL")) if nwc_rev_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Net working capital represents {nwc_rev_val:.1f}% of annual revenue." if nwc_rev_val is not None else "Not calculable: Current Assets, Current Liabilities, or Revenue missing in source schedules."),
            "reproducible": verify_ratio_reproducibility(nwc, rev, nwc_rev_val, multiply_100=True)
        }

        # =========================================================================
        # 2. PROFITABILITY RATIOS
        # =========================================================================
        profitability = {}

        # 2.1 Gross Profit Margin
        gp_calc = safe_div(gp, rev, multiply_100=True) if rev is not None else safe_div(None, None)
        gp_val = gp_calc["value"]
        profitability["gross_profit_margin"] = {
            "name": "Gross Profit Margin",
            "category": "profitability",
            "value": gp_val,
            "display_value": f"{gp_val:.1f}%" if gp_val is not None else "NOT_CALCULABLE",
            "unit": "%",
            "is_calculable": gp_calc["is_calculable"],
            "formula": "(Gross Profit / Total Revenue) * 100",
            "inputs": {
                "Gross Profit": gp,
                "Total Revenue": rev
            },
            "definition_used": "Gross Profit Margin: Percentage of revenue remaining after subtracting direct cost of goods sold.",
            "benchmark": "> 30.0% (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if gp_val >= 30.0 else ("WARNING" if gp_val >= 15.0 else "CRITICAL")) if gp_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Enterprise retains {gp_val:.1f}% of revenue after direct production / service costs." if gp_val is not None else "Not calculable: Gross Profit or Revenue not reported."),
            "reproducible": verify_ratio_reproducibility(gp, rev, gp_val, multiply_100=True)
        }

        # 2.2 Operating Margin (EBIT Margin)
        op_calc = safe_div(ebit, rev, multiply_100=True) if rev is not None else safe_div(None, None)
        op_val = op_calc["value"]
        profitability["operating_profit_margin"] = {
            "name": "Operating Profit Margin (EBIT Margin)",
            "category": "profitability",
            "value": op_val,
            "display_value": f"{op_val:.1f}%" if op_val is not None else "NOT_CALCULABLE",
            "unit": "%",
            "is_calculable": op_calc["is_calculable"],
            "formula": "(EBIT / Total Revenue) * 100",
            "inputs": {
                "EBIT": ebit,
                "Total Revenue": rev
            },
            "definition_used": "Operating Margin: Core operational profitability before interest and income taxes.",
            "benchmark": "> 15.0% (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if op_val >= 15.0 else ("WARNING" if op_val >= 5.0 else "CRITICAL")) if op_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Operational profitability yields {op_val:.1f}% operating income per dollar of revenue." if op_val is not None else "Not calculable: Operating Income (EBIT) or Revenue not reported."),
            "reproducible": verify_ratio_reproducibility(ebit, rev, op_val, multiply_100=True)
        }

        # 2.3 Net Profit Margin
        np_calc = safe_div(net_inc, rev, multiply_100=True) if rev is not None else safe_div(None, None)
        np_val = np_calc["value"]
        profitability["net_profit_margin"] = {
            "name": "Net Profit Margin",
            "category": "profitability",
            "value": np_val,
            "display_value": f"{np_val:.1f}%" if np_val is not None else "NOT_CALCULABLE",
            "unit": "%",
            "is_calculable": np_calc["is_calculable"],
            "formula": "(Net Income / Total Revenue) * 100",
            "inputs": {
                "Net Income": net_inc,
                "Total Revenue": rev
            },
            "definition_used": "Net Profit Margin: Bottom-line profitability after all operating expenses, finance costs, and taxes.",
            "benchmark": "> 10.0% (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if np_val >= 10.0 else ("WARNING" if np_val >= 5.0 else "CRITICAL")) if np_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"The enterprise yields {np_val:.1f}% net profit from total revenue." if (np_val is not None and np_val >= 0) else (f"Enterprise incurred a net loss margin of {np_val:.1f}%." if np_val is not None else "Not calculable: Net Income or Revenue not reported.")),
            "reproducible": verify_ratio_reproducibility(net_inc, rev, np_val, multiply_100=True)
        }

        # 2.4 Return on Assets (ROA)
        roa_calc = safe_div(net_inc, total_assets, multiply_100=True) if (bs_valid and total_assets is not None) else safe_div(None, None)
        roa_val = roa_calc["value"]
        profitability["return_on_assets"] = {
            "name": "Return on Assets (ROA)",
            "category": "profitability",
            "value": roa_val,
            "display_value": f"{roa_val:.1f}%" if roa_val is not None else "NOT_CALCULABLE",
            "unit": "%",
            "is_calculable": roa_calc["is_calculable"],
            "formula": "(Net Income / Total Assets) * 100",
            "inputs": {
                "Net Income": net_inc,
                "Total Assets": total_assets
            },
            "definition_used": "Asset Efficiency in Profit Generation: Evaluates net return per unit of asset base deployed.",
            "benchmark": "> 5.0% (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if roa_val >= 5.0 else ("WARNING" if roa_val >= 2.0 else "CRITICAL")) if roa_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Generates {roa_val:.2f}% net return per unit of total assets deployed." if roa_val is not None else "Not calculable: Net Income or Total Assets missing in source schedules."),
            "reproducible": verify_ratio_reproducibility(net_inc, total_assets, roa_val, multiply_100=True)
        }

        # 2.5 Return on Equity (ROE)
        roe_calc = safe_div(net_inc, equity, multiply_100=True) if (bs_valid and equity is not None and equity > 0) else safe_div(None, None)
        roe_val = roe_calc["value"]
        profitability["return_on_equity"] = {
            "name": "Return on Equity (ROE)",
            "category": "profitability",
            "value": roe_val,
            "display_value": f"{roe_val:.1f}%" if roe_val is not None else "NOT_CALCULABLE",
            "unit": "%",
            "is_calculable": roe_calc["is_calculable"],
            "formula": "(Net Income / Total Shareholders' Equity) * 100",
            "inputs": {
                "Net Income": net_inc,
                "Total Shareholders' Equity": equity
            },
            "definition_used": "Return on Shareholders' Equity: Measures annual net profit delivered per unit of equity capital.",
            "benchmark": "> 15.0% (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if roe_val >= 15.0 else ("WARNING" if roe_val >= 8.0 else "CRITICAL")) if roe_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Shareholders earn a {roe_val:.1f}% return on equity invested." if (roe_val is not None and roe_val >= 0) else (f"Shareholders experience a {roe_val:.1f}% loss on equity." if roe_val is not None else "Not calculable: Net Income or Shareholders' Equity missing in source schedules.")),
            "reproducible": verify_ratio_reproducibility(net_inc, equity, roe_val, multiply_100=True)
        }

        # 2.6 Return on Capital Employed (ROCE)
        # Explicit definition: Capital Employed = Total Assets - Current Liabilities (or Equity + Long-Term Debt)
        cap_employed = (total_assets - cl) if (total_assets is not None and cl is not None) else (((equity or 0.0) + (long_debt or 0.0)) if (equity is not None or long_debt is not None) else None)
        
        is_roce_data_error = (cap_employed is not None and cap_employed <= 0) or (equity is not None and equity <= 0)
        
        if is_roce_data_error:
            roce_calc = {
                "value": None,
                "display_value": "NOT_CALCULABLE",
                "is_calculable": False,
                "reason": "Capital Employed or Total Equity is zero or negative (Data Quality Error)"
            }
            roce_val = None
            roce_status = "DATA_QUALITY_ERROR"
        else:
            roce_calc = safe_div(ebit, cap_employed, multiply_100=True) if (bs_valid and cap_employed is not None and cap_employed > 0 and ebit is not None) else safe_div(None, None)
            roce_val = roce_calc["value"]
            roce_status = ("HEALTHY" if roce_val >= 12.0 else ("WARNING" if roce_val >= 6.0 else "CRITICAL")) if roce_val is not None else "NOT_CALCULABLE"

        profitability["return_on_capital_employed"] = {
            "name": "ROCE (Return on Capital Employed)",
            "category": "profitability",
            "value": roce_val,
            "display_value": roce_calc["display_value"] if roce_val is None else f"{roce_val:.1f}%",
            "unit": "%",
            "is_calculable": roce_calc["is_calculable"],
            "formula": "(EBIT / (Total Assets - Current Liabilities)) * 100",
            "inputs": {
                "EBIT": ebit,
                "Total Assets": total_assets,
                "Current Liabilities": cl,
                "Capital Employed": cap_employed
            },
            "definition_used": "Operating Return on Capital: EBIT divided by Capital Employed (defined as Total Assets minus Current Liabilities).",
            "benchmark": "> 12.0% (Industry benchmark unavailable from the provided data)",
            "status": roce_status,
            "interpretation": (f"Operating return on capital employed stands at {roce_val:.1f}%." if roce_val is not None else ("Capital employed or equity is zero or negative — indicates severe balance sheet distress or data quality issue." if is_roce_data_error else "Not calculable: EBIT, Total Assets, or Current Liabilities missing in source schedules.")),
            "reproducible": verify_ratio_reproducibility(ebit, cap_employed, roce_val, multiply_100=True)
        }

        # =========================================================================
        # 3. SOLVENCY & LEVERAGE RATIOS
        # =========================================================================
        solvency = {}

        # 3.1 Debt-to-Equity Ratio (Strict Interest-Bearing Borrowings)
        # Explicit Definition: Short-Term Debt + Long-Term Debt / Shareholders' Equity
        has_debt_schedule = (st_debt is not None or long_debt is not None)
        debt_for_de = total_debt if has_debt_schedule else 0.0
        de_calc = safe_div(debt_for_de, equity) if (bs_valid and equity is not None and equity > 0) else safe_div(None, None)
        de_val = de_calc["value"]
        solvency["debt_to_equity"] = {
            "name": "Debt to Equity Ratio",
            "category": "solvency",
            "value": de_val,
            "display_value": f"{de_val:.2f}x" if de_val is not None else "NOT_CALCULABLE",
            "unit": "x",
            "is_calculable": de_calc["is_calculable"],
            "formula": "Interest-bearing Debt / Equity",
            "inputs": {
                "Short-Term Debt": st_debt or 0.0,
                "Long-Term Debt": long_debt or 0.0,
                "Interest-bearing Debt": debt_for_de,
                "Equity": equity
            },
            "definition_used": "Interest-bearing Debt / Equity: Evaluates pure financial borrowing leverage relative to shareholder capital. Excludes non-debt operational liabilities like accounts payable.",
            "benchmark": "< 1.5x (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if de_val <= 1.0 else ("WARNING" if de_val <= 2.0 else "CRITICAL")) if de_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"For every 1.00 of equity capital, the enterprise carries {de_val:.2f} of interest-bearing debt." if de_val is not None else "Not calculable: Shareholders' Equity missing or zero in source schedules."),
            "reproducible": verify_ratio_reproducibility(debt_for_de, equity, de_val)
        }

        # 3.2 Total Liabilities to Equity Ratio (Separate, distinct metric)
        liab_to_eq_calc = safe_div(total_liab, equity) if (bs_valid and total_liab is not None and equity is not None and equity > 0) else safe_div(None, None)
        liab_to_eq_val = liab_to_eq_calc["value"]
        solvency["liabilities_to_equity"] = {
            "name": "Total Liabilities to Equity Ratio",
            "category": "solvency",
            "value": liab_to_eq_val,
            "display_value": f"{liab_to_eq_val:.2f}x" if liab_to_eq_val is not None else "NOT_CALCULABLE",
            "unit": "x",
            "is_calculable": liab_to_eq_calc["is_calculable"],
            "formula": "Total Liabilities / Equity",
            "inputs": {
                "Total Liabilities": total_liab,
                "Equity": equity
            },
            "definition_used": "Total Liabilities / Equity: Comprehensive leverage metric including both operating liabilities (payables, accruals) and funded debt.",
            "benchmark": "< 2.0x (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if liab_to_eq_val <= 1.5 else ("WARNING" if liab_to_eq_val <= 2.5 else "CRITICAL")) if liab_to_eq_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Total liabilities represent {liab_to_eq_val:.2f}x of shareholder equity capital." if liab_to_eq_val is not None else "Not calculable: Total Liabilities or Equity missing in source schedules."),
            "reproducible": verify_ratio_reproducibility(total_liab, equity, liab_to_eq_val)
        }

        # 3.3 Debt Ratio (Total Liabilities to Total Assets)
        dr_calc = safe_div(total_liab, total_assets, multiply_100=True) if (bs_valid and total_liab is not None and total_assets is not None) else safe_div(None, None)
        dr_val = dr_calc["value"]
        solvency["debt_ratio"] = {
            "name": "Debt Ratio (Liabilities to Assets)",
            "category": "solvency",
            "value": dr_val,
            "display_value": f"{dr_val:.1f}%" if dr_val is not None else "NOT_CALCULABLE",
            "unit": "%",
            "is_calculable": dr_calc["is_calculable"],
            "formula": "(Total Liabilities / Total Assets) * 100",
            "inputs": {
                "Total Liabilities": total_liab,
                "Total Assets": total_assets
            },
            "definition_used": "Total Liabilities to Assets: Percentage of enterprise assets funded through all claims of external creditors.",
            "benchmark": "< 60.0% (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if dr_val <= 50.0 else ("WARNING" if dr_val <= 70.0 else "CRITICAL")) if dr_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Creditors and liabilities finance {dr_val:.1f}% of total enterprise assets." if dr_val is not None else "Not calculable: Total Liabilities or Total Assets missing in source schedules."),
            "reproducible": verify_ratio_reproducibility(total_liab, total_assets, dr_val, multiply_100=True)
        }

        # 3.4 Equity Ratio
        eq_r_calc = safe_div(equity, total_assets, multiply_100=True) if (bs_valid and equity is not None and total_assets is not None) else safe_div(None, None)
        eq_r_val = eq_r_calc["value"]
        solvency["equity_ratio"] = {
            "name": "Equity Ratio",
            "category": "solvency",
            "value": eq_r_val,
            "display_value": f"{eq_r_val:.1f}%" if eq_r_val is not None else "NOT_CALCULABLE",
            "unit": "%",
            "is_calculable": eq_r_calc["is_calculable"],
            "formula": "(Total Shareholders' Equity / Total Assets) * 100",
            "inputs": {
                "Total Shareholders' Equity": equity,
                "Total Assets": total_assets
            },
            "definition_used": "Equity Ratio: Percentage of total asset base financed through permanent shareholder equity.",
            "benchmark": "> 40.0% (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if eq_r_val >= 40.0 else ("WARNING" if eq_r_val >= 25.0 else "CRITICAL")) if eq_r_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Shareholders' equity funds {eq_r_val:.1f}% of the enterprise asset base." if eq_r_val is not None else "Not calculable: Shareholders' Equity or Total Assets missing in source schedules."),
            "reproducible": verify_ratio_reproducibility(equity, total_assets, eq_r_val, multiply_100=True)
        }

        # 3.5 Interest Coverage Ratio
        ic_calc = safe_div(ebit, interest) if (ebit is not None and interest is not None and interest > 0) else safe_div(None, None)
        ic_val = ic_calc["value"]
        solvency["interest_coverage_ratio"] = {
            "name": "Interest Coverage Ratio",
            "category": "solvency",
            "value": ic_val,
            "display_value": f"{ic_val:.1f}x" if ic_val is not None else ("NOT_APPLICABLE (No Interest Expense)" if interest == 0.0 else "NOT_CALCULABLE"),
            "unit": "x",
            "is_calculable": ic_calc["is_calculable"],
            "formula": "EBIT / Interest Expense",
            "inputs": {
                "EBIT": ebit,
                "Interest Expense": interest
            },
            "definition_used": "Debt Service Capability: Number of times operating profit (EBIT) covers annual contractual interest obligations.",
            "benchmark": "> 3.0x (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if ic_val >= 3.0 else ("WARNING" if ic_val >= 1.5 else "CRITICAL")) if ic_val is not None else ("HEALTHY" if interest == 0.0 else "NOT_CALCULABLE"),
            "interpretation": (f"Operating earnings cover annual interest expense {ic_val:.1f} times." if ic_val is not None else ("Enterprise has zero interest expense reported." if interest == 0.0 else "Not calculable: EBIT or Interest Expense not reported.")),
            "reproducible": verify_ratio_reproducibility(ebit, interest, ic_val)
        }

        # =========================================================================
        # 4. EFFICIENCY & TURNOVER RATIOS
        # =========================================================================
        efficiency = {}

        # 4.1 Inventory Turnover (Strict Average vs Ending Disclosure)
        opening_inv = bs.get("opening_inventory") if isinstance(bs, dict) else None
        if opening_inv is None and isinstance(statements, dict):
            opening_inv = statements.get("opening_inventory")
        closing_inv = inv

        if opening_inv is not None and closing_inv is not None and (float(opening_inv) + float(closing_inv)) > 0 and cogs is not None and cogs > 0:
            avg_inv = (float(opening_inv) + float(closing_inv)) / 2.0
            inv_t_calc = safe_div(cogs, avg_inv)
            inv_t_def = "COGS / Average Inventory (Standard 2-Period Average)"
            inv_t_formula = "COGS / ((Opening Inventory + Closing Inventory) / 2)"
            inv_t_inputs = {
                "COGS": cogs,
                "Opening Inventory": float(opening_inv),
                "Closing Inventory": float(closing_inv),
                "Average Inventory": avg_inv
            }
            num_for_check, den_for_check = cogs, avg_inv
        else:
            inv_t_calc = {
                "value": None,
                "display_value": "Ratio Not Calculable — Required Source Data Missing (Average Inventory requires Opening and Closing balances) / Denominator = 0",
                "is_calculable": False,
                "reason": "Opening inventory not reported or COGS is zero; average inventory requires multi-period opening and closing balances"
            }
            inv_t_def = "COGS / Average Inventory (Not Calculable: Requires Opening and Closing Inventory for 2-period average)"
            inv_t_formula = "COGS / ((Opening Inventory + Closing Inventory) / 2)"
            inv_t_inputs = {
                "COGS": cogs,
                "Opening Inventory": float(opening_inv) if opening_inv is not None else None,
                "Closing Inventory": float(closing_inv) if closing_inv is not None else None
            }
            num_for_check, den_for_check = None, None

        inv_t_val = inv_t_calc["value"]
        efficiency["inventory_turnover"] = {
            "name": "Inventory Turnover",
            "category": "efficiency",
            "value": inv_t_val,
            "display_value": inv_t_calc["display_value"] if inv_t_val is None else f"{inv_t_val:.1f}x",
            "unit": "times",
            "is_calculable": inv_t_calc["is_calculable"],
            "formula": inv_t_formula,
            "inputs": inv_t_inputs,
            "definition_used": inv_t_def,
            "benchmark": "4.0x - 8.0x (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if inv_t_val >= 4.0 else ("WARNING" if inv_t_val >= 2.0 else "CRITICAL")) if inv_t_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Inventory is rotated and sold {inv_t_val:.1f} times per period." if inv_t_val is not None else "Not calculable: Multi-period opening and closing inventory balances required to calculate average inventory."),
            "reproducible": verify_ratio_reproducibility(num_for_check, den_for_check, inv_t_val)
        }

        # 4.2 Receivables Turnover
        rec_t_calc = safe_div(rev, rec) if (rev is not None and rec is not None and rec > 0) else safe_div(None, None)
        rec_t_val = rec_t_calc["value"]
        efficiency["receivable_turnover"] = {
            "name": "Receivables Turnover",
            "category": "efficiency",
            "value": rec_t_val,
            "display_value": f"{rec_t_val:.1f}x" if rec_t_val is not None else "NOT_CALCULABLE",
            "unit": "times",
            "is_calculable": rec_t_calc["is_calculable"],
            "formula": "Total Revenue / Accounts Receivable",
            "inputs": {
                "Total Revenue": rev,
                "Accounts Receivable": rec
            },
            "definition_used": "Receivables Turnover: Measures collection speed and frequency of trade receivables per year.",
            "benchmark": "> 6.0x (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if rec_t_val >= 6.0 else ("WARNING" if rec_t_val >= 3.0 else "CRITICAL")) if rec_t_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Accounts receivable are collected and replenished {rec_t_val:.1f} times annually." if rec_t_val is not None else "Not calculable: Revenue or Accounts Receivable missing or zero in source schedules."),
            "reproducible": verify_ratio_reproducibility(rev, rec, rec_t_val)
        }

        # 4.3 Asset Turnover
        ast_t_calc = safe_div(rev, total_assets) if (bs_valid and rev is not None and total_assets is not None and total_assets > 0) else safe_div(None, None)
        ast_t_val = ast_t_calc["value"]
        efficiency["asset_turnover"] = {
            "name": "Asset Turnover",
            "category": "efficiency",
            "value": ast_t_val,
            "display_value": f"{ast_t_val:.2f}x" if ast_t_val is not None else "NOT_CALCULABLE",
            "unit": "times",
            "is_calculable": ast_t_calc["is_calculable"],
            "formula": "Total Revenue / Total Assets",
            "inputs": {
                "Total Revenue": rev,
                "Total Assets": total_assets
            },
            "definition_used": "Total Asset Turnover: Evaluates revenue generating velocity per unit of total asset investment.",
            "benchmark": "> 1.0x (Industry benchmark unavailable from the provided data)",
            "status": ("HEALTHY" if ast_t_val >= 1.0 else ("WARNING" if ast_t_val >= 0.5 else "CRITICAL")) if ast_t_val is not None else "NOT_CALCULABLE",
            "interpretation": (f"Generates {ast_t_val:.2f} of annual revenue per dollar of total asset deployment." if ast_t_val is not None else "Not calculable: Revenue or Total Assets missing in source schedules."),
            "reproducible": verify_ratio_reproducibility(rev, total_assets, ast_t_val)
        }

        return {
            "liquidity": liquidity,
            "profitability": profitability,
            "solvency": solvency,
            "efficiency": efficiency
        }
