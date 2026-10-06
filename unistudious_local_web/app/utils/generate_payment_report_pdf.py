import io
import os
import re
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Flowable

try:
	import arabic_reshaper
	from bidi.algorithm import get_display
except ImportError:
	arabic_reshaper = None
	get_display = None

# ---------- Fonts (Arabic support) ----------
# Put Amiri-Regular.ttf and Amiri-Bold.ttf in app/utils/fonts/
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
FONT_REGULAR = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'

try:
	pdfmetrics.registerFont(TTFont('Amiri', os.path.join(FONT_DIR, 'Amiri-Regular.ttf')))
	pdfmetrics.registerFont(TTFont('Amiri-Bold', os.path.join(FONT_DIR, 'Amiri-Bold.ttf')))
	FONT_REGULAR = 'Amiri'
	FONT_BOLD = 'Amiri-Bold'
except Exception:
	pass

ARABIC_RE = re.compile(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]')

HEADER_BLUE = colors.HexColor('#007bff')
ZEBRA       = colors.HexColor('#f9f9f9')
ROW_LINE    = colors.HexColor('#dee2e6')
TEXT_COLOR  = colors.HexColor('#555555')

STATUS_COLORS = {
	'Paid':           colors.HexColor('#28a745'),
	'Pending':        colors.HexColor('#f5a014'),
	'Unpaid':         colors.HexColor('#dc3545'),
	'Cancelled':      colors.HexColor('#dc3545'),
	'Not Registered': colors.HexColor('#6c757d'),
}


class StatusBadge(Flowable):
	"""Rounded pill with white text, like the Bootstrap badge."""

	def __init__(self, text, color, font=FONT_BOLD, size=8.5):
		super().__init__()
		self.text = text
		self.color = color
		self.font = font
		self.size = size
		self.width = stringWidth(text, font, size) + 18
		self.height = 16

	def wrap(self, availWidth, availHeight):
		return self.width, self.height

	def draw(self):
		c = self.canv
		c.setFillColor(self.color)
		c.roundRect(0, 0, self.width, self.height, self.height / 2, fill=1, stroke=0)
		c.setFillColor(colors.white)
		c.setFont(self.font, self.size)
		c.drawCentredString(self.width / 2, 4.8, self.text)


def _shape(text):
	text = str(text or '')
	if arabic_reshaper and get_display and ARABIC_RE.search(text):
		return get_display(arabic_reshaper.reshape(text))
	return text


def _p(text, style):
	return Paragraph(escape(_shape(text)), style)


def _month_label(value):
	if not value:
		return 'N/A'
	value = str(value)
	try:
		return datetime.strptime(value[:10], '%Y-%m-%d').strftime('%B %Y')
	except ValueError:
		return value


def _student_label(full_name, virtual_name):
	name = full_name or ''
	if virtual_name is not None:
		return f"{name} ({virtual_name})"
	return name


def generate_payment_report_pdf(session, payments, from_interval, to_interval, statuses=None):
	buffer = io.BytesIO()
	doc = SimpleDocTemplate(
		buffer,
		pagesize=A4,
		leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30,
		title=f"Payments - {session['name']}",
	)

	styles = getSampleStyleSheet()
	title_style = ParagraphStyle('ReportTitle', parent=styles['Title'], fontName=FONT_BOLD, fontSize=20, spaceAfter=10, textColor=colors.HexColor('#333333'))
	h2_style    = ParagraphStyle('ReportH2', parent=styles['Heading2'], fontName=FONT_BOLD, fontSize=13, spaceBefore=6, spaceAfter=6, textColor=colors.HexColor('#333333'))
	info_style  = ParagraphStyle('ReportInfo', parent=styles['Normal'], fontName=FONT_REGULAR, fontSize=10, leading=14, textColor=TEXT_COLOR)
	cell_style  = ParagraphStyle('Cell', parent=styles['Normal'], fontName=FONT_REGULAR, fontSize=9.5, leading=12, textColor=TEXT_COLOR)
	head_style  = ParagraphStyle('Head', parent=cell_style, fontName=FONT_BOLD, fontSize=10, textColor=colors.white)

	cur = session.get('currency') or 'TND'
	all_status = (not statuses) or ('All Orders' in statuses)
	title = 'All Payment Details' if all_status else 'Payment Details'

	elements = [
		Paragraph(title, title_style),
		Paragraph('Session Information:', h2_style),
		Paragraph(f"<b>Session Name:</b> {escape(_shape(session['name']))}", info_style),
		Paragraph(f"<b>Price:</b> {session['price']:.2f} {escape(cur)}", info_style),
		Paragraph(f"<b>Start Date:</b> {session.get('start_date') or 'N/A'}", info_style),
		Paragraph(f"<b>End Date:</b> {session.get('end_date') or 'N/A'}", info_style),
		Spacer(1, 10),
		Paragraph('Payment History', h2_style),
	]

	data = [[
		Paragraph('#', head_style),
		Paragraph('Student', head_style),
		Paragraph('Payment<br/>Date', head_style),
		Paragraph('Amount', head_style),
		Paragraph('Status', head_style),
		Paragraph('Date<br/>Payment', head_style),
	]]

	for i, p in enumerate(payments, start=1):
		status_text = str(p['status'])
		badge = StatusBadge(status_text, STATUS_COLORS.get(status_text, colors.HexColor('#6c757d')))
		data.append([
			Paragraph(str(i), cell_style),
			_p(_student_label(p.get('full_name'), p.get('virtual_name')), cell_style),
			Paragraph(escape(_month_label(p.get('type_date'))), cell_style),
			Paragraph(f"{p['amount']:.2f} {escape(cur)}", cell_style),
			badge,
			Paragraph(p.get('date_payment') or 'N/A', cell_style),
		])

	table = Table(data, repeatRows=1, colWidths=[30, 175, 80, 75, 95, 80])
	table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), HEADER_BLUE),
		('LINEAFTER', (0, 0), (-2, 0), 0.5, colors.HexColor('#3d9bff')),
		('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, ZEBRA]),
		('LINEBELOW', (0, 1), (-1, -1), 0.5, ROW_LINE),
		('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
		('LEFTPADDING', (0, 0), (-1, -1), 8),
		('RIGHTPADDING', (0, 0), (-1, -1), 6),
		('TOPPADDING', (0, 0), (-1, -1), 8),
		('BOTTOMPADDING', (0, 0), (-1, -1), 8),
	]))
	elements.append(table)

	doc.build(elements)
	return buffer.getvalue()