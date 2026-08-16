import pytest
from app.engine.document_parser import classify_account, clean_value, parse_workbook
from app.engine.statement_generator import generate_financial_statements
from app.engine.financial_analyzer import calculate_financial_ratios, calculate_corporate_finance, calculate_npv, calculate_irr
from app.engine.multi_period_analyzer import generate_multi_period_analysis, calculate_cagr, calculate_yoy
from app.engine.ai_insights import compute_financial_health_score, generate_ai_insights

def test_financial_ratio_mathematical_precision():
    statements = {
        "income_statement": {
            "total_revenue": 1000000.0,
            "cost_of_goods_sold": 600000.0,
            "gross_profit": 400000.0,
            "ebit": 200000.0,
            "net_income": 150000.0,
            "interest_expense": 20000.0
        },
        "balance_sheet": {
            "total_assets": 1200000.0,
            "total_liabilities": 400000.0,
            "current_assets": {
                "total_current_assets": 600000.0,
                "cash": 200000.0,
                "accounts_receivable": 250000.0,
                "inventory": 150000.0
            },
            "current_liabilities": {
                "total_current_liabilities": 300000.0,
                "accounts_payable": 100000.0
            },
            "equity": {
                "total_equity": 800000.0
            },
            "non_current_liabilities": {
                "long_term_debt": 100000.0
            }
        }
    }

    ratios = calculate_financial_ratios(statements)

    # 1. Gross Margin: (400,000 / 1,000,000) * 100 = 40.0%
    assert ratios["profitability"]["gross_profit_margin"]["value"] == 40.0

    # 2. Net Margin: (150,000 / 1,000,000) * 100 = 15.0%
    assert ratios["profitability"]["net_profit_margin"]["value"] == 15.0

    # 3. ROA: (150,000 / 1,200,000) * 100 = 12.5%
    assert ratios["profitability"]["return_on_assets"]["value"] == 12.5

    # 4. ROE: (150,000 / 800,000) * 100 = 18.75% -> rounded 18.75%
    assert ratios["profitability"]["return_on_equity"]["value"] == 18.75

    # 5. Current Ratio: 600,000 / 300,000 = 2.0
    assert ratios["liquidity"]["current_ratio"]["value"] == 2.0

    # 6. Quick Ratio: (600,000 - 150,000) / 300,000 = 1.5
    assert ratios["liquidity"]["quick_ratio"]["value"] == 1.5

    # 7. Debt to Equity: 400,000 / 800,000 = 0.5
    assert ratios["solvency"]["debt_to_equity"]["value"] == 0.5

    # 8. Interest Coverage: 200,000 / 20,000 = 10.0
    assert ratios["solvency"]["interest_coverage_ratio"]["value"] == 10.0


def test_multi_period_cagr_and_yoy_accuracy():
    # 3-year revenue (FY23, FY24, FY25 -> 2 compounding periods): 100, 120, 144 -> CAGR = sqrt(144/100) - 1 = 20.0%
    cagr = calculate_cagr(100.0, 144.0, 2)
    assert cagr is not None and abs(cagr - 20.0) < 0.01

    # YoY growth: (120 - 100) / 100 * 100 = 20.0%
    yoy = calculate_yoy(100.0, 120.0)
    assert abs(yoy - 20.0) < 0.01

    # Zero beginning value edge case returns None to avoid false 0% override
    assert calculate_cagr(0.0, 100.0, 3) is None
    assert calculate_yoy(0.0, 100.0) == 0.0


def test_corporate_finance_npv_and_irr_accuracy():
    # Cash flows: -1000, 400, 400, 400 at 10%
    cf = [-1000.0, 400.0, 400.0, 400.0]
    npv = calculate_npv(0.10, cf)
    assert round(npv, 2) == -5.26  # 400/1.1 + 400/1.21 + 400/1.331 - 1000 = 363.64 + 330.58 + 300.53 - 1000 = -5.25

    irr = calculate_irr(cf)
    assert abs(irr - 0.097) < 0.01  # IRR is ~9.7%


def test_fuzzy_account_classification_accuracy():
    assert classify_account("Operating Revenue") == "REVENUE"
    assert classify_account("Gross Billing Turnover") == "REVENUE"
    assert classify_account("Cost of Goods Sold") == "EXPENSE"
    assert classify_account("Direct Manufacturing Expenses") == "EXPENSE"
    assert classify_account("Cash & Bank Balances") == "CASH_ASSET"
    assert classify_account("Trade Debtors Receivable") == "RECEIVABLE_ASSET"
    assert classify_account("Merchandise Inventory Stock") == "INVENTORY_ASSET"
    assert classify_account("Accounts Payable Creditors") == "PAYABLE_LIABILITY"
    assert classify_account("Common Capital Equity") == "EQUITY"


def test_capital_budgeting_zero_fabrication_safety():
    # Missing current assets and net income should mark capital budgeting non-calculable without fabricating $100k/$20k
    empty_statements = {
        "income_statement": {"total_revenue": 0.0, "net_income": 0.0},
        "balance_sheet": {"current_assets": {"total_current_assets": 0.0}},
        "cash_flow": {}
    }
    corp_fin = calculate_corporate_finance(empty_statements, {})
    cb = corp_fin["capital_budgeting"]
    assert cb["is_calculable"] is False
    assert cb["initial_investment"] == 0.0
    assert cb["projected_annual_fcf"] == 0.0
    assert "NOT_CALCULABLE" in cb["verdict"]


def test_beneish_tata_exact_accruals_integration():
    from app.engine.risk_analyzer import calculate_risk_intelligence
    statements = {
        "income_statement": {"net_income": 100.0, "total_revenue": 1000.0, "ebit": 150.0},
        "balance_sheet": {"total_assets": 500.0, "total_liabilities": 200.0, "current_assets": {"total_current_assets": 300.0}, "current_liabilities": {"total_current_liabilities": 100.0}},
        "cash_flow": {"operating_activities": 80.0}
    }
    risk = calculate_risk_intelligence(statements, {})
    # Exact accruals = net_inc (100) - ocf (80) = 20. TATA = 20 / 500 = 0.04
    assert risk["beneish_m_score"]["tata_accruals_ratio"] == 0.04

