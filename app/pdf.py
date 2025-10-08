from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import io

# Register Unicode font for Polish characters
try:
    # Register DejaVu Sans font
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/TTF/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf'))
    FONT_NAME = 'DejaVuSans'
    FONT_BOLD = 'DejaVuSans-Bold'
    print("Using DejaVu fonts for Polish characters")
except Exception as e:
    print(f"Could not load DejaVu fonts: {e}")
    FONT_NAME = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'

def generate_daily_pdf(date, time_spent):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Create custom styles with Polish font support
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=getSampleStyleSheet()['Title'],
        fontName=FONT_BOLD,
        fontSize=18,
    )
    
    elements = []
    
    # Title
    title = Paragraph(f"Raport dzienny dla {date}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5*inch))
    
    # Table data
    data = [['Imię', 'Nazwisko', 'Spędzony czas']]
    for name, surname, mins in time_spent:
        hours = int(mins // 60)
        minutes = int(mins % 60)
        time_str = f"{hours} godziny {minutes} minut"
        data.append([name, surname, time_str])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_monthly_pdf(year, month, monthly_time):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Create custom styles with Polish font support
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=getSampleStyleSheet()['Title'],
        fontName=FONT_BOLD,
        fontSize=18,
    )
    
    elements = []
    
    # Title
    title = Paragraph(f"Raport miesięczny dla {year}-{month:02d}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5*inch))
    
    # Table data
    data = [['Imię', 'Nazwisko', 'Spędzony czas']]
    for name, surname, mins in monthly_time:
        hours = int(mins // 60)
        minutes = int(mins % 60)
        time_str = f"{hours} godziny {minutes} minut"
        data.append([name, surname, time_str])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer
