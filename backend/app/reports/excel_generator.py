import io
import pandas as pd
from typing import Dict, Any, List, Optional

def format_excel_val(val: Any) -> Any:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return val

def generate_excel_report(
    company_name: str, 
    statements: Dict[str, Any], 
    ratios: Dict[str, Any], 
    corp_fin: Dict[str, Any], 
    ai_reports: Dict[str, Any],
    audit_report: Optional[Dict[str, Any]] = None
) -> bytes:
    output = io.BytesIO()
    
    val_report = statements.get("validation_report", {})
    bs_status = val_report.get("balance_sheet_check", "FAIL")

    from app.engine.quality_engine import calculate_financial_health_score
    health_obj = calculate_financial_health_score(statements, ratios, ai_reports.get("canonical_dataset"), ai_reports.get("quality_report"))
    health_score = health_obj["score"] if bs_status == "PASS" else "NOT_CALCULABLE"

    if audit_report is None:
        from app.engine.auditor_engine import perform_full_financial_audit
        audit_report = perform_full_financial_audit(statements, ratios)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # 1. Executive Summary & Health
        target_year = statements.get("ledger_summary", {}).get("target_year", "UNKNOWN")
        latest_period_str = str(target_year)

        summary_rows = [
            {"Metric": "Company Name", "Value": company_name},
            {"Metric": "Financial Health Score", "Value": health_score},
            {"Metric": "Balance Sheet Validation Status", "Value": f"BALANCE SHEET: {bs_status}"},
            {"Metric": "Latest Period", "Value": latest_period_str},
            {"Metric": "Executive Summary", "Value": ai_reports.get("executive_summary", "")}
        ]

        inc_latest = statements.get("income_statement", {})
        if inc_latest.get("revenue_from_operations") is not None:
            summary_rows.append({"Metric": "Revenue from Operations (Latest)", "Value": inc_latest.get("revenue_from_operations")})
        if inc_latest.get("total_revenue") is not None:
            summary_rows.append({"Metric": "Total Revenue (Latest)", "Value": inc_latest.get("total_revenue")})
        if inc_latest.get("net_income") is not None:
            summary_rows.append({"Metric": "Net Profit (Latest)", "Value": inc_latest.get("net_income")})

        cr_val = ratios.get("liquidity", {}).get("current_ratio", {}).get("value")
        if cr_val is not None and ratios.get("liquidity", {}).get("current_ratio", {}).get("is_calculable", True):
            summary_rows.append({"Metric": "Current Ratio (Latest)", "Value": cr_val})

        de_val = ratios.get("solvency", {}).get("debt_to_equity", {}).get("value")
        if de_val is not None and ratios.get("solvency", {}).get("debt_to_equity", {}).get("is_calculable", True):
            summary_rows.append({"Metric": "Debt-to-Equity (Latest)", "Value": de_val})

        pd.DataFrame(summary_rows).to_excel(writer, sheet_name="Executive Summary & Health", index=False)

        # 2. Validation & Audit Report
        opinion_obj = audit_report.get("auditor_opinion", {})
        planning_obj = audit_report.get("audit_planning", {})
        
        audit_overview_rows = [
            {"Audit Dimension": "Company Target", "Audit Assessment": company_name},
            {"Audit Dimension": "Auditor Opinion Type", "Audit Assessment": opinion_obj.get("opinion_type", "UNQUALIFIED_OPINION")},
            {"Audit Dimension": "Opinion Title", "Audit Assessment": opinion_obj.get("title", "")},
            {"Audit Dimension": "Opinion Summary", "Audit Assessment": opinion_obj.get("summary", "")},
            {"Audit Dimension": "Auditor Sign-off", "Audit Assessment": opinion_obj.get("auditor_signature", "Captrix AI-Assisted Automated Audit Intelligence (Non-Certified Finding — Requires Human Auditor Sign-Off)")},
            {"Audit Dimension": "Applicable Standards", "Audit Assessment": opinion_obj.get("audit_standards", "ISA / US GAAS")},
            {"Audit Dimension": "Planning Materiality (PM)", "Audit Assessment": planning_obj.get("planning_materiality", 0)},
            {"Audit Dimension": "Performance Materiality (75%)", "Audit Assessment": planning_obj.get("performance_materiality", 0)},
            {"Audit Dimension": "Clearly Trivial Limit (5%)", "Audit Assessment": planning_obj.get("clearly_trivial_threshold", 0)},
            {"Audit Dimension": "Materiality Benchmark Basis", "Audit Assessment": planning_obj.get("benchmark_basis", "")},
            {"Audit Dimension": "Materiality Statement", "Audit Assessment": planning_obj.get("materiality_statement", "")}
        ]
        pd.DataFrame(audit_overview_rows).to_excel(writer, sheet_name="Validation & Audit Report", index=False)

        # 3. Source Data Summary
        norm_items = statements.get("normalized_items", [])
        src_rows = []
        for i in norm_items:
            src_rows.append({
                "Account Code": i.get("account_code", ""),
                "Account Name": i.get("account_name", ""),
                "Classification": i.get("account_type", ""),
                "Net Amount": i.get("net_amount", 0.0),
                "Period": i.get("fiscal_year") or i.get("year") or "UNKNOWN",
                "Source Sheet": i.get("source_sheet", "Sheet1"),
                "Source Cell": i.get("source_cell", ""),
                "Source Row": i.get("source_row", ""),
                "Source Column": i.get("source_column", ""),
                "Raw Label in Source": i.get("source_label", "")
            })
        if src_rows:
            pd.DataFrame(src_rows).to_excel(writer, sheet_name="Source Data Summary", index=False)

        # 4. Multi-Year Statements (Consolidated & Dynamic)
        years = statements.get("multi_period_statements", {}).get("years", [latest_period_str])
        if not years:
            years = [latest_period_str]

        inc_keys = [
            ("Revenue from Operations", "revenue_from_operations"),
            ("Other Income", "other_income"),
            ("Total Revenue", "total_revenue"),
            ("Cost of Goods Sold (COGS)", "cost_of_goods_sold"),
            ("Gross Profit", "gross_profit"),
            ("Operating Expenses (OPEX)", "operating_expenses"),
            ("EBITDA", "ebitda"),
            ("Depreciation & Amortization", "depreciation_amortization"),
            ("EBIT (Operating Profit)", "ebit"),
            ("Interest Expense", "interest_expense"),
            ("Profit Before Tax (PBT)", "ebt"),
            ("Income Tax Expense", "tax_expense"),
            ("Net Income", "net_income")
        ]

        bs_keys = [
            ("Cash and Cash Equivalents", ["current_assets", "cash"]),
            ("Accounts Receivable", ["current_assets", "accounts_receivable"]),
            ("Inventory", ["current_assets", "inventory"]),
            ("Supplies", ["current_assets", "supplies"]),
            ("Prepaid Insurance", ["current_assets", "prepaid_insurance"]),
            ("Total Current Assets", ["current_assets", "total_current_assets"]),
            ("Investments", ["investment"]),
            ("Net Property, Plant & Equipment", ["property_plant_equipment", "net_property_plant_equipment"]),
            ("Total Intangible Assets", ["intangible_assets", "total_intangible_assets"]),
            ("Other Assets", ["other_assets"]),
            ("TOTAL ASSETS", ["total_assets"]),
            ("Notes Payable (Current)", ["current_liabilities", "notes_payable"]),
            ("Accounts Payable", ["current_liabilities", "accounts_payable"]),
            ("Wages Payable", ["current_liabilities", "wages_payable"]),
            ("Tax Payable", ["current_liabilities", "tax_payable"]),
            ("Total Current Liabilities", ["current_liabilities", "total_current_liabilities"]),
            ("Long-term Notes Payable", ["long_term_liabilities", "notes_payable_lt"]),
            ("Bonds Payable", ["long_term_liabilities", "bonds_payable"]),
            ("Total Long-term Liabilities", ["long_term_liabilities", "total_long_term_liabilities"]),
            ("TOTAL LIABILITIES", ["total_liabilities"]),
            ("Common Stock / Share Capital", ["equity", "common_stock"]),
            ("Retained Earnings", ["equity", "retained_earnings"]),
            ("Treasury Stock", ["equity", "treasury_stock"]),
            ("TOTAL EQUITY", ["equity", "total_equity"]),
            ("TOTAL LIABILITIES & EQUITY", ["total_liabilities_and_equity"])
        ]

        multi_stmt_table = []
        for label, k in inc_keys:
            row_data = {"Statement Section": "Income Statement", "Line Item": label}
            has_valid = False
            for yr in years:
                st = statements.get("multi_period_statements", {}).get("by_year", {}).get(yr, {}).get("income_statement", {})
                if not st and yr == latest_period_str:
                    st = statements.get("income_statement", {})
                val = st.get(k)
                if val is not None and not (isinstance(val, float) and pd.isna(val)):
                    has_valid = True
                row_data[yr] = format_excel_val(val)
            if has_valid:
                multi_stmt_table.append(row_data)

        for label, path in bs_keys:
            row_data = {"Statement Section": "Balance Sheet", "Line Item": label}
            has_valid = False
            for yr in years:
                st = statements.get("multi_period_statements", {}).get("by_year", {}).get(yr, {}).get("balance_sheet", {})
                if not st and yr == latest_period_str:
                    st = statements.get("balance_sheet", {})
                
                curr_dict = st
                for p in path:
                    if isinstance(curr_dict, dict):
                        curr_dict = curr_dict.get(p)
                    else:
                        curr_dict = None
                        break
                
                if curr_dict is not None and not (isinstance(curr_dict, float) and pd.isna(curr_dict)):
                    has_valid = True
                row_data[yr] = format_excel_val(curr_dict)
            if has_valid:
                multi_stmt_table.append(row_data)

        if multi_stmt_table:
            pd.DataFrame(multi_stmt_table).to_excel(writer, sheet_name="Statements (Multi-Year)", index=False)

        # 5. Lead Schedules (WP-A to WP-H)
        lead_scheds = audit_report.get("lead_schedules", [])
        lead_rows = []
        for ls in lead_scheds:
            for line in ls.get("lines", []):
                lead_rows.append({
                    "Schedule Ref": ls.get("schedule_ref"),
                    "Schedule Title": ls.get("title"),
                    "Category": ls.get("category"),
                    "Account Line Item": line.get("account_name"),
                    "Source Cross-Ref": line.get("cross_ref"),
                    "Audited Amount": line.get("amount"),
                    "Verification Status": line.get("status")
                })
        if lead_rows:
            pd.DataFrame(lead_rows).to_excel(writer, sheet_name="Lead Schedules (WP-A to H)", index=False)

        # 6. Exception Register & Management Letter
        exc_list = audit_report.get("exception_register", [])
        exc_rows = []
        for exc in exc_list:
            exc_rows.append({
                "Exception ID": exc.get("exception_id"),
                "Audit Area": exc.get("audit_area"),
                "Issue Title": exc.get("issue_title"),
                "Description": exc.get("description"),
                "Severity": exc.get("severity"),
                "Impact Amount": exc.get("impact_amount"),
                "Status": exc.get("status"),
                "Auditor Remediation": exc.get("remediation")
            })
        if exc_rows:
            pd.DataFrame(exc_rows).to_excel(writer, sheet_name="Audit Exception Register", index=False)

        # 7. Ratio Analysis (Only Calculable)
        ratio_rows = []
        for cat, cat_ratios in ratios.items():
            if isinstance(cat_ratios, dict):
                for r_key, r in cat_ratios.items():
                    if isinstance(r, dict):
                        is_calc = r.get("is_calculable", True)
                        val = r.get("value")
                        stat = r.get("status")
                        if is_calc and val is not None and stat not in ["NOT_CALCULABLE", "DATA_MISSING", "N/A"]:
                            ratio_rows.append({
                                "Category": cat.capitalize(),
                                "Ratio Name": r.get("name", r_key),
                                "Formula": r.get("formula", "-"),
                                "Calculated Value": val,
                                "Benchmark": r.get("benchmark", "-"),
                                "Audit Status": stat
                            })
        if ratio_rows:
            pd.DataFrame(ratio_rows).to_excel(writer, sheet_name="Ratio Analysis", index=False)

    output.seek(0)
    return output.getvalue()
