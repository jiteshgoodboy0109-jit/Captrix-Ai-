"""
DuPont ROE Analysis Engine Module
Decomposes Return on Equity (ROE) into 3-Step and 5-Step component drivers:
  3-Step: Net Profit Margin * Asset Turnover * Equity Multiplier
  5-Step: Tax Burden * Interest Burden * EBIT Margin * Asset Turnover * Equity Multiplier
Identifies key ROE growth drivers and financial leverage exposure.
"""

from typing import Dict, Any

def calculate_dupont_analysis(statements: Dict[str, Any], ratios: Dict[str, Any]) -> Dict[str, Any]:
    inc = statements.get("income_statement", {})
    bs = statements.get("balance_sheet", {})

    rev = float(inc.get("total_revenue") or 0.0)
    net_inc = float(inc.get("net_income") or 0.0)
    ebit = float(inc.get("ebit") or 0.0)
    ebt = float(inc.get("ebt") or 0.0)
    
    total_assets = float(bs.get("total_assets") or 0.0)
    
    eq_dict = bs.get("equity", {})
    equity = float((eq_dict.get("total_equity") if isinstance(eq_dict, dict) else bs.get("total_equity")) or 0.0)

    # 1. Core Component Ratios
    npm = (net_inc / rev) if rev > 0 else 0.0
    asset_turnover = (rev / total_assets) if total_assets > 0 else 0.0
    equity_multiplier = (total_assets / equity) if equity > 0 else 1.0

    # 3-Step DuPont Calculation
    roe_3step = round(npm * asset_turnover * equity_multiplier * 100.0, 2)
    
    # 2. 5-Step Component Ratios
    tax_burden = (net_inc / ebt) if (ebt != 0) else 1.0
    interest_burden = (ebt / ebit) if (ebit != 0) else 1.0
    ebit_margin = (ebit / rev) if rev > 0 else 0.0

    # 5-Step DuPont Calculation
    roe_5step = round(tax_burden * interest_burden * ebit_margin * asset_turnover * equity_multiplier * 100.0, 2)

    raw_roe = ratios.get("profitability", {}).get("return_on_equity", {}).get("value")
    reported_roe = float(raw_roe) if (raw_roe is not None and not isinstance(raw_roe, str)) else roe_3step

    # 3. Determine Primary ROE Driver
    driver_scores = {
        "profitability": round(npm * 100.0, 2),
        "asset_efficiency": round(asset_turnover, 2),
        "financial_leverage": round(equity_multiplier, 2)
    }

    if equity_multiplier > 2.5:
        primary_driver = "Financial Leverage (Debt-Driven)"
        driver_summary = (
            f"ROE of {reported_roe:.1f}% is significantly amplified by financial leverage "
            f"(Equity Multiplier of {equity_multiplier:.2f}x). While boosting returns, "
            f"it increases insolvency vulnerability if operating cash flows fluctuate."
        )
    elif (npm * 100.0) >= 15.0:
        primary_driver = "High Net Profit Margin (Pricing Power)"
        driver_summary = (
            f"ROE of {reported_roe:.1f}% is driven by strong pricing power and cost discipline, "
            f"retaining {npm * 100.0:.1f}% net profit margin per dollar of revenue."
        )
    elif asset_turnover >= 1.2:
        primary_driver = "Asset Velocity & Efficiency"
        driver_summary = (
            f"ROE of {reported_roe:.1f}% is propelled by efficient asset deployment, "
            f"generating {asset_turnover:.2f}x asset turnover annually."
        )
    else:
        primary_driver = "Balanced / Moderate Growth"
        driver_summary = (
            f"ROE stands at {reported_roe:.1f}%. Net profit margin is {npm * 100.0:.1f}%, "
            f"asset turnover is {asset_turnover:.2f}x, and equity multiplier is {equity_multiplier:.2f}x."
        )

    return {
        "reported_roe": reported_roe,
        "primary_driver": primary_driver,
        "driver_summary": driver_summary,
        "three_step": {
            "net_profit_margin_pct": round(npm * 100.0, 2),
            "asset_turnover_x": round(asset_turnover, 2),
            "equity_multiplier_x": round(equity_multiplier, 2),
            "calculated_roe": roe_3step,
            "formula": "ROE = Net Margin (%) * Asset Turnover (x) * Equity Multiplier (x)"
        },
        "five_step": {
            "tax_burden": round(tax_burden, 3),
            "interest_burden": round(interest_burden, 3),
            "ebit_margin_pct": round(ebit_margin * 100.0, 2),
            "asset_turnover_x": round(asset_turnover, 2),
            "equity_multiplier_x": round(equity_multiplier, 2),
            "calculated_roe": roe_5step,
            "formula": "ROE = Tax Burden * Interest Burden * EBIT Margin (%) * Asset Turnover (x) * Equity Multiplier (x)"
        },
        "driver_breakdown": driver_scores
    }
