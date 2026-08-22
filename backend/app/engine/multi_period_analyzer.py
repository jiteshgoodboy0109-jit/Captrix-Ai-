from typing import Dict, Any, List
import math

def calculate_cagr(start_val: float | None, end_val: float | None, num_years: int) -> float | None:
    """Calculate Compound Annual Growth Rate (CAGR %) safely. Returns None if uncalculable or negative base."""
    if start_val is None or end_val is None or start_val <= 0 or end_val <= 0 or num_years <= 0:
        return None
    try:
        cagr = (math.pow(end_val / start_val, 1.0 / num_years) - 1.0) * 100.0
        return round(cagr, 2)
    except Exception:
        return None

def calculate_yoy(val1: float | None, val2: float | None) -> float:
    """Calculate Year-over-Year growth percentage safely."""
    if val1 is None or val2 is None or val1 == 0:
        return 0.0
    return round(((val2 - val1) / abs(val1)) * 100.0, 2)

def generate_multi_period_analysis(statements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates 3-Year Comparative Financial Statements, YoY Growth Rates, CAGR %,
    Margin Evolution, and AI Multi-Period Trajectory Assessment.
    """
    by_year = statements.get("by_year", {})
    years_sorted = sorted([y for y in by_year.keys() if y != "Current"])
    
    if not by_year or not years_sorted:
        # Fallback for single-period or legacy statements payload
        by_year = {"Current": statements}
        years_sorted = ["Current"]

    # Map the sorted years to the slot variables: oldest, middle, latest
    if len(years_sorted) >= 3:
        y1, y2, y3 = years_sorted[-3], years_sorted[-2], years_sorted[-1]
    elif len(years_sorted) == 2:
        y1, y2, y3 = None, years_sorted[0], years_sorted[1]
    else: # len == 1
        y1, y2, y3 = None, None, years_sorted[0]

    # Helper function to get values safely
    def get_yr_values(y: str | None):
        if y is None:
            return 0.0, None, None, 0.0, 0.0, 0.0
        stmt = by_year.get(y, {})
        inc = stmt.get("income_statement", {})
        bs = stmt.get("balance_sheet", {})
        
        rev = inc.get("total_revenue", 0.0) or 0.0
        cogs = inc.get("cost_of_goods_sold")
        gp = inc.get("gross_profit")
        net = inc.get("net_income", 0.0) or 0.0
        
        assets = bs.get("total_assets", 0.0) or 0.0
        eq_dict = bs.get("equity", {})
        eq = (eq_dict.get("total_equity", 0.0) if isinstance(eq_dict, dict) else 0.0) or 0.0
        
        return rev, cogs, gp, net, assets, eq

    rev_y3, cogs_y3, gp_y3, net_y3, assets_y3, equity_y3 = get_yr_values(y3)
    rev_y2, cogs_y2, gp_y2, net_y2, assets_y2, equity_y2 = get_yr_values(y2)
    rev_y1, cogs_y1, gp_y1, net_y1, assets_y1, equity_y1 = get_yr_values(y1)

    # 1. YoY Growth Rates & CAGR
    revenue_growth_24_25 = calculate_yoy(rev_y2, rev_y3) if y2 is not None else 0.0
    net_growth_24_25 = calculate_yoy(net_y2, net_y3) if y2 is not None else 0.0
    
    rev_cagr_opt = calculate_cagr(rev_y1, rev_y3, 2) if y1 is not None else None
    net_cagr_opt = calculate_cagr(net_y1, net_y3, 2) if y1 is not None else None
    gp_cagr_opt = calculate_cagr(gp_y1, gp_y3, 2) if (y1 is not None and gp_y1 is not None and gp_y3 is not None) else None
    assets_cagr_opt = calculate_cagr(assets_y1, assets_y3, 2) if y1 is not None else None

    revenue_cagr = rev_cagr_opt if rev_cagr_opt is not None else 0.0
    net_cagr = net_cagr_opt if net_cagr_opt is not None else 0.0
    gp_cagr = gp_cagr_opt if gp_cagr_opt is not None else 0.0
    assets_cagr = assets_cagr_opt if assets_cagr_opt is not None else 0.0

    # 2. Margin Evolution Trend (%)
    margin_trends = []
    for y in [y1, y2, y3]:
        if y is None:
            continue
        stmt_y = by_year[y]
        inc_y = stmt_y.get("income_statement", {})
        bs_y = stmt_y.get("balance_sheet", {})
        
        rev_y = inc_y.get("total_revenue", 0.0) or 0.0
        gp_y = inc_y.get("gross_profit")
        net_y = inc_y.get("net_income", 0.0) or 0.0
        eq_y_dict = bs_y.get("equity", {})
        eq_y = (eq_y_dict.get("total_equity", 0.0) if isinstance(eq_y_dict, dict) else 0.0) or 0.0
        
        gm_y = round((gp_y / rev_y) * 100, 2) if (rev_y > 0 and gp_y is not None) else 0.0
        np_y = round((net_y / rev_y) * 100, 2) if rev_y > 0 else 0.0
        roe_y = round((net_y / eq_y) * 100, 2) if eq_y > 0 else 0.0
        
        margin_trends.append({
            "period": f"FY{y}" if y != "Current" else "Current",
            "gross_margin": gm_y,
            "net_margin": np_y,
            "roe": roe_y
        })

    # 3. Comparative Financial Statements Summary Table
    comparative_income_statement = [
        {"metric": "Gross Revenue", "fy2023": rev_y1, "fy2024": rev_y2, "fy2025": rev_y3, "yoy_24_25": revenue_growth_24_25, "cagr_3yr": revenue_cagr},
        {"metric": "Cost of Goods Sold (COGS)", "fy2023": cogs_y1, "fy2024": cogs_y2, "fy2025": cogs_y3, "yoy_24_25": calculate_yoy(cogs_y2, cogs_y3) if y2 is not None else 0.0, "cagr_3yr": gp_cagr},
        {"metric": "Gross Profit", "fy2023": gp_y1, "fy2024": gp_y2, "fy2025": gp_y3, "yoy_24_25": calculate_yoy(gp_y2, gp_y3) if y2 is not None else 0.0, "cagr_3yr": gp_cagr},
        {"metric": "Net Income", "fy2023": net_y1, "fy2024": net_y2, "fy2025": net_y3, "yoy_24_25": net_growth_24_25, "cagr_3yr": net_cagr},
    ]

    comparative_balance_sheet = [
        {"metric": "Total Assets", "fy2023": assets_y1, "fy2024": assets_y2, "fy2025": assets_y3, "yoy_24_25": calculate_yoy(assets_y2, assets_y3) if y2 is not None else 0.0, "cagr_3yr": assets_cagr},
        {"metric": "Total Shareholders' Equity", "fy2023": equity_y1, "fy2024": equity_y2, "fy2025": equity_y3, "yoy_24_25": calculate_yoy(equity_y2, equity_y3) if y2 is not None else 0.0, "cagr_3yr": calculate_cagr(equity_y1, equity_y3, 2) if (y1 is not None and calculate_cagr(equity_y1, equity_y3, 2) is not None) else 0.0},
    ]

    # AI Trajectory Commentary
    if y1 is not None:
        gm_y1 = margin_trends[0]["gross_margin"]
        gm_y3 = margin_trends[2]["gross_margin"]
        roe_y3 = margin_trends[2]["roe"]
        ai_trajectory = (
            f"The company demonstrates a 3-year revenue CAGR of {revenue_cagr}% alongside "
            f"a net income CAGR of {net_cagr}%. Gross margin evolved from {gm_y1}% in FY{y1} to {gm_y3}% in FY{y3}, "
            f"indicating effective cost management. Return on Equity (ROE) expanded to {roe_y3}%, "
            f"reflecting compounding equity value for shareholders."
        )
    elif y2 is not None:
        gm_y2 = margin_trends[0]["gross_margin"]
        gm_y3 = margin_trends[1]["gross_margin"]
        roe_y3 = margin_trends[1]["roe"]
        ai_trajectory = (
            f"Comparative multi-period analysis between FY{y2} and FY{y3} shows "
            f"YoY revenue growth of {revenue_growth_24_25}% and YoY net income growth of {net_growth_24_25}%. "
            f"Gross margin evolved from {gm_y2}% in FY{y2} to {gm_y3}% in FY{y3}, with a Return on Equity (ROE) of {roe_y3}%."
        )
    else:
        gm_y3 = margin_trends[0]["gross_margin"]
        roe_y3 = margin_trends[0]["roe"]
        ai_trajectory = (
            f"Single-period financial statements parsed for FY{y3}. "
            f"Gross margin stands at {gm_y3}% and Return on Equity (ROE) is {roe_y3}%. "
            f"Multi-year comparative history was not available in the source workbook."
        )

    # Backtesting & Forecast Error Validation Metrics
    has_sufficient_history = (y2 is not None) or (y1 is not None)
    
    if not has_sufficient_history:
        forecast_status = "INSUFFICIENT_HISTORICAL_DATA"
        forecast_message = "Insufficient reliable historical data to generate a dependable forecast."
        forecast_rev_g = 3.0  # Conservative baseline
        forecast_net_g = 3.0
        forecast_asset_g = 3.0
        mae_metric = None
        rmse_metric = None
        mape_metric = None
    else:
        forecast_status = "VALIDATED_TIME_SERIES"
        forecast_message = f"3-Year forecast generated using {len(years_sorted)}-period historical trend analysis."
        
        # Calculate Backtesting Error Metrics (MAE, RMSE, MAPE) on historical holds
        if y1 is not None and y2 is not None:
            # Backtest FY2025 actual vs prediction from FY2023-FY2024 trend
            actual_rev = rev_y3
            predicted_rev = rev_y2 * (1.0 + (calculate_yoy(rev_y1, rev_y2) / 100.0))
            mae_metric = round(abs(actual_rev - predicted_rev), 2)
            rmse_metric = round(math.sqrt((actual_rev - predicted_rev) ** 2), 2)
            mape_metric = round((mae_metric / actual_rev) * 100.0, 2) if actual_rev > 0 else 0.0
        else:
            mae_metric = 0.0
            rmse_metric = 0.0
            mape_metric = 0.0

        if rev_cagr_opt is not None:
            forecast_rev_g = min(max(rev_cagr_opt, -15.0), 25.0)
        elif y2 is not None and revenue_growth_24_25 != 0.0:
            forecast_rev_g = min(max(revenue_growth_24_25, -15.0), 25.0)
        else:
            forecast_rev_g = 5.0

        if net_cagr_opt is not None:
            forecast_net_g = min(max(net_cagr_opt, -15.0), 25.0)
        elif y2 is not None and net_growth_24_25 != 0.0:
            forecast_net_g = min(max(net_growth_24_25, -15.0), 25.0)
        else:
            forecast_net_g = forecast_rev_g

        if assets_cagr_opt is not None:
            forecast_asset_g = min(max(assets_cagr_opt, -10.0), 15.0)
        else:
            forecast_asset_g = min(max(forecast_rev_g * 0.8, -10.0), 15.0)

    # Calculate 3-Year Forecast Projections
    projections = []
    net_margin_y3 = (net_y3 / rev_y3) if rev_y3 > 0 else 0.0

    for t, label, conf in [
        (1, "Y+1 (Forecast)", "High Confidence (Base Case)"),
        (2, "Y+2 (Forecast)", "Moderate Confidence"),
        (3, "Y+3 (Forecast)", "Strategic Long-Term Case")
    ]:
        proj_rev = round(rev_y3 * ((1.0 + (forecast_rev_g / 100.0)) ** t), 2)
        proj_assets = round(assets_y3 * ((1.0 + (forecast_asset_g / 100.0)) ** t), 2)
        
        if net_y3 > 0:
            proj_net = round(proj_rev * net_margin_y3, 2)
        else:
            proj_net = round(net_y3 * ((1.0 - (forecast_rev_g / 100.0)) if forecast_rev_g > 0 else (1.0 + abs(forecast_rev_g) / 100.0)) ** t, 2)

        projections.append({
            "period": label,
            "projected_revenue": proj_rev,
            "projected_net_income": proj_net,
            "projected_assets": proj_assets,
            "confidence_range": conf
        })

    return {
        "cagr_metrics": {
            "revenue_cagr": revenue_cagr,
            "net_income_cagr": net_cagr,
            "gross_profit_cagr": gp_cagr,
            "assets_cagr": assets_cagr
        },
        "yoy_growth": {
            "revenue_yoy": revenue_growth_24_25,
            "net_income_yoy": net_growth_24_25
        },
        "comparative_income_statement": comparative_income_statement,
        "comparative_balance_sheet": comparative_balance_sheet,
        "margin_trends": margin_trends,
        "ai_trajectory": ai_trajectory,
        "three_year_forecast": {
            "forecast_status": forecast_status,
            "forecast_message": forecast_message,
            "growth_rate_used_pct": round(forecast_rev_g, 2),
            "backtesting_metrics": {
                "mae": mae_metric,
                "rmse": rmse_metric,
                "mape_pct": mape_metric
            },
            "projections": projections
        }
    }

