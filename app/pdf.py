from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import io
import os
import platform

def find_font_file(font_name):
    """Find font file in common system locations"""
    system = platform.system().lower()

    # Common font locations
    if system == 'windows':
        font_dirs = [
            'C:\\Windows\\Fonts',
            'C:\\Windows\\System32',
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\Fonts')
        ]
        # Windows font naming conventions
        font_files = [
            f'{font_name}.ttf',
            f'{font_name}.TTF',
            f'{font_name} Regular.ttf',
            f'{font_name}-Regular.ttf'
        ]
    else:  # Linux/Unix
        font_dirs = [
            '/usr/share/fonts/TTF',
            '/usr/share/fonts/truetype',
            '/usr/share/fonts',
            '/usr/local/share/fonts'
        ]
        font_files = [
            f'{font_name}.ttf',
            f'{font_name}.TTF'
        ]

    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            for font_file in font_files:
                font_path = os.path.join(font_dir, font_file)
                if os.path.exists(font_path):
                    return font_path

    return None

# Register Unicode font for Polish characters
try:
    # Try to find DejaVu Sans fonts
    dejavu_regular = find_font_file('DejaVuSans')
    dejavu_bold = find_font_file('DejaVuSans-Bold')

    if dejavu_regular and dejavu_bold:
        pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_regular))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', dejavu_bold))
        FONT_NAME = 'DejaVuSans'
        FONT_BOLD = 'DejaVuSans-Bold'
        print("Using DejaVu fonts for Polish characters")
    else:
        raise Exception("DejaVu fonts not found")

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
