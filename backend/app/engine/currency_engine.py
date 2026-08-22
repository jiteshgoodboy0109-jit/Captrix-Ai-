"""
Multi-Currency Management & Historical Exchange Rate Engine
Provides ISO 4217 currency identification, symbol disambiguation, historical conversion matrix,
conversion audit provenance tracking, and locale-aware professional formatting.
"""

import re
from typing import Dict, Any, Tuple, Optional, List

# ISO 4217 Supported Currency Registry
SUPPORTED_CURRENCIES: Dict[str, Dict[str, Any]] = {
    "INR": {"name": "Indian Rupee", "symbol": "₹", "country": "India", "format": "INDIAN"},
    "USD": {"name": "US Dollar", "symbol": "$", "country": "United States", "format": "WESTERN"},
    "EUR": {"name": "Euro", "symbol": "€", "country": "Eurozone", "format": "WESTERN"},
    "GBP": {"name": "British Pound", "symbol": "£", "country": "United Kingdom", "format": "WESTERN"},
    "JPY": {"name": "Japanese Yen", "symbol": "¥", "country": "Japan", "format": "WESTERN"},
    "CNY": {"name": "Chinese Yuan", "symbol": "¥", "country": "China", "format": "WESTERN"},
    "AUD": {"name": "Australian Dollar", "symbol": "$", "country": "Australia", "format": "WESTERN"},
    "CAD": {"name": "Canadian Dollar", "symbol": "$", "country": "Canada", "format": "WESTERN"},
    "SGD": {"name": "Singapore Dollar", "symbol": "$", "country": "Singapore", "format": "WESTERN"},
    "AED": {"name": "UAE Dirham", "symbol": "AED", "country": "United Arab Emirates", "format": "WESTERN"},
    "CHF": {"name": "Swiss Franc", "symbol": "CHF", "country": "Switzerland", "format": "WESTERN"}
}

# Historical Exchange Rate Matrix against USD (Base = USD = 1.0)
# Rates represent USD per 1 Unit of Source Currency (or Units of Target per 1 USD)
HISTORICAL_USD_RATES: Dict[str, Dict[str, float]] = {
    "2023": {
        "USD": 1.0, "INR": 0.0121, "EUR": 1.081, "GBP": 1.243, "JPY": 0.0071,
        "CNY": 0.141, "AUD": 0.664, "CAD": 0.741, "SGD": 0.743, "AED": 0.272, "CHF": 1.112
    },
    "2024": {
        "USD": 1.0, "INR": 0.0120, "EUR": 1.085, "GBP": 1.268, "JPY": 0.0066,
        "CNY": 0.138, "AUD": 0.658, "CAD": 0.735, "SGD": 0.746, "AED": 0.272, "CHF": 1.125
    },
    "2025": {
        "USD": 1.0, "INR": 0.0118, "EUR": 1.078, "GBP": 1.272, "JPY": 0.0065,
        "CNY": 0.137, "AUD": 0.652, "CAD": 0.730, "SGD": 0.748, "AED": 0.272, "CHF": 1.130
    },
    "2026": {
        "USD": 1.0, "INR": 0.0116, "EUR": 1.080, "GBP": 1.280, "JPY": 0.0064,
        "CNY": 0.136, "AUD": 0.650, "CAD": 0.728, "SGD": 0.750, "AED": 0.272, "CHF": 1.135
    }
}

def identify_currency(
    text: str, 
    country_context: str = "", 
    default_iso: str = "USD"
) -> Tuple[str, float]:
    """
    Identifies ISO currency code and unit multiplier from text, symbols, or headers.
    Returns Tuple[iso_code, unit_multiplier].
    Never guesses blindly when symbols are ambiguous.
    """
    if not text:
        return default_iso, 1.0

    t_lower = text.lower()
    
    # 1. Multiplier Detection (Crores, Lakhs, Millions, Billions, Thousands)
    multiplier = 1.0
    if "crore" in t_lower or "cr" in t_lower or "in cr" in t_lower:
        multiplier = 10000000.0  # 1 Crore = 10 Million
    elif "lakh" in t_lower or "lac" in t_lower:
        multiplier = 100000.0
    elif "billion" in t_lower or "bn" in t_lower:
        multiplier = 1000000000.0
    elif "million" in t_lower or "mn" in t_lower or "m" in t_lower.split():
        multiplier = 1000000.0
    elif "thousand" in t_lower or "k" in t_lower.split():
        multiplier = 1000.0

    # 2. ISO Code Exact Token Match (highest priority)
    for iso in SUPPORTED_CURRENCIES.keys():
        if re.search(rf'\b{iso}\b', text, re.IGNORECASE):
            return iso, multiplier

    # 3. Symbol Match & Disambiguation
    if "₹" in text or "rs" in t_lower or "rupee" in t_lower or "inr" in t_lower:
        return "INR", multiplier
    if "€" in text or "euro" in t_lower:
        return "EUR", multiplier
    if "£" in text or "pound" in t_lower:
        return "GBP", multiplier
    if "aed" in t_lower or "dirham" in t_lower:
        return "AED", multiplier
    if "chf" in t_lower or "franc" in t_lower:
        return "CHF", multiplier
    if "¥" in text:
        if "china" in country_context.lower() or "yuan" in t_lower or "rmb" in t_lower:
            return "CNY", multiplier
        return "JPY", multiplier

    # Ambiguous Symbol '$' Handling (USD vs CAD vs AUD vs SGD)
    if "$" in text:
        if "cad" in t_lower or "canada" in country_context.lower():
            return "CAD", multiplier
        if "aud" in t_lower or "australia" in country_context.lower():
            return "AUD", multiplier
        if "sgd" in t_lower or "singapore" in country_context.lower():
            return "SGD", multiplier
        return "USD", multiplier

    return default_iso, multiplier

def get_exchange_rate(source_curr: str, target_curr: str, year: str = "2026") -> float:
    """
    Retrieves historical exchange rate converting 1 Unit of source_curr into target_curr.
    """
    if source_curr == target_curr:
        return 1.0

    # pyrefly: ignore [unnecessary-type-conversion]
    yr_str = str(year)
    yr = yr_str if yr_str in HISTORICAL_USD_RATES else "2026"
    rates = HISTORICAL_USD_RATES[yr]

    s_to_usd = rates.get(source_curr, 1.0)
    t_to_usd = rates.get(target_curr, 1.0)

    # Rate converting source_curr to target_curr: (s_to_usd / t_to_usd)
    return round(s_to_usd / t_to_usd, 6)

def convert_currency(
    amount: float,
    source_curr: str,
    target_curr: str,
    year: str = "2026",
    rate_source: str = "Historical Matrix"
) -> Dict[str, Any]:
    """
    Converts currency with complete audit provenance tracking.
    Never mixes currencies without explicit conversion details.
    """
    if amount is None:
        return {
            "original_amount": None,
            "original_currency": source_curr,
            "converted_amount": None,
            "target_currency": target_curr,
            "exchange_rate": 1.0,
            "rate_date": year,
            "source": rate_source,
            "is_converted": False
        }

    rate = get_exchange_rate(source_curr, target_curr, year)
    converted = round(amount * rate, 2)

    return {
        "original_amount": round(amount, 2),
        "original_currency": source_curr,
        "converted_amount": converted,
        "target_currency": target_curr,
        "exchange_rate": rate,
        "rate_date": year,
        "source": rate_source,
        "is_converted": source_curr != target_curr
    }

def format_currency_amount(amount: float, iso_code: str = "USD") -> str:
    """
    Formats monetary amounts with professional locale rules.
    Uses Indian numbering (Lakhs/Crores) for INR and Western standard for others.
    """
    if amount is None:
        return "N/A"

    info = SUPPORTED_CURRENCIES.get(iso_code, {"symbol": "$", "format": "WESTERN"})
    symbol = info["symbol"]

    is_negative = amount < 0
    abs_val = abs(amount)

    if info["format"] == "INDIAN":
        # Format using Indian numbering system (e.g. 1,25,00,000.00)
        s = f"{abs_val:,.2f}"
        parts = s.split(".")
        integer_part = parts[0].replace(",", "")
        decimal_part = parts[1]
        
        if len(integer_part) > 3:
            last3 = integer_part[-3:]
            rest = integer_part[:-3]
            formatted_rest = re.sub(r'(?<=\d)(?=(\d\d)+$)', ',', rest)
            formatted_int = formatted_rest + "," + last3
        else:
            formatted_int = integer_part
            
        formatted_str = f"{symbol}{'-' if is_negative else ''}{formatted_int}.{decimal_part}"
    else:
        # Standard Western formatting (e.g. $1,250,000.00)
        formatted_str = f"{symbol}{'-' if is_negative else ''}{abs_val:,.2f}"

    return formatted_str
