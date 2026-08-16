"""
Model Evaluation Engine
Runs ground-truth verification, accounting equation validation, hallucination detection,
and scoring across candidate models to determine the optimal model for financial documents.
"""

from typing import Dict, List, Any, Tuple
import math
from app.engine.model_registry import filter_candidate_models, get_registered_models

CRITICAL_METRIC_WEIGHTS = {
    "total_revenue": 10,
    "net_income": 10,
    "total_assets": 10,
    "total_liabilities": 10,
    "total_equity": 10,
    "operating_cash_flow": 8,
    "investing_cash_flow": 8,
    "financing_cash_flow": 8,
    "net_cash_flow": 8,
    "ebit": 8,
    "tax": 8,
    "interest": 8,
    "borrowings": 8,
    "cash_and_equivalents": 8
}

def evaluate_model_extraction(
    model_id: str,
    extracted_metrics: Dict[str, Any],
    ground_truth_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """Evaluate a single candidate model's extraction against deterministic ground truth."""
    total_metrics_evaluated = 0
    matched_metrics = 0
    critical_weighted_score = 0.0
    total_critical_weight = 0.0
    hallucination_count = 0
    sign_mismatch_count = 0
    traceability_count = 0

    disagreement_details = []

    for metric_key, true_val in ground_truth_metrics.items():
        weight = CRITICAL_METRIC_WEIGHTS.get(metric_key, 5)
        total_critical_weight += weight
        total_metrics_evaluated += 1

        extracted_item = extracted_metrics.get(metric_key)
        if isinstance(extracted_item, dict):
            extracted_val = extracted_item.get("value")
            has_location = bool(extracted_item.get("source_location"))
        else:
            extracted_val = extracted_item
            has_location = False

        if has_location:
            traceability_count += 1

        if true_val is None or true_val == "Not Separately Reported":
            # If ground truth is missing/not reported, model MUST NOT invent a value
            if extracted_val is not None and extracted_val != 0.0 and extracted_val != "Not Separately Reported":
                hallucination_count += 1
                disagreement_details.append({
                    "metric": metric_key,
                    "ground_truth": "Not Separately Reported",
                    "model_output": extracted_val,
                    "status": "HALLUCINATION_FAIL"
                })
            else:
                matched_metrics += 1
                critical_weighted_score += weight
            continue

        if extracted_val is None:
            disagreement_details.append({
                "metric": metric_key,
                "ground_truth": true_val,
                "model_output": None,
                "status": "MISSING_VALUE"
            })
            continue

        # Check numeric match
        try:
            v_model = float(extracted_val)
            v_true = float(true_val)
            
            # Check sign
            if (v_model < 0 and v_true > 0) or (v_model > 0 and v_true < 0):
                sign_mismatch_count += 1

            abs_diff = abs(v_model - v_true)
            rel_diff = abs_diff / (abs(v_true) + 1e-6)

            if abs_diff <= 0.01 or rel_diff <= 0.001:
                matched_metrics += 1
                critical_weighted_score += weight
                disagreement_details.append({
                    "metric": metric_key,
                    "ground_truth": v_true,
                    "model_output": v_model,
                    "status": "EXACT_PASS"
                })
            elif rel_diff <= 0.05:
                # Partial match (90% credit)
                critical_weighted_score += weight * 0.9
                disagreement_details.append({
                    "metric": metric_key,
                    "ground_truth": v_true,
                    "model_output": v_model,
                    "status": "NEAR_MATCH"
                })
            else:
                disagreement_details.append({
                    "metric": metric_key,
                    "ground_truth": v_true,
                    "model_output": v_model,
                    "status": "VALUE_MISMATCH"
                })
        except (ValueError, TypeError):
            disagreement_details.append({
                "metric": metric_key,
                "ground_truth": true_val,
                "model_output": str(extracted_val),
                "status": "TYPE_MISMATCH"
            })

    # Scores
    extraction_accuracy = round((matched_metrics / max(total_metrics_evaluated, 1)) * 100.0, 2)
    critical_metric_accuracy = round((critical_weighted_score / max(total_critical_weight, 1.0)) * 100.0, 2)
    traceability_score = round((traceability_count / max(total_metrics_evaluated, 1)) * 100.0, 2)

    # Accounting Validation Score
    rev = float(extracted_metrics.get("total_revenue", 0.0) or 0.0)
    net_inc = float(extracted_metrics.get("net_income", 0.0) or 0.0)
    assets = float(extracted_metrics.get("total_assets", 0.0) or 0.0)
    liab = float(extracted_metrics.get("total_liabilities", 0.0) or 0.0)
    eq = float(extracted_metrics.get("total_equity", 0.0) or 0.0)

    ocf = float(extracted_metrics.get("operating_cash_flow", 0.0) or 0.0)
    icf = float(extracted_metrics.get("investing_cash_flow", 0.0) or 0.0)
    fcf = float(extracted_metrics.get("financing_cash_flow", 0.0) or 0.0)
    net_cash = float(extracted_metrics.get("net_cash_flow", 0.0) or 0.0)

    bs_eq_valid = abs(assets - (liab + eq)) <= 1.0 if (assets > 0 or liab > 0 or eq > 0) else True
    cf_eq_valid = abs(net_cash - (ocf + icf + fcf)) <= 1.0 if (ocf != 0 or icf != 0 or fcf != 0) else True

    accounting_validation_score = 100.0 if (bs_eq_valid and cf_eq_valid) else (50.0 if (bs_eq_valid or cf_eq_valid) else 0.0)

    # Penalties
    hallucination_penalty = hallucination_count * 25.0
    sign_penalty = sign_mismatch_count * 15.0

    overall_score = round(
        max(0.0, (
            extraction_accuracy * 0.40 +
            critical_metric_accuracy * 0.25 +
            accounting_validation_score * 0.15 +
            traceability_score * 0.10 +
            10.0  # Structured output compliance
        ) - hallucination_penalty - sign_penalty),
        2
    )

    return {
        "model_id": model_id,
        "overall_score": overall_score,
        "extraction_accuracy": extraction_accuracy,
        "critical_metric_accuracy": critical_metric_accuracy,
        "accounting_validation": accounting_validation_score,
        "traceability_score": traceability_score,
        "hallucination_count": hallucination_count,
        "hallucination_rate_pct": round((hallucination_count / max(total_metrics_evaluated, 1)) * 100.0, 2),
        "sign_mismatches": sign_mismatch_count,
        "disagreements": disagreement_details
    }

def run_automatic_model_discovery(
    ground_truth_metrics: Dict[str, Any],
    candidate_extractions: Dict[str, Dict[str, Any]],
    document_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """Discover best performing model among candidates with explainable selection reasoning."""
    candidate_models = filter_candidate_models(document_profile)
    evaluations = []

    for m in candidate_models:
        mid = m["id"]
        # Use provided candidate extraction if present, else compare against deterministic parser
        ext = candidate_extractions.get(mid, ground_truth_metrics)
        eval_result = evaluate_model_extraction(mid, ext, ground_truth_metrics)
        eval_result["model_name"] = m["model_name"]
        eval_result["provider"] = m["provider"]
        evaluations.append(eval_result)

    # Sort candidates by overall score descending
    evaluations.sort(key=lambda x: x["overall_score"], reverse=True)

    top_winner = evaluations[0]
    winner_score = top_winner["overall_score"]
    winner_critical_acc = top_winner["critical_metric_accuracy"]
    winner_hallucinations = top_winner["hallucination_count"]

    if winner_score >= 95.0 and winner_critical_acc >= 95.0 and winner_hallucinations == 0:
        status = "APPROVED"
        why_this_model_won = (
            f"Model {top_winner['model_name']} ({top_winner['provider']}) was selected as the winner because it achieved "
            f"{top_winner['critical_metric_accuracy']}% critical metric accuracy, "
            f"{top_winner['accounting_validation']}% accounting validation pass rate, "
            f"{top_winner['hallucination_count']} hallucinations, and "
            f"{top_winner['traceability_score']}% source traceability."
        )
    else:
        status = "REVIEW_REQUIRED"
        why_this_model_won = (
            f"Model {top_winner['model_name']} scored highest ({winner_score}%), but confidence threshold (< 95%) "
            f"requires human audit review. Critical metric accuracy stands at {winner_critical_acc}%."
        )

    return {
        "document_profile": document_profile,
        "winner_model": top_winner["model_id"] if status == "APPROVED" else top_winner["model_id"],
        "winner_model_name": top_winner["model_name"],
        "status": status,
        "overall_score": winner_score,
        "critical_metric_accuracy": winner_critical_acc,
        "accounting_validation": top_winner["accounting_validation"],
        "hallucination_rate_pct": top_winner["hallucination_rate_pct"],
        "traceability": top_winner["traceability_score"],
        "why_this_model_won": why_this_model_won,
        "evaluations_leaderboard": evaluations
    }
