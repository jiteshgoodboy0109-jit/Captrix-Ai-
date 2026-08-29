"""
Tests for OutputValidator and Master Requirement: Strict Source-Grounded Output Engine.
Verifies section presence rules, zero-fabrication safety, period safety, and single-query filtering.
"""

import pytest
from app.engine.output_validator import OutputValidator
from app.engine.ai_insights import answer_financial_query, generate_ai_insights

def test_scenario_a_pnl_only_omits_balance_sheet_and_cash_flow():
    """Scenario A: Document contains P&L only -> Output contains P&L only; BS & CF omitted."""
    canonical_dataset = [
        {"canonical_concept": "REVENUE", "canonical_value": 5000000.0, "statement_type": "INCOME_STATEMENT"},
        {"canonical_concept": "OPEX", "canonical_value": 3500000.0, "statement_type": "INCOME_STATEMENT"},
        {"canonical_concept": "NET_INCOME", "canonical_value": 1500000.0, "statement_type": "INCOME_STATEMENT"}
    ]
    raw_payload = {
        "statements": {
            "income_statement": {"total_revenue": 5000000.0, "net_income": 1500000.0},
            "balance_sheet": {},
            "cash_flow": {"status": "Missing"}
        },
        "ratios": {
            "profitability": {"net_profit_margin": {"value": 30.0, "is_calculable": True}},
            "liquidity": {"current_ratio": {"value": None, "is_calculable": False}}
        },
        "dupont_analysis": {"is_calculable": False},
        "risk_intelligence": {"z_score": {"is_calculable": False}},
        "corporate_finance": {"valuation_model": {"is_calculable": False}, "working_capital_cycle": {}},
        "multi_period": {"periods": ["FY2026"]},
        "ai_report": {"recommendations": ["Refinance short term debt", "Improve operating margins"]}
    }

    validated = OutputValidator.validate_and_filter_payload(raw_payload, canonical_dataset)
    manifest = validated["section_manifest"]

    assert manifest["has_income_statement"] is True
    assert manifest["has_balance_sheet"] is False
    assert manifest["has_cash_flow"] is False
    assert manifest["has_dupont"] is False
    assert manifest["has_solvency_risk"] is False
    assert validated["statements"]["balance_sheet"]["status"] == "NOT_REPORTED_IN_SOURCE"
    assert validated["statements"]["cash_flow"]["status"] == "NOT_REPORTED_IN_SOURCE"
    # Verify unevidenced debt recommendation is pruned
    assert "Refinance short term debt" not in validated["ai_report"]["recommendations"]

def test_scenario_b_balance_sheet_only_omits_income_statement():
    """Scenario B: Document contains Balance Sheet only -> Output contains BS only."""
    canonical_dataset = [
        {"canonical_concept": "TOTAL_ASSETS", "canonical_value": 10000000.0, "statement_type": "BALANCE_SHEET"},
        {"canonical_concept": "TOTAL_LIABILITIES", "canonical_value": 4000000.0, "statement_type": "BALANCE_SHEET"},
        {"canonical_concept": "EQUITY", "canonical_value": 6000000.0, "statement_type": "BALANCE_SHEET"}
    ]
    raw_payload = {
        "statements": {
            "income_statement": {},
            "balance_sheet": {"total_assets": 10000000.0, "total_liabilities": 4000000.0},
            "cash_flow": {"status": "Missing"}
        },
        "ratios": {
            "solvency": {"debt_to_equity": {"value": 0.67, "is_calculable": True}}
        },
        "dupont_analysis": {"is_calculable": False},
        "risk_intelligence": {"z_score": {"is_calculable": False}},
        "corporate_finance": {"valuation_model": {"is_calculable": False}, "working_capital_cycle": {}},
        "multi_period": {"periods": ["FY2026"]},
        "ai_report": {"recommendations": []}
    }

    validated = OutputValidator.validate_and_filter_payload(raw_payload, canonical_dataset)
    manifest = validated["section_manifest"]

    assert manifest["has_income_statement"] is False
    assert manifest["has_balance_sheet"] is True
    assert manifest["has_cash_flow"] is False

def test_scenario_c_user_query_filter_returns_only_requested_fact():
    """Scenario K: User asks one specific question -> answer only that question."""
    statements = {
        "income_statement": {"total_revenue": 1000000.0, "revenue_from_operations": 950000.0, "other_income": 50000.0, "net_income": 200000.0},
        "balance_sheet": {"status": "NOT_REPORTED_IN_SOURCE"},
        "cash_flow": {"status": "NOT_REPORTED_IN_SOURCE"}
    }
    ratios = {
        "profitability": {"net_profit_margin": {"value": 20.0, "is_calculable": True}}
    }
    corp_fin = {}
    ai_reports = {"health_score": 88.0, "recommendations": []}

    ans_rev = answer_financial_query("What is total revenue?", statements, ratios, corp_fin, ai_reports)
    assert "Revenue" in ans_rev
    assert "950,000.00" in ans_rev or "1,000,000.00" in ans_rev
    assert "Balance Sheet" not in ans_rev  # Does not dump balance sheet

    ans_bs = answer_financial_query("What is the balance sheet?", statements, ratios, corp_fin, ai_reports)
    assert "not reported" in ans_bs.lower()

def test_zero_preservation_and_missing_value_omission():
    """Scenario I & J: Explicit zero is preserved, missing value is omitted / None."""
    from app.engine.document_parser import clean_value_or_none
    
    assert clean_value_or_none(0) == 0.0
    assert clean_value_or_none("0.00") == 0.0
    assert clean_value_or_none("") is None
    assert clean_value_or_none("-") is None
    assert clean_value_or_none("N/A") is None
