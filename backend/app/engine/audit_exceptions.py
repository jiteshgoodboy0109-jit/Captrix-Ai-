"""
Audit Exception Register & Management Letter Engine Module
Aggregates all mathematical, reconciliation, accrual, and forensic anomalies into a unified
Exception Register and generates a formal Management Letter for executive leadership.
"""

from typing import Dict, List, Any, Optional

class AuditExceptionManager:
    """
    Centralizes all identified audit exceptions, assigns severity ratings,
    and formats formal management letter recommendations.
    """

    @classmethod
    def compile_audit_exceptions(
        cls,
        statements: Dict[str, Any],
        ratios: Dict[str, Any],
        forensic_report: Dict[str, Any],
        materiality: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compiles all identified audit exceptions into an actionable register.
        """
        exceptions = []
        exc_id_counter = 1

        pm = materiality.get("planning_materiality", 5000.0)
        sym = materiality.get("currency_symbol", "$")

        # 1. Balance Sheet Accounting Equation Check
        bs = statements.get("balance_sheet", {}) if isinstance(statements, dict) else {}
        val_rep = statements.get("validation_report", {}) if isinstance(statements, dict) else {}
        bs_check = val_rep.get("balance_sheet_check", "INCOMPLETE")

        assets_val = bs.get("total_assets")
        liab_val = bs.get("total_liabilities")
        eq_val = bs.get("equity", {}).get("total_equity") if isinstance(bs.get("equity"), dict) else bs.get("total_equity")

        if bs_check == "UNBALANCED" and assets_val is not None and liab_val is not None and eq_val is not None:
            assets = float(assets_val)
            liab = float(liab_val)
            eq = float(eq_val)
            diff = abs(assets - (liab + eq))
            if diff > 1.0:
                is_material = diff > pm
                exceptions.append({
                    "exception_id": f"EXC-{exc_id_counter:03d}",
                    "audit_area": "Balance Sheet Structure",
                    "issue_title": "Fundamental Accounting Equation Imbalance",
                    "description": f"Total Assets ({sym}{assets:,.2f}) does not equal Total Liabilities + Equity ({sym}{(liab+eq):,.2f}). Unreconciled difference: {sym}{diff:,.2f}.",
                    "severity": "MATERIAL_MISSTATEMENT" if is_material else "SIGNIFICANT_DEFICIENCY",
                    "impact_amount": diff,
                    "status": "OPEN",
                    "remediation": "Review unmapped asset/liability sub-accounts or unrecorded suspense entries."
                })
                exc_id_counter += 1
        elif bs_check == "INCOMPLETE" and (assets_val is not None or liab_val is not None or eq_val is not None):
            missing_sides = []
            if assets_val is None:
                missing_sides.append("Assets")
            if liab_val is None:
                missing_sides.append("Liabilities")
            if eq_val is None:
                missing_sides.append("Equity")
            exceptions.append({
                "exception_id": f"EXC-{exc_id_counter:03d}",
                "audit_area": "Balance Sheet Scope",
                "issue_title": "Incomplete Balance Sheet Schedules (Scope Limitation)",
                "description": f"Source document contains partial statement records. Missing: {', '.join(missing_sides)}. Fundamental accounting equation cannot be evaluated.",
                "severity": "CONTROL_OBSERVATION",
                "impact_amount": 0.0,
                "status": "OPEN",
                "remediation": "Upload complete multi-schedule financial statements including all liability and equity schedules."
            })
            exc_id_counter += 1

        # 2. Trial Balance Check (Applicable only if explicit Trial Balance exists in source)
        tb = statements.get("trial_balance", {}) if isinstance(statements, dict) else {}
        if tb and isinstance(tb, dict) and tb.get("status") == "FAIL":
            tb_diff = abs(float(tb.get("difference", 0.0) or 0.0))
            if tb_diff > 1.0:
                exceptions.append({
                    "exception_id": f"EXC-{exc_id_counter:03d}",
                    "audit_area": "General Ledger / Trial Balance",
                    "issue_title": "Trial Balance Out of Balance",
                    "description": f"Sum of Debits does not equal Sum of Credits. Net discrepancy: {sym}{tb_diff:,.2f}.",
                    "severity": "MATERIAL_MISSTATEMENT" if tb_diff > pm else "SIGNIFICANT_DEFICIENCY",
                    "impact_amount": tb_diff,
                    "status": "OPEN",
                    "remediation": "Locate single-sided journal entries or manual ledger overrides."
                })
                exc_id_counter += 1

        # 3. Accrual Realization Quality Check
        sloan = forensic_report.get("sloan_accruals", {}) if isinstance(forensic_report, dict) else {}
        if sloan.get("status") == "AUDIT_FLAG":
            exceptions.append({
                "exception_id": f"EXC-{exc_id_counter:03d}",
                "audit_area": "Revenue & Cash Realization",
                "issue_title": "High Accruals / Cash Realization Deficit",
                "description": f"Reported Net Income significantly outpaces Operating Cash Flow (Sloan Accrual Ratio: {sloan.get('sloan_ratio')}). High proportion of uncollected earnings.",
                "severity": "SIGNIFICANT_DEFICIENCY",
                "impact_amount": float(sloan.get("accruals_amount", 0.0) or 0.0),
                "status": "OPEN",
                "remediation": "Audit trade receivables aging and test for premature revenue recognition or uncollected billings."
            })
            exc_id_counter += 1

        # 4. Benford's Law Non-Conformity Check
        benford = forensic_report.get("benford_analysis", {}) if isinstance(forensic_report, dict) else {}
        if "Non-Conformity" in str(benford.get("conformity_status", "")):
            exceptions.append({
                "exception_id": f"EXC-{exc_id_counter:03d}",
                "audit_area": "Forensic Digit Distribution",
                "issue_title": "Benford's Law Logarithmic Non-Conformity",
                "description": f"First-digit distribution deviates significantly from natural logarithmic patterns (MAD: {benford.get('mean_absolute_deviation')}).",
                "severity": "CONTROL_OBSERVATION",
                "impact_amount": 0.0,
                "status": "OPEN",
                "remediation": "Investigate transaction authorization thresholds for artificial structuring below approval limits."
            })
            exc_id_counter += 1

        # 5. Round Number Transaction Check
        round_audit = forensic_report.get("round_number_audit", {}) if isinstance(forensic_report, dict) else {}
        if round_audit.get("risk_level") == "HIGH":
            exceptions.append({
                "exception_id": f"EXC-{exc_id_counter:03d}",
                "audit_area": "Manual Journal Entries",
                "issue_title": "Excessive Round-Number Transactions",
                "description": f"Over {round_audit.get('round_entries_pct')}% of journal postings are round thousands, suggesting manual adjustments without underlying invoice precision.",
                "severity": "CONTROL_OBSERVATION",
                "impact_amount": 0.0,
                "status": "OPEN",
                "remediation": "Enforce automated ERP posting and require invoice attachment for manual journal entries."
            })
            exc_id_counter += 1

        # 6. Income Statement Line-Item Arithmetic Reconciliation Mismatches
        inc = statements.get("income_statement", {}) if isinstance(statements, dict) else {}
        if inc.get("gross_profit_status") == "MISMATCH":
            gp_rep = inc.get("gross_profit", 0.0) or 0.0
            gp_calc = inc.get("gross_profit_calculated", 0.0) or 0.0
            gp_var = abs(inc.get("gross_profit_variance", 0.0) or (gp_rep - gp_calc))
            exceptions.append({
                "exception_id": f"EXC-{exc_id_counter:03d}",
                "category": "RECONCILIATION_FAILURE",
                "audit_area": "Gross Profit Arithmetic",
                "issue_title": "Gross Profit Subtotal Mismatch",
                "description": f"Reported Gross Profit ({sym}{gp_rep:,.2f}) does not equal Revenue minus COGS ({sym}{gp_calc:,.2f}). Arithmetic variance: {sym}{gp_var:,.2f}.",
                "severity": "MATERIAL_MISSTATEMENT" if gp_var > pm else "SIGNIFICANT_DEFICIENCY",
                "impact_amount": gp_var,
                "status": "OPEN",
                "remediation": "Reconcile reported cost of goods sold and revenue line items against product billing schedules."
            })
            exc_id_counter += 1

        if inc.get("pbt_status") == "MISMATCH":
            pbt_rep = inc.get("pbt", 0.0) or inc.get("ebt", 0.0) or 0.0
            pbt_calc = inc.get("pbt_calculated", 0.0) or 0.0
            pbt_var = abs(inc.get("pbt_variance", 0.0) or (pbt_rep - pbt_calc))
            exceptions.append({
                "exception_id": f"EXC-{exc_id_counter:03d}",
                "category": "RECONCILIATION_FAILURE",
                "audit_area": "Pre-Tax Earnings Arithmetic",
                "issue_title": "Profit Before Tax (PBT) Subtotal Mismatch",
                "description": f"Reported PBT ({sym}{pbt_rep:,.2f}) does not equal Operating Profit + Finance Items ({sym}{pbt_calc:,.2f}). Arithmetic variance: {sym}{pbt_var:,.2f}.",
                "severity": "MATERIAL_MISSTATEMENT" if pbt_var > pm else "SIGNIFICANT_DEFICIENCY",
                "impact_amount": pbt_var,
                "status": "OPEN",
                "remediation": "Verify non-operating expenses, finance income/costs, and exceptional items included in pre-tax earnings."
            })
            exc_id_counter += 1

        if inc.get("net_income_reconciliation_status") == "MISMATCH":
            ni_rep = inc.get("net_income", 0.0) or 0.0
            ni_calc = inc.get("net_income_calculated", 0.0) or 0.0
            ni_var = abs(inc.get("net_income_variance", 0.0) or (ni_rep - ni_calc))
            exceptions.append({
                "exception_id": f"EXC-{exc_id_counter:03d}",
                "category": "RECONCILIATION_FAILURE",
                "audit_area": "Net Income Reconciliation",
                "issue_title": "Net Profit to PBT Reconciliation Breakdown",
                "description": f"Reported Net Profit ({sym}{ni_rep:,.2f}) does not reconcile with PBT minus Tax ({sym}{ni_calc:,.2f}). Variance: {sym}{ni_var:,.2f}.",
                "severity": "MATERIAL_MISSTATEMENT" if ni_var > pm else "SIGNIFICANT_DEFICIENCY",
                "impact_amount": ni_var,
                "status": "OPEN",
                "remediation": "Audit tax expense line items, deferred tax adjustments, and discontinued operations allocations."
            })
            exc_id_counter += 1

        # Categorize all exceptions
        extraction_errors = [e for e in exceptions if e.get("audit_area") in ["Balance Sheet Scope", "Scope Limitation"] or e.get("category") == "EXTRACTION_OR_SCOPE_LIMITATION"]
        reconciliation_failures = [e for e in exceptions if e.get("category") == "RECONCILIATION_FAILURE"]
        accounting_inconsistencies = [e for e in exceptions if e.get("audit_area") in ["Balance Sheet Structure", "General Ledger / Trial Balance"]]
        forensic_observations = [e for e in exceptions if e.get("audit_area") in ["Revenue & Cash Realization", "Forensic Digit Distribution", "Manual Journal Entries"]]

        # Compile Management Letter Observations
        mgmt_letter = []
        for exc in exceptions:
            mgmt_letter.append({
                "ref": exc["exception_id"],
                "category": exc.get("category", "AUDIT_FINDING"),
                "area": exc["audit_area"],
                "deficiency": exc["description"],
                "risk_implication": "May lead to financial statement misstatement or regulatory audit scrutiny if uncorrected.",
                "recommendation": exc["remediation"]
            })

        return {
            "total_exceptions": len(exceptions),
            "critical_exceptions_count": sum(1 for e in exceptions if e["severity"] == "MATERIAL_MISSTATEMENT"),
            "significant_deficiencies_count": sum(1 for e in exceptions if e["severity"] == "SIGNIFICANT_DEFICIENCY"),
            "control_observations_count": sum(1 for e in exceptions if e["severity"] == "CONTROL_OBSERVATION"),
            "extraction_errors_count": len(extraction_errors),
            "reconciliation_failures_count": len(reconciliation_failures),
            "accounting_inconsistencies_count": len(accounting_inconsistencies),
            "forensic_observations_count": len(forensic_observations),
            "exception_items": exceptions,
            "extraction_errors": extraction_errors,
            "reconciliation_failures": reconciliation_failures,
            "accounting_inconsistencies": accounting_inconsistencies,
            "forensic_observations": forensic_observations,
            "management_letter": mgmt_letter
        }
