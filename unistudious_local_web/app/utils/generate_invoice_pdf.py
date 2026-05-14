"""
Invoice PDF Generator
Generates invoice PDFs matching the Piuma Academy template layout.

Flask usage:
    from generate_invoice_pdf import generate_invoice_pdf
    from flask import send_file
    import io

    @payment_bp.route('/api/download_invoice/<int:invoice_id>', methods=['GET'])
    def download_invoice(invoice_id):
        # fetch invoice data from DB ...
        invoice = {
            "invoice_number": "6a02f4fd02b89",
            "created_at": "May 12, 2026",
            "from_name": "piuma academy elearning math",
            "from_address": "123 rue de la république hammam lif",
            "from_phone": "28037571",
            "to_name": "hedi",
            "to_address": "15 rue monji slim hammam lif",
            "to_phone": "97705610",
            "to_email": "hedi.laater@gmail.com",
            "order_id": "4664",
            "order_type": "Year",
            "description": "2026",
            "status": "Paid",
            "price": "250.00",
            "total_amount": "250.00",
            "agent_name": "Mkaissi khalil",
            "agent_phone": "28037571",
            "agent_email": "khalilmkaissi@gmail.com",
        }
        pdf_bytes = generate_invoice_pdf(invoice)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"invoice_{invoice_id}.pdf"
        )
"""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER


# ── Colour palette (matches the PDF) ──────────────────────────────────────────
PURPLE      = colors.HexColor("#4B0082")   # header / accent
LIGHT_GRAY  = colors.HexColor("#F5F5F5")   # table header bg
DARK_TEXT   = colors.HexColor("#333333")
MID_TEXT    = colors.HexColor("#555555")
LIGHT_TEXT  = colors.HexColor("#888888")
WHITE       = colors.white


def _styles():
    """Return a dict of named ParagraphStyles."""
    base = dict(fontName="Helvetica", textColor=DARK_TEXT, leading=14)

    return {
        "title": ParagraphStyle(
            "title", fontSize=22, fontName="Helvetica-Bold",
            textColor=DARK_TEXT, alignment=TA_RIGHT, leading=28
        ),
        "meta_right": ParagraphStyle(
            "meta_right", fontSize=9, alignment=TA_RIGHT,
            textColor=MID_TEXT, leading=13, **{k: v for k, v in base.items()
                                                if k not in ("textColor", "leading")}
        ),
        "section_label": ParagraphStyle(
            "section_label", fontSize=9, fontName="Helvetica-Bold",
            textColor=DARK_TEXT, leading=14
        ),
        "body": ParagraphStyle(
            "body", fontSize=9, fontName="Helvetica",
            textColor=MID_TEXT, leading=13
        ),
        "bold_body": ParagraphStyle(
            "bold_body", fontSize=9, fontName="Helvetica-Bold",
            textColor=DARK_TEXT, leading=13
        ),
        "footer": ParagraphStyle(
            "footer", fontSize=8, fontName="Helvetica",
            textColor=LIGHT_TEXT, alignment=TA_CENTER, leading=12
        ),
        "total_label": ParagraphStyle(
            "total_label", fontSize=10, fontName="Helvetica-Bold",
            textColor=DARK_TEXT, alignment=TA_RIGHT, leading=14
        ),
        "total_value": ParagraphStyle(
            "total_value", fontSize=10, fontName="Helvetica-Bold",
            textColor=DARK_TEXT, alignment=TA_RIGHT, leading=14
        ),
    }


def generate_invoice_pdf(invoice: dict) -> bytes:
    """
    Build an invoice PDF and return it as bytes.

    Expected keys in `invoice`:
        invoice_number, created_at,
        from_name, from_address, from_phone,
        to_name, to_address, to_phone, to_email,
        order_id, order_type, description, status, price,
        total_amount,
        agent_name, agent_phone, agent_email
    """
    buf = io.BytesIO()
    PAGE_W, PAGE_H = A4
    MARGIN = 20 * mm

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )

    s = _styles()
    story = []
    usable_w = PAGE_W - 2 * MARGIN

    # ── 1. HEADER: logo placeholder (left) + "Invoice" title (right) ──────────
    logo_cell = Paragraph(
        "<font color='#4B0082' size='14'><b>Piuma<br/>Academy</b></font>",
        ParagraphStyle("logo", fontSize=14, fontName="Helvetica-Bold",
                       textColor=PURPLE, leading=18)
    )
    title_cell = Paragraph("Invoice", s["title"])

    header_table = Table(
        [[logo_cell, title_cell]],
        colWidths=[usable_w * 0.5, usable_w * 0.5]
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4 * mm))

    # ── 2. Invoice meta (number + date) — right-aligned ───────────────────────
    meta = Paragraph(
        f"Invoice #: {invoice.get('invoice_number', '')}<br/>"
        f"Created: {invoice.get('created_at', '')}",
        s["meta_right"]
    )
    meta_table = Table([[meta]], colWidths=[usable_w])
    meta_table.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8 * mm))

    # ── 3. HR divider ─────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 6 * mm))

    # ── 4. FROM / TO block ────────────────────────────────────────────────────
    def address_block(label, name, address, phone, email=None):
        lines = [Paragraph(label, s["section_label"]),
                 Paragraph(name,    s["body"]),
                 Paragraph(address, s["body"]),
                 Paragraph(phone,   s["body"])]
        if email:
            lines.append(Paragraph(email, s["body"]))
        return lines

    from_block = address_block(
        "From:",
        invoice.get("from_name", ""),
        invoice.get("from_address", ""),
        invoice.get("from_phone", ""),
    )
    to_block = address_block(
        "To:",
        invoice.get("to_name", ""),
        invoice.get("to_address", ""),
        invoice.get("to_phone", ""),
        invoice.get("to_email", ""),
    )

    # Pad both columns to the same row count
    max_rows = max(len(from_block), len(to_block))
    from_block += [Paragraph("", s["body"])] * (max_rows - len(from_block))
    to_block   += [Paragraph("", s["body"])] * (max_rows - len(to_block))

    # Right-align the "To" column paragraphs
    to_block_right = []
    for p in to_block:
        p.style = ParagraphStyle(
            p.style.name + "_r", parent=p.style, alignment=TA_RIGHT
        )
        to_block_right.append(p)

    addr_data = [[f, t] for f, t in zip(from_block, to_block_right)]
    addr_table = Table(addr_data,
                       colWidths=[usable_w * 0.5, usable_w * 0.5])
    addr_table.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 1),
    ]))
    story.append(addr_table)
    story.append(Spacer(1, 8 * mm))

    # ── 5. Items table ────────────────────────────────────────────────────────
    col_widths = [
        usable_w * 0.15,   # Order Id
        usable_w * 0.15,   # Type
        usable_w * 0.38,   # Description
        usable_w * 0.17,   # Status
        usable_w * 0.15,   # Price
    ]

    th = ParagraphStyle("th", fontSize=9, fontName="Helvetica-Bold",
                        textColor=DARK_TEXT, leading=13)
    td = ParagraphStyle("td", fontSize=9, fontName="Helvetica",
                        textColor=MID_TEXT,  leading=13)
    td_right = ParagraphStyle("td_r", fontSize=9, fontName="Helvetica",
                               textColor=MID_TEXT, alignment=TA_RIGHT, leading=13)
    th_right = ParagraphStyle("th_r", fontSize=9, fontName="Helvetica-Bold",
                               textColor=DARK_TEXT, alignment=TA_RIGHT, leading=13)

    items_data = [
        # Header row
        [Paragraph("Order Id",    th),
         Paragraph("Type",        th),
         Paragraph("Description", th),
         Paragraph("Status",      th),
         Paragraph("Price",       th_right)],
        # Data row
        [Paragraph(str(invoice.get("order_id",    "")), td),
         Paragraph(str(invoice.get("order_type",  "")), td),
         Paragraph(str(invoice.get("description", "")), td),
         Paragraph(str(invoice.get("status",      "")), td),
         Paragraph(str(invoice.get("price",       "")), td_right)],
    ]

    items_table = Table(items_data, colWidths=col_widths,
                        repeatRows=1)
    items_table.setStyle(TableStyle([
        # Header bg
        ("BACKGROUND",   (0, 0), (-1, 0), LIGHT_GRAY),
        ("LINEBELOW",    (0, 0), (-1, 0), 0.5, colors.HexColor("#DDDDDD")),
        # All cells
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        # Row separator
        ("LINEBELOW",    (0, 1), (-1, -1), 0.3, colors.HexColor("#EEEEEE")),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 4 * mm))

    # ── 6. Total row ──────────────────────────────────────────────────────────
    total_data = [[
        Paragraph("", s["body"]),
        Paragraph(f"Total: {invoice.get('total_amount', '0.00')}", s["total_label"])
    ]]
    total_table = Table(total_data,
                        colWidths=[usable_w * 0.6, usable_w * 0.4])
    total_table.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("LINEABOVE",    (0, 0), (-1, 0), 0.5, colors.HexColor("#DDDDDD")),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 10 * mm))

    # ── 7. Agent contact block ────────────────────────────────────────────────
    story.append(Paragraph("Agent Contact Information:", s["bold_body"]))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(f"Name: {invoice.get('agent_name', '')}",  s["body"]))
    story.append(Paragraph(f"Phone: {invoice.get('agent_phone', '')}", s["body"]))
    story.append(Paragraph(f"Email: {invoice.get('agent_email', '')}", s["body"]))
    story.append(Spacer(1, 10 * mm))

    # ── 8. Signature block ────────────────────────────────────────────────────
    story.append(Paragraph("Signature:", s["bold_body"]))
    story.append(Spacer(1, 15 * mm))   # blank space for handwritten signature

    # ── 9. Footer ─────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        "Thank you for your business! Please make payment by the due date.",
        s["footer"]
    ))
    story.append(Paragraph(
        f"If you have any questions, contact us at "
        f"{invoice.get('agent_phone', '')} or {invoice.get('agent_email', '')}",
        s["footer"]
    ))

    doc.build(story)
    return buf.getvalue()

