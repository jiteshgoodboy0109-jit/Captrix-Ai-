"""
Document Profiling Engine
Profiles uploaded financial documents to analyze structural layout complexity, table density,
period counts, currency/unit flags, and capability requirements before model evaluation.
"""

from typing import Dict, List, Any
import os

def profile_financial_document(
    sheet_data: Dict[str, Any], 
    filename: str = "", 
    detected_currency: str = "NOT_DETERMINED", 
    detected_unit: str = "NOT_DETERMINED"
) -> Dict[str, Any]:
    """Generate detailed document profile for candidate model capability matching."""
    ext = os.path.splitext(filename)[1].lower() if filename else ".xlsx"
    file_type = "excel_workbook" if ext in [".xlsx", ".xls", ".xlsm"] else ("pdf_report" if ext == ".pdf" else "csv_data")
    
    sheet_count = len(sheet_data) if isinstance(sheet_data, dict) else 1
    total_rows = 0
    total_cells = 0
    non_empty_cells = 0
    merged_cell_count = 0
    periods_detected = set()
    statements_found = set()

    statement_keywords = {
        "profit_loss": ["revenue", "sales", "cogs", "gross profit", "net profit", "p&l", "income statement"],
        "balance_sheet": ["total assets", "fixed assets", "equity", "borrowings", "liabilities", "balance sheet"],
        "cash_flow": ["operating cash", "investing cash", "financing cash", "net cash", "cash flow"]
    }

    if isinstance(sheet_data, dict):
        for sname, df in sheet_data.items():
            if df is None or getattr(df, "empty", True):
                continue
            r, c = df.shape
            total_rows += r
            total_cells += r * c
            
            # Check cell contents
            for col in df.columns:
                col_str = str(col).lower()
                if any(yr in col_str for yr in ["2023", "2024", "2025", "2026", "fy23", "fy24", "fy25", "fy26"]):
                    periods_detected.add(col_str)
                    
            for idx, row in df.iterrows():
                row_str = " ".join([str(val).lower() for val in row.values if val is not None and str(val) != "nan"])
                if row_str.strip():
                    non_empty_cells += len(row)
                
                for stype, kws in statement_keywords.items():
                    if any(kw in row_str for kw in kws):
                        statements_found.add(stype)

    table_density = round(non_empty_cells / max(total_cells, 1), 2)
    layout_complexity = "high" if (sheet_count > 3 or total_rows > 300 or len(statements_found) >= 3) else ("medium" if total_rows > 100 else "low")
    
    requires_vision = file_type == "pdf_report" and table_density < 0.3
    requires_ocr = file_type == "pdf_report"

    return {
        "filename": filename,
        "type": file_type,
        "sheet_count": sheet_count,
        "total_rows": total_rows,
        "table_density": table_density,
        "layout_complexity": layout_complexity,
        "requires_vision": requires_vision,
        "requires_ocr": requires_ocr,
        "financial_statement_count": max(len(statements_found), 1),
        "number_of_periods": max(len(periods_detected), 1),
        "currency": detected_currency,
        "unit": detected_unit,
        "language": "English",
        "has_multi_level_headers": layout_complexity == "high"
    }
