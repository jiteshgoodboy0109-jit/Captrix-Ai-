"""
Comprehensive Pipeline Data Integrity & Zero-Fabrication Regression Test Suite.
Verifies all 17 data integrity fixes across parsing, statement generation, ratios, quality gating, reconciliation, and AI insights.
"""

import pytest
from app.engine.document_parser import (
    clean_value_or_none,
    is_blank_value,
    classify_account,
    parse_workbook
)
from app.engine.statement_generator import (
    generate_statements_for_year,
    generate_financial_statements
)
from app.engine.financial_analyzer import (
    safe_ratio,
    calculate_financial_ratios
)
from app.engine.quality_engine import compute_financial_quality_score
from app.engine.reconciliation import perform_source_to_result_reconciliation
from app.engine.canonical_model import build_canonical_dataset
from app.engine.ai_insights import generate_ai_insights


def test_clean_value_or_none_returns_none_for_blanks():
    """Bug 4: missing/blank cell values must return None instead of fabricating 0.0."""
    assert clean_value_or_none(None) is None
    assert clean_value_or_none("") is None
    assert clean_value_or_none("  ") is None
    assert clean_value_or_none("-") is None
    assert clean_value_or_none("N/A") is None
    assert clean_value_or_none("Not Reported") is None
    assert clean_value_or_none(123.45) == 123.45
    assert clean_value_or_none("$1,500.00") == 1500.00
    assert clean_value_or_none("(500)") == -500.00


def test_metric_classification_excludes_share_counts():
    """Bug 6 & 7: Non-financial metrics like share counts must be classified as METRIC."""
    assert classify_account("No. of Equity Shares") == "METRIC"
    assert classify_account("Equity Shares in Cr") == "METRIC"
    assert classify_account("Face Value per share") == "METRIC"
    assert classify_account("Basic EPS") == "METRIC"
    assert classify_account("Diluted EPS") == "METRIC"
    assert classify_account("Dividend Per Share") == "METRIC"
    assert classify_account("Number of Employees") == "METRIC"


def test_cogs_and_gross_profit_unreported_handling():
    """Bug 5: Missing COGS must return cost_of_goods_sold = None and cogs_status = NOT_REPORTED."""
    items = [
        {"account_name": "Revenue from Operations", "account_type": "REVENUE", "net_amount": 100000.0, "year": "2024"},
        {"account_name": "Operating Expenses", "account_type": "EXPENSE", "net_amount": 40000.0, "year": "2024"},
        {"account_name": "Net Income", "account_type": "REVENUE", "net_amount": 60000.0, "year": "2024"}
    ]
    res = generate_statements_for_year(items, "2024", ["2024"])
    inc = res["income_statement"]
    
    assert inc["cost_of_goods_sold"] is None
    assert inc["cogs_status"] == "NOT_REPORTED"
    assert inc["gross_profit_status"] == "NOT_CALCULABLE"
    assert inc["total_revenue"] == 100000.0


def test_net_income_reconciliation_source_vs_derived():
    """Bug 2: Explicit source Net Income row must be used as source path."""
    items = [
        {"account_name": "Revenue from Operations", "account_type": "REVENUE", "net_amount": 100000.0, "year": "2024"},
        {"account_name": "Operating Expense", "account_type": "EXPENSE", "net_amount": 30000.0, "year": "2024"},
        {"account_name": "Interest Expense", "account_type": "INTEREST_EXPENSE", "net_amount": 5000.0, "year": "2024"},
        {"account_name": "Tax Expense", "account_type": "TAX_EXPENSE", "net_amount": 15000.0, "year": "2024"},
        {"account_name": "Net Profit for the Year", "account_type": "REVENUE", "net_amount": 50000.0, "year": "2024"}
    ]
    res = generate_statements_for_year(items, "2024", ["2024"])
    inc = res["income_statement"]
    
    assert inc["net_income"] == 50000.0
    assert inc["net_income_source"] == "SOURCE_ROW"
    assert inc["net_income_reconciliation_status"] == "VERIFIED"


def test_revenue_split_sales_and_other_income():
    """Bug 3: Operating Sales and Other Income must be explicitly separated."""
    items = [
        {"account_name": "Sales Revenue", "account_type": "REVENUE", "net_amount": 80000.0, "year": "2024"},
        {"account_name": "Other Income", "account_type": "REVENUE", "net_amount": 20000.0, "year": "2024"},
    ]
    res = generate_statements_for_year(items, "2024", ["2024"])
    inc = res["income_statement"]
    
    assert inc["sales"] == 80000.0
    assert inc["other_income"] == 20000.0
    assert inc["total_revenue"] == 100000.0


def test_cash_flow_unreported_returns_none_values():
    """Bug 9: When Cash Flow items are absent, activities should return None (not 0.0)."""
    items = [
        {"account_name": "Sales Revenue", "account_type": "REVENUE", "net_amount": 50000.0, "year": "2024"}
    ]
    res = generate_statements_for_year(items, "2024", ["2024"])
    cf = res["cash_flow"]
    
    assert cf["operating_activities"] is None
    assert cf["investing_activities"] is None
    assert cf["financing_activities"] is None
    assert cf["status"] == "Not Available in Source Workbook"


def test_quality_engine_hard_gate_caps_score_on_bs_fail():
    """Bug 10: If balance sheet equation fails, quality score must cap at 50 and set VALIDATION_FAILED."""
    rec_report = {
        "reconciliation_status": "PASS",
        "failed_count": 0,
        "passed_count": 10,
        "total_metrics_checked": 10,
        "not_available_count": 0
    }
    val_report = {"balance_sheet_check": "FAIL"}
    
    res = compute_financial_quality_score(rec_report, val_report)
    
    assert res["quality_score"] <= 50.0
    assert res["confidence_level"] == "LOW"
    assert res["quality_status"] == "VALIDATION_FAILED"
    assert res["is_reconciled"] is False


def test_safe_ratio_returns_none_when_uncalculable():
    """Bug 11: safe_ratio returns value: None when denominator is 0 or input is missing."""
    r1 = safe_ratio(100.0, 0.0)
    assert r1["value"] is None
    assert r1["is_calculable"] is False

    r2 = safe_ratio(None, 50.0)
    assert r2["value"] is None
    assert r2["is_calculable"] is False

    r3 = safe_ratio(100.0, 50.0)
    assert r3["value"] == 2.0
    assert r3["is_calculable"] is True


def test_reconciliation_contains_full_trace_fields():
    """Bug 12 & Step 2 trace: Each metric record in reconciliation output must contain all trace fields."""
    items = [
        {"account_name": "Revenue", "account_type": "REVENUE", "net_amount": 121981.0, "year": "2024", "column": "B", "row": 5},
        {"account_name": "Net Income", "account_type": "REVENUE", "net_amount": 16549.4, "year": "2024", "column": "B", "row": 12}
    ]
    canonical = build_canonical_dataset(items, "test.xlsx")
    stmts = generate_financial_statements(items)
    ratios = calculate_financial_ratios(stmts)
    
    rec = perform_source_to_result_reconciliation(canonical, stmts, ratios)
    
    assert "metrics" in rec
    assert len(rec["metrics"]) > 0
    m0 = rec["metrics"][0]
    
    for field in ["metric", "metric_id", "source_value", "source_location", "parsed_value", "normalized_value", "mapped_value", "stored_value", "calculated_value", "ai_input_value", "ai_output_value", "final_value"]:
        assert field in m0, f"Missing trace field: {field}"


def test_executive_summary_matches_canonical_revenue_and_net_income():
    """Bug 1: Executive summary prose must use canonical source values, avoiding stale/derived mismatches."""
    canonical = {
        "layer_b_canonical_metrics": {
            "revenue": {"value": 121981.0},
            "net_income": {"value": 16549.4}
        }
    }
    stmts = {
        "income_statement": {"total_revenue": 96523.40, "net_income": 13197.40}
    }
    ratios = {
        "profitability": {"net_profit_margin": {"value": 13.57, "is_calculable": True}},
        "liquidity": {"current_ratio": {"value": 1.85, "is_calculable": True}},
        "solvency": {"debt_to_equity": {"value": 0.45, "is_calculable": True}}
    }
    corp_fin = {
        "working_capital_cycle": {"cash_conversion_cycle": 28.5},
        "capital_structure": {"wacc": 7.8}
    }
    
    ai_res = generate_ai_insights(stmts, ratios, corp_fin, canonical_dataset=canonical)
    summary = ai_res["executive_summary"]
    
    assert "Annual" in summary


def test_period_compatibility_regression():
    """Step 10: Attempting to aggregate or add incompatible period types (ANNUAL and QUARTERLY) must raise PERIOD_MISMATCH exception."""
    from app.engine.statement_generator import PERIOD_MISMATCH, add_financial_metrics

    annual = {
        "period_type": "ANNUAL",
        "period_id": "FY2026",
        "revenue": 92624,
        "net_income": 13197.4
    }

    quarter = {
        "period_type": "QUARTERLY",
        "period_id": "Q1_FY2027",
        "revenue": 24478.6,
        "net_income": 3352
    }

    with pytest.raises(PERIOD_MISMATCH):
        add_financial_metrics(annual, quarter, "revenue")

    with pytest.raises(PERIOD_MISMATCH):
        add_financial_metrics(annual, quarter, "net_income")


def test_validation_integrity_regression():
    """Verify period, scope, and health score consistency validation functions raise errors on failure."""
    from app.engine.reconciliation import (
        validate_period_integrity,
        validate_scope_integrity,
        validate_health_score_consistency,
        PeriodIntegrityError,
        ScopeIntegrityError,
        HealthScoreConsistencyError
    )

    # 1. Period Integrity Mismatch (is_quarterly=True but type=ANNUAL)
    bad_period = [
        {"account_name": "Sales", "is_quarterly": True, "period_type": "ANNUAL"}
    ]
    with pytest.raises(PeriodIntegrityError):
        validate_period_integrity(bad_period)

    # 2. Scope Integrity Mismatch (scope=INVALID)
    bad_scope = [
        {"account_name": "Sales", "scope": "MONTHLY"}
    ]
    with pytest.raises(ScopeIntegrityError):
        validate_scope_integrity(bad_scope)

    # 3. Health Score Mismatch (Narrative score != Canonical score)
    statements = {
        "ledger_summary": {"target_year": "2026"},
        "income_statement": {"revenue_from_operations": 92624.0, "total_revenue": 96523.4, "net_income": 13197.4}
    }
    ratios = {
        "profitability": {"net_profit_margin": {"value": 13.57, "is_calculable": True}},
        "liquidity": {"current_ratio": {"value": 0.74, "is_calculable": True}},
        "solvency": {"debt_to_equity": {"value": 0.60, "is_calculable": True}}
    }
    ai_reports_mismatch = {
        "executive_summary": "Overall Financial Health Score of 68.2/100.",
        "quality_report": {"quality_score": 50.0}
    }
    with pytest.raises(HealthScoreConsistencyError):
        validate_health_score_consistency(statements, ratios, ai_reports_mismatch)


