import os, json
from app.engine.document_parser import parse_workbook, sanitize_json_data, clean_value
from app.engine.statement_generator import generate_financial_statements
from app.engine.financial_analyzer import calculate_financial_ratios, calculate_corporate_finance
from app.engine.canonical_model import build_canonical_dataset
from app.engine.reconciliation import perform_source_to_result_reconciliation
from app.engine.quality_engine import compute_financial_quality_score
from app.engine.ai_insights import generate_ai_insights
from app.engine.auditor_engine import perform_full_financial_audit

file_path = r'd:\ai-financial-intelligence-platform\backend\uploaded_files\5_Captrix_Level_1_Simple_Financial_Test.docx'
filename = '5_Captrix_Level_1_Simple_Financial_Test.docx'

with open(file_path, 'rb') as f:
    file_bytes = f.read()

# 1. Parse workbook
parsed = parse_workbook(file_bytes, filename)
items = parsed.get("normalized_items", [])
company_name = parsed.get("company_name", "")
currency = parsed.get("currency", "NOT_DETERMINED")

# 2. Statements
statements = sanitize_json_data(generate_financial_statements(items))

# 3. Ratios & Corporate Finance
ratios = sanitize_json_data(calculate_financial_ratios(statements))
corp_fin = sanitize_json_data(calculate_corporate_finance(statements, ratios))

# 4. Canonical Dataset & Reconciliation
canonical_dataset = sanitize_json_data(build_canonical_dataset(items, filename))
reconciliation = sanitize_json_data(perform_source_to_result_reconciliation(canonical_dataset, statements, ratios))
quality_report = sanitize_json_data(compute_financial_quality_score(reconciliation, statements.get("validation_report", {})))

# 5. AI Insights
ai_insights = sanitize_json_data(generate_ai_insights(statements, ratios, corp_fin, canonical_dataset, quality_report=quality_report))

# 6. Auditor Engine
audit_report = sanitize_json_data(perform_full_financial_audit(
    statements=statements,
    ratios=ratios,
    canonical_items=items,
    currency_symbol="₹" if currency == "INR" else "$"
))

out = {
    "company_name": company_name,
    "currency": currency,
    "items_count": len(items),
    "items": items,
    "statements": statements,
    "ratios": ratios,
    "reconciliation": reconciliation,
    "quality_report": quality_report,
    "ai_insights": ai_insights,
    "audit_report": audit_report
}

with open("level1_full_output.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, default=str)

print("Saved level1_full_output.json cleanly!")
