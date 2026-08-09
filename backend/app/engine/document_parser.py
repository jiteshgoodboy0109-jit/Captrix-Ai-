import io
import re
import math
import json
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple

ACCOUNT_TYPE_RULES = {
    "REVENUE": [r"revenue", r"sales", r"income", r"turnover", r"fees earned", r"service revenue", r"gain"],
    "EXPENSE": [r"expense", r"cogs", r"cost of goods", r"salary", r"wages", r"rent", r"utility", r"depreciation", r"tax", r"interest", r"supplies", r"advertising", r"freight", r"payroll"],
    "ASSET": [r"asset", r"cash", r"bank", r"receivable", r"debtor", r"inventory", r"stock", r"prepaid", r"building", r"equipment", r"machinery", r"vehicle", r"investment", r"land"],
    "LIABILITY": [r"payable", r"creditor", r"debt", r"loan", r"borrowing", r"liability", r"accrued", r"mortgage", r"overdraft", r"tax payable", r"gst payable"],
    "EQUITY": [r"capital", r"equity", r"retained earnings", r"common stock", r"share capital", r"drawings", r"reserves"]
}

def clean_value(val: Any) -> float:
    if pd.isna(val) or val is None:
        return 0.0
    if isinstance(val, (int, float)):
        v = float(val)
        if math.isnan(v) or math.isinf(v):
            return 0.0
        return v
    # String cleaning
    s = str(val).replace("$", "").replace("₹", "").replace("€", "").replace("£", "").replace(",", "").strip()
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        v = float(s)
        if math.isnan(v) or math.isinf(v):
            return 0.0
        return v
    except ValueError:
        return 0.0

def sanitize_json_data(obj: Any) -> Any:
    """Recursively replace any NaN or Infinity floats with 0.0 so JSON serialization never fails."""
    if isinstance(obj, dict):
        return {k: sanitize_json_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json_data(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
        return obj
    return obj

def classify_account(name: str, sheet_context: str = "") -> str:
    name_lower = name.lower()
    ctx_lower = sheet_context.lower()
    
    # Check specific keyword overrides
    if "cash" in name_lower or "bank" in name_lower:
        return "CASH_ASSET"
    if "receivable" in name_lower or "debtor" in name_lower:
        return "RECEIVABLE_ASSET"
    if "inventory" in name_lower or "stock" in name_lower:
        return "INVENTORY_ASSET"
    if "payable" in name_lower or "creditor" in name_lower:
        return "PAYABLE_LIABILITY"

    for acct_type, patterns in ACCOUNT_TYPE_RULES.items():
        for p in patterns:
            if re.search(p, name_lower):
                return acct_type

    # Fallback to sheet context
    if "income" in ctx_lower or "sales" in ctx_lower:
        return "REVENUE" if "cost" not in name_lower else "EXPENSE"
    if "balance" in ctx_lower:
        return "ASSET"

    return "EXPENSE" if "cost" in name_lower or "fee" in name_lower else "ASSET"

def detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    mapping = {}
    cols = [str(c).strip() for c in df.columns]
    
    for c in cols:
        clow = c.lower()
        if not mapping.get("account_name") and any(k in clow for k in ["account", "particulars", "description", "name", "ledger", "item"]):
            mapping["account_name"] = c
        elif not mapping.get("debit") and any(k in clow for k in ["debit", "dr", "dr."]):
            mapping["debit"] = c
        elif not mapping.get("credit") and any(k in clow for k in ["credit", "cr", "cr."]):
            mapping["credit"] = c
        elif not mapping.get("amount") and any(k in clow for k in ["amount", "balance", "total", "val", "value"]):
            mapping["amount"] = c
        elif not mapping.get("account_code") and any(k in clow for k in ["code", "id", "account no", "acct#", "no."]):
            mapping["account_code"] = c
        elif not mapping.get("type") and any(k in clow for k in ["type", "group", "category", "class"]):
            mapping["type"] = c

    # Fallback if text columns are present
    if not mapping.get("account_name"):
        for c in cols:
            if df[c].dtype == "object":
                mapping["account_name"] = c
                break
        if not mapping.get("account_name") and len(cols) > 0:
            mapping["account_name"] = cols[0]

    # Positional fallbacks for debit/credit/amount
    if not mapping.get("debit") and not mapping.get("amount") and len(cols) > 1:
        mapping["debit"] = cols[1]
    if not mapping.get("credit") and len(cols) > 2:
        mapping["credit"] = cols[2]

    return mapping

def extract_docx_xml_text(file_bytes: bytes) -> Tuple[List[str], List[List[List[str]]]]:
    """Extracts text paragraphs and table rows/cells directly from docx XML without python-docx."""
    paragraphs = []
    tables = []
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            xml_content = z.read("word/document.xml")
            root = ET.fromstring(xml_content)
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            def get_element_text(elem):
                texts = []
                for t in elem.findall('.//w:t', ns):
                    if t.text:
                        texts.append(t.text)
                return "".join(texts)

            for p in root.findall('.//w:p', ns):
                text = get_element_text(p)
                if text.strip():
                    paragraphs.append(text.strip())

            for tbl in root.findall('.//w:tbl', ns):
                table_rows = []
                for tr in tbl.findall('.//w:tr', ns):
                    row_cells = []
                    for tc in tr.findall('.//w:tc', ns):
                        cell_text = " ".join([get_element_text(p) for p in tc.findall('.//w:p', ns)]).strip()
                        row_cells.append(cell_text)
                    if any(row_cells):
                        table_rows.append(row_cells)
                if table_rows:
                    tables.append(table_rows)
    except Exception as e:
        print("XML Docx fallback error:", e)
    return paragraphs, tables

def parse_docx(file_bytes: bytes) -> List[Dict[str, Any]]:
    items = []
    paragraphs = []
    tables = []
    
    try:
        import docx  # type: ignore
        doc = docx.Document(io.BytesIO(file_bytes))
        for p in doc.paragraphs:
            if p.text.strip():
                paragraphs.append(p.text.strip())
        for tbl in doc.tables:
            table_rows = []
            for row in tbl.rows:
                row_cells = [cell.text.strip() for cell in row.cells]
                if any(row_cells):
                    table_rows.append(row_cells)
            if table_rows:
                tables.append(table_rows)
    except Exception:
        paragraphs, tables = extract_docx_xml_text(file_bytes)

    for t_idx, tbl in enumerate(tables):
        sheet_name = f"Word Table {t_idx+1}"
        header_row_idx = -1
        for r_idx, row in enumerate(tbl[:3]):
            row_lower = [c.lower() for c in row]
            if any(k in " ".join(row_lower) for k in ["account", "particulars", "debit", "credit", "amount", "balance", "description"]):
                header_row_idx = r_idx
                break
        
        headers = []
        rows_to_process = []
        if header_row_idx != -1:
            headers = tbl[header_row_idx]
            rows_to_process = tbl[header_row_idx+1:]
        else:
            if len(tbl) > 0:
                cols_count = len(tbl[0])
                if cols_count >= 3:
                    headers = ["account_name", "debit", "credit"] + [f"col_{i}" for i in range(3, cols_count)]
                elif cols_count == 2:
                    headers = ["account_name", "amount"]
                else:
                    headers = ["account_name"]
                rows_to_process = tbl

        df_temp = pd.DataFrame(rows_to_process, columns=headers[:len(rows_to_process[0])] if rows_to_process else None)
        col_map = detect_columns(df_temp)
        acct_col = col_map.get("account_name")
        dr_col = col_map.get("debit")
        cr_col = col_map.get("credit")
        amt_col = col_map.get("amount")
        code_col = col_map.get("account_code")
        type_col = col_map.get("type")

        for r_idx, row_vals in enumerate(rows_to_process):
            row_dict = {}
            for col_idx, h in enumerate(headers):
                if col_idx < len(row_vals):
                    row_dict[h] = row_vals[col_idx]
            
            acct_name = row_dict.get(acct_col, "").strip() if acct_col else ""
            if not acct_name or acct_name.lower() in ["total", "subtotal", "grand total", "nan", "particulars", "account name", "description"]:
                continue
            
            dr = clean_value(row_dict.get(dr_col)) if dr_col else 0.0
            cr = clean_value(row_dict.get(cr_col)) if cr_col else 0.0
            amt = clean_value(row_dict.get(amt_col)) if amt_col else (dr - cr)
            acct_code = row_dict.get(code_col, "").strip() if code_col else f"WD-{t_idx}-{r_idx}"
            raw_type = row_dict.get(type_col, "").strip() if type_col else ""
            acct_type = raw_type.upper() if raw_type else classify_account(acct_name, sheet_name)
            net = dr - cr if (dr or cr) else amt

            items.append({
                "account_code": acct_code,
                "account_name": acct_name,
                "account_type": acct_type,
                "debit": dr,
                "credit": cr,
                "net_amount": net,
                "sheet": sheet_name
            })

    for p_idx, text in enumerate(paragraphs):
        match = re.search(r'([A-Za-z\s&\(\)/\-]{4,30})[:\-]?\s+[\$₹€£]?\s*(-?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text)
        if match:
            acct_name = match.group(1).strip()
            val = clean_value(match.group(2))
            if acct_name.lower() not in ["total", "subtotal", "grand total", "nan", "particulars", "account name", "description"] and val != 0.0:
                acct_type = classify_account(acct_name, "Paragraph")
                items.append({
                    "account_code": f"TX-{p_idx}",
                    "account_name": acct_name,
                    "account_type": acct_type,
                    "debit": val if val > 0 and acct_type in ["ASSET", "EXPENSE"] else 0.0,
                    "credit": abs(val) if val < 0 or acct_type in ["LIABILITY", "EQUITY", "REVENUE"] else 0.0,
                    "net_amount": val,
                    "sheet": "Word Paragraphs"
                })

    return items

def parse_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    items = []
    text_content = ""
    
    try:
        from pypdf import PdfReader  # type: ignore
        reader = PdfReader(io.BytesIO(file_bytes))
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_content += f"\n--- Page {page_idx+1} ---\n" + page_text
    except Exception as e:
        print("pypdf parsing error, trying raw stream search:", e)
        
    if not text_content:
        try:
            text_content = re.sub(r'[^\x20-\x7E\n\t]', ' ', file_bytes.decode('utf-8', errors='ignore'))
        except Exception:
            pass

    lines = [line.strip() for line in text_content.splitlines() if line.strip()]
    
    for line_idx, line in enumerate(lines):
        tokens = line.split()
        if len(tokens) < 2:
            continue
            
        numbers = []
        non_numbers = []
        for token in tokens:
            cleaned_tok = token.replace("$", "").replace("₹", "").replace("€", "").replace("£", "").replace(",", "")
            if re.match(r'^-?\d+(?:\.\d+)?$', cleaned_tok) or re.match(r'^\(-?\d+(?:\.\d+)?\)$', cleaned_tok):
                numbers.append(clean_value(token))
            else:
                non_numbers.append(token)
                
        if len(numbers) > 0 and len(non_numbers) > 0:
            acct_name = " ".join(non_numbers)
            acct_code = f"PDF-{line_idx}"
            first_word = non_numbers[0]
            if re.match(r'^\d+$', first_word) or re.match(r'^[A-Z0-9\-]{3,8}$', first_word):
                acct_code = first_word
                acct_name = " ".join(non_numbers[1:])
                
            if not acct_name or acct_name.lower() in ["total", "subtotal", "grand total", "nan", "particulars", "account name", "description"]:
                continue
                
            acct_type = classify_account(acct_name, "PDF")
            
            dr = 0.0
            cr = 0.0
            
            if len(numbers) >= 2:
                dr = numbers[0]
                cr = numbers[1]
                net = dr - cr
            else:
                net = numbers[0]
                if acct_type in ["ASSET", "EXPENSE"]:
                    dr = net if net > 0 else 0.0
                    cr = abs(net) if net < 0 else 0.0
                else:
                    cr = net if net > 0 else 0.0
                    dr = abs(net) if net < 0 else 0.0
                    
            if net != 0.0 or dr != 0.0 or cr != 0.0:
                items.append({
                    "account_code": acct_code,
                    "account_name": acct_name,
                    "account_type": acct_type,
                    "debit": dr,
                    "credit": cr,
                    "net_amount": net,
                    "sheet": "PDF Pages"
                })
                
    return items

def parse_json(file_bytes: bytes) -> List[Dict[str, Any]]:
    items = []
    try:
        data = json.loads(file_bytes.decode('utf-8', errors='ignore'))
        
        if isinstance(data, list):
            for idx, obj in enumerate(data):
                if isinstance(obj, dict):
                    name = obj.get("account_name") or obj.get("account") or obj.get("name") or obj.get("particulars") or ""
                    if not name:
                        continue
                    dr = clean_value(obj.get("debit") or obj.get("dr") or 0.0)
                    cr = clean_value(obj.get("credit") or obj.get("cr") or 0.0)
                    net = clean_value(obj.get("net_amount") or obj.get("amount") or obj.get("balance") or (dr - cr))
                    code = str(obj.get("account_code") or obj.get("code") or obj.get("id") or f"JS-{idx}")
                    acct_type = str(obj.get("account_type") or obj.get("type") or classify_account(name, "JSON")).upper()
                    
                    items.append({
                        "account_code": code,
                        "account_name": name,
                        "account_type": acct_type,
                        "debit": dr,
                        "credit": cr,
                        "net_amount": net,
                        "sheet": "JSON File"
                    })
        elif isinstance(data, dict):
            def traverse(d: dict, path: str = ""):
                for k, v in d.items():
                    current_path = f"{path} {k}".strip()
                    if isinstance(v, (int, float)):
                        val = clean_value(v)
                        if val != 0.0:
                            acct_type = classify_account(k, current_path)
                            items.append({
                                "account_code": f"JS-{len(items)}",
                                "account_name": k,
                                "account_type": acct_type,
                                "debit": val if val > 0 and acct_type in ["ASSET", "EXPENSE"] else 0.0,
                                "credit": abs(val) if val < 0 or acct_type in ["LIABILITY", "EQUITY", "REVENUE"] else 0.0,
                                "net_amount": val,
                                "sheet": "JSON Object"
                            })
                    elif isinstance(v, dict):
                        traverse(v, current_path)
                    elif isinstance(v, list):
                        for el in v:
                            if isinstance(el, dict):
                                traverse(el, current_path)
            traverse(data)
    except Exception as e:
        print("JSON parse error:", e)
    return items

def parse_text_lines(file_bytes: bytes) -> List[Dict[str, Any]]:
    items = []
    try:
        content = file_bytes.decode('utf-8', errors='ignore')
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        for line_idx, line in enumerate(lines):
            match = re.search(r'([A-Za-z\s&\(\)/\-]{4,30})[:\-]?\s+[\$₹€£]?\s*(-?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', line)
            if match:
                name = match.group(1).strip()
                val = clean_value(match.group(2))
                if name.lower() not in ["total", "subtotal", "grand total", "nan", "particulars", "account name", "description"] and val != 0.0:
                    acct_type = classify_account(name, "Text")
                    items.append({
                        "account_code": f"TXT-{line_idx}",
                        "account_name": name,
                        "account_type": acct_type,
                        "debit": val if val > 0 and acct_type in ["ASSET", "EXPENSE"] else 0.0,
                        "credit": abs(val) if val < 0 or acct_type in ["LIABILITY", "EQUITY", "REVENUE"] else 0.0,
                        "net_amount": val,
                        "sheet": "Text Lines"
                    })
    except Exception as e:
        print("Text parse error:", e)
    return items

def parse_workbook(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    sheet_data = {}
    normalized_items = []
    detected_sheets = []
    
    fname = (filename or "").lower()
    
    try:
        if fname.endswith(".pdf"):
            normalized_items = parse_pdf(file_bytes)
        elif fname.endswith(".docx") or fname.endswith(".doc"):
            normalized_items = parse_docx(file_bytes)
        elif fname.endswith(".json"):
            normalized_items = parse_json(file_bytes)
        elif fname.endswith(".csv") or fname.endswith(".tsv"):
            try:
                df = pd.read_csv(io.BytesIO(file_bytes), sep=None, engine='python')
                sheet_data["Sheet1"] = df
                detected_sheets = ["Sheet1"]
            except Exception:
                normalized_items = parse_text_lines(file_bytes)
        elif fname.endswith(".txt") or fname.endswith(".md") or fname.endswith(".log"):
            normalized_items = parse_text_lines(file_bytes)
        elif fname.endswith(".xlsx") or fname.endswith(".xls") or fname.endswith(".xlsm") or fname.endswith(".xlsb"):
            xls = pd.ExcelFile(io.BytesIO(file_bytes))
            detected_sheets = list(xls.sheet_names)
            for sheet in xls.sheet_names:
                try:
                    sheet_data[sheet] = pd.read_excel(xls, sheet_name=sheet)
                except Exception:
                    continue
        else:
            normalized_items = parse_text_lines(file_bytes)
    except Exception as e:
        print(f"Error parsing document {filename}: {e}")

    if sheet_data:
        for sheet_name, df in sheet_data.items():
            if df.empty:
                continue
            df = df.dropna(how="all").dropna(axis=1, how="all")
            if df.empty:
                continue

            found_header = False
            cols_lower = [str(c).lower() for c in df.columns]
            if any(kw in " ".join(cols_lower) for kw in ["account", "particulars", "debit", "credit", "amount", "description", "balance"]):
                found_header = True
            
            if not found_header:
                for r_idx in range(min(5, len(df))):
                    row_vals = [str(v).lower() for v in df.iloc[r_idx].values if pd.notna(v)]
                    if any(kw in " ".join(row_vals) for kw in ["account", "particulars", "debit", "credit", "amount", "description", "balance"]):
                        new_header = df.iloc[r_idx]
                        df = df.iloc[r_idx + 1:].copy()
                        df.columns = new_header
                        found_header = True
                        break

            col_map = detect_columns(df)
            acct_col = col_map.get("account_name")
            dr_col = col_map.get("debit")
            cr_col = col_map.get("credit")
            amt_col = col_map.get("amount")
            code_col = col_map.get("account_code")
            type_col = col_map.get("type")

            if not acct_col or acct_col not in df.columns:
                continue

            for idx, row in df.iterrows():
                acct_name = str(row[acct_col]).strip() if pd.notna(row[acct_col]) else ""
                if not acct_name or acct_name.lower() in ["total", "subtotal", "grand total", "nan", "particulars", "account name", "description"]:
                    continue

                dr = clean_value(row[dr_col]) if dr_col and dr_col in row else 0.0
                cr = clean_value(row[cr_col]) if cr_col and cr_col in row else 0.0
                amt = clean_value(row[amt_col]) if amt_col and amt_col in row else (dr - cr)
                acct_code = str(row[code_col]).strip() if code_col and code_col in row and pd.notna(row[code_col]) else f"ACC-{idx}"
                raw_type = str(row[type_col]).strip() if type_col and type_col in row and pd.notna(row[type_col]) else ""
                acct_type = raw_type.upper() if raw_type else classify_account(acct_name, sheet_name)
                net = dr - cr if (dr or cr) else amt

                normalized_items.append({
                    "account_code": acct_code,
                    "account_name": acct_name,
                    "account_type": acct_type,
                    "debit": clean_value(dr),
                    "credit": clean_value(cr),
                    "net_amount": clean_value(net),
                    "sheet": sheet_name
                })

    if not normalized_items:
        # Dynamic fallback: Scan raw text lines from uploaded file to extract custom items
        normalized_items = parse_text_lines(file_bytes)

    if not normalized_items:
        # Extract generic rows if numbers exist in file bytes
        try:
            content_str = file_bytes.decode('utf-8', errors='ignore')
            lines = [l.strip() for l in content_str.splitlines() if l.strip()]
            for l_idx, line in enumerate(lines[:30]):
                nums = re.findall(r'[-+]?\d*\.\d+|\d+', line)
                if nums:
                    val = clean_value(nums[0])
                    if val != 0.0:
                        normalized_items.append({
                            "account_code": f"DYNAMIC-{l_idx}",
                            "account_name": line[:30].strip(),
                            "account_type": classify_account(line, "Extracted"),
                            "debit": val if val > 0 else 0.0,
                            "credit": abs(val) if val < 0 else 0.0,
                            "net_amount": val,
                            "sheet": "ExtractedData"
                        })
        except Exception:
            pass

    unique_items = []
    seen = set()
    for item in normalized_items:
        key = (str(item.get("account_name", "")).lower(), item.get("net_amount", 0.0))
        if key not in seen:
            seen.add(key)
            unique_items.append(item)

    if not detected_sheets:
        detected_sheets = sorted(list(set(item["sheet"] for item in unique_items))) if unique_items else ["ParsedSheet"]

    return {
        "filename": filename,
        "sheet_names": detected_sheets,
        "normalized_items": unique_items
    }

