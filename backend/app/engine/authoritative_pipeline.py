"""
Authoritative Production Pipeline Engine
Single Source of Truth coordinating:
User Upload -> Extraction -> Mapping -> Normalization -> Calculation -> Validation -> DB Sync -> Final Report Payload
Ensures zero-staleness: Database records are continuously synchronized from raw accounting line items.
"""

from typing import Dict, Any, Tuple, Optional, List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import Upload, Statement, Ratio, CorporateFinance, AIReport, Company, FinancialData, User, History
from app.engine.statement_generator import generate_financial_statements
from app.engine.ratio_engine import RatioEngine
from app.engine.financial_analyzer import calculate_corporate_finance
from app.engine.multi_period_analyzer import generate_multi_period_analysis
from app.engine.dupont_analyzer import calculate_dupont_analysis
from app.engine.risk_analyzer import calculate_risk_intelligence
from app.engine.auditor_engine import perform_full_financial_audit
from app.engine.canonical_model import build_canonical_dataset
from app.engine.reconciliation import perform_source_to_result_reconciliation
from app.engine.quality_engine import compute_financial_quality_score
from app.engine.ai_insights import generate_ai_insights
from app.engine.output_validator import OutputValidator, ReportConsistencyValidator
from app.engine.currency_engine import SUPPORTED_CURRENCIES
from app.engine.document_parser import clean_value


def build_authoritative_analysis_payload(
    upload_id: int,
    db: Session,
    current_user: User
) -> Tuple[Dict[str, Any], str, str, str]:
    """
    Executes the deterministic, authoritative pipeline for a given upload.
    Returns:
      (validated_payload, company_name, currency, currency_symbol)
    """
    # 1. Enforce strict user-level multi-tenant data isolation
    upload = db.query(Upload).filter(Upload.id == upload_id, Upload.user_id == current_user.id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload analysis not found or access denied.")

    company = db.query(Company).filter(Company.id == upload.company_id).first()
    company_name = company.name if company else "Enterprise Target"

    # 2. Reconstruct accounting line items from raw source FinancialData
    fd_items = db.query(FinancialData).filter(FinancialData.upload_id == upload_id).all()
    items: List[Dict[str, Any]] = []
    
    for f in fd_items:
        meta = f.metadata_json or {}
        col = meta.get("source_column") or meta.get("column", "A")
        row = meta.get("source_row") or meta.get("row", 1)
        src_cell = meta.get("source_cell") or f"{col}{row}"
        src_sheet = meta.get("source_sheet") or meta.get("sheet", "Sheet1")
        raw_hdr = meta.get("period_raw") or meta.get("source_header") or meta.get("fiscal_year", "")
        f_yr = meta.get("fiscal_year") or meta.get("period_raw") or ""

        items.append({
            "account_code": f.account_code,
            "account_name": f.account_name,
            "account_type": f.account_type,
            "debit": f.debit,
            "credit": f.credit,
            "net_amount": f.net_amount,
            "value": f.net_amount,
            "raw_value": meta.get("raw_value", f.net_amount),
            "sheet": src_sheet,
            "row": row,
            "column": col,
            "year": meta.get("year", "UNKNOWN"),
            "unit": meta.get("unit", "NOT_DETERMINED"),
            "currency": meta.get("currency", "NOT_DETERMINED"),
            "source_sheet": src_sheet,
            "source_cell": src_cell,
            "source_column": col,
            "source_row": row,
            "source_header": raw_hdr,
            "period_raw": raw_hdr,
            "source_label": meta.get("source_label", f.account_name),
            "source_value": meta.get("source_value", f.net_amount),
            "is_summary": meta.get("is_summary", False),
            "is_quarterly": meta.get("is_quarterly", False),
            "period_type": meta.get("period_type", "ANNUAL"),
            "fiscal_year": f_yr,
            "period_id": meta.get("period_id", ""),
            "scope": meta.get("scope", "STANDALONE")
        })

    # 3. Currency resolution
    doc_currency = (company.currency if company and company.currency else None) or "USD"
    if doc_currency == "USD":
        for it in items:
            c = it.get("currency")
            if c and c != "USD":
                doc_currency = c
                break

    curr_info = SUPPORTED_CURRENCIES.get(doc_currency.upper(), {"symbol": "$"})
    sym = curr_info.get("symbol", "$")
    if sym == "₹":
        sym = "INR "

    # 4. Authoritative Deterministic Calculation Engine
    statements_payload = generate_financial_statements(items)
    ratios_dict = RatioEngine.calculate_all_ratios(statements_payload)
    corp_fin_payload = calculate_corporate_finance(statements_payload, ratios_dict)
    multi_period = generate_multi_period_analysis(statements_payload)
    dupont_analysis = calculate_dupont_analysis(statements_payload, ratios_dict)
    risk_intelligence = calculate_risk_intelligence(statements_payload, ratios_dict)
    audit_report = perform_full_financial_audit(statements_payload, ratios_dict, canonical_items=items, currency_symbol=sym)

    # 5. Canonical Dataset, Extraction Mapping Validation & Source-to-Result Reconciliation
    canonical_dataset = build_canonical_dataset(items, upload.filename)
    reconciliation = perform_source_to_result_reconciliation(canonical_dataset, statements_payload, ratios_dict)
    quality_report = compute_financial_quality_score(reconciliation, statements_payload.get("validation_report", {}))

    # 6. AI Insights (Explaining verified calculations, zero arithmetic authority)
    ai_insights = generate_ai_insights(statements_payload, ratios_dict, corp_fin_payload, canonical_dataset, quality_report=quality_report)
    fresh_health_score = ai_insights.get("canonical_health_score", {}).get("score", quality_report.get("quality_score", 85.0))

    # 7. Final Report Pre-Flight Validation and Evidence Filtering
    raw_response = {
        "upload_id": upload.id,
        "company_name": company_name,
        "currency": doc_currency,
        "currency_symbol": sym,
        "filename": upload.filename,
        "sheet_names": upload.sheet_names,
        "created_at": upload.created_at,
        "health_score": fresh_health_score,
        "quality_report": quality_report,
        "reconciliation": reconciliation,
        "statements": statements_payload,
        "multi_period": multi_period,
        "dupont_analysis": dupont_analysis,
        "risk_intelligence": risk_intelligence,
        "audit_report": audit_report,
        "canonical_dataset": canonical_dataset,
        "ratios": ratios_dict,
        "corporate_finance": corp_fin_payload,
        "ai_report": {
            "health_score": fresh_health_score,
            "executive_summary": ai_insights.get("executive_summary", ""),
            "strengths": ai_insights.get("strengths", []),
            "weaknesses": ai_insights.get("weaknesses", []),
            "recommendations": ai_insights.get("recommendations", [])
        }
    }

    b_dataset = canonical_dataset.get("layer_a_raw_records", []) if isinstance(canonical_dataset, dict) else []
    validated_payload = OutputValidator.validate_and_filter_payload(raw_response, b_dataset)
    validated_payload = ReportConsistencyValidator.sanitize_audit_wording(validated_payload)
    val_result = ReportConsistencyValidator.validate_final_report_payload(validated_payload, raise_on_error=False)

    validated_payload["pre_flight_validation"] = val_result

    # 8. Database Synchronization to eliminate stale data override
    try:
        ratio_record = db.query(Ratio).filter(Ratio.upload_id == upload_id).first()
        if not ratio_record:
            ratio_record = Ratio(upload_id=upload_id)
            db.add(ratio_record)
        ratio_record.profitability = ratios_dict.get("profitability", {})
        ratio_record.liquidity = ratios_dict.get("liquidity", {})
        ratio_record.solvency = ratios_dict.get("solvency", {})
        ratio_record.efficiency = ratios_dict.get("efficiency", {})

        stmt_record = db.query(Statement).filter(Statement.upload_id == upload_id).first()
        if not stmt_record:
            stmt_record = Statement(upload_id=upload_id)
            db.add(stmt_record)
        stmt_record.balance_sheet = statements_payload.get("balance_sheet", {})
        stmt_record.income_statement = statements_payload.get("income_statement", {})
        stmt_record.cash_flow = statements_payload.get("cash_flow", {})
        stmt_record.trial_balance = statements_payload.get("trial_balance", {})
        stmt_record.ledger_summary = statements_payload.get("ledger_summary", {})

        corp_record = db.query(CorporateFinance).filter(CorporateFinance.upload_id == upload_id).first()
        if not corp_record:
            corp_record = CorporateFinance(upload_id=upload_id)
            db.add(corp_record)
        corp_record.capital_budgeting = corp_fin_payload.get("capital_budgeting", {})
        corp_record.capital_structure = corp_fin_payload.get("capital_structure", {})
        corp_record.working_capital_cycle = corp_fin_payload.get("working_capital_cycle", {})

        ai_record = db.query(AIReport).filter(AIReport.upload_id == upload_id).first()
        if not ai_record:
            ai_record = AIReport(upload_id=upload_id)
            db.add(ai_record)
        ai_record.health_score = clean_value(fresh_health_score)
        val_ai = validated_payload.get("ai_report", {})
        ai_record.executive_summary = val_ai.get("executive_summary", "")
        ai_record.strengths = val_ai.get("strengths", [])
        ai_record.weaknesses = val_ai.get("weaknesses", [])
        ai_record.recommendations = val_ai.get("recommendations", [])

        db.commit()
    except Exception as db_err:
        db.rollback()
        # Non-fatal log so payload return is not blocked by DB sync lock
        print(f"Warning: Database sync encountered issue: {db_err}")

    return validated_payload, company_name, doc_currency, sym
