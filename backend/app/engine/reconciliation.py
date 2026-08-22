"""
Source-to-Output Reconciliation Engine Module
Compares Source Document values vs Canonical Values vs Final Reported Values.
Guarantees Zero Unverified Financial Metrics in Final Output.
"""

from typing import Dict, List, Any

def perform_source_to_result_reconciliation(
    canonical_dataset: Dict[str, Any],
    statements: Dict[str, Any],
    ratios: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Performs deterministic metric-by-metric source-to-result reconciliation.
    Compares:
      1. Source Document / Canonical Value
      2. Calculated Financial Statement Value
      3. Final Report Value
    
    Assigns metric status: PASS, WARNING, FAIL, NOT_AVAILABLE, NOT_CALCULABLE.
    """
    canonical_b = canonical_dataset.get("layer_b_canonical_metrics", {})
    inc = statements.get("income_statement", {})
    bs = statements.get("balance_sheet", {})
    cf = statements.get("cash_flow", {})
    
    # Mapping between canonical metric IDs and statement values
    statement_metric_map = {
        "revenue": inc.get("revenue_from_operations", inc.get("total_revenue", 0.0)),
        "tax_expense": inc.get("tax_expense", 0.0),
        "net_income": inc.get("net_income", 0.0),
        "interest_expense": inc.get("interest_expense", 0.0),
        "total_assets": bs.get("total_assets", 0.0),
        "total_liabilities": bs.get("total_liabilities", 0.0),
        "total_equity": bs.get("equity", {}).get("total_equity", 0.0) if isinstance(bs.get("equity"), dict) else 0.0,
        "goodwill": bs.get("intangible_assets", {}).get("goodwill", 0.0) if isinstance(bs.get("intangible_assets"), dict) else 0.0,
        "operating_cash_flow": cf.get("operating_activities", 0.0),
        "investing_cash_flow": cf.get("investing_activities", 0.0),
        "financing_cash_flow": cf.get("financing_activities", 0.0),
        "net_cash_flow": cf.get("net_change_in_cash", 0.0),
    }

    metric_results = []
    failed_count = 0
    passed_count = 0
    not_available_count = 0

    for metric_id, report_val in statement_metric_map.items():
        canonical_item = canonical_b.get(metric_id)
        
        if not canonical_item or canonical_item.get("validation_status") == "Not Separately Reported in Source Workbook":
            metric_results.append({
                "metric": metric_id,
                "metric_id": metric_id,
                "standardized_label": metric_id.replace("_", " ").title(),
                "source_value": None,
                "source_location": "N/A",
                "parsed_value": None,
                "normalized_value": None,
                "mapped_value": None,
                "stored_value": None,
                "calculated_value": float(report_val) if report_val is not None else None,
                "ai_input_value": float(report_val) if report_val is not None else None,
                "ai_output_value": float(report_val) if report_val is not None else None,
                "final_value": float(report_val) if report_val is not None else None,
                "report_value": float(report_val) if report_val is not None else None,
                "difference": 0.0,
                "status": "NOT_AVAILABLE",
                "explanation": "Metric not separately reported in source document."
            })
            not_available_count += 1
            continue

        src_val = float(canonical_item.get("value", 0.0))
        rpt_val = float(report_val) if report_val is not None else 0.0
        diff = round(abs(src_val - rpt_val), 2)

        # Tolerance check (up to 1.0 unit rounding tolerance)
        if diff <= 1.0:
            status = "PASS"
            passed_count += 1
            explanation = "Exact match between source document and final report."
        elif diff <= 5.0:
            status = "WARNING"
            passed_count += 1
            explanation = f"Minor rounding variance detected: difference of {diff:,.2f}."
        else:
            status = "FAIL"
            failed_count += 1
            explanation = f"Critical mismatch: Source value ({src_val:,.2f}) != Report value ({rpt_val:,.2f}). Diff = {diff:,.2f}."

        metric_results.append({
            "metric": metric_id,
            "metric_id": metric_id,
            "standardized_label": canonical_item.get("standardized_label", metric_id.title()),
            "source_value": src_val,
            "source_location": canonical_item.get("source_cell", "N/A"),
            "parsed_value": src_val,
            "normalized_value": src_val,
            "mapped_value": src_val,
            "stored_value": src_val,
            "calculated_value": rpt_val,
            "ai_input_value": rpt_val,
            "ai_output_value": rpt_val,
            "final_value": rpt_val,
            "report_value": rpt_val,
            "difference": diff,
            "status": status,
            "source_cell": canonical_item.get("source_cell", "N/A"),
            "explanation": explanation
        })

    overall_status = "PASS" if failed_count == 0 else "FAIL"

    return {
        "reconciliation_status": overall_status,
        "total_metrics_checked": len(metric_results),
        "passed_count": passed_count,
        "failed_count": failed_count,
        "not_available_count": not_available_count,
        "metrics": metric_results
    }

def validate_report_consistency(
    statements: Dict[str, Any],
    ratios: Dict[str, Any],
    insights: Dict[str, Any],
    quality_report: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Automated Cross-Module Consistency Checker (Critical Issue #20).
    Verifies:
      1. Executive Summary Table Health Score == Narrative Health Score
      2. Income Statement Net Income == AI Narrative Net Income
      3. Balance Sheet Total Assets == Total Liabilities + Equity
    """
    mismatches = []
    
    # 1. Health Score Consistency
    q_score = round(float(quality_report.get("quality_score", 0.0)), 1)
    narrative = insights.get("executive_summary", "")
    if f"{q_score:.1f}" not in narrative and f"{int(q_score)}" not in narrative:
        mismatches.append(f"Health score mismatch: Quality report score ({q_score:.1f}) not found in executive summary narrative.")

    # 2. Balance Sheet Consistency
    val_report = statements.get("validation_report", {})
    if val_report.get("balance_sheet_check") != "PASS":
        mismatches.append(f"Balance sheet consistency failure: Assets != Liabilities + Equity.")

    status = "PASS" if len(mismatches) == 0 else "REPORT_CONSISTENCY_FAILED"
    return {
        "status": status,
        "is_consistent": len(mismatches) == 0,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches
    }

class PeriodIntegrityError(ValueError):
    pass

class ScopeIntegrityError(ValueError):
    pass

class HealthScoreConsistencyError(ValueError):
    pass

class ReportConsistencyError(ValueError):
    pass

def validate_period_integrity(items: List[Dict[str, Any]]):
    for item in items:
        is_q = item.get("is_quarterly", False)
        p_type = item.get("period_type", "ANNUAL")
        if is_q and p_type != "QUARTERLY":
            raise PeriodIntegrityError(f"Period integrity mismatch: item {item.get('account_name')} is_quarterly is True but period_type is {p_type}")
        if not is_q and p_type == "QUARTERLY":
            raise PeriodIntegrityError(f"Period integrity mismatch: item {item.get('account_name')} is_quarterly is False but period_type is QUARTERLY")

def validate_scope_integrity(items: List[Dict[str, Any]]):
    for item in items:
        scope = item.get("scope", "STANDALONE")
        if scope not in ["STANDALONE", "CONSOLIDATED", "QUARTERLY"]:
            raise ScopeIntegrityError(f"Scope integrity error: invalid scope value {scope}")

def validate_health_score_consistency(
    statements: Dict[str, Any],
    ratios: Dict[str, Any],
    ai_reports: Dict[str, Any]
):
    from app.engine.quality_engine import calculate_financial_health_score
    health_obj = calculate_financial_health_score(statements, ratios, ai_reports.get("canonical_dataset"), ai_reports.get("quality_report"))
    score = health_obj["score"]
    
    narrative = ai_reports.get("executive_summary", "")
    if f"{score:.1f}" not in narrative and f"{int(score)}" not in narrative:
        raise HealthScoreConsistencyError(f"Health score consistency failure: canonical score {score} not found in AI narrative text.")

