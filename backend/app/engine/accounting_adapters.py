"""
Accounting System Format Ingestion Adapters Module
Provides format parsing adapters for Tally XML/CSV, QuickBooks, and Xero General Ledger exports.
Enforces strict zero-fabrication: extracts only genuine source transactions and line items.
"""

import io
import re
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
import pandas as pd

class TallyAdapter:
    """Adapter for parsing Tally XML and hierarchical Tally exported files."""
    
    @staticmethod
    def is_tally_format(content_bytes: bytes, filename: str) -> bool:
        fname = (filename or "").lower()
        if fname.endswith(".xml"):
            sample = content_bytes[:2000].decode("utf-8", errors="ignore").lower()
            return "<envelope>" in sample or "<tallymessage" in sample or "<ledger" in sample or "<voucher" in sample
        elif fname.endswith(".csv") or fname.endswith(".tsv"):
            sample = content_bytes[:2000].decode("utf-8", errors="ignore").lower()
            return "tally" in sample or ("closing balance" in sample and "debit" in sample and "credit" in sample)
        return False

    @staticmethod
    def parse_tally_xml(content_bytes: bytes) -> Dict[str, pd.DataFrame]:
        try:
            root = ET.fromstring(content_bytes.decode("utf-8", errors="ignore"))
            records = []
            
            # 1. Search for LEDGER tags
            for ledger in root.iter("LEDGER"):
                name = ledger.get("NAME") or ""
                parent = ""
                parent_elem = ledger.find("PARENT")
                if parent_elem is not None and parent_elem.text:
                    parent = parent_elem.text.strip()
                
                open_bal = 0.0
                open_elem = ledger.find("OPENINGBALANCE")
                if open_elem is not None and open_elem.text:
                    try:
                        open_bal = float(open_elem.text.strip())
                    except ValueError:
                        open_bal = 0.0
                
                clos_bal = 0.0
                clos_elem = ledger.find("CLOSINGBALANCE")
                if clos_elem is not None and clos_elem.text:
                    try:
                        clos_bal = float(clos_elem.text.strip())
                    except ValueError:
                        clos_bal = 0.0

                net_amt = clos_bal if clos_bal != 0.0 else open_bal
                debit = net_amt if net_amt > 0 else 0.0
                credit = abs(net_amt) if net_amt < 0 else 0.0

                if name:
                    records.append({
                        "Account Code": f"TALLY-{len(records)+1}",
                        "Particulars": name,
                        "Category": parent,
                        "Debit": debit,
                        "Credit": credit,
                        "Net Amount": net_amt
                    })

            # 2. Search for VOUCHER tags
            if not records:
                for voucher in root.iter("VOUCHER"):
                    v_type = voucher.get("VCHTYPE") or "Journal"
                    for item in voucher.iter("ALLLEDGERENTRIES.LIST"):
                        name_elem = item.find("LEDGERNAME")
                        amt_elem = item.find("AMOUNT")
                        if name_elem is not None and amt_elem is not None and name_elem.text and amt_elem.text:
                            try:
                                amt = float(amt_elem.text.strip())
                            except ValueError:
                                amt = 0.0
                            
                            records.append({
                                "Account Code": f"TALLY-V-{len(records)+1}",
                                "Particulars": name_elem.text.strip(),
                                "Category": v_type,
                                "Debit": abs(amt) if amt < 0 else 0.0,
                                "Credit": amt if amt > 0 else 0.0,
                                "Net Amount": -amt
                            })

            if records:
                return {"Tally Ledger": pd.DataFrame(records)}
        except Exception as e:
            print(f"Tally XML parsing fallback: {e}")
        return {}


class QuickBooksAdapter:
    """Adapter for parsing QuickBooks Desktop and QuickBooks Online CSV/JSON reports."""
    
    @staticmethod
    def is_quickbooks_format(content_bytes: bytes, filename: str) -> bool:
        sample = content_bytes[:2000].decode("utf-8", errors="ignore").lower()
        return "quickbooks" in sample or "qbo" in sample or "intuit" in sample or ("profit and loss" in sample and "total for" in sample)

    @staticmethod
    def parse_quickbooks_csv(df: pd.DataFrame) -> pd.DataFrame:
        """Flattens QuickBooks hierarchical sectioned export into a clean financial table."""
        records = []
        current_section = "General"
        
        for _, row in df.iterrows():
            row_vals = [str(v).strip() for v in row.values if pd.notna(v) and str(v).strip()]
            if not row_vals:
                continue
            first_col = row_vals[0]
            
            # Detect section header
            if len(row_vals) == 1 and not any(char.isdigit() for char in first_col):
                current_section = first_col
                continue
            
            # Parse line items
            if len(row_vals) >= 2:
                # Find the numeric amount
                numeric_val = None
                label = first_col
                for v in reversed(row_vals):
                    clean_v = v.replace("$", "").replace(",", "").replace("(", "-").replace(")", "").strip()
                    try:
                        numeric_val = float(clean_v)
                        break
                    except ValueError:
                        continue

                if numeric_val is not None and not label.lower().startswith("total for"):
                    records.append({
                        "Particulars": label,
                        "Section": current_section,
                        "Amount": numeric_val,
                        "Debit": numeric_val if numeric_val > 0 else 0.0,
                        "Credit": abs(numeric_val) if numeric_val < 0 else 0.0
                    })

        return pd.DataFrame(records) if records else df


class XeroAdapter:
    """Adapter for parsing Xero Trial Balance and General Ledger exports."""
    
    @staticmethod
    def is_xero_format(content_bytes: bytes, filename: str) -> bool:
        sample = content_bytes[:2000].decode("utf-8", errors="ignore").lower()
        return "xero" in sample or ("trial balance" in sample and "debit" in sample and "credit" in sample and "ytd" in sample)

    @staticmethod
    def parse_xero_csv(df: pd.DataFrame) -> pd.DataFrame:
        """Cleans Xero trial balance or ledger export into normalized account records."""
        records = []
        for _, row in df.iterrows():
            row_str = " ".join([str(v).lower() for v in row.values if pd.notna(v)])
            if "total" in row_str or "unnamed" in row_str or "page" in row_str:
                continue
            
            # Extract Account Code and Name if formatted as '200 - Sales'
            first_val = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            if not first_val:
                continue

            debit = 0.0
            credit = 0.0
            for v in row.values[1:]:
                if pd.notna(v):
                    clean_v = str(v).replace("$", "").replace(",", "").replace("(", "-").replace(")", "").strip()
                    try:
                        num = float(clean_v)
                        if num > 0 and debit == 0.0:
                            debit = num
                        elif num > 0:
                            credit = num
                    except ValueError:
                        continue

            net = debit - credit
            records.append({
                "Particulars": first_val,
                "Debit": debit,
                "Credit": credit,
                "Net Amount": net
            })
            
        return pd.DataFrame(records) if records else df
