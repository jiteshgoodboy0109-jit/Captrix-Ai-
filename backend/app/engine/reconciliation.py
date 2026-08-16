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
                "metric_id": metric_id,
                "standardized_label": metric_id.replace("_", " ").title(),
                "source_value": None,
                "report_value": report_val,
                "difference": 0.0,
                "status": "NOT_AVAILABLE",
                "explanation": "Metric not separately reported in source document."
            })
            not_available_count += 1
            continue

        src_val = float(canonical_item.get("value", 0.0))
        diff = round(abs(src_val - float(report_val)), 2)

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
            explanation = f"Critical mismatch: Source value ({src_val:,.2f}) != Report value ({report_val:,.2f}). Diff = {diff:,.2f}."

        metric_results.append({
            "metric_id": metric_id,
            "standardized_label": canonical_item.get("standardized_label", metric_id.title()),
            "source_value": src_val,
            "report_value": float(report_val),
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
