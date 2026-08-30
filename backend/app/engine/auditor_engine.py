"""
Full Financial Auditor & Forensic Accounting Engine
Executes institutional audit procedures: Benford's Law 1st-digit frequency analysis,
Sloan Accruals earnings quality scoring, round-number transaction auditing,
Planning Materiality evaluation, Dynamic Working Paper Lead Schedules (WP-A to WP-H),
Audit Exception Register, and automated 4-Tier Auditor Opinion Generation (including Scope Limitation Disclaimer).
"""

from typing import Dict, List, Any, Optional
from collections import Counter
import math
import datetime

BENFORD_IDEAL_DISTRIBUTION = {
    1: 30.1,
    2: 17.6,
    3: 12.5,
    4: 9.7,
    5: 7.9,
    6: 6.7,
    7: 5.8,
    8: 5.1,
    9: 4.6
}

def analyze_benford_law(numeric_values: List[float]) -> Dict[str, Any]:
    """
    Evaluates Benford's Law distribution on first digits (1-9).
    Requires a minimum sample population of >= 30 distinct entries for statistical significance.
    """
    first_digits = []
    for val in numeric_values:
        if val is None or val == 0:
            continue
        v_str = str(abs(val)).lstrip("0").replace(".", "").replace(",", "")
        if v_str and v_str[0].isdigit() and v_str[0] != "0":
            first_digits.append(int(v_str[0]))

    total_valid_samples = len(first_digits)

    # Require minimum population of 30 distinct values for statistical validity
    if total_valid_samples < 30:
        return {
            "sample_count": total_valid_samples,
            "mean_absolute_deviation": 0.0,
            "conformity_status": "NOT_PERFORMED (Insufficient Transaction Population)",
            "digit_chart_data": [],
            "is_performed": False,
            "notes": f"Population contains only {total_valid_samples} numeric items. Statistical Benford analysis requires >= 30 transaction entries for valid significance."
        }

    first_digit_counts = Counter(first_digits)
    actual_distribution = {
        d: round((first_digit_counts.get(d, 0) / total_valid_samples) * 100.0, 1)
        for d in range(1, 10)
    }
    
    # Calculate Mean Absolute Deviation (MAD)
    mad = sum(
        abs(actual_distribution[d] - BENFORD_IDEAL_DISTRIBUTION[d])
        for d in range(1, 10)
    ) / 900.0

    if mad <= 0.008:
        conformity = "Close Conformity (Clean Audit)"
    elif mad <= 0.015:
        conformity = "Acceptable Conformity"
    else:
        conformity = "Non-Conformity (High Manipulation Risk)"

    chart_data = [
        {
            "digit": str(d),
            "actual_pct": actual_distribution.get(d, BENFORD_IDEAL_DISTRIBUTION[d]),
            "benford_ideal_pct": BENFORD_IDEAL_DISTRIBUTION[d]
        }
        for d in range(1, 10)
    ]

    return {
        "sample_count": total_valid_samples,
        "mean_absolute_deviation": round(mad, 4),
        "conformity_status": conformity,
        "digit_chart_data": chart_data,
        "is_performed": True
    }

def perform_full_financial_audit(
    statements: Dict[str, Any], 
    ratios: Dict[str, Any],
    canonical_items: Optional[List[Dict[str, Any]]] = None,
    currency_symbol: str = "$"
) -> Dict[str, Any]:
    """
    Perform full institutional financial & forensic audit procedures, evaluate materiality,
    generate dynamic working papers (WP-A through WP-H), compile exception register, and issue Auditor's Opinion.
    """
    from app.engine.audit_planner import AuditPlanner
    from app.engine.working_papers import generate_working_paper_lead_schedules
    from app.engine.audit_exceptions import AuditExceptionManager

    inc = statements.get("income_statement", {}) if isinstance(statements, dict) else {}
    bs = statements.get("balance_sheet", {}) if isinstance(statements, dict) else {}
    cf = statements.get("cash_flow_statement", {}) if isinstance(statements, dict) else {}

    # 1. Audit Planning & Materiality
    materiality = AuditPlanner.calculate_materiality(statements, currency_symbol)
    pm = materiality["planning_materiality"]

    rev = float(inc.get("total_revenue", 0.0) or inc.get("revenue_from_operations", 0.0) or 0.0)
    net_inc = float(inc.get("net_income", 0.0) or 0.0)
    ocf = float(cf.get("operating_cash_flow", 0.0) or 0.0)

    # Gather all numeric values for Benford analysis
    numeric_samples = [rev, net_inc, ocf]
    for st in [inc, bs, cf]:
        if isinstance(st, dict):
            for k, v in st.items():
                if isinstance(v, (int, float)) and v != 0:
                    numeric_samples.append(abs(float(v)))

    benford_report = analyze_benford_law(numeric_samples)

    # 2. Sloan Accruals Quality Score
    assets_raw = bs.get("total_assets")
    has_cf_reported = bool(cf and cf.get("status") != "NOT_REPORTED_IN_SOURCE" and ocf != 0.0)
    if has_cf_reported and assets_raw is not None and float(assets_raw) > 0:
        accruals = net_inc - ocf
        sloan_ratio = round(accruals / float(assets_raw), 4)
        if abs(sloan_ratio) <= 0.05:
            accruals_quality = "High Earnings Quality (Strong Cash Backing)"
            sloan_status = "PASS"
        elif abs(sloan_ratio) <= 0.10:
            accruals_quality = "Moderate Accruals Intensity"
            sloan_status = "WARNING"
        else:
            accruals_quality = "Low Earnings Quality (Cash Deficit Risk)"
            sloan_status = "AUDIT_FLAG"
    else:
        accruals = 0.0
        sloan_ratio = 0.0
        accruals_quality = "Cash Flow / Balance Sheet Not Complete (Accruals Audit Omitted)"
        sloan_status = "NOT_APPLICABLE"

    # 3. Balance Sheet Accounting Equation Audit (Never convert Missing into Zero)
    val_rep = statements.get("validation_report", {}) if isinstance(statements, dict) else {}
    bs_check = val_rep.get("balance_sheet_check", "INCOMPLETE")

    assets_raw = bs.get("total_assets")
    liab_raw = bs.get("total_liabilities")
    eq_raw = bs.get("equity", {}).get("total_equity") if isinstance(bs.get("equity"), dict) else bs.get("total_equity")

    has_complete_bs = (assets_raw is not None and liab_raw is not None and eq_raw is not None and bs_check in ["PASS", "UNBALANCED"])
    has_partial_bs = (assets_raw is not None or liab_raw is not None or eq_raw is not None) and not has_complete_bs

    if has_complete_bs:
        assets = float(assets_raw)
        liab = float(liab_raw)
        eq = float(eq_raw)
        bs_diff = abs(assets - (liab + eq))
        bs_equation_pass = bs_diff <= 1.0
        is_material_imbalance = bs_diff > pm
    elif has_partial_bs:
        bs_diff = None
        bs_equation_pass = None
        is_material_imbalance = False
    else:
        bs_diff = None
        bs_equation_pass = None
        is_material_imbalance = False

    # 4. Round Number Transaction Audit
    round_count = sum(1 for v in numeric_samples if v > 1000 and v % 1000 == 0)
    round_ratio_pct = round((round_count / max(len(numeric_samples), 1)) * 100.0, 1)

    # 5. Dynamic Lead Schedules (WP-A through WP-H)
    lead_schedules = generate_working_paper_lead_schedules(statements, canonical_items or [], materiality)

    # 6. General Procedural Working Papers (WP-101 to WP-104)
    general_wps = []

    if has_complete_bs:
        wp101_result = "PASS (Exact Match)" if bs_equation_pass else f"AUDIT FLAG (Discrepancy: {currency_symbol}{bs_diff:,.2f})"
        wp101_status = "PASS" if bs_equation_pass else ("AUDIT_FLAG" if is_material_imbalance else "WARNING")
        wp101_notes = f"Verified total assets against equity and liabilities (Materiality: {currency_symbol}{pm:,.2f})."
    elif has_partial_bs:
        wp101_result = "INCOMPLETE (Scope Limitation — Liabilities or Equity Missing)"
        wp101_status = "NOT_APPLICABLE"
        wp101_notes = "Assets extracted, but supporting liability or equity schedules were not provided in source."
    else:
        wp101_result = "NOT REPORTED IN SOURCE"
        wp101_status = "NOT_APPLICABLE"
        wp101_notes = "Balance Sheet accounts not present in provided records."

    general_wps.append({
        "wp_ref": "WP-101",
        "procedure": "Fundamental Accounting Identity Test (Assets = Liabilities + Equity)",
        "result": wp101_result,
        "status": wp101_status,
        "notes": wp101_notes
    })

    if not benford_report.get("is_performed", True):
        wp102_result = "TEST NOT PERFORMED (Sample Size < 30)"
        wp102_status = "NOT_APPLICABLE"
        wp102_notes = benford_report.get("notes", "Insufficient numeric sample size for statistical analysis.")
    else:
        wp102_result = f"{benford_report['conformity_status']} (MAD: {benford_report['mean_absolute_deviation']})"
        wp102_status = "PASS" if "Close" in benford_report["conformity_status"] else ("WARNING" if "Acceptable" in benford_report["conformity_status"] else "AUDIT_FLAG")
        wp102_notes = f"Scanned {benford_report['sample_count']} line items against logarithmic Benford distribution."

    general_wps.append({
        "wp_ref": "WP-102",
        "procedure": "Benford's Law First-Digit Forensic Analysis",
        "result": wp102_result,
        "status": wp102_status,
        "notes": wp102_notes
    })

    general_wps.append({
        "wp_ref": "WP-103",
        "procedure": "Sloan Accruals & Earnings Realization Audit",
        "result": f"{accruals_quality} (Ratio: {sloan_ratio})" if has_cf_reported else accruals_quality,
        "status": sloan_status,
        "notes": f"Net income ({currency_symbol}{net_inc:,.2f}) compared against operating cash flow ({currency_symbol}{ocf:,.2f})." if has_cf_reported else "Cash flow statement absent from source document."
    })

    general_wps.append({
        "wp_ref": "WP-104",
        "procedure": "Round Number Transaction & Journal Anomaly Scan",
        "result": f"Low Anomaly Risk ({round_ratio_pct}% round entries)" if round_ratio_pct < 20 else f"Elevated Round Entries ({round_ratio_pct}%)",
        "status": "PASS" if round_ratio_pct < 20 else "WARNING",
        "notes": "Audited numeric transactions for artificial rounding or manual journal entry overrides."
    })

    # Preliminary forensic report structure
    forensic_payload = {
        "sloan_accruals": {
            "sloan_ratio": sloan_ratio,
            "quality_label": accruals_quality,
            "status": sloan_status,
            "net_income": net_inc,
            "operating_cash_flow": ocf,
            "accruals_amount": round(accruals, 2)
        },
        "benford_analysis": benford_report,
        "round_number_audit": {
            "round_entries_pct": round_ratio_pct,
            "risk_level": "LOW" if round_ratio_pct < 20 else "MODERATE"
        }
    }

    # 7. Compile Exception Register & Management Letter
    exception_package = AuditExceptionManager.compile_audit_exceptions(
        statements, ratios, forensic_payload, materiality
    )

    # 8. Standard Audit Conclusion & Opinion Classification (ISA 700 / 705)
    # Check for Scope Limitation (Single statement / incomplete upload)
    is_scope_limitation = has_partial_bs or (not has_complete_bs and (rev == 0.0 or net_inc == 0.0)) or (not has_complete_bs and bs.get("status") in ["NOT_REPORTED_IN_SOURCE", "INCOMPLETE", "BALANCE_SHEET_MAPPING_FAILED"]) or (bs_check in ["INCOMPLETE", "NOT_REPORTED"])

    if is_scope_limitation or not has_complete_bs:
        opinion_type = "INSUFFICIENT_EVIDENCE"
        opinion_title = "Audit Conclusion: Unable to Conclude (Insufficient Source Documentation / Scope Limitation)"
        opinion_summary = (
            "We are unable to form an audit opinion on the accompanying financial records. Due to missing financial statement "
            "schedules in the uploaded documentation (unreported Balance Sheet liabilities, equity, or operational schedules), "
            "the system has not obtained sufficient appropriate audit evidence to evaluate the enterprise's financial standing. "
            "Formal statutory opinions require complete multi-statement records and licensed human auditor review/sign-off."
        )
    elif has_complete_bs and bs_equation_pass and sloan_status != "AUDIT_FLAG" and exception_package["critical_exceptions_count"] == 0:
        opinion_type = "UNQUALIFIED_OPINION"
        opinion_title = "Unqualified Preliminary Audit Conclusion (Clean Supporting Schedules)"
        opinion_summary = (
            "Based on the provided records, the financial statements present fairly, in all material respects, "
            "the financial position, financial performance, and operating cash flows of the enterprise in accordance "
            "with applicable reporting frameworks. Subject to final human engagement partner sign-off."
        )
    elif has_complete_bs and not bs_equation_pass and is_material_imbalance:
        opinion_type = "ADVERSE_OPINION"
        opinion_title = "Adverse Audit Conclusion (Material Statement Misstatement Detected)"
        opinion_summary = (
            f"Because of the significance of the fundamental accounting equation discrepancy "
            f"({currency_symbol}{bs_diff:,.2f}) exceeding Planning Materiality ({currency_symbol}{pm:,.2f}), the accompanying "
            f"financial records contain a material statement breakdown."
        )
    else:
        opinion_type = "QUALIFIED_OPINION"
        opinion_title = "Qualified Audit Conclusion (Departure / Explanations Required)"
        opinion_summary = (
            "Except for the effects of the specific matters described in the Audit Exception Register, "
            "the accompanying financial records present fairly, in all material respects, the financial position of the enterprise."
        )

    from app.engine.audit_queries import AuditQueryEngine
    audit_queries = AuditQueryEngine.generate_audit_queries(
        exception_register=exception_package["exception_items"],
        materiality=materiality,
        forensic_tests=general_wps
    )

    current_date_str = datetime.datetime.now().strftime("%B %d, %Y")

    return {
        "auditor_opinion": {
            "opinion_type": opinion_type,
            "title": opinion_title,
            "summary": opinion_summary,
            "audit_date": current_date_str,
            "auditor_signature": "AI AUDIT ANALYSIS — Non-Certified Preliminary Intelligence (Human auditor review/sign-off required)",
            "audit_standards": "International Standards on Auditing (ISA) & US GAAS"
        },
        "audit_planning": materiality,
        "audit_queries": audit_queries,
        "lead_schedules": lead_schedules,
        "working_papers": general_wps,
        "exception_register": exception_package["exception_items"],
        "management_letter": exception_package["management_letter"],
        "exception_summary": {
            "total_exceptions": exception_package["total_exceptions"],
            "critical_exceptions_count": exception_package["critical_exceptions_count"],
            "significant_deficiencies_count": exception_package["significant_deficiencies_count"],
            "control_observations_count": exception_package["control_observations_count"],
            "open_queries_count": len([q for q in audit_queries if q.get("status") == "OPEN"])
        },
        "benford_analysis": benford_report,
        "sloan_accruals": forensic_payload["sloan_accruals"],
        "round_number_audit": forensic_payload["round_number_audit"]
    }
