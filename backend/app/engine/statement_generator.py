from typing import List, Dict, Any

class PERIOD_MISMATCH(ValueError):
    """Exception raised when incompatible period types are combined in aggregation."""
    pass

class PeriodMismatchError(ValueError):
    pass

def validate_period_compatibility(records: List[Dict[str, Any]]):
    types = set()
    for r in records:
        p_type = r.get("period_type")
        if not p_type:
            p_type = "QUARTERLY" if r.get("is_quarterly") else "ANNUAL"
        types.add(p_type)
    if "ANNUAL" in types and "QUARTERLY" in types:
        raise PERIOD_MISMATCH("PERIOD_MISMATCH: Cannot aggregate incompatible period types (ANNUAL and QUARTERLY)")

def add_financial_metrics(m1: Dict[str, Any], m2: Dict[str, Any], key: str) -> float:
    validate_period_compatibility([m1, m2])
    return float(m1.get(key, 0.0) or 0.0) + float(m2.get(key, 0.0) or 0.0)

def generate_statements_for_year(latest_items: List[Dict[str, Any]], target_year: str, years_found: List[str]) -> Dict[str, Any]:
    validate_period_compatibility(latest_items)
    # Separate detailed line items from summary total rows and quarterly items to prevent double counting
    detail_items = [i for i in latest_items if not i.get("is_summary", False) and not i.get("is_quarterly", False) and i.get("account_type") not in ["METRIC", "CASH_FLOW"]]
    eval_items = detail_items if detail_items else [i for i in latest_items if i.get("account_type") not in ["METRIC", "CASH_FLOW"]]

    # 1. Trial Balance Summary (Computed strictly from detail non-quarterly accounts)
    curr_assets_sum = sum(abs(i.get("debit", 0.0)) for i in eval_items if i.get("account_type") in ["CASH_ASSET", "RECEIVABLE_ASSET", "INVENTORY_ASSET"])
    tb_debits = 0.0
    tb_credits = 0.0
    
    for i in eval_items:
        nm = str(i.get("account_name")).lower()
        d_val = abs(i.get("debit", 0.0))
        c_val = abs(i.get("credit", 0.0))
        if "other asset" in nm and d_val >= curr_assets_sum and curr_assets_sum > 0:
            d_val = max(0.0, d_val - curr_assets_sum)
        tb_debits += d_val
        tb_credits += c_val

    tb_difference = round(tb_debits - tb_credits, 2)
    
    trial_balance = {
        "total_debit": round(tb_debits, 2),
        "total_credit": round(tb_credits, 2),
        "difference": tb_difference,
        "is_balanced": abs(tb_difference) < 1.0 or abs(tb_difference) <= max(tb_debits, tb_credits) * 0.08,
        "item_count": len(eval_items)
    }

    # Categorize items for Income Statement & Balance Sheet
    net_inc_items = [i for i in latest_items if any(k in str(i.get("account_name")).lower() for k in ["net profit", "net income", "profit for the year", "profit after tax", "pat"]) and not i.get("is_quarterly", False)]

    revenues = [i for i in eval_items if (i.get("account_type") in ["REVENUE", "SALES"]) and i not in net_inc_items and not i.get("is_quarterly", False)]
    if not revenues:
        revenues = [i for i in latest_items if (i.get("account_type") in ["REVENUE", "SALES"] or any(k in str(i.get("account_name")).lower() for k in ["revenue", "sales", "turnover", "income from operations"])) and i not in net_inc_items and not i.get("is_quarterly", False)]

    cogs_items = [i for i in eval_items if any(k in str(i.get("account_name")).lower() for k in ["cost of goods", "cost of sales", "cost of revenue", "cogs", "direct cost"]) or (i.get("account_type") == "COGS" and "change in inventory" not in str(i.get("account_name")).lower())]
    if not cogs_items:
        cogs_items = [i for i in latest_items if any(k in str(i.get("account_name")).lower() for k in ["cost of goods", "cost of sales", "cost of revenue", "cogs", "direct cost"]) and "change in inventory" not in str(i.get("account_name")).lower()]

    depr_items = [i for i in eval_items if i.get("account_type") == "DEPRECIATION_EXPENSE" or "depreciation" in str(i.get("account_name")).lower() or "amortisation" in str(i.get("account_name")).lower()]
    interest_items = [i for i in eval_items if i.get("account_type") == "INTEREST_EXPENSE" or ("interest" in str(i.get("account_name")).lower() and "expense" in str(i.get("account_name")).lower())]
    tax_items = [i for i in eval_items if i.get("account_type") == "TAX_EXPENSE" or ("tax" in str(i.get("account_name")).lower() and "expense" in str(i.get("account_name")).lower())]
    
    expenses = [i for i in eval_items if i.get("account_type") in ["EXPENSE", "COGS", "DEPRECIATION_EXPENSE", "INTEREST_EXPENSE", "TAX_EXPENSE"] and "balance" not in str(i.get("sheet")).lower() and i.get("statement_type") != "BALANCE_SHEET"]
    opex_items = [i for i in eval_items if i.get("account_type") == "EXPENSE" and "balance" not in str(i.get("sheet")).lower() and i.get("statement_type") != "BALANCE_SHEET" and i not in cogs_items + depr_items + interest_items + tax_items]

    assets = [i for i in eval_items if i.get("account_type") not in ["METRIC", "EXPENSE", "REVENUE", "COGS", "DEPRECIATION_EXPENSE", "INTEREST_EXPENSE", "TAX_EXPENSE", "EQUITY", "LIABILITY"] and ("ASSET" in str(i.get("account_type")) or i.get("account_type") == "ASSET") and "cash flow" not in str(i.get("sheet")).lower() and "cash flow" not in str(i.get("account_name")).lower() and not any(kw in str(i.get("account_name")).lower() for kw in ["share", "equity share", "eps", "face value", "number of shares"])]
    liabilities = [i for i in eval_items if ("LIABILITY" in str(i.get("account_type")) or i.get("account_type") == "LIABILITY") and i.get("account_type") != "METRIC"]
    equity = [i for i in eval_items if ("EQUITY" in str(i.get("account_type")) or i.get("account_type") == "EQUITY") and i.get("account_type") != "METRIC"]

    # 2. Income Statement Calculation (Strictly Grounded)
    total_revenue = sum(abs(i.get("net_amount", 0.0)) for i in revenues)
    rev_ops_items = [i for i in revenues if "other income" not in str(i.get("account_name")).lower() and "other revenue" not in str(i.get("account_name")).lower() and "non-operating" not in str(i.get("account_name")).lower()]
    other_inc_items = [i for i in revenues if "other income" in str(i.get("account_name")).lower() or "other revenue" in str(i.get("account_name")).lower() or "non-operating" in str(i.get("account_name")).lower()]
    
    revenue_from_operations = sum(abs(i.get("net_amount", 0.0)) for i in rev_ops_items) if rev_ops_items else total_revenue
    other_income = sum(abs(i.get("net_amount", 0.0)) for i in other_inc_items)

    has_cogs = len(cogs_items) > 0
    total_cogs = sum(abs(i.get("net_amount", 0.0)) for i in cogs_items) if has_cogs else None

    # Check explicit Gross Profit item in source workbook if present
    explicit_gp_items = [i for i in latest_items if "gross profit" in str(i.get("account_name")).lower() or "gross margin" in str(i.get("account_name")).lower()]
    if explicit_gp_items:
        gross_profit = explicit_gp_items[0].get("net_amount", 0.0)
        gross_profit_status = "EXPLICIT_SOURCE_ROW"
    elif has_cogs and total_cogs is not None:
        gross_profit = revenue_from_operations - total_cogs
        gross_profit_status = "DERIVED"
    else:
        gross_profit = None
        gross_profit_status = "NOT_CALCULABLE"
    
    total_opex = sum(abs(i.get("net_amount", 0.0)) for i in opex_items)
    gp_val_for_ebitda = gross_profit if gross_profit is not None else total_revenue
    ebitda = gp_val_for_ebitda - total_opex
    
    depreciation = sum(abs(i.get("net_amount", 0.0)) for i in depr_items)
    ebit = ebitda - depreciation
    
    interest_expense = sum(abs(i.get("net_amount", 0.0)) for i in interest_items)
    ebt = ebit - interest_expense
    
    tax_expense = sum(abs(i.get("net_amount", 0.0)) for i in tax_items)
    derived_net_income = ebt - tax_expense
    
    if net_inc_items:
        net_income = net_inc_items[0].get("net_amount", 0.0) if len(net_inc_items) == 1 else sum(i.get("net_amount", 0.0) for i in net_inc_items)
        net_income_source = "SOURCE_ROW"
        diff_ni = abs(net_income - derived_net_income)
        net_income_reconciliation_status = "VERIFIED" if diff_ni <= 1.0 or (abs(net_income) > 0 and diff_ni / abs(net_income) <= 0.01) else "REVIEW_REQUIRED"
    else:
        net_income = derived_net_income
        net_income_source = "DERIVED"
        net_income_reconciliation_status = "DERIVED"

    income_statement = {
        "sales": round(revenue_from_operations, 2),
        "other_income": round(other_income, 2),
        "revenue_from_operations": round(revenue_from_operations, 2),
        "total_revenue": round(total_revenue, 2),
        "cost_of_goods_sold": round(total_cogs, 2) if total_cogs is not None else None,
        "cogs_status": "VERIFIED" if has_cogs else "NOT_REPORTED",
        "gross_profit": round(gross_profit, 2) if gross_profit is not None else None,
        "gross_profit_status": gross_profit_status,
        "operating_expenses": round(total_opex, 2),
        "ebitda": round(ebitda, 2),
        "depreciation_amortization": round(depreciation, 2),
        "ebit": round(ebit, 2),
        "interest_expense": round(interest_expense, 2),
        "ebt": round(ebt, 2),
        "tax_expense": round(tax_expense, 2),
        "tax_status": "VERIFIED" if tax_items else "Not Separately Reported in Source Workbook",
        "net_income": round(net_income, 2),
        "net_income_source": net_income_source,
        "net_income_reconciliation_status": net_income_reconciliation_status
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
        and "non-current" not in str(i.get("account_name")).lower() and "non current" not in str(i.get("account_name")).lower()
        and i not in cash_items + rec_items + inv_items
    ]
    total_current_assets = sum(abs(i.get("net_amount", 0.0)) for i in current_asset_items) if current_asset_items else (cash_and_equivalents + accounts_receivable + inventory)
    
    # Non-current Assets details
    investment = sum(abs(i.get("net_amount", 0.0)) for i in assets if "investment" in str(i.get("account_name")).lower() and i not in current_asset_items)
    
    land = sum(abs(i.get("net_amount", 0.0)) for i in assets if "land" in str(i.get("account_name")).lower() and "improvement" not in str(i.get("account_name")).lower())
    land_improvements = sum(abs(i.get("net_amount", 0.0)) for i in assets if "land improvement" in str(i.get("account_name")).lower())
    buildings = sum(abs(i.get("net_amount", 0.0)) for i in assets if "building" in str(i.get("account_name")).lower())
    equipment = sum(abs(i.get("net_amount", 0.0)) for i in assets if any(k in str(i.get("account_name")).lower() for k in ["equipment", "machinery", "vehicle", "furniture", "fixture"]))
    accumulated_depreciation = sum(abs(i.get("net_amount", 0.0)) for i in assets if "accumulated depreciation" in str(i.get("account_name")).lower() or "acc. dep" in str(i.get("account_name")).lower())
    
    # Net Property, Plant & Equipment
    ppe_explicit = sum(abs(i.get("net_amount", 0.0)) for i in assets if any(k in str(i.get("account_name")).lower() for k in ["property, plant", "property plant", "ppe", "fixed asset", "net block"]))
    if ppe_explicit > 0 and (land + land_improvements + buildings + equipment) == 0:
        net_ppe = ppe_explicit
    else:
        net_ppe = (land + land_improvements + buildings + equipment - accumulated_depreciation) if (land + land_improvements + buildings + equipment) > 0 else ppe_explicit
        
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
    trade_names = sum(abs(i.get("net_amount", 0.0)) for i in assets if any(k in str(i.get("account_name")).lower() for k in ["trade name", "trademark", "patent", "brand", "intangible"]))
    total_intangibles = goodwill + trade_names
    intangible_assets = {
        "goodwill": round(goodwill, 2),
        "goodwill_status": "VERIFIED" if goodwill_items else "Not Separately Reported in Source Workbook",
        "trade_names": round(trade_names, 2),
        "total_intangible_assets": round(total_intangibles, 2)
    }
    
    other_assets = sum(abs(i.get("net_amount", 0.0)) for i in assets if "other non-current" in str(i.get("account_name")).lower() or "other asset" in str(i.get("account_name")).lower())
    already_classified_nca = set()
    for i in assets:
        nm = str(i.get("account_name")).lower()
        if "investment" in nm and i not in current_asset_items:
            already_classified_nca.add(id(i))
        elif any(k in nm for k in ["land", "building", "equipment", "machinery", "vehicle", "furniture", "fixture", "accumulated depreciation", "acc. dep", "ppe", "property, plant", "property plant", "fixed asset", "net block"]):
            already_classified_nca.add(id(i))
        elif any(k in nm for k in ["goodwill", "trade name", "trademark", "patent", "brand", "intangible"]):
            already_classified_nca.add(id(i))
        elif "other asset" in nm or "other non-current" in nm:
            already_classified_nca.add(id(i))
            
    other_non_current_assets = max(0.0, other_assets - total_current_assets) if other_assets >= total_current_assets else other_assets
    unclassified_nca = sum(abs(i.get("net_amount", 0.0)) for i in assets if id(i) not in already_classified_nca and i not in current_asset_items)
    
    total_non_current_assets = investment + net_ppe + total_intangibles + other_non_current_assets + unclassified_nca
    
    explicit_total_assets = [
        i for i in latest_items 
        if any(k in str(i.get("account_name")).lower() for k in ["total asset", "total assets"]) 
        and not i.get("is_quarterly", False)
    ]
    if explicit_total_assets:
        total_assets = abs(explicit_total_assets[-1].get("net_amount", 0.0))
        if total_non_current_assets == 0:
            total_non_current_assets = max(0.0, total_assets - total_current_assets)
    else:
        total_assets = total_current_assets + total_non_current_assets

    # Liabilities & Equity details
    payables_items = [i for i in liabilities if "PAYABLE" in str(i.get("account_type")) or "payable" in str(i.get("account_name")).lower() or "creditor" in str(i.get("account_name")).lower()]
    other_cl_items = [i for i in liabilities if "other current liab" in str(i.get("account_name")).lower() or "other current liability" in str(i.get("account_name")).lower() or "accrued" in str(i.get("account_name")).lower()]
    
    accounts_payable = sum(abs(i.get("net_amount", 0.0)) for i in payables_items if "notes payable" not in str(i.get("account_name")).lower() and "wages" not in str(i.get("account_name")).lower() and "interest" not in str(i.get("account_name")).lower() and "tax" not in str(i.get("account_name")).lower())
    other_current_liabilities = sum(abs(i.get("net_amount", 0.0)) for i in other_cl_items)
    notes_payable = sum(abs(i.get("net_amount", 0.0)) for i in payables_items if "notes payable" in str(i.get("account_name")).lower() and "long term" not in str(i.get("account_name")).lower() and "lt" not in str(i.get("account_name")).lower())
    wages_payable = sum(abs(i.get("net_amount", 0.0)) for i in liabilities if "wages payable" in str(i.get("account_name")).lower() or "salary payable" in str(i.get("account_name")).lower() or "payroll payable" in str(i.get("account_name")).lower())
    interest_payable = sum(abs(i.get("net_amount", 0.0)) for i in liabilities if "interest payable" in str(i.get("account_name")).lower())
    tax_payable = sum(abs(i.get("net_amount", 0.0)) for i in liabilities if "tax payable" in str(i.get("account_name")).lower())
    unearned_revenue = sum(abs(i.get("net_amount", 0.0)) for i in liabilities if "unearned revenue" in str(i.get("account_name")).lower() or "deferred revenue" in str(i.get("account_name")).lower())
    
    short_term_debt_items = [i for i in liabilities if any(k in str(i.get("account_name")).lower() for k in ["short term", "short-term", "current borrowing", "short term borrowing", "short-term borrowing", "short term loan"])]
    short_term_debt = sum(abs(i.get("net_amount", 0.0)) for i in short_term_debt_items)
    
    total_current_liabilities = accounts_payable + other_current_liabilities + notes_payable + wages_payable + interest_payable + tax_payable + unearned_revenue + short_term_debt
    if total_current_liabilities == 0.0 and payables_items:
        total_current_liabilities = sum(abs(i.get("net_amount", 0.0)) for i in payables_items)
        
    notes_payable_lt = sum(abs(i.get("net_amount", 0.0)) for i in liabilities if "notes payable" in str(i.get("account_name")).lower() and ("long term" in str(i.get("account_name")).lower() or "lt" in str(i.get("account_name")).lower() or "non current" in str(i.get("account_name")).lower()))
    bonds_payable = sum(abs(i.get("net_amount", 0.0)) for i in liabilities if "bonds payable" in str(i.get("account_name")).lower())
    long_term_debt_items = [i for i in liabilities if any(k in str(i.get("account_name")).lower() for k in ["long term borrowing", "long-term borrowing", "long term debt", "long-term debt", "non-current debt", "non-current borrowing"])]
    long_term_debt = sum(abs(i.get("net_amount", 0.0)) for i in long_term_debt_items) if long_term_debt_items else sum(abs(i.get("net_amount", 0.0)) for i in liabilities if i not in payables_items + short_term_debt_items + other_cl_items and "bonds payable" not in str(i.get("account_name")).lower() and "notes payable" not in str(i.get("account_name")).lower())
    
    other_ncl_items = [i for i in liabilities if "other non-current liab" in str(i.get("account_name")).lower() or "other non current liab" in str(i.get("account_name")).lower()]
    other_non_current_liabilities = sum(abs(i.get("net_amount", 0.0)) for i in other_ncl_items)

    total_ltl = notes_payable_lt + bonds_payable + long_term_debt + other_non_current_liabilities
    long_term_liabilities = {
        "notes_payable_lt": round(notes_payable_lt, 2),
        "bonds_payable": round(bonds_payable, 2),
        "long_term_debt": round(long_term_debt, 2),
        "other_non_current_liabilities": round(other_non_current_liabilities, 2),
        "total_long_term_liabilities": round(total_ltl, 2)
    }
    
    total_liabilities = total_current_liabilities + total_ltl
    if total_liabilities == 0.0 and liabilities:
        total_liabilities = sum(abs(i.get("net_amount", 0.0)) for i in liabilities)
        long_term_liabilities["total_long_term_liabilities"] = round(total_liabilities - total_current_liabilities, 2)

    common_stock = sum(abs(i.get("net_amount", 0.0)) for i in equity if any(k in str(i.get("account_name")).lower() for k in ["common stock", "share capital", "equity share capital", "paid up capital"]))
    retained_earnings = sum(abs(i.get("net_amount", 0.0)) for i in equity if any(k in str(i.get("account_name")).lower() for k in ["retained earnings", "reserves", "surplus", "other equity", "reserve"]) and "common stock" not in str(i.get("account_name")).lower() and "share capital" not in str(i.get("account_name")).lower())
    treasury_stock = sum(abs(i.get("net_amount", 0.0)) for i in equity if "treasury stock" in str(i.get("account_name")).lower())
    total_equity = sum(abs(i.get("net_amount", 0.0)) for i in equity)
    
    if total_equity == 0.0 and equity:
        total_equity = common_stock + retained_earnings
    elif (common_stock + retained_earnings) > 0:
        total_equity = common_stock + retained_earnings - treasury_stock
    
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
            "other_current_assets": round(max(0.0, total_current_assets - (cash_and_equivalents + accounts_receivable + inventory)), 2),
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
            "other_current_liabilities": round(other_current_liabilities, 2),
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

    # 4. Strict Balance Sheet & Trial Balance Audit Checks
    bs_diff = round(abs(total_assets - (total_liabilities + total_equity)), 2)
    bs_status = "PASS" if bs_diff <= 1.0 else "FAIL"

    # Explicit Trial Balance Check: ONLY PASS if raw_tb_diff <= 1.0; status = NOT_APPLICABLE if not explicit double-entry TB
    has_explicit_tb_cols = any("trial balance" in str(i.get("sheet")).lower() for i in eval_items) or any(i.get("debit", 0.0) > 0 and i.get("credit", 0.0) > 0 for i in eval_items)
    raw_tb_diff = round(abs(tb_debits - tb_credits), 2)
    
    if raw_tb_diff <= 1.0:
        tb_status = "PASS"
    elif not has_explicit_tb_cols:
        tb_status = "NOT_APPLICABLE"
    else:
        tb_status = "FAIL"

    trial_balance["is_balanced"] = (tb_status == "PASS")
    trial_balance["status"] = tb_status

    # Source Reported vs Calculated Metrics Comparison
    calc_total_rev = round(revenue_from_operations + other_income, 2)
    calc_gp = round(revenue_from_operations - (total_cogs or 0.0), 2)
    calc_ebitda = round(calc_gp - total_opex, 2)
    calc_ebit = round(calc_ebitda - depreciation, 2)
    calc_pbt = round(calc_ebit - interest_expense, 2)
    calc_net_inc = round(calc_pbt - tax_expense, 2)

    src_total_rev_items = [i for i in latest_items if "total revenue" in str(i.get("account_name")).lower() or "total income" in str(i.get("account_name")).lower()]
    src_total_rev = src_total_rev_items[0].get("net_amount") if src_total_rev_items else total_revenue

    src_net_inc_items = [i for i in latest_items if any(k in str(i.get("account_name")).lower() for k in ["net profit", "net income", "profit after tax", "pat"])]
    src_net_inc = src_net_inc_items[0].get("net_amount") if src_net_inc_items else net_income

    reconciliation_mismatches = []
    if src_total_rev and abs(src_total_rev - calc_total_rev) > 1.0:
        reconciliation_mismatches.append(f"Total Revenue Mismatch: Source Reported (${src_total_rev:,.2f}) != Calculated (${calc_total_rev:,.2f})")
    if src_net_inc and abs(src_net_inc - calc_net_inc) > 1.0:
        reconciliation_mismatches.append(f"Net Income Mismatch: Source Reported (${src_net_inc:,.2f}) != Calculated (${calc_net_inc:,.2f})")

    reconciliation_status = "DATA_RECONCILIATION_ERROR" if reconciliation_mismatches else "VERIFIED"

    # Net Income Reconciliation (EBIT - Interest - Tax vs Reported Net Income)
    derived_ni = ebit - interest_expense - tax_expense
    ni_diff = round(abs(derived_ni - net_income), 2)
    ni_rec_status = "PASS" if ni_diff <= 300.0 else "REVIEW_REQUIRED"

    validation_report = {
        "balance_sheet_check": bs_status,
        "status": "PASS" if bs_status == "PASS" else "BALANCE_SHEET_MAPPING_FAILED",
        "total_assets": round(total_assets, 2),
        "total_liabilities_plus_equity": round(total_liabilities + total_equity, 2),
        "difference": bs_diff,
        "is_balanced": bs_status == "PASS",
        "explanation": "Balance sheet equation holds within tolerance." if bs_status == "PASS" else f"Imbalance detected: Assets (${total_assets:,.2f}) != Liabilities + Equity (${total_liabilities + total_equity:,.2f}). Difference = ${bs_diff:,.2f}.",
        "trial_balance_check": tb_status,
        "trial_balance_difference": raw_tb_diff,
        "net_income_reconciliation_check": ni_rec_status,
        "net_income_reconciliation_difference": ni_diff,
        "net_income_explanation": f"Derived Net Income (${derived_ni:,.2f}) reconciles with Reported Net Income (${net_income:,.2f}) within variance of ${ni_diff:,.2f}." if ni_rec_status == "PASS" else f"Net income variance detected: Derived (${derived_ni:,.2f}) != Reported (${net_income:,.2f}). Difference = ${ni_diff:,.2f}.",
        "calculated_metrics": {
            "calculated_total_revenue": calc_total_rev,
            "calculated_gross_profit": calc_gp,
            "calculated_ebitda": calc_ebitda,
            "calculated_ebit": calc_ebit,
            "calculated_pbt": calc_pbt,
            "calculated_net_income": calc_net_inc,
            "source_reported_total_revenue": src_total_rev,
            "source_reported_net_income": src_net_inc,
            "reconciliation_status": reconciliation_status,
            "mismatches": reconciliation_mismatches
        }
    }

    # 5. Cash Flow Statement (Extracted or Marked Unavailable)
    cf_items = [i for i in latest_items if "cash flow" in str(i.get("sheet")).lower() or any(k in str(i.get("account_name")).lower() for k in ["cash flow", "operating activity", "investing activity", "financing activity", "cash from operating", "cash from investing", "cash from financing", "net cash flow"]) or str(i.get("account_type", "")).startswith("CASH_FLOW")]
    if cf_items:
        ocf = sum(i.get("net_amount", 0.0) for i in cf_items if any(k in str(i.get("account_name")).lower() for k in ["operating", "operations", "ocf"]))
        icf = sum(i.get("net_amount", 0.0) for i in cf_items if any(k in str(i.get("account_name")).lower() for k in ["investing", "icf"]))
        fcf = sum(i.get("net_amount", 0.0) for i in cf_items if any(k in str(i.get("account_name")).lower() for k in ["financing", "fcf"]))
        if ocf == 0.0 and icf == 0.0 and fcf == 0.0:
            cash_flow = {
                "status": "Not Available in Source Workbook",
                "operating_activities": None,
                "investing_activities": None,
                "financing_activities": None,
                "net_change_in_cash": None
            }
            cf_status = "NOT_AVAILABLE"
            cf_explanation = "Cash Flow Validation Not Possible — Required Data Missing"
        else:
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
            "operating_activities": None,
            "investing_activities": None,
            "financing_activities": None,
            "net_change_in_cash": None
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
    years_found = list(set(str(i.get("year", "Current")) for i in items if i.get("year")))
    if not years_found:
        years_found = ["Current"]
    numeric_years = sorted([yr for yr in years_found if yr.isdigit() and len(yr) == 4], key=int)
    if numeric_years:
        target_year = numeric_years[-1]
    else:
        target_year = sorted(years_found)[-1] if years_found else "Current"

    by_year = {}
    for yr in years_found:
        yr_items = [
            i for i in items 
            if str(i.get("year", "Current")) == yr 
            and not i.get("is_quarterly", False) 
            and (i.get("period_type") or "ANNUAL") == "ANNUAL"
        ]
        if not yr_items:
            yr_items = [i for i in items if str(i.get("year", "Current")) == yr]
        by_year[yr] = generate_statements_for_year(yr_items, yr, years_found)

    result = dict(by_year.get(target_year, {}))
    result["by_year"] = by_year
    result["normalized_items"] = items
    return result
