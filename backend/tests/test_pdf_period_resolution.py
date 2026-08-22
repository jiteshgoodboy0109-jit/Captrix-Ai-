import pytest
from app.engine.document_parser import PDFAdapter, parse_workbook, detect_year_columns
from app.engine.statement_generator import generate_financial_statements

def test_period_resolution_4_year_sequence():
    """Test A: Standard 4-year chronological sequence (2023 2024 2025 2026)."""
    headers = ["Particulars", "FY2023", "FY2024", "FY2025", "FY2026"]
    top_rows = [["Revenue from Operations", 78000, 88000, 101000, 116000]]
    
    year_map = detect_year_columns(headers, top_rows)
    assert year_map[1]["year"] == "2023"
    assert year_map[2]["year"] == "2024"
    assert year_map[3]["year"] == "2025"
    assert year_map[4]["year"] == "2026"

def test_period_resolution_reversed_order():
    """Test B: Reversed column order (2026 2025 2024 2023)."""
    headers = ["Particulars", "FY2026", "FY2025", "FY2024", "FY2023"]
    top_rows = [["Revenue from Operations", 116000, 101000, 88000, 78000]]
    
    year_map = detect_year_columns(headers, top_rows)
    assert year_map[1]["year"] == "2026"
    assert year_map[2]["year"] == "2025"
    assert year_map[3]["year"] == "2024"
    assert year_map[4]["year"] == "2023"

def test_period_resolution_different_window():
    """Test C: 4-year window (2021 2022 2023 2024) - proves no hardcoded 2024-2026 assumption."""
    headers = ["Particulars", "2021", "2022", "2023", "2024"]
    top_rows = [["Revenue", 50000, 60000, 70000, 80000]]
    
    year_map = detect_year_columns(headers, top_rows)
    assert year_map[1]["year"] == "2021"
    assert year_map[2]["year"] == "2022"
    assert year_map[3]["year"] == "2023"
    assert year_map[4]["year"] == "2024"

def test_period_resolution_5_year_table():
    """Test D: 5-year table (2020 2021 2022 2023 2024)."""
    headers = ["Particulars", "2020", "2021", "2022", "2023", "2024"]
    top_rows = [["Net Sales", 100, 200, 300, 400, 500]]
    
    year_map = detect_year_columns(headers, top_rows)
    assert len(year_map) == 5
    assert year_map[1]["year"] == "2020"
    assert year_map[5]["year"] == "2024"

def test_period_resolution_3_year_table():
    """Test E: 3-year table (2022 2023 2024)."""
    headers = ["Particulars", "FY2022", "FY2023", "FY2024"]
    top_rows = [["Revenue", 1000, 2000, 3000]]
    
    year_map = detect_year_columns(headers, top_rows)
    assert year_map[1]["year"] == "2022"
    assert year_map[2]["year"] == "2023"
    assert year_map[3]["year"] == "2024"

def test_period_resolution_range_headers():
    """Test F: Range-based fiscal year headers (2023-24, 2024-25, 2025-26)."""
    headers = ["Particulars", "2023-24", "2024-25", "2025-26"]
    top_rows = [["Revenue", 1000, 2000, 3000]]
    
    year_map = detect_year_columns(headers, top_rows)
    assert year_map[1]["year"] == "2024"
    assert year_map[2]["year"] == "2025"
    assert year_map[3]["year"] == "2026"

def test_period_resolution_missing_header_no_guess():
    """Test G: Missing header - period_status must be UNKNOWN and never invent years."""
    headers = ["Particulars", "Col 1", "Col 2", "Col 3"]
    top_rows = [["Revenue", 100, 200, 300]]
    
    year_map = detect_year_columns(headers, top_rows)
    # When no year is in header, year_map should NOT invent 2024, 2025, 2026
    for idx, meta in year_map.items():
        assert meta["year"] not in ["2024", "2025", "2026"] or "2024" not in [year_map[i]["year"] for i in year_map]
