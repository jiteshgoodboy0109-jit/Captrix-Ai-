"""
Wipro Golden Test & Benchmark Suite
Embedded regression benchmark evaluating model candidates against authoritative ground truth values.
"""

from typing import Dict, Any
from app.engine.model_evaluator import run_automatic_model_discovery, evaluate_model_extraction

WIPRO_GROUND_TRUTH: Dict[str, Any] = {
    "company": "Wipro Limited",
    "period": "FY2026",
    "currency": "INR",
    "unit": "Crores",
    "total_revenue": 92624.0,
    "tax": 4076.7,
    "net_income": 13197.4,
    "interest": 1457.7,
    "total_assets": 140883.5,
    "borrowings": 20291.0,
    "total_liabilities": 65000.0,
    "total_equity": 75883.5,
    "operating_cash_flow": 14931.6,
    "investing_cash_flow": -2447.5,
    "financing_cash_flow": -14126.0,
    "net_cash_flow": -1641.9,
    "goodwill": "Not Separately Reported"
}

# Simulated candidate model outputs for regression benchmarking
CANDIDATE_MODEL_EXTRACTIONS: Dict[str, Dict[str, Any]] = {
    "deterministic-source-parser": {
        "total_revenue": 92624.0,
        "tax": 4076.7,
        "net_income": 13197.4,
        "interest": 1457.7,
        "total_assets": 140883.5,
        "borrowings": 20291.0,
        "total_liabilities": 65000.0,
        "total_equity": 75883.5,
        "operating_cash_flow": 14931.6,
        "investing_cash_flow": -2447.5,
        "financing_cash_flow": -14126.0,
        "net_cash_flow": -1641.9,
        "goodwill": "Not Separately Reported"
    },
    "gemini-3.6-flash-high": {
        "total_revenue": 92624.0,
        "tax": 4076.7,
        "net_income": 13197.4,
        "interest": 1457.7,
        "total_assets": 140883.5,
        "borrowings": 20291.0,
        "total_liabilities": 65000.0,
        "total_equity": 75883.5,
        "operating_cash_flow": 14931.6,
        "investing_cash_flow": -2447.5,
        "financing_cash_flow": -14126.0,
        "net_cash_flow": -1641.9,
        "goodwill": "Not Separately Reported"
    },
    "gemini-1.5-pro": {
        "total_revenue": 92624.0,
        "tax": 4076.7,
        "net_income": 13197.4,
        "interest": 1457.7,
        "total_assets": 140883.5,
        "borrowings": 20291.0,
        "total_liabilities": 65000.0,
        "total_equity": 75883.5,
        "operating_cash_flow": 14931.6,
        "investing_cash_flow": -2447.5,
        "financing_cash_flow": -14126.0,
        "net_cash_flow": -1641.9,
        "goodwill": "Not Separately Reported"
    },
    "gpt-4o-financial-extractor": {
        "total_revenue": 92624.0,
        "tax": 4076.7,
        "net_income": -14092.82,  # Simulated sign error to test critical failure penalty
        "interest": 1457.7,
        "total_assets": 140883.5,
        "borrowings": 20291.0,
        "total_liabilities": 65000.0,
        "total_equity": 75883.5,
        "operating_cash_flow": 14931.6,
        "investing_cash_flow": -2447.5,
        "financing_cash_flow": -14126.0,
        "net_cash_flow": -1641.9,
        "goodwill": 4523.2  # Simulated hallucination
    },
    "claude-3-5-sonnet-financial": {
        "total_revenue": 91624.0,  # Value mismatch
        "tax": 4076.7,
        "net_income": 13197.4,
        "interest": 1457.7,
        "total_assets": 140883.5,
        "borrowings": 20291.0,
        "total_liabilities": 65000.0,
        "total_equity": 75883.5,
        "operating_cash_flow": 14931.6,
        "investing_cash_flow": -2447.5,
        "financing_cash_flow": -14126.0,
        "net_cash_flow": -1641.9,
        "goodwill": "Not Separately Reported"
    }
}

def run_wipro_golden_benchmark() -> Dict[str, Any]:
    """Execute the golden Wipro regression benchmark across all registered candidate models."""
    profile = {
        "filename": "Wipro_FY2026_Audited_Financials.xlsx",
        "type": "excel_workbook",
        "sheet_count": 4,
        "total_rows": 280,
        "table_density": 0.85,
        "layout_complexity": "high",
        "requires_vision": False,
        "requires_ocr": False,
        "financial_statement_count": 4,
        "number_of_periods": 3,
        "currency": "INR",
        "unit": "Crores"
    }

    result = run_automatic_model_discovery(
        ground_truth_metrics=WIPRO_GROUND_TRUTH,
        candidate_extractions=CANDIDATE_MODEL_EXTRACTIONS,
        document_profile=profile
    )

    result["benchmark_name"] = "Wipro FY2026 Golden Regression Benchmark"
    result["passed_regression_test"] = result["critical_metric_accuracy"] >= 98.0 and result["hallucination_rate_pct"] == 0.0

    return result
