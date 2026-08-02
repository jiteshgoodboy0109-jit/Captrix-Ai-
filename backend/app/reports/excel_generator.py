import io
import pandas as pd
from typing import Dict, Any

def generate_excel_report(company_name: str, statements: Dict[str, Any], ratios: Dict[str, Any], corp_fin: Dict[str, Any], ai_reports: Dict[str, Any]) -> bytes:
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Sheet 1: Executive Summary
        summary_rows = [
            {"Metric": "Company Name", "Value": company_name},
            {"Metric": "Financial Health Score", "Value": ai_reports.get("health_score", 80)},
            {"Metric": "Total Revenue", "Value": statements.get("income_statement", {}).get("total_revenue", 0)},
            {"Metric": "Net Profit", "Value": statements.get("income_statement", {}).get("net_income", 0)},
            {"Metric": "Current Ratio", "Value": ratios.get("liquidity", {}).get("current_ratio", {}).get("value", 0)},
            {"Metric": "Debt-to-Equity", "Value": ratios.get("solvency", {}).get("debt_to_equity", {}).get("value", 0)},
            {"Metric": "WACC (%)", "Value": corp_fin.get("capital_structure", {}).get("wacc", 0)}
        ]
        pd.DataFrame(summary_rows).to_excel(writer, sheet_name="Executive Summary", index=False)

        # Sheet 2: Balance Sheet (2-Column Structured Accounting Layout)
        bs = statements.get("balance_sheet", {})
        ca = bs.get("current_assets", {})
        ppe = bs.get("property_plant_equipment", {})
        intangibles = bs.get("intangible_assets", {})
        cl = bs.get("current_liabilities", {})
        ltl = bs.get("long_term_liabilities", {})
        eq = bs.get("equity", {})

        assets_items = [
            ("--- ASSETS ---", ""),
            ("Current assets", ""),
            ("Cash", ca.get("cash", 0)),
            ("Petty cash", ca.get("petty_cash", 0)),
            ("Temporary Investment", ca.get("temporary_investments", 0)),
            ("Accounts receivable", ca.get("accounts_receivable", 0)),
            ("Inventory", ca.get("inventory", 0)),
            ("Supply", ca.get("supplies", 0)),
            ("Prepaid Insurance", ca.get("prepaid_insurance", 0)),
            ("Total current assets", ca.get("total_current_assets", 0)),
            ("Investment", bs.get("investment", 0)),
            ("Property plant and equipment", ""),
            ("Land", ppe.get("land", 0)),
            ("Land improvements", ppe.get("land_improvements", 0)),
            ("Buildings", ppe.get("buildings", 0)),
            ("Equipment", ppe.get("equipment", 0)),
            ("Accumulated depreciation", ppe.get("accumulated_depreciation", 0)),
            ("Prop, plant and equip-net", ppe.get("net_property_plant_equipment", 0)),
            ("Intangible assets", ""),
            ("Goodwill", intangibles.get("goodwill", 0)),
            ("Trade names", intangibles.get("trade_names", 0)),
            ("Total intangible assets", intangibles.get("total_intangible_assets", 0)),
            ("Other assets", bs.get("other_assets", 0)),
            ("TOTAL ASSETS", bs.get("total_assets", 0))
        ]

        liabilities_items = [
            ("--- LIABILITIES & EQUITY ---", ""),
            ("Current liabilities", ""),
            ("Notes payable", cl.get("notes_payable", 0)),
            ("Accounts payable", cl.get("accounts_payable", 0)),
            ("Wages payable", cl.get("wages_payable", 0)),
            ("Interest payable", cl.get("interest_payable", 0)),
            ("Tax payable", cl.get("tax_payable", 0)),
            ("Unearned revenue", cl.get("unearned_revenue", 0)),
            ("Total current liabilities", cl.get("total_current_liabilities", 0)),
            ("Long-term liabilities", ""),
            ("Notes payable", ltl.get("notes_payable_lt", 0)),
            ("Bonds payable", ltl.get("bonds_payable", 0)),
            ("Total long term liabilities", ltl.get("total_long_term_liabilities", 0)),
            ("Total liabilities", bs.get("total_liabilities", 0)),
            ("--- OWNER'S EQUITY ---", ""),
            ("Common stock", eq.get("common_stock", 0)),
            ("Retained earnings", eq.get("retained_earnings", 0)),
            ("Less: Treasury stock", eq.get("treasury_stock", 0)),
            ("Total owner's equity", eq.get("total_equity", 0)),
            ("", ""),
            ("", ""),
            ("", ""),
            ("", ""),
            ("TOTAL LIABILITIES & EQUITY", bs.get("total_liabilities_and_equity", 0))
        ]

        max_len = max(len(assets_items), len(liabilities_items))
        bs_2col_rows = []

        for i in range(max_len):
            a_name, a_val = assets_items[i] if i < len(assets_items) else ("", "")
            l_name, l_val = liabilities_items[i] if i < len(liabilities_items) else ("", "")
            bs_2col_rows.append({
                "Assets Line Item": a_name,
                "Assets Amount (USD)": a_val,
                " ": "",
                "Liabilities & Equity Line Item": l_name,
                "Liabilities & Equity Amount (USD)": l_val
            })

        pd.DataFrame(bs_2col_rows).to_excel(writer, sheet_name="Balance Sheet & Trial Balance", index=False)

        # Sheet 3: Income Statement
        inc = statements.get("income_statement", {})
        inc_rows = [
            {"Line Item": "Total Revenue", "Amount": inc.get("total_revenue", 0)},
            {"Line Item": "Cost of Goods Sold (COGS)", "Amount": inc.get("cost_of_goods_sold", 0)},
            {"Line Item": "Gross Profit", "Amount": inc.get("gross_profit", 0)},
            {"Line Item": "Operating Expenses (OPEX)", "Amount": inc.get("operating_expenses", 0)},
            {"Line Item": "EBITDA", "Amount": inc.get("ebitda", 0)},
            {"Line Item": "Depreciation & Amortization", "Amount": inc.get("depreciation_amortization", 0)},
            {"Line Item": "EBIT (Operating Income)", "Amount": inc.get("ebit", 0)},
            {"Line Item": "Interest Expense", "Amount": inc.get("interest_expense", 0)},
            {"Line Item": "Tax Expense", "Amount": inc.get("tax_expense", 0)},
            {"Line Item": "NET INCOME", "Amount": inc.get("net_income", 0)}
        ]
        pd.DataFrame(inc_rows).to_excel(writer, sheet_name="Income Statement", index=False)

        # Sheet 4: Ratios
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
                            "Status": r.get("status", "INFO")
                        })
        if r_rows:
            pd.DataFrame(r_rows).to_excel(writer, sheet_name="Ratio Analysis", index=False)

    output.seek(0)
    return output.getvalue()
