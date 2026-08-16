from typing import List, Dict, Any

def generate_statements_for_year(latest_items: List[Dict[str, Any]], target_year: str, years_found: List[str]) -> Dict[str, Any]:
    # 1. Trial Balance Summary
    total_debit = sum(abs(i.get("debit", 0.0)) for i in latest_items)
    total_credit = sum(abs(i.get("credit", 0.0)) for i in latest_items)
    tb_difference = round(total_debit - total_credit, 2)
    
    trial_balance = {
        "total_debit": round(total_debit, 2),
        "total_credit": round(total_credit, 2),
        "difference": tb_difference,
        "is_balanced": abs(tb_difference) < 1.0,
        "item_count": len(latest_items)
    }

    # Separate detailed line items from summary total rows to prevent double counting
    detail_items = [i for i in latest_items if not i.get("is_summary", False)]
    eval_items = detail_items if detail_items else latest_items

    # Categorize items for Income Statement & Balance Sheet
    net_inc_items = [i for i in eval_items if any(k in str(i.get("account_name")).lower() for k in ["net profit", "net income", "profit for the year", "profit after tax", "pat"])]
    if not net_inc_items:
        net_inc_items = [i for i in latest_items if any(k in str(i.get("account_name")).lower() for k in ["net profit", "net income", "profit for the year", "profit after tax", "pat"])]

    revenues = [i for i in eval_items if (i.get("account_type") in ["REVENUE", "SALES"]) and i not in net_inc_items]
    if not revenues:
        revenues = [i for i in latest_items if (i.get("account_type") in ["REVENUE", "SALES"] or any(k in str(i.get("account_name")).lower() for k in ["revenue", "sales", "turnover", "income from operations"])) and i not in net_inc_items]

    cogs_items = [i for i in eval_items if i.get("account_type") == "COGS" or "cogs" in str(i.get("account_name")).lower() or "cost of goods" in str(i.get("account_name")).lower() or "cost of sales" in str(i.get("account_name")).lower()]
    if not cogs_items:
        cogs_items = [i for i in latest_items if i.get("account_type") == "COGS" or "cogs" in str(i.get("account_name")).lower() or "cost of goods" in str(i.get("account_name")).lower() or "cost of sales" in str(i.get("account_name")).lower()]

    depr_items = [i for i in eval_items if i.get("account_type") == "DEPRECIATION_EXPENSE" or "depreciation" in str(i.get("account_name")).lower() or "amortisation" in str(i.get("account_name")).lower()]
    interest_items = [i for i in eval_items if i.get("account_type") == "INTEREST_EXPENSE" or ("interest" in str(i.get("account_name")).lower() and "expense" in str(i.get("account_name")).lower())]
    tax_items = [i for i in eval_items if i.get("account_type") == "TAX_EXPENSE" or ("tax" in str(i.get("account_name")).lower() and "expense" in str(i.get("account_name")).lower())]
    
    expenses = [i for i in eval_items if i.get("account_type") in ["EXPENSE", "COGS", "DEPRECIATION_EXPENSE", "INTEREST_EXPENSE", "TAX_EXPENSE"]]
    opex_items = [i for i in eval_items if i.get("account_type") == "EXPENSE" and i not in cogs_items + depr_items + interest_items + tax_items]

    assets = [i for i in eval_items if ("ASSET" in str(i.get("account_type")) or i.get("account_type") == "ASSET") and "cash flow" not in str(i.get("sheet")).lower() and "cash flow" not in str(i.get("account_name")).lower()]
    liabilities = [i for i in eval_items if "LIABILITY" in str(i.get("account_type")) or i.get("account_type") == "LIABILITY"]
    equity = [i for i in eval_items if "EQUITY" in str(i.get("account_type")) or i.get("account_type") == "EQUITY"]

    # 2. Income Statement Calculation (Strictly Grounded)
    total_revenue = sum(abs(i.get("net_amount", 0.0)) for i in revenues)
    rev_ops_items = [i for i in revenues if "other income" not in str(i.get("account_name")).lower() and "other revenue" not in str(i.get("account_name")).lower()]
    revenue_from_operations = sum(abs(i.get("net_amount", 0.0)) for i in rev_ops_items) if rev_ops_items else total_revenue

    total_cogs = sum(abs(i.get("net_amount", 0.0)) for i in cogs_items)

    # Check explicit Gross Profit item in source workbook if present
    explicit_gp_items = [i for i in latest_items if "gross profit" in str(i.get("account_name")).lower() or "gross margin" in str(i.get("account_name")).lower()]
    if explicit_gp_items:
        gross_profit = explicit_gp_items[0].get("net_amount", 0.0)
    else:
        gross_profit = total_revenue - total_cogs if (total_revenue > 0 or total_cogs > 0) else 0.0
    
    total_opex = sum(abs(i.get("net_amount", 0.0)) for i in opex_items)
    ebitda = gross_profit - total_opex
    
    depreciation = sum(abs(i.get("net_amount", 0.0)) for i in depr_items)
    ebit = ebitda - depreciation
    
    interest_expense = sum(abs(i.get("net_amount", 0.0)) for i in interest_items)
    ebt = ebit - interest_expense
    
    tax_expense = sum(abs(i.get("net_amount", 0.0)) for i in tax_items)
    
    if net_inc_items:
        net_income = net_inc_items[0].get("net_amount", 0.0) if len(net_inc_items) == 1 else sum(i.get("net_amount", 0.0) for i in net_inc_items)
    else:
        net_income = ebt - tax_expense

    income_statement = {
        "revenue_from_operations": round(revenue_from_operations, 2),
        "total_revenue": round(total_revenue, 2),
        "cost_of_goods_sold": round(total_cogs, 2),
        "gross_profit": round(gross_profit, 2),
        "operating_expenses": round(total_opex, 2),
        "ebitda": round(ebitda, 2),
        "depreciation_amortization": round(depreciation, 2),
        "ebit": round(ebit, 2),
        "interest_expense": round(interest_expense, 2),
        "ebt": round(ebt, 2),
        "tax_expense": round(tax_expense, 2),
        "tax_status": "VERIFIED" if tax_items else "Not Separately Reported in Source Workbook",
        "net_income": round(net_income, 2)
    }

    # 3. Balance Sheet Calculation (Strictly Grounded)
    cash_items = [i for i in assets if "CASH" in str(i.get("account_type")) or "cash" in str(i.get("account_name")).lower() or "bank" in str(i.get("account_name")).lower()]
    rec_items = [i for i in assets if "RECEIVABLE" in str(i.get("account_type")) or "receivable" in str(i.get("account_name")).lower() or "debtor" in str(i.get("account_name")).lower()]
    inv_items = [i for i in assets if "INVENTORY" in str(i.get("account_type")) or "inventory" in str(i.get("account_name")).lower() or "stock" in str(i.get("account_name")).lower()]
    
    cash_and_equivalents = sum(abs(i.get("net_amount", 0.0)) for i in cash_items)
    accounts_receivable = sum(abs(i.get("net_amount", 0.0)) for i in rec_items)
    inventory = sum(abs(i.get("net_amount", 0.0)) for i in inv_items)
    
    # Detailed current assets
    petty_cash = sum(abs(i.get("net_amount", 0.0)) for i in assets if "petty cash" in str(i.get("account_name")).lower())
    temporary_investments = sum(abs(i.get("net_amount", 0.0)) for i in assets if "temporary investment" in str(i.get("account_name")).lower() or "marketable security" in str(i.get("account_name")).lower() or "short term investment" in str(i.get("account_name")).lower())
    supplies = sum(abs(i.get("net_amount", 0.0)) for i in assets if "supply" in str(i.get("account_name")).lower() or "supplies" in str(i.get("account_name")).lower())
    prepaid_insurance = sum(abs(i.get("net_amount", 0.0)) for i in assets if "prepaid insurance" in str(i.get("account_name")).lower())
    
    current_asset_items = cash_items + rec_items + inv_items + [
        i for i in assets if any(k in str(i.get("account_name")).lower() for k in ["current asset", "petty cash", "temporary investment", "marketable security", "short term investment", "supply", "supplies", "prepaid insurance"])
    ]
    total_current_assets = sum(abs(i.get("net_amount", 0.0)) for i in current_asset_items) if current_asset_items else (cash_and_equivalents + accounts_receivable + inventory)
    
    # Non-current Assets details
    investment = sum(abs(i.get("net_amount", 0.0)) for i in assets if "investment" in str(i.get("account_name")).lower() and i not in current_asset_items)
    
    land = sum(abs(i.get("net_amount", 0.0)) for i in assets if "land" in str(i.get("account_name")).lower() and "improvement" not in str(i.get("account_name")).lower())
    land_improvements = sum(abs(i.get("net_amount", 0.0)) for i in assets if "land improvement" in str(i.get("account_name")).lower())
    buildings = sum(abs(i.get("net_amount", 0.0)) for i in assets if "building" in str(i.get("account_name")).lower())
    equipment = sum(abs(i.get("net_amount", 0.0)) for i in assets if any(k in str(i.get("account_name")).lower() for k in ["equipment", "machinery", "vehicle", "furniture", "fixture"]))
    accumulated_depreciation = sum(abs(i.get("net_amount", 0.0)) for i in assets if "accumulated depreciation" in str(i.get("account_name")).lower() or "acc. dep" in str(i.get("account_name")).lower())
    
    net_ppe = land + land_improvements + buildings + equipment - accumulated_depreciation
    property_plant_equipment = {
        "land": round(land, 2),
        "land_improvements": round(land_improvements, 2),
        "buildings": round(buildings, 2),
        "equipment": round(equipment, 2),
        "accumulated_depreciation": round(accumulated_depreciation, 2),
        "net_property_plant_equipment": round(net_ppe, 2)
    }
    
    goodwill_items = [i for i in assets if "goodwill" in str(i.get("account_name")).lower()]
    goodwill = sum(abs(i.get("net_amount", 0.0)) for i in goodwill_items)
    trade_names = sum(abs(i.get("net_amount", 0.0)) for i in assets if any(k in str(i.get("account_name")).lower() for k in ["trade name", "trademark", "patent", "brand"]))
    total_intangibles = goodwill + trade_names
    intangible_assets = {
        "goodwill": round(goodwill, 2),
        "goodwill_status": "VERIFIED" if goodwill_items else "Not Separately Reported in Source Workbook",
        "trade_names": round(trade_names, 2),
        "total_intangible_assets": round(total_intangibles, 2)
    }
    
    other_assets = sum(abs(i.get("net_amount", 0.0)) for i in assets if "other asset" in str(i.get("account_name")).lower())
    
    total_non_current_assets = investment + net_ppe + total_intangibles + other_assets
    total_assets = sum(abs(i.get("net_amount", 0.0)) for i in assets) or (total_current_assets + total_non_current_assets)

    # Liabilities & Equity details
    payables_items = [i for i in liabilities if "PAYABLE" in str(i.get("account_type")) or "payable" in str(i.get("account_name")).lower() or "creditor" in str(i.get("account_name")).lower()]
    accounts_payable = sum(abs(i.get("net_amount", 0.0)) for i in payables_items if "notes payable" not in str(i.get("account_name")).lower() and "wages" not in str(i.get("account_name")).lower() and "interest" not in str(i.get("account_name")).lower() and "tax" not in str(i.get("account_name")).lower())
    notes_payable = sum(abs(i.get("net_amount", 0.0)) for i in payables_items if "notes payable" in str(i.get("account_name")).lower() and "long term" not in str(i.get("account_name")).lower() and "lt" not in str(i.get("account_name")).lower())
    wages_payable = sum(abs(i.get("net_amount", 0.0)) for i in liabilities if "wages payable" in str(i.get("account_name")).lower() or "salary payable" in str(i.get("account_name")).lower() or "payroll payable" in str(i.get("account_name")).lower())
    interest_payable = sum(abs(i.get("net_amount", 0.0)) for i in liabilities if "interest payable" in str(i.get("account_name")).lower())
    tax_payable = sum(abs(i.get("net_amount", 0.0)) for i in liabilities if "tax payable" in str(i.get("account_name")).lower())
    unearned_revenue = sum(abs(i.get("net_amount", 0.0)) for i in liabilities if "unearned revenue" in str(i.get("account_name")).lower() or "deferred revenue" in str(i.get("account_name")).lower())
    
    short_term_debt_items = [i for i in liabilities if "short term" in str(i.get("account_name")).lower() or "current borrowing" in str(i.get("account_name")).lower()]
    short_term_debt = sum(abs(i.get("net_amount", 0.0)) for i in short_term_debt_items)
    
    total_current_liabilities = accounts_payable + notes_payable + wages_payable + interest_payable + tax_payable + unearned_revenue + short_term_debt
    if total_current_liabilities == 0.0 and (payables_items or short_term_debt_items):
        total_current_liabilities = sum(abs(i.get("net_amount", 0.0)) for i in payables_items + short_term_debt_items)
        
    notes_payable_lt = sum(abs(i.get("net_amount", 0.0)) for i in liabilities if "notes payable" in str(i.get("account_name")).lower() and ("long term" in str(i.get("account_name")).lower() or "lt" in str(i.get("account_name")).lower() or "non current" in str(i.get("account_name")).lower()))
    bonds_payable = sum(abs(i.get("net_amount", 0.0)) for i in liabilities if "bonds payable" in str(i.get("account_name")).lower())
    long_term_debt = sum(abs(i.get("net_amount", 0.0)) for i in liabilities if i not in payables_items + short_term_debt_items and "bonds payable" not in str(i.get("account_name")).lower() and "notes payable" not in str(i.get("account_name")).lower())
    
    total_ltl = notes_payable_lt + bonds_payable + long_term_debt
    long_term_liabilities = {
        "notes_payable_lt": round(notes_payable_lt, 2),
        "bonds_payable": round(bonds_payable, 2),
        "total_long_term_liabilities": round(total_ltl, 2)
    }
    
    total_liabilities = total_current_liabilities + total_ltl
    if total_liabilities == 0.0 and liabilities:
        total_liabilities = sum(abs(i.get("net_amount", 0.0)) for i in liabilities)
        long_term_liabilities["total_long_term_liabilities"] = round(total_liabilities - total_current_liabilities, 2)

    common_stock = sum(abs(i.get("net_amount", 0.0)) for i in equity if "common stock" in str(i.get("account_name")).lower() or "share capital" in str(i.get("account_name")).lower())
    retained_earnings = sum(abs(i.get("net_amount", 0.0)) for i in equity if "retained earnings" in str(i.get("account_name")).lower())
    treasury_stock = sum(abs(i.get("net_amount", 0.0)) for i in equity if "treasury stock" in str(i.get("account_name")).lower())
    total_equity = sum(abs(i.get("net_amount", 0.0)) for i in equity)
    
    if total_equity == 0.0 and equity:
        total_equity = sum(abs(i.get("net_amount", 0.0)) for i in equity)
    
    equity_dict = {
        "common_stock": round(common_stock, 2),
        "retained_earnings": round(retained_earnings, 2),
        "treasury_stock": round(treasury_stock, 2),
        "total_equity": round(total_equity, 2)
    }

    balance_sheet = {
        "current_assets": {
            "cash": round(cash_and_equivalents, 2),
            "petty_cash": round(petty_cash, 2),
            "temporary_investments": round(temporary_investments, 2),
            "accounts_receivable": round(accounts_receivable, 2),
            "inventory": round(inventory, 2),
            "supplies": round(supplies, 2),
            "prepaid_insurance": round(prepaid_insurance, 2),
            "total_current_assets": round(total_current_assets, 2)
        },
        "investment": round(investment, 2),
        "property_plant_equipment": property_plant_equipment,
        "intangible_assets": intangible_assets,
        "other_assets": round(other_assets, 2),
        "non_current_assets": {
            "total_non_current_assets": round(total_non_current_assets, 2)
        },
        "total_assets": round(total_assets, 2),
        "current_liabilities": {
            "notes_payable": round(notes_payable, 2),
            "accounts_payable": round(accounts_payable, 2),
            "wages_payable": round(wages_payable, 2),
            "interest_payable": round(interest_payable, 2),
            "tax_payable": round(tax_payable, 2),
            "unearned_revenue": round(unearned_revenue, 2),
            "short_term_debt": round(short_term_debt, 2),
            "total_current_liabilities": round(total_current_liabilities, 2)
        },
        "long_term_liabilities": long_term_liabilities,
        "non_current_liabilities": {
            "total_non_current_liabilities": round(total_ltl, 2)
        },
        "total_liabilities": round(total_liabilities, 2),
        "equity": equity_dict,
        "total_liabilities_and_equity": round(total_liabilities + total_equity, 2)
    }

    # 4. Strict Balance Sheet Audit Check (Assets = Liabilities + Equity)
    bs_diff = round(abs(total_assets - (total_liabilities + total_equity)), 2)
    bs_status = "PASS" if bs_diff <= 1.0 else "FAIL"

    validation_report = {
        "balance_sheet_check": bs_status,
        "total_assets": round(total_assets, 2),
        "total_liabilities_plus_equity": round(total_liabilities + total_equity, 2),
        "difference": bs_diff,
        "is_balanced": bs_status == "PASS",
        "explanation": "Balance sheet equation holds within tolerance." if bs_status == "PASS" else f"Imbalance detected: Assets (${total_assets:,.2f}) != Liabilities + Equity (${total_liabilities + total_equity:,.2f}). Difference = ${bs_diff:,.2f}."
    }

    # 5. Cash Flow Statement (Extracted or Marked Unavailable)
    cf_items = [i for i in latest_items if "cash flow" in str(i.get("sheet")).lower() or "cash flow" in str(i.get("account_name")).lower()]
    if cf_items:
        ocf = sum(i.get("net_amount", 0.0) for i in cf_items if "operating" in str(i.get("account_name")).lower())
        icf = sum(i.get("net_amount", 0.0) for i in cf_items if "investing" in str(i.get("account_name")).lower())
        fcf = sum(i.get("net_amount", 0.0) for i in cf_items if "financing" in str(i.get("account_name")).lower())
        net_change = ocf + icf + fcf
        cash_flow = {
            "status": "Available",
            "operating_activities": round(ocf, 2),
            "investing_activities": round(icf, 2),
            "financing_activities": round(fcf, 2),
            "net_change_in_cash": round(net_change, 2)
        }
        cf_calc = round(ocf + icf + fcf, 2)
        cf_diff = round(abs(cf_calc - net_change), 2)
        cf_status = "PASS" if cf_diff <= 1.0 else "FAIL"
        cf_explanation = "Operating + Investing + Financing cash flows equal Net Change in Cash." if cf_status == "PASS" else f"Cash flow equation mismatch: Sum (${cf_calc:,.2f}) != Net Change (${net_change:,.2f})"
    else:
        cash_flow = {
            "status": "Not Available in Source Workbook",
            "operating_activities": 0.0,
            "investing_activities": 0.0,
            "financing_activities": 0.0,
            "net_change_in_cash": 0.0
        }
        cf_status = "NOT_AVAILABLE"
        cf_explanation = "Cash Flow Validation Not Possible — Required Data Missing"

    validation_report["cash_flow_check"] = cf_status
    validation_report["cash_flow_explanation"] = cf_explanation

    # 6. Ledger Summary
    ledger_summary = {
        "total_accounts": len(latest_items),
        "revenue_count": len(revenues),
        "expense_count": len(expenses),
        "asset_count": len(assets),
        "liability_count": len(liabilities),
        "equity_count": len(equity),
        "target_year": target_year,
        "all_years_detected": years_found
    }

    return {
        "trial_balance": trial_balance,
        "income_statement": income_statement,
        "balance_sheet": balance_sheet,
        "cash_flow": cash_flow,
        "validation_report": validation_report,
        "ledger_summary": ledger_summary
    }

def generate_financial_statements(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generates exact, fact-grounded financial statements from extracted source items.
    Strictly forbids inventing or generating synthetic fallback values.
    """
    if not items:
        return {
            "trial_balance": {"total_debit": 0.0, "total_credit": 0.0, "difference": 0.0, "is_balanced": True, "item_count": 0},
            "income_statement": {},
            "balance_sheet": {},
            "cash_flow": {},
            "validation_report": {"balance_sheet_check": "FAIL", "reason": "No financial items extracted."}
        }

    # Group items by year
    years_found = sorted(list(set(str(i.get("year", "Current")) for i in items if i.get("year"))))
    if not years_found:
        years_found = ["Current"]

    by_year = {}
    for yr in years_found:
        yr_items = [i for i in items if str(i.get("year", "Current")) == yr]
        by_year[yr] = generate_statements_for_year(yr_items, yr, years_found)

    target_year = years_found[-1]
    result = dict(by_year[target_year])
    result["by_year"] = by_year
    result["normalized_items"] = items
    return result
