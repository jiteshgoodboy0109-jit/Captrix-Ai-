"""
Multi-Currency & Production Prediction Engine Test Suite
Validates ISO currency resolution, symbol disambiguation, exchange rate conversion audit provenance,
locale formatting, prediction backtesting error metrics (MAE, RMSE, MAPE), and insufficient data protection.
"""

import pytest
from app.engine.currency_engine import (
    identify_currency,
    get_exchange_rate,
    convert_currency,
    format_currency_amount,
    SUPPORTED_CURRENCIES
)
from app.engine.multi_period_analyzer import generate_multi_period_analysis

def test_iso_currency_identification_and_disambiguation():
    # 1. Exact ISO Code Identification
    iso, mult = identify_currency("Revenue in INR Crores")
    assert iso == "INR"
    assert mult == 10000000.0

    iso, mult = identify_currency("Total Sales USD Millions")
    assert iso == "USD"
    assert mult == 1000000.0

    iso, mult = identify_currency("Operating Profit EUR Thousands")
    assert iso == "EUR"
    assert mult == 1000.0

    iso, mult = identify_currency("Expenses in GBP")
    assert iso == "GBP"
    assert mult == 1.0

    iso, mult = identify_currency("Net Income JPY Millions")
    assert iso == "JPY"
    assert mult == 1000000.0

    # 2. Ambiguous Symbol Resolution ($ symbol with country context)
    iso_cad, _ = identify_currency("Revenue $", country_context="Canada")
    assert iso_cad == "CAD"

    iso_aud, _ = identify_currency("Revenue $", country_context="Australia")
    assert iso_aud == "AUD"

    iso_sgd, _ = identify_currency("Revenue $", country_context="Singapore")
    assert iso_sgd == "SGD"

    iso_usd, _ = identify_currency("Revenue $", country_context="United States")
    assert iso_usd == "USD"

def test_currency_conversion_audit_provenance():
    # Convert 1000 USD to INR for FY2026
    res = convert_currency(1000.0, "USD", "INR", year="2026")
    
    assert res["original_amount"] == 1000.0
    assert res["original_currency"] == "USD"
    assert res["target_currency"] == "INR"
    assert res["is_converted"] is True
    assert res["converted_amount"] > 0
    assert "exchange_rate" in res
    assert "source" in res

    # Same currency conversion should be identity (rate = 1.0)
    same_res = convert_currency(500.0, "EUR", "EUR")
    assert same_res["converted_amount"] == 500.0
    assert same_res["exchange_rate"] == 1.0
    assert same_res["is_converted"] is False

def test_professional_currency_formatting():
    # Indian formatting rule for INR
    fmt_inr = format_currency_amount(12500000.0, "INR")
    assert "₹" in fmt_inr
    assert "1,25,00,000.00" in fmt_inr

    # Western formatting rule for USD
    fmt_usd = format_currency_amount(1250000.0, "USD")
    assert "$" in fmt_usd
    assert "1,250,000.00" in fmt_usd

    # European formatting rule for EUR
    fmt_eur = format_currency_amount(50000.0, "EUR")
    assert "€" in fmt_eur
    assert "50,000.00" in fmt_eur

def test_prediction_engine_backtesting_and_insufficient_data_guard():
    # 1. Test Single-Period Input -> Triggers INSUFFICIENT_HISTORICAL_DATA Guard
    single_period_statements = {
        "income_statement": {"total_revenue": 100000.0, "net_income": 15000.0},
        "balance_sheet": {"total_assets": 200000.0, "equity": {"total_equity": 120000.0}}
    }
    analysis_single = generate_multi_period_analysis(single_period_statements)
    fc_single = analysis_single["three_year_forecast"]

    assert fc_single["forecast_status"] == "INSUFFICIENT_HISTORICAL_DATA"
    assert "Insufficient reliable historical data" in fc_single["forecast_message"]
    assert len(fc_single["projections"]) == 3

    # 2. Test 3-Year Historical Inputs -> Triggers Time-Series Backtesting (MAE, RMSE, MAPE)
    multi_period_statements = {
        "by_year": {
            "2023": {
                "income_statement": {"total_revenue": 80000.0, "cost_of_goods_sold": 50000.0, "gross_profit": 30000.0, "net_income": 10000.0},
                "balance_sheet": {"total_assets": 150000.0, "equity": {"total_equity": 90000.0}}
            },
            "2024": {
                "income_statement": {"total_revenue": 90000.0, "cost_of_goods_sold": 55000.0, "gross_profit": 35000.0, "net_income": 12000.0},
                "balance_sheet": {"total_assets": 170000.0, "equity": {"total_equity": 105000.0}}
            },
            "2025": {
                "income_statement": {"total_revenue": 100000.0, "cost_of_goods_sold": 60000.0, "gross_profit": 40000.0, "net_income": 15000.0},
                "balance_sheet": {"total_assets": 200000.0, "equity": {"total_equity": 120000.0}}
            }
        }
    }
    analysis_multi = generate_multi_period_analysis(multi_period_statements)
    fc_multi = analysis_multi["three_year_forecast"]

    assert fc_multi["forecast_status"] == "VALIDATED_TIME_SERIES"
    assert "backtesting_metrics" in fc_multi
    assert fc_multi["backtesting_metrics"]["mae"] is not None
    assert fc_multi["backtesting_metrics"]["rmse"] is not None
    assert fc_multi["backtesting_metrics"]["mape_pct"] is not None
    assert len(fc_multi["projections"]) == 3
