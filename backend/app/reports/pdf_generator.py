import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from typing import Dict, Any, Optional

def fmt(val: Any, currency_symbol: str = "$") -> str:
    if val is None:
        return ""
    try:
        n = float(val)
        is_neg = n < 0
        abs_n = abs(n)
        formatted = f"{abs_n:,.0f}"
        sym_str = f"{currency_symbol} " if currency_symbol and not currency_symbol.endswith(" ") and len(currency_symbol) > 1 else currency_symbol
        return f"({sym_str}{formatted})" if is_neg else f"{sym_str}{formatted}"
    except (ValueError, TypeError):
        return str(val)

def generate_pdf_report(
    company_name: str, 
    statements: Dict[str, Any], 
    ratios: Dict[str, Any], 
    corp_fin: Dict[str, Any], 
    ai_reports: Dict[str, Any],
    currency: str = "USD",
    audit_report: Optional[Dict[str, Any]] = None
) -> bytes:
    from app.engine.currency_engine import SUPPORTED_CURRENCIES
    curr_upper = (currency or "USD").upper()
    if curr_upper == "NOT_DETERMINED":
        sym = ""
    elif curr_upper == "INR":
        sym = "INR "  # Font-safe glyph for ReportLab PDF engines to prevent □/■
    elif curr_upper in ["USD", "AUD", "CAD", "SGD"]:
        sym = "$"
    elif curr_upper == "GBP":
        sym = "£"
    elif curr_upper == "EUR":
        sym = "€"
    elif curr_upper in ["JPY", "CNY"]:
        sym = "¥"
    elif curr_upper in ["AED", "CHF"]:
        sym = f"{curr_upper} "
    else:
        curr_info = SUPPORTED_CURRENCIES.get(curr_upper, {"symbol": "$"})
        sym = curr_info.get("symbol", "$")
        if sym == "₹":
            sym = "INR "

    if audit_report is None:
        from app.engine.auditor_engine import perform_full_financial_audit
        audit_report = perform_full_financial_audit(statements, ratios, currency_symbol=sym)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        alignment=0,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475569'),
        spaceAfter=10
    )

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0369A1'),
        spaceBefore=8,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=5
    )

    story = []

    # Cover Header
    story.append(Paragraph(f"Captrix AI — Statutory Financial Audit & Intelligence Report", title_style))
    story.append(Paragraph(f"<b>Engagement Target:</b> {company_name} | <b>Audit Date:</b> {datetime.datetime.now().strftime('%B %d, %Y')} | <b>Standards:</b> ISA / US GAAS", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0284C7"), spaceAfter=10))

    # 1. Official Auditor's Opinion Certificate Card
    opinion_obj = audit_report.get("auditor_opinion", {})
    op_type = opinion_obj.get("opinion_type", "UNQUALIFIED_OPINION")
    op_title = opinion_obj.get("title", "Independent Auditor's Report")
    op_summary = opinion_obj.get("summary", "")

    if op_type == "UNQUALIFIED_OPINION":
        op_bg = "#DCFCE7"
        op_border = "#16A34A"
        op_tag = "CLEAN BILL OF HEALTH"
    elif op_type == "QUALIFIED_OPINION":
        op_bg = "#FEF3C7"
        op_border = "#D97706"
        op_tag = "QUALIFIED WITH EXCEPTIONS"
    elif op_type in ["DISCLAIMER_OF_OPINION", "INSUFFICIENT_EVIDENCE"]:
        op_bg = "#F1F5F9"
        op_border = "#64748B"
        op_tag = "EVIDENCE LIMITATION / INSUFFICIENT EVIDENCE"
    else:
        op_bg = "#FFE4E6"
        op_border = "#E11D48"
        op_tag = "MATERIAL MISSTATEMENT"

    op_card_data = [
        [Paragraph(f"<b>AUDITOR'S OPINION: {op_title.upper()}</b>", ParagraphStyle('OpH', parent=body_style, fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor(op_border)))],
        [Paragraph(f"<b>Classification:</b> {op_tag} | <b>Standards:</b> ISA 700/705 | <b>Sign-Off:</b> {opinion_obj.get('auditor_signature', 'Captrix AI-Assisted Automated Audit Intelligence (Requires Human Auditor Sign-Off)')}", body_style)],
        [Paragraph(op_summary, body_style)]
    ]
    t_op = Table(op_card_data, colWidths=[540])
    t_op.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(op_bg)),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor(op_border)),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_op)
    story.append(Spacer(1, 8))

    # 2. Audit Planning & Materiality Summary
    planning_obj = audit_report.get("audit_planning", {})
    if planning_obj:
        story.append(Paragraph("Audit Planning & Materiality Benchmarks (ISA 320)", h2_style))
        mat_statement = planning_obj.get("materiality_statement", "")
        story.append(Paragraph(mat_statement, body_style))
        
        base_val = planning_obj.get("benchmark_base", planning_obj.get("base_amount", 0))
        pm_val = planning_obj.get("planning_materiality", 0)
        perf_val = planning_obj.get("performance_materiality", 0)
        triv_val = planning_obj.get("clearly_trivial_threshold", 0)

        mat_table_data = [
            ["Materiality Benchmark", "Base Value / Source Reference", "Threshold Amount", "Audit Action Threshold"],
            ["Planning Materiality (1.0%)", f"Total Revenue ({fmt(base_val, sym)})", fmt(pm_val, sym), "Errors above PM require evaluation / investigation."],
            ["Performance Materiality (75%)", f"Planning Materiality ({fmt(pm_val, sym)})", fmt(perf_val, sym), "Substantive sample adjustment threshold"],
            ["Clearly Trivial Limit (5%)", f"Planning Materiality ({fmt(pm_val, sym)})", fmt(triv_val, sym), "Variances < Limit deemed de minimis"]
        ]
        t_mat = Table(mat_table_data, colWidths=[150, 150, 90, 150])
        t_mat.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284C7')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7.5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ALIGN', (1,0), (2,-1), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_mat)
        story.append(Spacer(1, 10))

    # 3. Dynamic Lead Schedules (WP-A to WP-H) Summary
    lead_scheds = audit_report.get("lead_schedules", [])
    if lead_scheds:
        story.append(Paragraph("Working Paper Lead Schedules Index", h2_style))
        sched_rows = [["WP Ref", "Schedule Title", "Category", "Audited Total", "Audit Status"]]
        for ls in lead_scheds:
            sched_rows.append([
                ls.get("schedule_ref", "-"),
                ls.get("title", "-"),
                ls.get("category", "-"),
                fmt(ls.get("total_amount"), sym),
                ls.get("status", "PASS")
            ])
        t_sched = Table(sched_rows, colWidths=[60, 240, 90, 90, 60])
        t_sched.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7.5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('ALIGN', (3,0), (3,-1), 'RIGHT'),
            ('ALIGN', (4,0), (4,-1), 'CENTER'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t_sched)
        story.append(Spacer(1, 10))

    # 4. Income Statement (Source-Grounded Dynamic Generation)
    inc = statements.get("income_statement", {})
    inc_items = []
    if inc.get("revenue_from_operations") is not None:
        inc_items.append(["Revenue from Operations", fmt(inc.get("revenue_from_operations"), sym)])
    if inc.get("other_operating_income") is not None and inc.get("other_operating_income") > 0:
        inc_items.append(["Other Operating Income", fmt(inc.get("other_operating_income"), sym)])
    elif inc.get("other_income") is not None and inc.get("other_income") > 0:
        inc_items.append(["Other Operating Income", fmt(inc.get("other_income"), sym)])
    if inc.get("total_revenue_and_income") is not None and inc.get("other_operating_income") and inc.get("other_operating_income") > 0:
        inc_items.append(["Total Revenue & Operating Income", fmt(inc.get("total_revenue_and_income"), sym)])
    if inc.get("cost_of_goods_sold") is not None:
        inc_items.append(["Cost of Goods Sold (COGS)", f"({fmt(abs(inc.get('cost_of_goods_sold')), sym)})"])
    if inc.get("gross_profit") is not None:
        inc_items.append(["Gross Profit", fmt(inc.get("gross_profit"), sym)])
    if inc.get("operating_expenses") is not None and inc.get("operating_expenses") > 0:
        inc_items.append(["Administrative & Operating Expenses", f"({fmt(abs(inc.get('operating_expenses')), sym)})"])
    if inc.get("profit_from_operations") is not None:
        inc_items.append(["Profit from Operations", fmt(inc.get("profit_from_operations"), sym)])
    elif inc.get("ebitda") is not None:
        inc_items.append(["Profit from Operations", fmt(inc.get("ebitda"), sym)])
    if inc.get("depreciation_amortization") is not None and inc.get("depreciation_amortization") > 0:
        inc_items.append(["Depreciation & Amortization", f"({fmt(abs(inc.get('depreciation_amortization')), sym)})"])
    if inc.get("finance_income") is not None and inc.get("finance_income") > 0:
        inc_items.append(["Interest Received (Finance Income)", fmt(inc.get("finance_income"), sym)])
    elif inc.get("interest_income") is not None and inc.get("interest_income") > 0:
        inc_items.append(["Interest Received (Finance Income)", fmt(inc.get("interest_income"), sym)])
    if inc.get("finance_cost") is not None and inc.get("finance_cost") > 0:
        inc_items.append(["Finance Costs (Interest Expense)", f"({fmt(abs(inc.get('finance_cost')), sym)})"])
    elif inc.get("interest_expense") is not None and inc.get("interest_expense") > 0:
        inc_items.append(["Finance Costs (Interest Expense)", f"({fmt(abs(inc.get('interest_expense')), sym)})"])
    if inc.get("pbt") is not None:
        inc_items.append(["Profit Before Taxation (PBT)", fmt(inc.get("pbt"), sym)])
    elif inc.get("ebt") is not None:
        inc_items.append(["Profit Before Taxation (PBT)", fmt(inc.get("ebt"), sym)])
    if inc.get("tax_expense") is not None and inc.get("tax_expense") > 0:
        inc_items.append(["Taxation Expense", f"({fmt(abs(inc.get('tax_expense')), sym)})"])
    if inc.get("net_profit") is not None:
        inc_items.append(["NET PROFIT FOR THE YEAR", fmt(inc.get("net_profit"), sym)])
    elif inc.get("net_income") is not None:
        inc_items.append(["NET PROFIT FOR THE YEAR", fmt(inc.get("net_income"), sym)])

    if inc_items:
        story.append(Paragraph("Income Statement (Audited Provenance)", h2_style))
        inc_table_data = [["Line Item", f"Amount ({currency})"]] + inc_items
        t_inc = Table(inc_table_data, colWidths=[360, 180])
        t_inc.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#BAE6FD')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#93C5FD')),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_inc)
        story.append(Spacer(1, 10))

    # 5. Dynamic 2-Column Balance Sheet Layout
    bs = statements.get("balance_sheet", {})
    if bs and bs.get("status") != "NOT_REPORTED_IN_SOURCE":
        ca = bs.get("current_assets", {})
        ppe = bs.get("property_plant_equipment", {})
        intangibles = bs.get("intangible_assets", {})
        cl = bs.get("current_liabilities", {})
        ltl = bs.get("long_term_liabilities", {})
        eq = bs.get("equity", {})

        left_column_items = ["<b>ASSETS</b>"]
        ca_subitems = []
        if ca.get("cash") is not None:
            ca_subitems.append(f"&nbsp;&nbsp;Cash: {fmt(ca.get('cash'), sym)}")
        if ca.get("petty_cash") is not None:
            ca_subitems.append(f"&nbsp;&nbsp;Petty cash: {fmt(ca.get('petty_cash'), sym)}")
        if ca.get("temporary_investments") is not None:
            ca_subitems.append(f"&nbsp;&nbsp;Temporary Investment: {fmt(ca.get('temporary_investments'), sym)}")
        if ca.get("accounts_receivable") is not None:
            ca_subitems.append(f"&nbsp;&nbsp;Accounts receivable: {fmt(ca.get('accounts_receivable'), sym)}")
        if ca.get("inventory") is not None:
            ca_subitems.append(f"&nbsp;&nbsp;Inventory: {fmt(ca.get('inventory'), sym)}")
        if ca.get("supplies") is not None:
            ca_subitems.append(f"&nbsp;&nbsp;Supply: {fmt(ca.get('supplies'), sym)}")
        if ca.get("prepaid_insurance") is not None:
            ca_subitems.append(f"&nbsp;&nbsp;Prepaid Insurance: {fmt(ca.get('prepaid_insurance'), sym)}")

        if ca_subitems:
            left_column_items.append("<b>Current assets</b>")
            left_column_items.extend(ca_subitems)
            if ca.get("total_current_assets") is not None:
                left_column_items.append(f"<b>Total current assets: {fmt(ca.get('total_current_assets'), sym)}</b>")

        if bs.get("investment") is not None:
            left_column_items.append(f"<b>Investment: {fmt(bs.get('investment'), sym)}</b>")

        ppe_subitems = []
        if ppe.get("land") is not None:
            ppe_subitems.append(f"&nbsp;&nbsp;Land: {fmt(ppe.get('land'), sym)}")
        if ppe.get("buildings") is not None:
            ppe_subitems.append(f"&nbsp;&nbsp;Buildings: {fmt(ppe.get('buildings'), sym)}")
        if ppe.get("equipment") is not None:
            ppe_subitems.append(f"&nbsp;&nbsp;Equipment: {fmt(ppe.get('equipment'), sym)}")
        if ppe.get("accumulated_depreciation") is not None:
            ppe_subitems.append(f"&nbsp;&nbsp;Accumulated depreciation: ({fmt(abs(float(ppe.get('accumulated_depreciation'))), sym)})")

        if ppe_subitems:
            left_column_items.append("<b>Property plant and equipment</b>")
            left_column_items.extend(ppe_subitems)
            if ppe.get("net_property_plant_equipment") is not None:
                left_column_items.append(f"<b>Prop, plant and equip-net: {fmt(ppe.get('net_property_plant_equipment'), sym)}</b>")

        intangible_subitems = []
        if intangibles.get("goodwill") is not None:
            intangible_subitems.append(f"&nbsp;&nbsp;Goodwill: {fmt(intangibles.get('goodwill'), sym)}")
        if intangibles.get("trade_names") is not None:
            intangible_subitems.append(f"&nbsp;&nbsp;Trade names: {fmt(intangibles.get('trade_names'), sym)}")

        if intangible_subitems:
            left_column_items.append("<b>Intangible assets</b>")
            left_column_items.extend(intangible_subitems)
            if intangibles.get("total_intangible_assets") is not None:
                left_column_items.append(f"<b>Total intangible assets: {fmt(intangibles.get('total_intangible_assets'), sym)}</b>")

        if bs.get("other_assets") is not None:
            left_column_items.append(f"<b>Other assets: {fmt(bs.get('other_assets'), sym)}</b>")

        if bs.get("total_assets") is not None:
            left_column_items.append(f"<b>TOTAL ASSETS: {fmt(bs.get('total_assets'), sym)}</b>")

        # Right Column: Liabilities & Equity
        right_column_items = ["<b>LIABILITIES & EQUITY</b>"]
        cl_subitems = []
        if cl.get("notes_payable") is not None:
            cl_subitems.append(f"&nbsp;&nbsp;Notes payable: {fmt(cl.get('notes_payable'), sym)}")
        if cl.get("accounts_payable") is not None:
            cl_subitems.append(f"&nbsp;&nbsp;Accounts payable: {fmt(cl.get('accounts_payable'), sym)}")
        if cl.get("wages_payable") is not None:
            cl_subitems.append(f"&nbsp;&nbsp;Wages payable: {fmt(cl.get('wages_payable'), sym)}")
        if cl.get("tax_payable") is not None:
            cl_subitems.append(f"&nbsp;&nbsp;Tax payable: {fmt(cl.get('tax_payable'), sym)}")

        if cl_subitems:
            right_column_items.append("<b>Current liabilities</b>")
            right_column_items.extend(cl_subitems)
            if cl.get("total_current_liabilities") is not None:
                right_column_items.append(f"<b>Total current liabilities: {fmt(cl.get('total_current_liabilities'), sym)}</b>")

        ltl_subitems = []
        if ltl.get("notes_payable_lt") is not None:
            ltl_subitems.append(f"&nbsp;&nbsp;Notes payable: {fmt(ltl.get('notes_payable_lt'), sym)}")
        if ltl.get("bonds_payable") is not None:
            ltl_subitems.append(f"&nbsp;&nbsp;Bonds payable: {fmt(ltl.get('bonds_payable'), sym)}")

        if ltl_subitems:
            right_column_items.append("<b>Long-term liabilities</b>")
            right_column_items.extend(ltl_subitems)
            if ltl.get("total_long_term_liabilities") is not None:
                right_column_items.append(f"<b>Total long term liabilities: {fmt(ltl.get('total_long_term_liabilities'), sym)}</b>")

        if bs.get("total_liabilities") is not None and (cl_subitems or ltl_subitems):
            right_column_items.append(f"<b>Total liabilities: {fmt(bs.get('total_liabilities'), sym)}</b>")

        eq_subitems = []
        if eq.get("common_stock") is not None or eq.get("share_capital") is not None:
            eq_subitems.append(f"&nbsp;&nbsp;Share capital: {fmt(eq.get('common_stock') or eq.get('share_capital'), sym)}")
        if eq.get("retained_earnings") is not None or eq.get("reserves_and_retained_earnings") is not None:
            eq_subitems.append(f"&nbsp;&nbsp;Retained earnings: {fmt(eq.get('retained_earnings') or eq.get('reserves_and_retained_earnings'), sym)}")
        if eq.get("treasury_stock") is not None:
            eq_subitems.append(f"&nbsp;&nbsp;Less: Treasury stock: ({fmt(abs(float(eq.get('treasury_stock'))), sym)})")

        if eq_subitems:
            right_column_items.append("<b>Owner's Equity</b>")
            right_column_items.extend(eq_subitems)
            if eq.get("total_equity") is not None:
                right_column_items.append(f"<b>Total owner's equity: {fmt(eq.get('total_equity'), sym)}</b>")

        if bs.get("total_liabilities_and_equity") is not None:
            right_column_items.append(f"<b>TOTAL LIABILITIES & EQUITY: {fmt(bs.get('total_liabilities_and_equity'), sym)}</b>")

        if len(left_column_items) > 1 or len(right_column_items) > 1:
            story.append(Paragraph("Balance Sheet (Verified Ledger Structure)", h2_style))
            bs_table_data = []
            max_len = max(len(left_column_items), len(right_column_items))
            
            bs_table_data.append([
                Paragraph("<b>ASSETS</b>", ParagraphStyle('H1', parent=body_style, fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0F172A'))),
                Paragraph("<b>LIABILITIES & EQUITY</b>", ParagraphStyle('H2', parent=body_style, fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0F172A')))
            ])

            for i in range(1, max_len):
                l_text = left_column_items[i] if i < len(left_column_items) else "&nbsp;"
                r_text = right_column_items[i] if i < len(right_column_items) else "&nbsp;"
                bs_table_data.append([
                    Paragraph(l_text, body_style),
                    Paragraph(r_text, body_style)
                ])

            t_bs = Table(bs_table_data, colWidths=[270, 270])
            t_bs.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,0), colors.HexColor('#BAE6FD')),
                ('BACKGROUND', (1,0), (1,0), colors.HexColor('#BAE6FD')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#93C5FD')),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('TOPPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t_bs)
            story.append(Spacer(1, 12))

    # Page Break for Management Letter & Exceptions
    story.append(PageBreak())

    # 6. Audit Exception Register & Management Letter
    mgmt_letter = audit_report.get("management_letter", [])
    if mgmt_letter:
        story.append(Paragraph("Management Letter — Internal Control Deficiencies & Recommendations", h2_style))
        from typing import List
        ml_rows: List[List[Any]] = [["Ref", "Audit Area", "Internal Control Finding", "Remediation Action Required"]]
        for ml in mgmt_letter:
            ml_rows.append([
                str(ml.get("ref", "EXC")),
                str(ml.get("area", "General")),
                Paragraph(str(ml.get("deficiency", "")), body_style),
                Paragraph(str(ml.get("recommendation", "")), body_style)
            ])
        t_ml = Table(ml_rows, colWidths=[55, 115, 185, 185])
        t_ml.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F59E0B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7.5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_ml)
        story.append(Spacer(1, 12))

    # 7. Ratios Table - Only Calculable Ratios
    ratio_rows = []
    for cat_name, cat_ratios in ratios.items():
        if isinstance(cat_ratios, dict):
            for r_key, r in cat_ratios.items():
                if isinstance(r, dict):
                    is_calc = r.get("is_calculable", True)
                    val = r.get("value")
                    stat = r.get("status")
                    if is_calc and val is not None and stat not in ["NOT_CALCULABLE", "DATA_MISSING", "N/A"]:
                        val_str = f"{val}{r.get('unit', '')}"
                        ratio_rows.append([cat_name.capitalize(), r.get('name', r_key), r.get('formula', '-'), val_str, stat])

    if ratio_rows:
        story.append(Paragraph("Financial Ratio Analysis & Audit Metrics", h2_style))
        ratio_data = [["Category", "Ratio Name", "Formula", "Value", "Status"]] + ratio_rows
        t_ratios = Table(ratio_data, colWidths=[80, 130, 170, 70, 70])
        t_ratios.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284C7')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ALIGN', (3,0), (3,-1), 'CENTER'),
            ('ALIGN', (4,0), (4,-1), 'CENTER'),
        ]))
        story.append(t_ratios)
        story.append(Spacer(1, 12))

    # 8. AI Recommendations (Evidence-Filtered)
    recs = ai_reports.get("recommendations", []) if isinstance(ai_reports, dict) else []
    if recs:
        story.append(Paragraph("Strategic Financial Governance & Executive Action Plan", h2_style))
        for rec in recs:
            if isinstance(rec, dict):
                prio = rec.get('priority', 'HIGH')
                ttl = rec.get('title', 'Recommendation')
                act = rec.get('action', rec.get('recommendation', ''))
                rec_text = f"<b>[{prio}] {ttl}:</b> {act}"
            else:
                rec_text = f"• {str(rec)}"
            story.append(Paragraph(rec_text, body_style))
            story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
