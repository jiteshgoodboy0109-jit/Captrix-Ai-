from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Upload, Statement, Ratio, CorporateFinance, AIReport, Company, User, FinancialData
from app.auth.jwt import get_current_user
from app.engine.statement_generator import generate_financial_statements
from app.reports.pdf_generator import generate_pdf_report
from app.reports.excel_generator import generate_excel_report

router = APIRouter(prefix="/api/reports", tags=["Report Download Engine"])

def fetch_upload_payload(upload_id: int, db: Session, current_user: User):
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload or upload.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Upload analysis not found.")

    company = db.query(Company).filter(Company.id == upload.company_id).first()
    company_name = company.name if company else "Enterprise Target"

    ratio = db.query(Ratio).filter(Ratio.upload_id == upload_id).first()
    corp = db.query(CorporateFinance).filter(CorporateFinance.upload_id == upload_id).first()
    ai_rep = db.query(AIReport).filter(AIReport.upload_id == upload_id).first()

    # Reconstruct statements_dict dynamically from database line items
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
    from app.engine.financial_analyzer import calculate_financial_ratios, calculate_corporate_finance
    from app.engine.output_validator import OutputValidator, ReportConsistencyValidator
    from app.engine.canonical_model import build_canonical_dataset
    from app.engine.quality_engine import compute_financial_quality_score
    from app.engine.reconciliation import perform_source_to_result_reconciliation
    from app.engine.ai_insights import generate_ai_insights

    statements_dict = generate_financial_statements(items)
    # Dynamic recalculation using authoritative RatioEngine as single source of truth
    ratios_dict = calculate_financial_ratios(statements_dict)
    corp_dict = calculate_corporate_finance(statements_dict, ratios_dict)

    canonical_dataset = build_canonical_dataset(items, upload.filename)
    reconciliation_report = perform_source_to_result_reconciliation(canonical_dataset, statements_dict, ratios_dict)
    quality_report = compute_financial_quality_score(reconciliation_report, statements_dict.get("validation_report", {}))
    ai_insights = generate_ai_insights(statements_dict, ratios_dict, corp_dict, canonical_dataset, quality_report=quality_report)
    health_score = ai_insights.get("canonical_health_score", {}).get("score", quality_report.get("quality_score", 85.0))

    ai_report_dict = {
        "health_score": health_score,
        "executive_summary": ai_insights.get("executive_summary") or "Captrix AI Financial Analysis Report Completed.",
        "strengths": ai_insights.get("strengths", []),
        "weaknesses": ai_insights.get("weaknesses", []),
        "recommendations": ai_insights.get("recommendations", []),
        "canonical_dataset": canonical_dataset,
        "quality_report": quality_report
    }

    raw_payload = {
        "company_name": company_name,
        "statements": statements_dict,
        "ratios": ratios_dict,
        "corporate_finance": corp_dict,
        "ai_report": ai_report_dict,
    }
    validated_payload = OutputValidator.validate_and_filter_payload(raw_payload, items)
    validated_payload = ReportConsistencyValidator.sanitize_audit_wording(validated_payload)
    ReportConsistencyValidator.validate_final_report_payload(validated_payload, raise_on_error=False)

    statements_dict = validated_payload.get("statements", statements_dict)
    ratios_dict = validated_payload.get("ratios", ratios_dict)
    corp_dict = validated_payload.get("corporate_finance", corp_dict)
    ai_report_dict = validated_payload.get("ai_report", ai_report_dict)

    currency = company.currency if company and company.currency else "USD"
    if currency == "USD":
        for it in items:
            c = it.get("currency")
            if c and c != "USD":
                currency = c
                break

    return company_name, statements_dict, ratios_dict, corp_dict, ai_report_dict, currency

@router.get("/pdf/{upload_id}")
@router.get("/{upload_id}/pdf")
def download_pdf_report(upload_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    company_name, statements_dict, ratios_dict, corp_dict, ai_report_dict, currency = fetch_upload_payload(upload_id, db, current_user)
    pdf_bytes = generate_pdf_report(company_name, statements_dict, ratios_dict, corp_dict, ai_report_dict, currency=currency)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Financial_Analysis_{upload_id}.pdf"
        }
    )

@router.get("/excel/{upload_id}")
@router.get("/{upload_id}/excel")
def download_excel_report(upload_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    company_name, statements_dict, ratios_dict, corp_dict, ai_report_dict, currency = fetch_upload_payload(upload_id, db, current_user)
    excel_bytes = generate_excel_report(company_name, statements_dict, ratios_dict, corp_dict, ai_report_dict)

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=Financial_Analysis_{upload_id}.xlsx"
        }
    )
