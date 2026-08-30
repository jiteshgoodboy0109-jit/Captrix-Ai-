from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Upload, Statement, Ratio, CorporateFinance, AIReport, Company, FinancialData
from app.auth.jwt import get_current_user, User
from app.engine.statement_generator import generate_financial_statements
from app.engine.multi_period_analyzer import generate_multi_period_analysis
from app.engine.canonical_model import build_canonical_dataset
from app.engine.reconciliation import perform_source_to_result_reconciliation
from app.engine.quality_engine import compute_financial_quality_score
from app.engine.dupont_analyzer import calculate_dupont_analysis
from app.engine.risk_analyzer import calculate_risk_intelligence
from app.engine.auditor_engine import perform_full_financial_audit

router = APIRouter(prefix="/api/analysis", tags=["Financial Analysis"])

@router.get("/{upload_id}")
def get_analysis_results(upload_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Enforce strict user-level data isolation
    upload = db.query(Upload).filter(Upload.id == upload_id, Upload.user_id == current_user.id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload analysis not found or access denied.")

    company = db.query(Company).filter(Company.id == upload.company_id).first()
    ratio = db.query(Ratio).filter(Ratio.upload_id == upload_id).first()
    corp = db.query(CorporateFinance).filter(CorporateFinance.upload_id == upload_id).first()
    ai_report = db.query(AIReport).filter(AIReport.upload_id == upload_id).first()

    if not ratio or not corp or not ai_report:
        raise HTTPException(status_code=404, detail="Incomplete analysis data.")

    # Reconstruct statements payload dynamically from database line items
    fd_items = db.query(FinancialData).filter(FinancialData.upload_id == upload_id).all()
    items = []
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
            "year": meta.get("year", "Current"),
            "unit": meta.get("unit", "Units"),
            "currency": meta.get("currency", "USD"),
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
    statements_payload = generate_financial_statements(items)
    multi_period = generate_multi_period_analysis(statements_payload)

    ratios_dict = {
        "profitability": ratio.profitability,
        "liquidity": ratio.liquidity,
        "solvency": ratio.solvency,
        "efficiency": ratio.efficiency
    }

    from app.engine.financial_analyzer import calculate_corporate_finance
    corp_fin_payload = calculate_corporate_finance(statements_payload, ratios_dict)

    # Determine document currency
    doc_currency = (company.currency if company and company.currency else None) or "USD"
    if doc_currency == "USD":
        for it in items:
            c = it.get("currency")
            if c and c != "USD":
                doc_currency = c
                break

    from app.engine.currency_engine import SUPPORTED_CURRENCIES
    curr_info = SUPPORTED_CURRENCIES.get(doc_currency.upper(), {"symbol": "$"})
    sym = curr_info.get("symbol", "$")

    dupont_analysis = calculate_dupont_analysis(statements_payload, ratios_dict)
    risk_intelligence = calculate_risk_intelligence(statements_payload, ratios_dict)
    audit_report = perform_full_financial_audit(statements_payload, ratios_dict, canonical_items=items, currency_symbol=sym)

    canonical_dataset = build_canonical_dataset(items, upload.filename)
    reconciliation = perform_source_to_result_reconciliation(canonical_dataset, statements_payload, ratios_dict)
    quality_report = compute_financial_quality_score(reconciliation, statements_payload.get("validation_report", {}))

    from app.engine.output_validator import OutputValidator

    raw_response = {
        "upload_id": upload.id,
        "company_name": company.name if company else "Enterprise Target",
        "currency": doc_currency,
        "filename": upload.filename,
        "sheet_names": upload.sheet_names,
        "created_at": upload.created_at,
        "health_score": quality_report.get("quality_score", ai_report.health_score),
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
            "health_score": quality_report.get("quality_score", ai_report.health_score),
            "executive_summary": ai_report.executive_summary,
            "strengths": ai_report.strengths,
            "weaknesses": ai_report.weaknesses,
            "recommendations": ai_report.recommendations
        }
    }

    b_dataset = canonical_dataset.get("layer_a_raw_records", []) if isinstance(canonical_dataset, dict) else []
    validated_response = OutputValidator.validate_and_filter_payload(raw_response, b_dataset)

    return validated_response
