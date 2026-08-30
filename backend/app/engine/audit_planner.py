"""
Audit Planning & Materiality Engine Module
Calculates institutional Planning Materiality (PM), Performance Materiality (PM_perf),
and Clearly Trivial / De Minimis thresholds based on International Standards on Auditing (ISA 320 / US GAAS).
Evaluates identified variances against materiality cutoffs.
"""

from typing import Dict, Any, List, Optional
import math

class AuditPlanner:
    """
    Computes materiality thresholds and establishes the audit strategy and scope.
    """

    @classmethod
    def calculate_materiality(
        cls, 
        statements: Dict[str, Any],
        currency_symbol: str = "$"
    ) -> Dict[str, Any]:
        """
        Determines the appropriate materiality benchmark:
        - 5.0% of Normalized Profit Before Tax / Net Income
        - 1.0% of Total Revenue
        - 1.0% of Total Assets
        """
        inc = statements.get("income_statement", {}) if isinstance(statements, dict) else {}
        bs = statements.get("balance_sheet", {}) if isinstance(statements, dict) else {}

        rev = abs(float(inc.get("total_revenue", 0.0) or inc.get("revenue_from_operations", 0.0) or 0.0))
        net_inc = abs(float(inc.get("net_income", 0.0) or 0.0))
        pbt = abs(float(inc.get("pbt", 0.0) or inc.get("ebt", 0.0) or net_inc))
        assets = abs(float(bs.get("total_assets", 0.0) or 0.0))

        candidates = []
        if pbt > 0:
            candidates.append({"benchmark": "Profit Before Tax (5.0%)", "value": pbt * 0.05, "base_amount": pbt, "pct": 5.0})
        if rev > 0:
            candidates.append({"benchmark": "Total Revenue (1.0%)", "value": rev * 0.01, "base_amount": rev, "pct": 1.0})
        if assets > 0:
            candidates.append({"benchmark": "Total Assets (1.0%)", "value": assets * 0.01, "base_amount": assets, "pct": 1.0})

        if not candidates:
            # Fallback default nominal materiality
            selected = {"benchmark": "Standard Nominal Base", "value": 5000.0, "base_amount": 100000.0, "pct": 5.0, "name": "Revenue / Asset Fallback"}
        else:
            # Select highest reliable benchmark
            selected = max(candidates, key=lambda x: x["value"])
            selected["name"] = selected["benchmark"]

        base_amt = float(selected["base_amount"])
        pct = float(selected.get("pct", 1.0))
        pm = max(round(base_amt * (pct / 100.0), 2), 1000.0)
        perf_mat = round(pm * 0.75, 2)
        trivial_threshold = round(pm * 0.05, 2)

        return {
            "benchmark_name": selected.get("name", selected["benchmark"]),
            "benchmark_basis": selected["benchmark"],
            "benchmark_base": base_amt,
            "base_amount": base_amt,
            "benchmark_percentage": pct,
            "planning_materiality": pm,
            "performance_materiality_percentage": 75.0,
            "performance_materiality": perf_mat,
            "clearly_trivial_percentage": 5.0,
            "clearly_trivial_threshold": trivial_threshold,
            "currency_symbol": currency_symbol,
            "audit_approach": "Substantive Analytical & Forensic Ledger Testing",
            "materiality_statement": (
                f"Benchmark Base ({selected.get('name', selected['benchmark'])}): {currency_symbol}{base_amt:,.2f} | "
                f"Planning Materiality (PM @ {pct:.1f}%): {currency_symbol}{pm:,.2f} | "
                f"Performance Materiality (75% of PM): {currency_symbol}{perf_mat:,.2f} | "
                f"Clearly Trivial Threshold (5% of PM): {currency_symbol}{trivial_threshold:,.2f}"
            )
        }

    @classmethod
    def evaluate_variance(cls, variance_amount: float, materiality: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifies a variance against materiality thresholds.
        """
        abs_var = abs(variance_amount or 0.0)
        pm = materiality.get("planning_materiality", 5000.0)
        perf_mat = materiality.get("performance_materiality", 3750.0)
        trivial = materiality.get("clearly_trivial_threshold", 250.0)

        if abs_var > pm:
            classification = "MATERIAL_MISSTATEMENT"
            severity = "CRITICAL"
            requires_adjustment = True
        elif abs_var > perf_mat:
            classification = "POTENTIALLY_MATERIAL"
            severity = "HIGH"
            requires_adjustment = True
        elif abs_var > trivial:
            classification = "SIGNIFICANT_OBSERVATION"
            severity = "MEDIUM"
            requires_adjustment = False
        else:
            classification = "CLEARLY_TRIVIAL"
            severity = "LOW"
            requires_adjustment = False

        return {
            "variance_amount": abs_var,
            "classification": classification,
            "severity": severity,
            "requires_adjustment": requires_adjustment
        }
