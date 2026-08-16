import io
import pandas as pd
from typing import Dict, Any

def generate_excel_report(company_name: str, statements: Dict[str, Any], ratios: Dict[str, Any], corp_fin: Dict[str, Any], ai_reports: Dict[str, Any]) -> bytes:
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # 1. Executive Summary & Health
        summary_rows = [
            {"Metric": "Company Name", "Value": company_name},
            {"Metric": "Financial Health Score", "Value": ai_reports.get("health_score", 85)},
            {"Metric": "Latest Period", "Value": statements.get("ledger_summary", {}).get("target_year", "Current")},
            {"Metric": "Revenue from Operations (Latest)", "Value": statements.get("income_statement", {}).get("revenue_from_operations", 0)},
            {"Metric": "Total Revenue (Latest)", "Value": statements.get("income_statement", {}).get("total_revenue", 0)},
            {"Metric": "Net Profit (Latest)", "Value": statements.get("income_statement", {}).get("net_income", 0)},
            {"Metric": "Current Ratio (Latest)", "Value": ratios.get("liquidity", {}).get("current_ratio", {}).get("value", 0)},
            {"Metric": "Debt-to-Equity (Latest)", "Value": ratios.get("solvency", {}).get("debt_to_equity", {}).get("value", 0)},
            {"Metric": "WACC (%)", "Value": corp_fin.get("capital_structure", {}).get("wacc", 0)},
            {"Metric": "Executive Summary", "Value": ai_reports.get("executive_summary", "")}
        ]
        pd.DataFrame(summary_rows).to_excel(writer, sheet_name="Executive Summary & Health", index=False)

        # 2. Source Data Summary
        norm_items = statements.get("normalized_items", [])
        src_rows = []
        for i in norm_items:
            src_rows.append({
                "Account Code": i.get("account_code", ""),
                "Account Name": i.get("account_name", ""),
                "Account Type": i.get("account_type", ""),
                "Debit": i.get("debit", 0.0),
                "Credit": i.get("credit", 0.0),
                "Net Amount": i.get("net_amount", 0.0),
                "Sheet": i.get("sheet", ""),
                "Row": i.get("row", ""),
                "Column": i.get("column", ""),
                "Year": i.get("year", ""),
                "Unit": i.get("unit", ""),
                "Currency": i.get("currency", "")
            })
        if not src_rows:
            src_rows.append({"Status": "No raw line items extracted"})
        pd.DataFrame(src_rows).to_excel(writer, sheet_name="Source Data Summary", index=False)

        # 3. Financial Statements (Multi-Year)
        by_year = statements.get("by_year", {})
        years_sorted = sorted([y for y in by_year.keys() if y != "Current"])
        if not by_year or not years_sorted:
            by_year = {"Current": statements}
            years_sorted = ["Current"]

        fs_rows = []
        # Add Income Statement Header
        fs_rows.append({"Line Item": "--- INCOME STATEMENT ---", **{str(y): "" for y in years_sorted}})
        
        inc_keys = [
            ("Revenue from Operations", "revenue_from_operations"),
            ("Total / Gross Revenue", "total_revenue"),
            ("Cost of Goods Sold (COGS)", "cost_of_goods_sold"),
            ("Gross Profit", "gross_profit"),
            ("Operating Expenses (OPEX)", "operating_expenses"),
            ("EBITDA", "ebitda"),
            ("Depreciation & Amortization", "depreciation_amortization"),
            ("EBIT (Operating Income)", "ebit"),
            ("Interest Expense", "interest_expense"),
            ("Tax Expense", "tax_expense"),
            ("NET INCOME", "net_income")
        ]
        
        for label, key in inc_keys:
            row_dict = {"Line Item": label}
            for y in years_sorted:
                val = by_year.get(y, {}).get("income_statement", {}).get(key, 0.0)
                row_dict[str(y)] = val
            fs_rows.append(row_dict)

        fs_rows.append({"Line Item": "", **{str(y): "" for y in years_sorted}})
        fs_rows.append({"Line Item": "--- BALANCE SHEET ---", **{str(y): "" for y in years_sorted}})

        # Helper to retrieve nested bs values
        def get_bs_val(bs_dict, path):
            curr = bs_dict
            for p in path:
                if isinstance(curr, dict):
                    curr = curr.get(p, 0.0)
                else:
                    return 0.0
            return curr

        bs_keys = [
            ("Cash & Equivalents", ["current_assets", "cash"]),
            ("Petty Cash", ["current_assets", "petty_cash"]),
            ("Temporary Investment", ["current_assets", "temporary_investments"]),
            ("Accounts Receivable", ["current_assets", "accounts_receivable"]),
            ("Inventory", ["current_assets", "inventory"]),
            ("Supplies", ["current_assets", "supplies"]),
            ("Prepaid Insurance", ["current_assets", "prepaid_insurance"]),
            ("Total Current Assets", ["current_assets", "total_current_assets"]),
            ("Investment", ["investment"]),
            ("Property, Plant & Equipment (Net)", ["property_plant_equipment", "net_property_plant_equipment"]),
            ("Total Intangible Assets", ["intangible_assets", "total_intangible_assets"]),
            ("Other Assets", ["other_assets"]),
            ("Total Non-Current Assets", ["non_current_assets", "total_non_current_assets"]),
            ("TOTAL ASSETS", ["total_assets"]),
            ("Notes Payable (Short-Term)", ["current_liabilities", "notes_payable"]),
            ("Accounts Payable", ["current_liabilities", "accounts_payable"]),
            ("Wages Payable", ["current_liabilities", "wages_payable"]),
            ("Interest Payable", ["current_liabilities", "interest_payable"]),
            ("Tax Payable", ["current_liabilities", "tax_payable"]),
            ("Unearned Revenue", ["current_liabilities", "unearned_revenue"]),
            ("Short-Term Debt", ["current_liabilities", "short_term_debt"]),
            ("Total Current Liabilities", ["current_liabilities", "total_current_liabilities"]),
            ("Long-Term Liabilities", ["long_term_liabilities", "total_long_term_liabilities"]),
            ("Total Liabilities", ["total_liabilities"]),
            ("Common Stock", ["equity", "common_stock"]),
            ("Retained Earnings", ["equity", "retained_earnings"]),
            ("Less: Treasury Stock", ["equity", "treasury_stock"]),
            ("Total Owner's Equity", ["equity", "total_equity"]),
            ("TOTAL LIABILITIES & EQUITY", ["total_liabilities_and_equity"])
        ]

        for label, path in bs_keys:
            row_dict = {"Line Item": label}
            for y in years_sorted:
                val = get_bs_val(by_year.get(y, {}).get("balance_sheet", {}), path)
                row_dict[str(y)] = val
            fs_rows.append(row_dict)

        fs_rows.append({"Line Item": "", **{str(y): "" for y in years_sorted}})
        fs_rows.append({"Line Item": "--- CASH FLOW ---", **{str(y): "" for y in years_sorted}})

        cf_keys = [
            ("Cash Flow from Operating Activities", "operating_activities"),
            ("Cash Flow from Investing Activities", "investing_activities"),
            ("Cash Flow from Financing Activities", "financing_activities"),
            ("Net Increase/Decrease in Cash", "net_change_in_cash")
        ]

        for label, key in cf_keys:
            row_dict = {"Line Item": label}
            for y in years_sorted:
                val = by_year.get(y, {}).get("cash_flow", {}).get(key, 0.0)
                row_dict[str(y)] = val
            fs_rows.append(row_dict)

        pd.DataFrame(fs_rows).to_excel(writer, sheet_name="Statements (Multi-Year)", index=False)

        # 4. Ratio Analytics
        r_rows = []
        for cat, items in ratios.items():
            if isinstance(items, dict):
                for r_key, r in items.items():
                    if isinstance(r, dict):
                        r_rows.append({
                            "Category": cat.capitalize(),
                            "Ratio Name": r.get("name", r_key),
                            "Formula": r.get("formula", "-"),
                            "Value": r.get("value", 0),
                            "Benchmark": r.get("benchmark", "-"),
                            "Status": r.get("status", "INFO"),
                            "Interpretation": r.get("interpretation", "-")
                        })
        if not r_rows:
            r_rows.append({"Status": "No ratio metrics calculable"})
        pd.DataFrame(r_rows).to_excel(writer, sheet_name="Ratio Analytics", index=False)

        # 5. Validation & Audit Report
        val_rows = []
        for y in years_sorted:
            v_rep = by_year.get(y, {}).get("validation_report", {})
            tb_rep = by_year.get(y, {}).get("trial_balance", {})
            val_rows.append({
                "Year": y,
                "Balance Sheet Audit Check": v_rep.get("balance_sheet_check", "FAIL"),
                "Total Assets": v_rep.get("total_assets", 0.0),
                "Total Liabilities + Equity": v_rep.get("total_liabilities_plus_equity", 0.0),
                "BS Imbalance Difference": v_rep.get("difference", 0.0),
                "BS Audit Explanation": v_rep.get("explanation", ""),
                "Trial Balance Balanced Check": "PASS" if tb_rep.get("is_balanced", True) else "FAIL",
                "TB Difference": tb_rep.get("difference", 0.0)
            })
        if not val_rows:
            val_rows.append({"Status": "No validation data"})
        pd.DataFrame(val_rows).to_excel(writer, sheet_name="Validation & Audit Report", index=False)

        # 6. AI Insights & Recommendations
        insights_rows = []
        for idx, rec in enumerate(ai_reports.get("recommendations", [])):
            insights_rows.append({
                "Recommendation No": idx + 1,
                "Actionable Recommendations & CFO Insights": rec
            })
        if not insights_rows:
            insights_rows.append({"Actionable Recommendations & CFO Insights": "No recommendations generated"})
        pd.DataFrame(insights_rows).to_excel(writer, sheet_name="AI Insights & Recommendations", index=False)

    output.seek(0)
    return output.getvalue()
