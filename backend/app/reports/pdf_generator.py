import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from typing import Dict, Any

def fmt(val: Any) -> str:
    if val is None:
        return "$0"
    try:
        n = float(val)
        is_neg = n < 0
        abs_n = abs(n)
        formatted = f"{abs_n:,.0f}"
        return f"({formatted})" if is_neg else f"{formatted}"
    except (ValueError, TypeError):
        return str(val)

def generate_pdf_report(company_name: str, statements: Dict[str, Any], ratios: Dict[str, Any], corp_fin: Dict[str, Any], ai_reports: Dict[str, Any]) -> bytes:
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
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        alignment=0,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0369A1'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=6
    )

    story = []

    # Cover Header
    story.append(Paragraph(f"Captrix AI - Financial Intelligence & Audit Report", title_style))
    story.append(Paragraph(f"<b>Company Target:</b> {company_name} | <b>Report Date:</b> {datetime.datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0284C7"), spaceAfter=12))

    # Health Score Box
    from app.engine.quality_engine import calculate_financial_health_score
    health_obj = calculate_financial_health_score(statements, ratios, ai_reports.get("canonical_dataset"), ai_reports.get("quality_report"))
    score = health_obj["score"]
    score_color = "#16A34A" if score >= 75 else ("#D97706" if score >= 55 else "#DC2626")
    story.append(Paragraph(f"Overall Financial Health Score: <b><font color='{score_color}'>{score} / 100</font></b>", h2_style))
    story.append(Paragraph(ai_reports["executive_summary"], body_style))
    story.append(Spacer(1, 8))

    # DETAILED 2-COLUMN BALANCE SHEET & TRIAL BALANCE (Matching User Reference Layout)
    bs = statements.get("balance_sheet", {})
    ca = bs.get("current_assets", {})
    ppe = bs.get("property_plant_equipment", {})
    intangibles = bs.get("intangible_assets", {})
    cl = bs.get("current_liabilities", {})
    ltl = bs.get("long_term_liabilities", {})
    eq = bs.get("equity", {})

    story.append(Paragraph("Structured Balance Sheet & Assets / Liabilities Audit Layout", h2_style))
    
    # 2-Column Side-by-Side Accounting Layout Table
    left_column_items = [
        "<b>ASSETS</b>",
        "<b>Current assets</b>",
        f"&nbsp;&nbsp;Cash: ${fmt(ca.get('cash'))}",
        f"&nbsp;&nbsp;Petty cash: {fmt(ca.get('petty_cash'))}",
        f"&nbsp;&nbsp;Temporary Investment: {fmt(ca.get('temporary_investments'))}",
        f"&nbsp;&nbsp;Accounts receivable: {fmt(ca.get('accounts_receivable'))}",
        f"&nbsp;&nbsp;Inventory: {fmt(ca.get('inventory'))}",
        f"&nbsp;&nbsp;Supply: {fmt(ca.get('supplies'))}",
        f"&nbsp;&nbsp;Prepaid Insurance: {fmt(ca.get('prepaid_insurance'))}",
        f"<b>Total current assets: {fmt(ca.get('total_current_assets'))}</b>",
        f"<b>Investment: {fmt(bs.get('investment'))}</b>",
        "<b>Property plant and equipment</b>",
        f"&nbsp;&nbsp;Land: {fmt(ppe.get('land'))}",
        f"&nbsp;&nbsp;Land improvements: {fmt(ppe.get('land_improvements'))}",
        f"&nbsp;&nbsp;Buildings: {fmt(ppe.get('buildings'))}",
        f"&nbsp;&nbsp;Equipment: {fmt(ppe.get('equipment'))}",
        f"&nbsp;&nbsp;Accumulated depreciation: ({fmt(abs(float(ppe.get('accumulated_depreciation', 0))))})",
        f"<b>Prop, plant and equip-net: {fmt(ppe.get('net_property_plant_equipment'))}</b>",
        "<b>Intangible assets</b>",
        f"&nbsp;&nbsp;Goodwill: {fmt(intangibles.get('goodwill'))}",
        f"&nbsp;&nbsp;Trade names: {fmt(intangibles.get('trade_names'))}",
        f"<b>Total intangible assets: {fmt(intangibles.get('total_intangible_assets'))}</b>",
        f"<b>Other assets: {fmt(bs.get('other_assets'))}</b>",
        f"<b>TOTAL ASSETS: ${fmt(bs.get('total_assets'))}</b>"
    ]

    right_column_items = [
        "<b>LIABILITIES</b>",
        "<b>Current liabilities</b>",
        f"&nbsp;&nbsp;Notes payable: ${fmt(cl.get('notes_payable'))}",
        f"&nbsp;&nbsp;Accounts payable: {fmt(cl.get('accounts_payable'))}",
        f"&nbsp;&nbsp;Wages payable: {fmt(cl.get('wages_payable'))}",
        f"&nbsp;&nbsp;Interest payable: {fmt(cl.get('interest_payable'))}",
        f"&nbsp;&nbsp;Tax payable: {fmt(cl.get('tax_payable'))}",
        f"&nbsp;&nbsp;Unearned revenue: {fmt(cl.get('unearned_revenue'))}",
        f"<b>Total current liabilities: {fmt(cl.get('total_current_liabilities'))}</b>",
        "<b>Long-term liabilities</b>",
        f"&nbsp;&nbsp;Notes payable: {fmt(ltl.get('notes_payable_lt'))}",
        f"&nbsp;&nbsp;Bonds payable: {fmt(ltl.get('bonds_payable'))}",
        f"<b>Total long term liabilities: {fmt(ltl.get('total_long_term_liabilities'))}</b>",
        f"<b>Total liabilities: {fmt(bs.get('total_liabilities'))}</b>",
        "<b>Owner's Equity</b>",
        f"&nbsp;&nbsp;Common stock: {fmt(eq.get('common_stock'))}",
        f"&nbsp;&nbsp;Retained earnings: {fmt(eq.get('retained_earnings'))}",
        f"&nbsp;&nbsp;Less: Treasury stock: ({fmt(abs(float(eq.get('treasury_stock', 0))))})",
        f"<b>Total owner's equity: {fmt(eq.get('total_equity'))}</b>",
        "&nbsp;",
        "&nbsp;",
        "&nbsp;",
        "&nbsp;",
        f"<b>TOTAL LIABILITIES & EQUITY: ${fmt(bs.get('total_liabilities_and_equity'))}</b>"
    ]

    # Convert to Paragraph items for ReportLab table
    bs_table_data = []
    max_len = max(len(left_column_items), len(right_column_items))
    
    # Table Header Row
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

    t_bs = Table(bs_table_data, colWidths=[260, 260])
    t_bs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#BAE6FD')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#BAE6FD')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#93C5FD')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0,-1), (0,-1), colors.HexColor('#BAE6FD')),
        ('BACKGROUND', (1,-1), (1,-1), colors.HexColor('#BAE6FD')),
    ]))
    story.append(t_bs)
    story.append(Spacer(1, 14))

    # Page Break for Ratio Analysis & Strategic Insights
    story.append(PageBreak())

    # Ratios Table
    story.append(Paragraph("Financial Ratio Analysis & Audit Metrics", h2_style))
    ratio_data = [["Category", "Ratio Name", "Formula", "Value", "Status"]]
    
    for cat_name, cat_ratios in ratios.items():
        for r_key, r in cat_ratios.items():
            val_str = f"{r['value']}{r.get('unit', '')}"
            ratio_data.append([cat_name.capitalize(), r['name'], r['formula'], val_str, r['status']])

    t_ratios = Table(ratio_data, colWidths=[80, 130, 170, 70, 70])
    t_ratios.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284C7')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ALIGN', (3,0), (3,-1), 'CENTER'),
        ('ALIGN', (4,0), (4,-1), 'CENTER'),
    ]))
    story.append(t_ratios)
    story.append(Spacer(1, 12))

    # Corporate Finance Section
    story.append(Paragraph("Corporate Finance & WACC Valuation", h2_style))
    cap_bud = corp_fin.get('capital_budgeting', {}) if isinstance(corp_fin, dict) else {}
    cap_struct = corp_fin.get('capital_structure', {}) if isinstance(corp_fin, dict) else {}
    work_cap = corp_fin.get('working_capital_cycle', {}) if isinstance(corp_fin, dict) else {}

    npv_val = cap_bud.get('npv', 0)
    irr_val = cap_bud.get('irr', 0)
    disc_rate = cap_bud.get('discount_rate', 10)
    verdict = cap_bud.get('verdict', 'Feasible')
    wacc_val = cap_struct.get('wacc', 0)
    ccc_val = work_cap.get('cash_conversion_cycle', 0)

    cf_data = [
        ["Metric", "Value", "Benchmark / Audit Note"],
        ["Net Present Value (NPV)", f"${npv_val:,.2f}" if isinstance(npv_val, (int, float)) else str(npv_val), str(verdict)],
        ["Internal Rate of Return (IRR)", f"{irr_val:.1f}%" if isinstance(irr_val, (int, float)) else str(irr_val), f"Hurdle Rate: {disc_rate}%"],
        ["Weighted Avg Cost of Capital (WACC)", f"{wacc_val:.1f}%" if isinstance(wacc_val, (int, float)) else str(wacc_val), "Weighted Cost of Capital"],
        ["Cash Conversion Cycle (CCC)", f"{ccc_val} days", "Operational Cash Efficiency"]
    ]
    t_cf = Table(cf_data, colWidths=[180, 140, 200])
    t_cf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_cf)
    story.append(Spacer(1, 12))

    # AI Recommendations
    story.append(Paragraph("Strategic AI Recommendations & Executive Action Plan", h2_style))
    recs = ai_reports.get("recommendations", []) if isinstance(ai_reports, dict) else []
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
