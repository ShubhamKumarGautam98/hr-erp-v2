"""
pdf_generator.py
================
Generates payslip PDFs using ReportLab.
Completely decoupled from Flask routes — just takes data, returns bytes.
"""
import io
import calendar
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm

# ── Color palette ─────────────────────────────────────────────────────────────
DARK_BLUE  = colors.HexColor('#1a237e')
MID_BLUE   = colors.HexColor('#2980b9')
LIGHT_BLUE = colors.HexColor('#eaf0fb')
GREEN      = colors.HexColor('#27ae60')
LIGHT_GREEN= colors.HexColor('#e8f5e9')
RED        = colors.HexColor('#e74c3c')
GREY_BG    = colors.HexColor('#f5f7fc')
BORDER     = colors.HexColor('#cccccc')


def generate_payslip_pdf(payroll, employee) -> bytes:
    """
    Accepts a Payroll ORM object and an Employee ORM object.
    Returns the PDF as raw bytes.
    """
    buffer     = io.BytesIO()
    month_name = calendar.month_name[payroll.month]

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.2*cm, bottomMargin=1.2*cm,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
    )

    styles = getSampleStyleSheet()
    elements = []

    # ── Header ────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'],
        fontSize=20, textColor=DARK_BLUE, spaceAfter=2,
    )
    sub_style = ParagraphStyle(
        'Sub', parent=styles['Normal'],
        fontSize=10, textColor=colors.grey,
    )
    elements.append(Paragraph("SALARY SLIP", title_style))
    elements.append(Paragraph(f"{month_name} {payroll.year}", sub_style))
    elements.append(Spacer(1, 0.4*cm))

    # ── Employee info grid ────────────────────────────────────────────
    info_data = [
        ['Employee Name',  employee.full_name,
         'Employee Code',  employee.employee_code],
        ['Designation',
         employee.designation.name if employee.designation else '—',
         'Department',
         employee.department.name  if employee.department  else '—'],
        ['UAN Number',     employee.uan_number   or '—',
         'ESIC IP No.',    employee.esic_ip_number or '—'],
        ['PAN Number',     employee.pan_number   or '—',
         'Pay Period',     f'{month_name} {payroll.year}'],
    ]
    info_table = Table(info_data, colWidths=[4*cm, 6.5*cm, 4*cm, 6.5*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_BLUE),
        ('BACKGROUND', (2, 0), (2, -1), LIGHT_BLUE),
        ('FONTNAME',   (0, 0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',   (0, 0), (-1,-1), 9),
        ('GRID',       (0, 0), (-1,-1), 0.5, BORDER),
        ('PADDING',    (0, 0), (-1,-1), 5),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*cm))

    # ── Earnings & Deductions ─────────────────────────────────────────
    earn_ded = [
        ['EARNINGS', 'Amount (₹)', 'DEDUCTIONS', 'Amount (₹)'],
        ['Basic Salary',       f'{payroll.basic_salary:,.2f}',
         'EPF Employee (12%)', f'{payroll.epf_employee:,.2f}'],
        ['HRA',                f'{payroll.hra:,.2f}',
         'ESIC Employee (0.75%)', f'{payroll.esic_employee:,.2f}'],
        ['Special Allowance',  f'{payroll.special_allowance:,.2f}',
         'Professional Tax',   f'{payroll.professional_tax:,.2f}'],
        ['Travel Allowance',   f'{payroll.travel_allowance:,.2f}',
         'TDS',                f'{payroll.tds:,.2f}'],
        ['', '', '', ''],
        ['GROSS SALARY',       f'{payroll.gross_salary:,.2f}',
         'TOTAL DEDUCTIONS',   f'{payroll.total_deductions:,.2f}'],
    ]
    ed_table = Table(earn_ded, colWidths=[5.5*cm, 4.5*cm, 5.5*cm, 5.5*cm])
    ed_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0),  DARK_BLUE),
        ('TEXTCOLOR',  (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',   (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTNAME',   (0, 1), (-1, -1), 'Helvetica'),
        ('FONTNAME',   (0,-1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1, -1), LIGHT_BLUE),
        ('FONTSIZE',   (0, 0), (-1, -1), 9),
        ('GRID',       (0, 0), (-1, -1), 0.5, BORDER),
        ('PADDING',    (0, 0), (-1, -1), 6),
    ]))
    elements.append(ed_table)
    elements.append(Spacer(1, 0.4*cm))

    # ── Employer contributions ────────────────────────────────────────
    emp_contrib = [
        ['EMPLOYER CONTRIBUTIONS (Statutory — not deducted from salary)', 'Amount (₹)'],
        ['EPF Employer (12%)',    f'{payroll.epf_employer:,.2f}'],
        ['EPS Employer (8.33%)',  f'{payroll.eps_employer:,.2f}'],
        ['EPF Deposit (3.67%)',   f'{payroll.epf_deposit:,.2f}'],
        ['ESIC Employer (3.25%)', f'{payroll.esic_employer:,.2f}'],
    ]
    ec_table = Table(emp_contrib, colWidths=[15*cm, 6*cm])
    ec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0),  GREEN),
        ('TEXTCOLOR',  (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',   (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTNAME',   (0, 1), (-1,-1),  'Helvetica'),
        ('FONTSIZE',   (0, 0), (-1,-1),  9),
        ('GRID',       (0, 0), (-1,-1),  0.5, BORDER),
        ('PADDING',    (0, 0), (-1,-1),  6),
    ]))
    elements.append(ec_table)
    elements.append(Spacer(1, 0.4*cm))

    # ── Net Pay banner ────────────────────────────────────────────────
    net_data = [['NET PAY (Take Home)', f'₹ {payroll.net_pay:,.2f}']]
    net_table = Table(net_data, colWidths=[15*cm, 6*cm])
    net_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1,-1), MID_BLUE),
        ('TEXTCOLOR',  (0, 0), (-1,-1), colors.white),
        ('FONTNAME',   (0, 0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1,-1), 13),
        ('ALIGN',      (0, 0), (-1,-1), 'CENTER'),
        ('PADDING',    (0, 0), (-1,-1), 10),
    ]))
    elements.append(net_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
