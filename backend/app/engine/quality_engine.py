"""
Financial Data Quality & Confidence Engine Module
Calculates a 0.0 to 100.0 Quality Score across Extraction, Accounting Equations, and Reconciliation.
Enforces that confidence level cannot be HIGH if critical reconciliation failures exist.
"""

from typing import Dict, Any

def compute_financial_quality_score(
    reconciliation_report: Dict[str, Any],
    validation_report: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes a comprehensive 100-point Financial Data Quality Score.
    
    1. Extraction & Mapping Quality (30 pts)
    2. Balance Sheet Equation Validation (25 pts)
    3. Cash Flow Equation Validation (20 pts)
    4. Source-to-Result Reconciliation Pass Rate (25 pts)
    """
    rec_status = reconciliation_report.get("reconciliation_status", "FAIL")
    failed_count = reconciliation_report.get("failed_count", 0)
    passed_count = reconciliation_report.get("passed_count", 0)
    total_checked = reconciliation_report.get("total_metrics_checked", 1)

    bs_status = validation_report.get("balance_sheet_check", "FAIL")
    cf_status = validation_report.get("cash_flow_check", "NOT_AVAILABLE")

    # 1. Extraction & Mapping (Max 30 pts)
    extraction_pts = 30.0 if failed_count == 0 else max(0.0, 30.0 - (failed_count * 10.0))

    # 2. Balance Sheet Check (Max 25 pts)
    bs_pts = 25.0 if bs_status == "PASS" else 0.0

    # 3. Cash Flow Check (Max 20 pts)
    cf_pts = 20.0 if cf_status in ["PASS", "NOT_AVAILABLE"] else 0.0

    # 4. Reconciliation Pass Rate (Max 25 pts)
    not_available_count = reconciliation_report.get("not_available_count", 0)
    reported_checked = max(1, total_checked - not_available_count)
    pass_rate = passed_count / reported_checked
    reconciliation_pts = round(pass_rate * 25.0, 1)

    total_score = round(min(100.0, max(0.0, extraction_pts + bs_pts + cf_pts + reconciliation_pts)), 1)
    
    tb_status = validation_report.get("trial_balance_check", "PASS")
    ni_status = validation_report.get("net_income_reconciliation_check", "PASS")

    # HARD GATE: If balance sheet check or trial balance check fails, cap score at 50.0 and require review
    quality_status = "VERIFIED"
    if bs_status == "FAIL":
        total_score = min(50.0, total_score)
        confidence_level = "LOW"
        quality_status = "VALIDATION_FAILED"
    elif tb_status == "FAIL":
        total_score = min(50.0, total_score)
        confidence_level = "LOW"
        quality_status = "REVIEW_REQUIRED"
    elif total_score >= 90.0 and failed_count == 0 and bs_status == "PASS":
        confidence_level = "HIGH"
        if ni_status == "REVIEW_REQUIRED":
            quality_status = "REVIEW_REQUIRED"
    elif total_score >= 70.0 and failed_count == 0:
        confidence_level = "MEDIUM"
    else:
        confidence_level = "LOW"

    return {
        "quality_score": total_score,
        "quality_status": quality_status,
        "confidence_level": confidence_level,
        "is_reconciled": failed_count == 0 and bs_status == "PASS",
        "breakdown": {
            "extraction_and_mapping": round(extraction_pts, 1),
            "balance_sheet_equation": round(bs_pts, 1),
            "cash_flow_equation": round(cf_pts, 1),
            "source_reconciliation": round(reconciliation_pts, 1)
        }
    }

def calculate_financial_health_score(
    statements: Dict[str, Any],
    ratios: Dict[str, Any],
    canonical_dataset: Any = None,
    quality_report: Any = None
) -> Dict[str, Any]:
    """
    Authoritative single-source-of-truth function for computing the Financial Health Score.
    Guarantees absolute consistency between the narrative, report tables, and metadata.
    """
    if quality_report and isinstance(quality_report, dict) and "quality_score" in quality_report:
        score = quality_report["quality_score"]
    else:
        from app.engine.reconciliation import perform_source_to_result_reconciliation
        if not canonical_dataset:
            from app.engine.canonical_model import build_canonical_dataset
            items = statements.get("normalized_items", [])
            canonical_dataset = build_canonical_dataset(items, "5_Wipro.xlsx")
        rec = perform_source_to_result_reconciliation(canonical_dataset, statements, ratios)
        val = statements.get("validation_report", {})
        q_res = compute_financial_quality_score(rec, val)
        score = q_res["quality_score"]

    target_year = statements.get("ledger_summary", {}).get("target_year", "2026")
    return {
        "score": float(score),
        "period_type": "ANNUAL",
        "period_id": f"FY{target_year}",
        "methodology_version": "v1"
    }

