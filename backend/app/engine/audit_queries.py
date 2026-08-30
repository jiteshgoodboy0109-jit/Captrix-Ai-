import datetime
from typing import Dict, Any, List, Optional

class AuditQueryEngine:
    """
    Manages the formal Audit Query & Management Response lifecycle (PBC - Provided By Client).
    Tracks observations, management explanations, auditor evaluations, and resolution verdicts.
    """

    @classmethod
    def generate_audit_queries(
        cls, 
        exception_register: List[Dict[str, Any]], 
        materiality: Dict[str, Any],
        forensic_tests: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Converts identified accounting discrepancies and forensic flags into formal Audit Queries.
        """
        queries: List[Dict[str, Any]] = []
        q_counter = 1
        curr_sym = materiality.get("currency_symbol", "$")

        # 1. Generate queries from Exception Register
        for exc in exception_register:
            ref_code = f"AQ-{q_counter:03d}"
            q_counter += 1
            severity = exc.get("severity", "SIGNIFICANT_DEFICIENCY")
            area = exc.get("area", "Financial Reporting")
            amount = exc.get("amount", 0.0)
            
            # Initial template query
            query_item = {
                "query_id": ref_code,
                "exception_ref": exc.get("ref", "EXC-001"),
                "area": area,
                "severity": severity,
                "impact_amount": amount,
                "query_title": f"Discrepancy in {area} ({curr_sym}{amount:,.2f})" if amount > 0 else f"Observation in {area}",
                "auditor_observation": exc.get("description", "Material departure or discrepancy identified during substantive procedures."),
                "management_query": (
                    f"Please provide documentary evidence, reconciliation, and formal management justification "
                    f"for the discrepancy noted in {area} (Amount: {curr_sym}{amount:,.2f})."
                ),
                "management_response": None,
                "management_responder": None,
                "response_received_at": None,
                "auditor_evaluation": None,
                "auditor_signoff": None,
                "status": "OPEN",  # OPEN | MANAGEMENT_REPLIED | RESOLVED | ESCALATED_TO_MANAGEMENT_LETTER
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            queries.append(query_item)

        # 2. Generate queries for non-conforming forensic tests
        if forensic_tests:
            for ft in forensic_tests:
                if ft.get("status") == "FAIL" or ft.get("status") == "AUDIT_FLAG":
                    ref_code = f"AQ-{q_counter:03d}"
                    q_counter += 1
                    queries.append({
                        "query_id": ref_code,
                        "exception_ref": ft.get("test_ref", "WP-TEST"),
                        "area": "Forensic Ledger Integrity",
                        "severity": "SIGNIFICANT_DEFICIENCY",
                        "impact_amount": 0.0,
                        "query_title": f"Forensic Indicator: {ft.get('name')}",
                        "auditor_observation": ft.get("details", "Statistical irregularity detected in journal entries."),
                        "management_query": (
                            f"Statistical testing ({ft.get('name')}) indicated potential non-conformity. "
                            f"Please provide internal control sign-offs and sample journal entry backup."
                        ),
                        "management_response": None,
                        "management_responder": None,
                        "response_received_at": None,
                        "auditor_evaluation": None,
                        "auditor_signoff": None,
                        "status": "OPEN",
                        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

        return queries

    @classmethod
    def resolve_query(
        cls,
        query: Dict[str, Any],
        management_response: str,
        responder_name: str,
        auditor_verdict: str,
        is_satisfactory: bool
    ) -> Dict[str, Any]:
        """
        Updates an audit query with management explanation and auditor sign-off.
        """
        updated = dict(query)
        updated["management_response"] = management_response
        updated["management_responder"] = responder_name
        updated["response_received_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated["auditor_evaluation"] = auditor_verdict
        updated["auditor_signoff"] = "AI Lead Statutory Auditor"
        updated["status"] = "RESOLVED" if is_satisfactory else "ESCALATED_TO_MANAGEMENT_LETTER"
        return updated
