import pytest
import pandas as pd
from app.engine.accounting_adapters import TallyAdapter, QuickBooksAdapter, XeroAdapter
from app.engine.valuation_engine import calculate_dcf_valuation, calculate_scenario_sensitivity
from app.engine.financial_analyzer import calculate_corporate_finance

def test_tally_xml_adapter_parsing():
    sample_tally_xml = b"""<?xml version="1.0" encoding="utf-8"?>
    <ENVELOPE>
        <HEADER>
            <TALLYREQUEST>Export Data</TALLYREQUEST>
        </HEADER>
        <BODY>
            <IMPORTDATA>
                <REQUESTDATA>
                    <TALLYMESSAGE xmlns:UDF="TallyUDF">
                        <LEDGER NAME="Sales Account">
                            <PARENT>Direct Income</PARENT>
                            <OPENINGBALANCE>0.00</OPENINGBALANCE>
                            <CLOSINGBALANCE>-500000.00</CLOSINGBALANCE>
                        </LEDGER>
                        <LEDGER NAME="Purchases Account">
                            <PARENT>Direct Expenses</PARENT>
                            <OPENINGBALANCE>0.00</OPENINGBALANCE>
                            <CLOSINGBALANCE>300000.00</CLOSINGBALANCE>
                        </LEDGER>
                        <LEDGER NAME="Cash in Hand">
                            <PARENT>Current Assets</PARENT>
                            <OPENINGBALANCE>50000.00</OPENINGBALANCE>
                            <CLOSINGBALANCE>85000.00</CLOSINGBALANCE>
                        </LEDGER>
                    </TALLYMESSAGE>
                </REQUESTDATA>
            </IMPORTDATA>
        </BODY>
    </ENVELOPE>"""
    
    assert TallyAdapter.is_tally_format(sample_tally_xml, "tally_trial_balance.xml") is True
    sheets = TallyAdapter.parse_tally_xml(sample_tally_xml)
    assert "Tally Ledger" in sheets
    df = sheets["Tally Ledger"]
    assert len(df) == 3
    assert "Sales Account" in df["Particulars"].values
    assert "Cash in Hand" in df["Particulars"].values

def test_quickbooks_csv_adapter():
    sample_qb_data = {
        "Col1": ["Revenue", "Product Sales", "Service Revenue", "Total for Revenue", "Expenses", "Office Supplies", "Total for Expenses"],
        "Col2": ["", "$450,000", "$150,000", "$600,000", "", "$25,000", "$25,000"]
    }
    df_raw = pd.DataFrame(sample_qb_data)
    df_parsed = QuickBooksAdapter.parse_quickbooks_csv(df_raw)
    
    assert len(df_parsed) >= 3
    assert "Product Sales" in df_parsed["Particulars"].values
    assert df_parsed.loc[df_parsed["Particulars"] == "Product Sales", "Amount"].values[0] == 450000.0

def test_xero_csv_adapter():
    sample_xero_data = {
        "Account": ["200 - Sales Revenue", "400 - Advertising", "600 - Bank Account", "Total"],
        "Debit": ["", "15000.00", "45000.00", "60000.00"],
        "Credit": ["250000.00", "", "", "250000.00"]
    }
    df_raw = pd.DataFrame(sample_xero_data)
    df_parsed = XeroAdapter.parse_xero_csv(df_raw)
    
    assert len(df_parsed) == 3  # "Total" row filtered
    assert "200 - Sales Revenue" in df_parsed["Particulars"].values

def test_dcf_valuation_calculable():
    sample_statements = {
        "income_statement": {
            "total_revenue": 1000000.0,
            "ebit": 200000.0,
            "ebt": 180000.0,
            "tax_expense": 37800.0,
            "depreciation_amortization": 25000.0
        },
        "balance_sheet": {
            "total_assets": 1200000.0,
            "total_liabilities": 400000.0,
            "current_assets": {"cash": 100000.0},
            "long_term_liabilities": {"total_long_term_liabilities": 200000.0},
            "current_liabilities": {"short_term_borrowings": 50000.0}
        },
        "cash_flow": {
            "status": "Available",
            "operating_activities": 160000.0
        }
    }
    sample_ratios = {}

    dcf = calculate_dcf_valuation(sample_statements, sample_ratios, wacc=0.09, perpetual_growth_rate=0.025)
    
    assert dcf["is_calculable"] is True
    assert dcf["status"] == "VERIFIED"
    assert dcf["enterprise_value"] > 0
    assert dcf["equity_value"] > 0
    assert len(dcf["projected_cash_flows"]) == 5
    assert len(dcf["sensitivity_matrix"]) == 5
    assert dcf["parameters"]["net_debt_deducted"] == 150000.0  # (200k + 50k - 100k)

def test_dcf_valuation_zero_fabrication_safety():
    """When positive revenue or operational EBIT is missing, DCF must NOT invent phantom numbers."""
    empty_statements = {
        "income_statement": {"total_revenue": 0.0, "ebit": 0.0},
        "balance_sheet": {"total_assets": 0.0},
        "cash_flow": {"status": "Missing"}
    }
    dcf = calculate_dcf_valuation(empty_statements, {})
    
    assert dcf["is_calculable"] is False
    assert dcf["enterprise_value"] is None
    assert dcf["equity_value"] is None
    assert dcf["projected_cash_flows"] == []

def test_scenario_sensitivity_analysis():
    statements = {
        "income_statement": {
            "total_revenue": 500000.0,
            "net_income": 60000.0
        }
    }
    scen = calculate_scenario_sensitivity(statements, {})
    
    assert scen["is_calculable"] is True
    assert len(scen["scenarios"]) == 3
    cases = [s["case"] for s in scen["scenarios"]]
    assert any("Bear" in c for c in cases)
    assert any("Base" in c for c in cases)
    assert any("Bull" in c for c in cases)

def test_calculate_corporate_finance_with_valuation_and_clean_ccc():
    statements = {
        "income_statement": {
            "total_revenue": 800000.0,
            "cost_of_goods_sold": 450000.0,
            "net_income": 95000.0,
            "ebit": 130000.0
        },
        "balance_sheet": {
            "total_assets": 900000.0,
            "current_assets": {
                "total_current_assets": 300000.0,
                "accounts_receivable": 80000.0,
                "inventory": 60000.0
            },
            "current_liabilities": {
                "total_current_liabilities": 150000.0,
                "accounts_payable": 50000.0
            },
            "equity": {"total_equity": 500000.0}
        },
        "cash_flow": {"status": "Missing"}
    }
    
    res = calculate_corporate_finance(statements, {})
    
    assert "valuation_model" in res
    assert res["valuation_model"]["is_calculable"] is True
    assert "scenario_analysis" in res
    assert res["scenario_analysis"]["is_calculable"] is True
    
    wc = res["working_capital_cycle"]
    assert wc["days_inventory_outstanding_dio"] is not None
    assert wc["days_sales_outstanding_dso"] is not None
    assert wc["days_payable_outstanding_dpo"] is not None
    assert wc["cash_conversion_cycle"] is not None
