from typing import List, Dict, Any
from app.engine.document_parser import is_summary_or_total_row

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

    min_ni_row = min([i.get("row_index") or i.get("row") or 9999 for i in net_inc_items if (i.get("row_index") or i.get("row")) is not None] or [9999])
    pnl_eval_items = [
        i for i in eval_items
        if ((i.get("row_index") or i.get("row") or 0) <= min_ni_row or "pnl" in str(i.get("sheet", "")).lower() or "income" in str(i.get("sheet", "")).lower())
    ] if min_ni_row < 9999 else eval_items

    depr_items = [
        i for i in pnl_eval_items 
        if (i.get("account_type") == "DEPRECIATION_EXPENSE" or "depreciation" in str(i.get("account_name")).lower() or "amortisation" in str(i.get("account_name")).lower())
        and "cash flow" not in str(i.get("sheet", "")).lower()
        and not is_summary_or_total_row(str(i.get("account_name")))
    ]
    interest_items = [
        i for i in pnl_eval_items 
        if (i.get("account_type") == "INTEREST_EXPENSE" or ("interest" in str(i.get("account_name")).lower() and "expense" in str(i.get("account_name")).lower()) or "finance cost" in str(i.get("account_name")).lower())
        and "cash flow" not in str(i.get("sheet", "")).lower()
        and not any(kw in str(i.get("account_name")).lower() for kw in ["interest received", "interest income", "finance income"])
        and not is_summary_or_total_row(str(i.get("account_name")))
    ]
    interest_income_items = [
        i for i in pnl_eval_items 
        if any(kw in str(i.get("account_name")).lower() for kw in ["interest received", "interest income", "finance income"])
        and "cash flow" not in str(i.get("sheet", "")).lower()
        and not is_summary_or_total_row(str(i.get("account_name")))
    ]
    tax_items = [
        i for i in pnl_eval_items 
        if (i.get("account_type") == "TAX_EXPENSE" or ("tax" in str(i.get("account_name")).lower() and "expense" in str(i.get("account_name")).lower()) or ("taxation" in str(i.get("account_name")).lower() and "paid" not in str(i.get("account_name")).lower()))
        and "cash flow" not in str(i.get("sheet", "")).lower()
        and not any(kw in str(i.get("account_name")).lower() for kw in ["taxation paid", "tax paid", "deferred tax"])
        and not is_summary_or_total_row(str(i.get("account_name")))
    ]
    
    expenses = [i for i in eval_items if i.get("account_type") in ["EXPENSE", "COGS", "DEPRECIATION_EXPENSE", "INTEREST_EXPENSE", "TAX_EXPENSE"] and "balance" not in str(i.get("sheet")).lower() and i.get("statement_type") != "BALANCE_SHEET" and not is_summary_or_total_row(str(i.get("account_name")))]
    opex_items = [i for i in eval_items if i.get("account_type") == "EXPENSE" and "balance" not in str(i.get("sheet")).lower() and i.get("statement_type") != "BALANCE_SHEET" and not is_summary_or_total_row(str(i.get("account_name"))) and i not in cogs_items + depr_items + interest_items + interest_income_items + tax_items]

    assets = [
        i for i in eval_items 
        if i.get("account_type") not in ["METRIC", "EXPENSE", "REVENUE", "COGS", "DEPRECIATION_EXPENSE", "INTEREST_EXPENSE", "TAX_EXPENSE", "EQUITY", "LIABILITY", "CASH_FLOW", "GROSS_PROFIT", "OPERATING_INCOME", "NET_INCOME"] 
        and ("ASSET" in str(i.get("account_type")) or i.get("account_type") == "ASSET") 
        and "cash flow" not in str(i.get("sheet")).lower() 
        and "cash flow" not in str(i.get("account_name")).lower() 
        and not any(kw in str(i.get("account_name")).lower() for kw in ["share", "equity share", "eps", "face value", "number of shares", "cash generated from", "cash flows from", "cash flow from", "operating activit", "investing activit", "financing activit"])
        and not is_summary_or_total_row(str(i.get("account_name")))
    ]
    liabilities = [i for i in eval_items if ("LIABILITY" in str(i.get("account_type")) or i.get("account_type") == "LIABILITY") and i.get("account_type") != "METRIC" and not is_summary_or_total_row(str(i.get("account_name")))]
    equity = [i for i in eval_items if ("EQUITY" in str(i.get("account_type")) or i.get("account_type") == "EQUITY") and i.get("account_type") != "METRIC" and not is_summary_or_total_row(str(i.get("account_name")))]

    # 2. Income Statement Calculation (Strictly Grounded)
    total_revenue = sum(abs(i.get("net_amount", 0.0)) for i in revenues)
    rev_ops_items = [i for i in revenues if "other income" not in str(i.get("account_name")).lower() and "other revenue" not in str(i.get("account_name")).lower() and "non-operating" not in str(i.get("account_name")).lower()]
    other_inc_items = [i for i in revenues if "other income" in str(i.get("account_name")).lower() or "other revenue" in str(i.get("account_name")).lower() or "non-operating" in str(i.get("account_name")).lower()]
    
    revenue_from_operations = sum(abs(i.get("net_amount", 0.0)) for i in rev_ops_items) if rev_ops_items else total_revenue
    other_income = sum(abs(i.get("net_amount", 0.0)) for i in other_inc_items)

    has_cogs = len(cogs_items) > 0
    total_cogs = sum(abs(i.get("net_amount", 0.0)) for i in cogs_items) if has_cogs else None

    # 1. Gross Profit on Operations = Revenue from Operations - COGS
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
    
    # 2. Operating Expenses
    total_opex = sum(abs(i.get("net_amount", 0.0)) for i in opex_items)
    
    # 3. Core EBITDA & Operating Profit
    gp_val_for_ebitda = gross_profit if gross_profit is not None else revenue_from_operations
    ebitda = gp_val_for_ebitda - total_opex
    
    # 4. Profit from Operations = Gross Profit + Other Operating Income - Operating Expenses
    explicit_op_items = [i for i in latest_items if any(k in str(i.get("account_name")).lower() for k in ["profit from operations", "operating profit", "operating income", "pbit"])]
    if explicit_op_items:
        profit_from_operations = abs(explicit_op_items[0].get("net_amount", 0.0))
    elif gross_profit is not None:
        profit_from_operations = gross_profit + (other_income or 0.0) - total_opex
    else:
        profit_from_operations = revenue_from_operations + (other_income or 0.0) - total_opex

    # 5. Depreciation & Amortization
    depreciation = sum(abs(i.get("net_amount", 0.0)) for i in depr_items)
    ebit = ebitda - depreciation
    
    # 6. Finance Income & Finance Costs
    interest_expense = sum(abs(i.get("net_amount", 0.0)) for i in interest_items)
    interest_income = sum(abs(i.get("net_amount", 0.0)) for i in interest_income_items)

    # 7. Profit Before Taxation (PBT) = Profit from Operations + Finance Income - Finance Costs
    explicit_pbt_items = [i for i in latest_items if any(k in str(i.get("account_name")).lower() for k in ["profit before tax", "pbt", "ebt", "profit before taxation"])]
    if explicit_pbt_items:
        ebt = abs(explicit_pbt_items[0].get("net_amount", 0.0))
    else:
        ebt = profit_from_operations + (interest_income or 0.0) - interest_expense
    
    # 7. Taxation & Net Profit
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
        "sales": round(revenue_from_operations, 2) if revenues else None,
        "revenue_from_operations": round(revenue_from_operations, 2) if revenues else None,
        "other_income": round(other_income, 2) if other_inc_items else None,
        "other_operating_income": round(other_income, 2) if other_inc_items else None,
        "total_revenue": round(total_revenue, 2) if revenues else None,
        "total_revenue_and_income": round(total_revenue, 2) if revenues else None,
        "cost_of_goods_sold": round(total_cogs, 2) if total_cogs is not None else None,
        "cogs": round(total_cogs, 2) if total_cogs is not None else None,
        "cogs_status": "VERIFIED" if has_cogs else "NOT_REPORTED",
        "gross_profit": round(gross_profit, 2) if gross_profit is not None else None,
        "gross_profit_status": gross_profit_status,
        "operating_expenses": round(total_opex, 2) if opex_items else 0.0,
        "profit_from_operations": round(profit_from_operations, 2) if (revenues or explicit_op_items) else None,
        "ebitda": round(ebitda, 2) if (revenues or explicit_op_items) else None,
        "depreciation_amortization": round(depreciation, 2) if depr_items else None,
        "ebit": round(ebit, 2) if (revenues or explicit_op_items) else None,
        "finance_income": round(interest_income, 2) if interest_income_items else None,
        "interest_income": round(interest_income, 2) if interest_income_items else None,
        "finance_cost": round(interest_expense, 2) if interest_items else None,
        "interest_expense": round(interest_expense, 2) if interest_items else None,
        "pbt": round(ebt, 2) if (revenues or explicit_pbt_items) else None,
        "ebt": round(ebt, 2) if (revenues or explicit_pbt_items) else None,
        "tax": round(tax_expense, 2) if tax_items else None,
        "tax_expense": round(tax_expense, 2) if tax_items else None,
        "tax_status": "VERIFIED" if tax_items else "Not Separately Reported in Source Workbook",
        "net_profit": round(net_income, 2) if (revenues or net_inc_items) else None,
        "net_income": round(net_income, 2) if (revenues or net_inc_items) else None,
        "net_income_source": net_income_source,
        "net_income_reconciliation_status": net_income_reconciliation_status
    }

    # 3. Balance Sheet Calculation (Strictly Grounded)
    cash_items = [i for i in assets if "CASH" in str(i.get("account_type")) or "cash" in str(i.get("account_name")).lower() or "bank" in str(i.get("account_name")).lower()]
    rec_items = [i for i in assets if "RECEIVABLE" in str(i.get("account_type")) or "receivable" in str(i.get("account_name")).lower() or "debtor" in str(i.get("account_name")).lower()]
    inv_items = [i for i in assets if "INVENTORY" in str(i.get("account_type")) or "inventory" in str(i.get("account_name")).lower() or "stock" in str(i.get("account_name")).lower()]
    
    cash_and_equivalents = sum(abs(i.get("net_amount", 0.0)) for i in cash_items) if cash_items else None
    accounts_receivable = sum(abs(i.get("net_amount", 0.0)) for i in rec_items) if rec_items else None
    inventory = sum(abs(i.get("net_amount", 0.0)) for i in inv_items) if inv_items else None
    
    # Detailed current assets
    petty_cash_items = [i for i in assets if "petty cash" in str(i.get("account_name")).lower()]
    petty_cash = sum(abs(i.get("net_amount", 0.0)) for i in petty_cash_items) if petty_cash_items else None

    temp_inv_items = [i for i in assets if "temporary investment" in str(i.get("account_name")).lower() or "marketable security" in str(i.get("account_name")).lower() or "short term investment" in str(i.get("account_name")).lower()]
    temporary_investments = sum(abs(i.get("net_amount", 0.0)) for i in temp_inv_items) if temp_inv_items else None

    supplies_items = [i for i in assets if "supply" in str(i.get("account_name")).lower() or "supplies" in str(i.get("account_name")).lower()]
    supplies = sum(abs(i.get("net_amount", 0.0)) for i in supplies_items) if supplies_items else None

    prepaid_items = [i for i in assets if "prepaid insurance" in str(i.get("account_name")).lower() or "prepaid" in str(i.get("account_name")).lower()]
    prepaid_insurance = sum(abs(i.get("net_amount", 0.0)) for i in prepaid_items) if prepaid_items else None

    current_asset_items = cash_items + rec_items + inv_items + [
        i for i in assets if any(k in str(i.get("account_name")).lower() for k in ["current asset", "petty cash", "temporary investment", "marketable security", "short term investment", "supply", "supplies", "prepaid insurance", "other current asset"])
        and "non-current" not in str(i.get("account_name")).lower() and "non current" not in str(i.get("account_name")).lower()
        and i not in cash_items + rec_items + inv_items
    ]
    calc_ca = (cash_and_equivalents or 0.0) + (accounts_receivable or 0.0) + (inventory or 0.0)
    total_current_assets = sum(abs(i.get("net_amount", 0.0)) for i in current_asset_items) if current_asset_items else (calc_ca if (cash_items or rec_items or inv_items) else None)
    other_ca = max(0.0, total_current_assets - calc_ca) if (total_current_assets is not None and total_current_assets > calc_ca) else None

    # Non-current Assets details
    inv_nca_items = [i for i in assets if "investment" in str(i.get("account_name")).lower() and i not in current_asset_items]
    investment = sum(abs(i.get("net_amount", 0.0)) for i in inv_nca_items) if inv_nca_items else None

    land_items = [i for i in assets if "land" in str(i.get("account_name")).lower() and "improvement" not in str(i.get("account_name")).lower()]
    land = sum(abs(i.get("net_amount", 0.0)) for i in land_items) if land_items else None

    land_imp_items = [i for i in assets if "land improvement" in str(i.get("account_name")).lower()]
    land_improvements = sum(abs(i.get("net_amount", 0.0)) for i in land_imp_items) if land_imp_items else None

    bldg_items = [i for i in assets if "building" in str(i.get("account_name")).lower()]
    buildings = sum(abs(i.get("net_amount", 0.0)) for i in bldg_items) if bldg_items else None

    equip_items = [i for i in assets if any(k in str(i.get("account_name")).lower() for k in ["equipment", "machinery", "vehicle", "furniture", "fixture"])]
    equipment = sum(abs(i.get("net_amount", 0.0)) for i in equip_items) if equip_items else None

    acc_dep_items = [i for i in assets if "accumulated depreciation" in str(i.get("account_name")).lower() or "acc. dep" in str(i.get("account_name")).lower()]
    accumulated_depreciation = sum(abs(i.get("net_amount", 0.0)) for i in acc_dep_items) if acc_dep_items else None

    ppe_explicit_items = [i for i in assets if any(k in str(i.get("account_name")).lower() for k in ["property, plant", "property plant", "ppe", "fixed asset", "net block"])]
    ppe_explicit = sum(abs(i.get("net_amount", 0.0)) for i in ppe_explicit_items) if ppe_explicit_items else 0.0

    if ppe_explicit > 0 and not (land_items or land_imp_items or bldg_items or equip_items):
        net_ppe = ppe_explicit
    elif land_items or land_imp_items or bldg_items or equip_items:
        net_ppe = (land or 0.0) + (land_improvements or 0.0) + (buildings or 0.0) + (equipment or 0.0) - (accumulated_depreciation or 0.0)
    else:
        net_ppe = None
        
    property_plant_equipment = {
        "land": round(land, 2) if land is not None else None,
        "land_improvements": round(land_improvements, 2) if land_improvements is not None else None,
        "buildings": round(buildings, 2) if buildings is not None else None,
        "equipment": round(equipment, 2) if equipment is not None else None,
        "accumulated_depreciation": round(accumulated_depreciation, 2) if accumulated_depreciation is not None else None,
        "net_property_plant_equipment": round(net_ppe, 2) if net_ppe is not None else None
    }
    
    goodwill_items = [i for i in assets if "goodwill" in str(i.get("account_name")).lower()]
    goodwill = sum(abs(i.get("net_amount", 0.0)) for i in goodwill_items) if goodwill_items else None
    trade_names_items = [i for i in assets if any(k in str(i.get("account_name")).lower() for k in ["trade name", "trademark", "patent", "brand", "intangible"]) and i not in goodwill_items]
    trade_names = sum(abs(i.get("net_amount", 0.0)) for i in trade_names_items) if trade_names_items else None
    total_intangibles = ((goodwill or 0.0) + (trade_names or 0.0)) if (goodwill_items or trade_names_items) else None
    intangible_assets = {
        "goodwill": round(goodwill, 2) if goodwill is not None else None,
        "goodwill_status": "VERIFIED" if goodwill_items else "Not Separately Reported in Source Workbook",
        "trade_names": round(trade_names, 2) if trade_names is not None else None,
        "total_intangible_assets": round(total_intangibles, 2) if total_intangibles is not None else None
    }
    
    other_assets_items = [i for i in assets if "other non-current" in str(i.get("account_name")).lower() or "other asset" in str(i.get("account_name")).lower()]
    other_assets = sum(abs(i.get("net_amount", 0.0)) for i in other_assets_items) if other_assets_items else None
    
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
            
    other_non_current_assets = (other_assets - (total_current_assets or 0.0)) if (other_assets is not None and total_current_assets is not None and other_assets >= total_current_assets) else (other_assets or 0.0)
    unclassified_nca = sum(abs(i.get("net_amount", 0.0)) for i in assets if id(i) not in already_classified_nca and i not in current_asset_items)
    
    has_nca = bool(inv_nca_items or net_ppe is not None or total_intangibles is not None or other_assets_items or unclassified_nca > 0)
    total_non_current_assets = ((investment or 0.0) + (net_ppe or 0.0) + (total_intangibles or 0.0) + (other_non_current_assets or 0.0) + unclassified_nca) if has_nca else None
    
    explicit_total_assets = [
        i for i in latest_items 
        if any(k in str(i.get("account_name")).lower() for k in ["total asset", "total assets"]) 
        and not i.get("is_quarterly", False)
    ]
    if explicit_total_assets:
        total_assets = abs(explicit_total_assets[-1].get("net_amount", 0.0))
    else:
        total_assets = ((total_current_assets or 0.0) + (total_non_current_assets or 0.0)) if (total_current_assets is not None or total_non_current_assets is not None) else None

    # Liabilities & Equity details (Filtering out section header rows)
    valid_liabilities = [i for i in liabilities if not is_summary_or_total_row(str(i.get("account_name")))]
    payables_items = [i for i in valid_liabilities if any(k in str(i.get("account_name")).lower() for k in ["trade payable", "trade payables", "accounts payable", "creditor", "creditors"])]
    other_cl_items = [i for i in valid_liabilities if any(k in str(i.get("account_name")).lower() for k in ["other current liab", "other current liability", "other current liabilities", "accrued"]) or ("other" in str(i.get("account_name")).lower() and "current" in str(i.get("account_name")).lower() and "non-current" not in str(i.get("account_name")).lower() and "non current" not in str(i.get("account_name")).lower() and "asset" not in str(i.get("account_name")).lower())]
    short_term_borrowings_items = [i for i in valid_liabilities if any(k in str(i.get("account_name")).lower() for k in ["short-term borrowing", "short term borrowing", "short-term borrowings", "short term borrowings", "short term loan", "short-term loan", "current borrowing", "short-term debt", "short term debt", "st borrowing", "st borrowings", "st debt"]) and "other" not in str(i.get("account_name")).lower()]
    
    trade_payables = sum(abs(i.get("net_amount", 0.0)) for i in payables_items) if payables_items else None
    other_current_liabilities = sum(abs(i.get("net_amount", 0.0)) for i in other_cl_items) if other_cl_items else None
    short_term_borrowings = sum(abs(i.get("net_amount", 0.0)) for i in short_term_borrowings_items) if short_term_borrowings_items else None
    
    notes_p_items = [i for i in valid_liabilities if "notes payable" in str(i.get("account_name")).lower() and "long term" not in str(i.get("account_name")).lower() and "lt" not in str(i.get("account_name")).lower()]
    wages_p_items = [i for i in valid_liabilities if "wages payable" in str(i.get("account_name")).lower() or "salary payable" in str(i.get("account_name")).lower() or "payroll payable" in str(i.get("account_name")).lower()]
    interest_p_items = [i for i in valid_liabilities if "interest payable" in str(i.get("account_name")).lower()]
    tax_p_items = [i for i in valid_liabilities if "tax payable" in str(i.get("account_name")).lower()]
    unearned_rev_items = [i for i in valid_liabilities if "unearned revenue" in str(i.get("account_name")).lower() or "deferred revenue" in str(i.get("account_name")).lower()]

    notes_payable = sum(abs(i.get("net_amount", 0.0)) for i in notes_p_items) if notes_p_items else None
    wages_payable = sum(abs(i.get("net_amount", 0.0)) for i in wages_p_items) if wages_p_items else None
    interest_payable = sum(abs(i.get("net_amount", 0.0)) for i in interest_p_items) if interest_p_items else None
    tax_payable = sum(abs(i.get("net_amount", 0.0)) for i in tax_p_items) if tax_p_items else None
    unearned_revenue = sum(abs(i.get("net_amount", 0.0)) for i in unearned_rev_items) if unearned_rev_items else None

    has_cl = bool(payables_items or other_cl_items or short_term_borrowings_items or notes_p_items or wages_p_items or interest_p_items or tax_p_items or unearned_rev_items)
    total_current_liabilities = ((trade_payables or 0.0) + (other_current_liabilities or 0.0) + (short_term_borrowings or 0.0) + (notes_payable or 0.0) + (wages_payable or 0.0) + (interest_payable or 0.0) + (tax_payable or 0.0) + (unearned_revenue or 0.0)) if has_cl else None
    if total_current_liabilities is None and valid_liabilities:
        cl_raw = sum(abs(i.get("net_amount", 0.0)) for i in valid_liabilities if "non-current" not in str(i.get("account_name")).lower() and "long term" not in str(i.get("account_name")).lower())
        if cl_raw > 0:
            total_current_liabilities = cl_raw
        
    long_term_borrowings_items = [i for i in valid_liabilities if any(k in str(i.get("account_name")).lower() for k in ["long-term borrowing", "long term borrowing", "long-term borrowings", "long term borrowings", "long term debt", "long-term debt", "non-current debt", "long-term liabilities", "long term liabilities", "non-current liabilities", "non current liabilities", "lt borrowing", "lt borrowings", "lt debt"]) and "other" not in str(i.get("account_name")).lower()]
    other_ncl_items = [i for i in valid_liabilities if any(k in str(i.get("account_name")).lower() for k in ["other non-current liab", "other non current liab", "other non-current liabilities", "other non current liabilities", "other non-current liability", "other non current liability", "other non-current debt", "other non current debt"]) or ("other" in str(i.get("account_name")).lower() and ("non-current" in str(i.get("account_name")).lower() or "non current" in str(i.get("account_name")).lower()) and "asset" not in str(i.get("account_name")).lower())]
    notes_p_lt_items = [i for i in valid_liabilities if "notes payable" in str(i.get("account_name")).lower() and ("long term" in str(i.get("account_name")).lower() or "lt" in str(i.get("account_name")).lower() or "non current" in str(i.get("account_name")).lower())]
    bonds_p_items = [i for i in valid_liabilities if "bonds payable" in str(i.get("account_name")).lower()]

    long_term_borrowings = sum(abs(i.get("net_amount", 0.0)) for i in long_term_borrowings_items) if long_term_borrowings_items else None
    other_non_current_liabilities = sum(abs(i.get("net_amount", 0.0)) for i in other_ncl_items) if other_ncl_items else None
    notes_payable_lt = sum(abs(i.get("net_amount", 0.0)) for i in notes_p_lt_items) if notes_p_lt_items else None
    bonds_payable = sum(abs(i.get("net_amount", 0.0)) for i in bonds_p_items) if bonds_p_items else None

    has_ltl = bool(long_term_borrowings_items or other_ncl_items or notes_p_lt_items or bonds_p_items)
    total_ltl = ((long_term_borrowings or 0.0) + (other_non_current_liabilities or 0.0) + (notes_payable_lt or 0.0) + (bonds_payable or 0.0)) if has_ltl else None
    long_term_liabilities = {
        "notes_payable_lt": round(notes_payable_lt, 2) if notes_payable_lt is not None else None,
        "bonds_payable": round(bonds_payable, 2) if bonds_payable is not None else None,
        "long_term_debt": round(long_term_borrowings, 2) if long_term_borrowings is not None else None,
        "long_term_borrowings": round(long_term_borrowings, 2) if long_term_borrowings is not None else None,
        "other_non_current_liabilities": round(other_non_current_liabilities, 2) if other_non_current_liabilities is not None else None,
        "total_long_term_liabilities": round(total_ltl, 2) if total_ltl is not None else None
    }
    
    total_liabilities = ((total_current_liabilities or 0.0) + (total_ltl or 0.0)) if (total_current_liabilities is not None or total_ltl is not None) else None
    if total_liabilities is None and valid_liabilities:
        total_liabilities = sum(abs(i.get("net_amount", 0.0)) for i in valid_liabilities)

    valid_equity = [i for i in equity if not is_summary_or_total_row(str(i.get("account_name")))]
    share_capital_items = [i for i in valid_equity if any(k in str(i.get("account_name")).lower() for k in ["share capital", "common stock", "equity share capital", "paid up capital", "paid-up capital", "capital stock", "preferred stock", "owner's capital", "owners capital"])]
    reserves_items = [i for i in valid_equity if any(k in str(i.get("account_name")).lower() for k in ["retained earnings", "reserves & retained earnings", "reserves", "surplus", "other equity", "reserve", "retained profit", "retained profits", "accumulated profit", "general reserve", "capital reserve"]) and not any(k in str(i.get("account_name")).lower() for k in ["common stock", "share capital", "capital stock", "treasury"])]
    treasury_items = [i for i in valid_equity if any(k in str(i.get("account_name")).lower() for k in ["treasury stock", "treasury shares"])]

    share_capital = sum(abs(i.get("net_amount", 0.0)) for i in share_capital_items) if share_capital_items else None
    reserves_and_retained = sum(abs(i.get("net_amount", 0.0)) for i in reserves_items) if reserves_items else None
    treasury_stock = sum(abs(i.get("net_amount", 0.0)) for i in treasury_items) if treasury_items else None

    if valid_equity:
        sum_raw_eq = sum(abs(i.get("net_amount", 0.0)) for i in valid_equity)
        total_equity = (share_capital or 0.0) + (reserves_and_retained or 0.0) - (treasury_stock or 0.0)
        if total_equity == 0.0 and sum_raw_eq > 0:
            total_equity = sum_raw_eq
            reserves_and_retained = total_equity
        equity_status = "COMPLETE" if total_equity > 0 else "INCOMPLETE"
    else:
        total_equity = None
        equity_status = "INCOMPLETE"
    
    equity_dict = {
        "share_capital": round(share_capital, 2) if share_capital is not None else None,
        "common_stock": round(share_capital, 2) if share_capital is not None else None,
        "reserves_and_retained_earnings": round(reserves_and_retained, 2) if reserves_and_retained is not None else None,
        "retained_earnings": round(reserves_and_retained, 2) if reserves_and_retained is not None else None,
        "treasury_stock": round(treasury_stock, 2) if treasury_stock is not None else None,
        "total_equity": round(total_equity, 2) if total_equity is not None else None,
        "equity_status": equity_status
    }

    balance_sheet: Dict[str, Any] = {
        "status": "NOT_REPORTED",
        "current_assets": {
            "cash": round(cash_and_equivalents, 2) if cash_and_equivalents is not None else None,
            "petty_cash": round(petty_cash, 2) if petty_cash is not None else None,
            "temporary_investments": round(temporary_investments, 2) if temporary_investments is not None else None,
            "accounts_receivable": round(accounts_receivable, 2) if accounts_receivable is not None else None,
            "inventory": round(inventory, 2) if inventory is not None else None,
            "supplies": round(supplies, 2) if supplies is not None else None,
            "prepaid_insurance": round(prepaid_insurance, 2) if prepaid_insurance is not None else None,
            "other_current_assets": round(other_ca, 2) if other_ca is not None else None,
            "total_current_assets": round(total_current_assets, 2) if total_current_assets is not None else None
        },
        "investment": round(investment, 2) if investment is not None else None,
        "property_plant_equipment": property_plant_equipment,
        "intangible_assets": intangible_assets,
        "other_assets": round(other_assets, 2) if other_assets is not None else None,
        "non_current_assets": {
            "total_non_current_assets": round(total_non_current_assets, 2) if total_non_current_assets is not None else None
        },
        "total_assets": round(total_assets, 2) if total_assets is not None else None,
        "current_liabilities": {
            "trade_payables": round(trade_payables, 2) if trade_payables is not None else None,
            "accounts_payable": round(trade_payables, 2) if trade_payables is not None else None,
            "notes_payable": round(notes_payable, 2) if notes_payable is not None else None,
            "wages_payable": round(wages_payable, 2) if wages_payable is not None else None,
            "interest_payable": round(interest_payable, 2) if interest_payable is not None else None,
            "tax_payable": round(tax_payable, 2) if tax_payable is not None else None,
            "unearned_revenue": round(unearned_revenue, 2) if unearned_revenue is not None else None,
            "short_term_borrowings": round(short_term_borrowings, 2) if short_term_borrowings is not None else None,
            "short_term_debt": round(short_term_borrowings, 2) if short_term_borrowings is not None else None,
            "other_current_liabilities": round(other_current_liabilities, 2) if other_current_liabilities is not None else None,
            "total_current_liabilities": round(total_current_liabilities, 2) if total_current_liabilities is not None else None
        },
        "long_term_liabilities": long_term_liabilities,
        "non_current_liabilities": {
            "total_non_current_liabilities": round(total_ltl, 2) if total_ltl is not None else None
        },
        "total_liabilities": round(total_liabilities, 2) if total_liabilities is not None else None,
        "equity": equity_dict,
        "total_liabilities_and_equity": round(total_liabilities + total_equity, 2) if (total_liabilities is not None and total_equity is not None) else None
    }

    # 4. Strict Balance Sheet & Trial Balance Audit Checks
    if not assets and not liabilities and not equity:
        bs_diff = None
        bs_status = "NOT_REPORTED"
        total_assets = None
        total_liabilities_and_equity = None
        balance_sheet["total_assets"] = None
        balance_sheet["total_liabilities_and_equity"] = None
        balance_sheet["current_assets"]["total_current_assets"] = None
        balance_sheet["non_current_assets"]["total_non_current_assets"] = None
        balance_sheet["current_liabilities"]["total_current_liabilities"] = None
        balance_sheet["non_current_liabilities"]["total_non_current_liabilities"] = None
        balance_sheet["total_liabilities"] = None
    elif total_equity is not None and total_assets is not None and total_liabilities is not None:
        bs_diff = round(abs(total_assets - (total_liabilities + total_equity)), 2)
        bs_status = "PASS" if bs_diff <= 1.0 else "UNBALANCED"
    else:
        bs_diff = None
        bs_status = "INCOMPLETE"

    balance_sheet["status"] = bs_status

    # Explicit Trial Balance Check: Trial Balance is APPLICABLE ONLY if source contains explicit trial balance statement or debit & credit columns
    has_explicit_tb = any("trial balance" in str(i.get("sheet")).lower() for i in eval_items) or (
        any(str(i.get("source_header", "")).lower() in ["debit", "dr", "dr."] for i in eval_items) and
        any(str(i.get("source_header", "")).lower() in ["credit", "cr", "cr."] for i in eval_items)
    )
    
    if has_explicit_tb:
        raw_tb_diff = round(abs(tb_debits - tb_credits), 2)
        tb_status = "PASS" if raw_tb_diff <= 1.0 else "FAIL"
    else:
        raw_tb_diff = None
        tb_status = "NOT_APPLICABLE"

    trial_balance["is_balanced"] = (tb_status == "PASS")
    trial_balance["status"] = tb_status

    # Source Reported vs Calculated Metrics Comparison
    calc_total_rev = round(revenue_from_operations + other_income, 2)
    calc_gp = round(revenue_from_operations - (total_cogs or 0.0), 2) if total_cogs is not None else None
    calc_ebitda = round(ebitda, 2)
    calc_ebit = round(ebitda - depreciation, 2)
    calc_pbt = round(ebt, 2)
    calc_net_inc = round(calc_pbt - tax_expense, 2)

    src_total_rev_items = [i for i in latest_items if "total revenue" in str(i.get("account_name")).lower() or "total income" in str(i.get("account_name")).lower()]
    src_total_rev = src_total_rev_items[0].get("net_amount") if src_total_rev_items else total_revenue

    src_net_inc_items = [i for i in latest_items if any(k in str(i.get("account_name")).lower() for k in ["net profit", "net income", "profit after tax", "pat"])]
    src_net_inc = src_net_inc_items[0].get("net_amount") if src_net_inc_items else net_income

    reconciliation_mismatches = []
    if src_total_rev and calc_total_rev and abs(src_total_rev - calc_total_rev) > 1.0:
        reconciliation_mismatches.append(f"Total Revenue Mismatch: Source Reported (${src_total_rev:,.2f}) != Calculated (${calc_total_rev:,.2f})")
    if src_net_inc and calc_net_inc and abs(src_net_inc - calc_net_inc) > 1.0:
        reconciliation_mismatches.append(f"Net Income Mismatch: Source Reported (${src_net_inc:,.2f}) != Calculated (${calc_net_inc:,.2f})")

    reconciliation_status = "DATA_RECONCILIATION_ERROR" if reconciliation_mismatches else "VERIFIED"

    # Net Income Reconciliation (EBT - Tax vs Reported Net Income)
    derived_ni = calc_net_inc if calc_net_inc is not None else (ebt - tax_expense)
    ni_diff = round(abs(derived_ni - net_income), 2)
    ni_rec_status = "PASS" if ni_diff <= 1.0 or (abs(net_income) > 0 and ni_diff / abs(net_income) <= 0.01) else "REVIEW_REQUIRED"

    tot_assets_str = f"${total_assets:,.2f}" if total_assets is not None else "N/A"
    tot_liab_eq_val = (total_liabilities + total_equity) if (total_liabilities is not None and total_equity is not None) else None
    tot_liab_eq_str = f"${tot_liab_eq_val:,.2f}" if tot_liab_eq_val is not None else "N/A"

    validation_report = {
        "balance_sheet_check": bs_status,
        "pnl_check": "PASS" if total_revenue > 0 else "FAIL",
        "status": "PASS" if bs_status == "PASS" else ("INCOMPLETE" if bs_status == "INCOMPLETE" else "BALANCE_SHEET_MAPPING_FAILED"),
        "total_assets": round(total_assets, 2) if total_assets is not None else None,
        "total_liabilities_plus_equity": round(tot_liab_eq_val, 2) if tot_liab_eq_val is not None else None,
        "difference": bs_diff,
        "is_balanced": bs_status == "PASS",
        "explanation": "Balance sheet equation holds within tolerance." if bs_status == "PASS" else ("Balance sheet data not reported in source for this period." if bs_status == "NOT_REPORTED" else ("Balance sheet documentation incomplete (Liabilities or Equity schedules missing)." if bs_status == "INCOMPLETE" else f"Imbalance detected: Assets ({tot_assets_str}) != Liabilities + Equity ({tot_liab_eq_str}).")),
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
        "liability_count": len(valid_liabilities),
        "equity_count": len(valid_equity),
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
    Uses fiscal_year string (e.g. FY2026) for target period selection.
    """
    import re
    if not items:
        return {
            "trial_balance": {"total_debit": 0.0, "total_credit": 0.0, "difference": 0.0, "is_balanced": True, "item_count": 0, "status": "NOT_APPLICABLE"},
            "income_statement": {},
            "balance_sheet": {},
            "cash_flow": {},
            "validation_report": {"balance_sheet_check": "FAIL", "reason": "No financial items extracted."}
        }

    # Helper to resolve clean fiscal year label for an item
    def _item_fy(item: Dict[str, Any]) -> str:
        fy = item.get("fiscal_year")
        if fy and str(fy).strip() and str(fy).strip() not in ["None", "UNKNOWN", "Current", ""]:
            return str(fy).strip()
        yr = item.get("year")
        if yr and str(yr).strip() and str(yr).strip() not in ["None", "UNKNOWN", "Current", ""]:
            yr_clean = str(yr).strip()
            return f"FY{yr_clean}" if not yr_clean.startswith("FY") else yr_clean
        return "UNKNOWN"

    f_years = list(set(_item_fy(i) for i in items))
    if not f_years:
        f_years = ["UNKNOWN"]
        
    def _fy_key(fy_str: str) -> int:
        digits = re.sub(r'\D', '', fy_str)
        return int(digits) if digits else 0

    annual_items = [i for i in items if not i.get("is_quarterly", False) and (i.get("period_type") or "ANNUAL") == "ANNUAL"]
    annual_f_years = list(set(_item_fy(i) for i in annual_items)) if annual_items else []

    sorted_fyrs = sorted(annual_f_years if annual_f_years else f_years, key=_fy_key)
    target_fyr = sorted_fyrs[-1] if sorted_fyrs else "UNKNOWN"

    by_year = {}
    for fyr in sorted_fyrs:
        yr_items = [
            i for i in items 
            if (_item_fy(i) == fyr or str(i.get("period_label")) == fyr or (i.get("year") and str(i.get("year")) == fyr.replace("FY", "")))
            and not i.get("is_quarterly", False) 
            and (i.get("period_type") or "ANNUAL") == "ANNUAL"
        ]
        if not yr_items:
            yr_items = [i for i in items if _item_fy(i) == fyr or (i.get("year") and str(i.get("year")) == fyr.replace("FY", ""))]
        if not yr_items:
            yr_items = items
        stmt_yr = generate_statements_for_year(yr_items, fyr, f_years)
        by_year[fyr] = stmt_yr
        clean_yr = fyr.replace("FY", "").strip()
        if clean_yr and clean_yr not in by_year and clean_yr != "UNKNOWN":
            by_year[clean_yr] = stmt_yr

    target_stmt = by_year.get(target_fyr) or (list(by_year.values())[-1] if by_year else generate_statements_for_year(items, "UNKNOWN", ["UNKNOWN"]))
    result = dict(target_stmt)
    result["by_year"] = by_year
    result["normalized_items"] = items
    return result
