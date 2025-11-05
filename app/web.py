from . import database
from . import files
from flask import Flask, request, send_file, redirect, url_for, flash
from loguru import logger
from . import pdf
from . import events
from datetime import datetime

# Load configuration for web
in_event_ids, out_event_ids, event_ids, events_file, archive_folder, processing_interval_minutes = files.load_config()

app = Flask(__name__)

@app.route('/')
def index():
    # Get current year and month for default values
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    return f"""
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MINI RCP</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="text-center mb-4">MINI RCP</h1>
            
            <div class="row">
                <div class="col-md-4">
                    <h2>Obecność</h2>
                    <a href='/users_on_site' class="btn btn-primary">Wyświetl obecnych pracowników</a>
                    <br><br>
                    <a href='/process_data' class="btn btn-warning">Pobierz dane</a>
                </div>
                
                <div class="col-md-4">
                    <h2>Raport dzienny</h2>
                    <form action="/day_report" method="post" class="mb-3">
                        <div class="mb-3">
                            <label for="date" class="form-label">Wybierz datę (DD/MM/YYYY):</label>
                            <input type="text" class="form-control" id="date" name="date" placeholder="DD/MM/YYYY" maxlength="10" oninput="formatDate(this)" required>
                        </div>
                        <button type="submit" class="btn btn-success">Generuj raport dzienny</button>
                    </form>
                </div>
                
                <div class="col-md-4">
                    <h2>Raport miesięczny</h2>
                    <form action="/monthly_report" method="post" class="mb-3">
                        <div class="mb-3">
                            <label for="year" class="form-label">Rok:</label>
                            <input type="number" class="form-control" id="year" name="year" value="{current_year}" required>
                        </div>
                        <div class="mb-3">
                            <label for="month" class="form-label">Miesiąc:</label>
                            <input type="number" class="form-control" id="month" name="month" min="1" max="12" value="{current_month}" required>
                        </div>
                        <button type="submit" class="btn btn-success">Generuj raport miesięczny</button>
                    </form>
                </div>
            </div>
        </div>
        
        <script>
        function formatDate(input) {{
            // Remove all non-digit characters
            let value = input.value.replace(/\D/g, '');
            
            // Limit to 8 digits (DDMMYYYY)
            if (value.length > 8) {{
                value = value.substring(0, 8);
            }}
            
            // Add slashes at appropriate positions
            if (value.length >= 2) {{
                value = value.substring(0, 2) + '/' + value.substring(2);
            }}
            if (value.length >= 5) {{
                value = value.substring(0, 5) + '/' + value.substring(5);
            }}
            
            input.value = value;
        }}
        </script>
    </body>
    </html>
    """

@app.route('/users_on_site')
def users_on_site():
    users = database.get_users_on_site(in_event_ids, out_event_ids)
    html = """
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Użytkownicy na miejscu</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>Użytkownicy obecnie na miejscu</h1>
            <ul class="list-group mb-3">
    """
    for name, surname in users:
        html += f"<li class='list-group-item'>{name} {surname}</li>"
    html += """
            </ul>
            <a href='/' class="btn btn-secondary">Powrót</a>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/day_report', methods=['POST'])
def day_report():
    date_input = request.form['date']
    # Convert from DD/MM/YYYY to YYYY-MM-DD format
    try:
        date_obj = datetime.strptime(date_input, '%d/%m/%Y')
        date = date_obj.strftime('%Y-%m-%d')
        display_date = date_obj.strftime('%d/%m/%Y')  # For display
    except ValueError:
        # If conversion fails, assume it's already in correct format
        date = date_input
        display_date = date_input
    
    time_spent = database.calculate_time_spent(date, in_event_ids, out_event_ids)
    html = f"""
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Raport dzienny</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>Raport dzienny dla {display_date}</h1>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Imię</th>
                        <th>Nazwisko</th>
                        <th>Spędzony czas</th>
                    </tr>
                </thead>
                <tbody>
    """
    for name, surname, mins in time_spent:
        hours = int(mins // 60)
        minutes = int(mins % 60)
        time_str = f"{hours} godziny {minutes} minut"
        html += f"<tr><td>{name}</td><td>{surname}</td><td>{time_str}</td></tr>"
    html += f"""
                </tbody>
            </table>
            <a href='/' class="btn btn-secondary">Powrót</a>
            <a href='/day_report_pdf/{date}' class="btn btn-primary ms-2">Pobierz PDF</a>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/monthly_report', methods=['POST'])
def monthly_report():
    year = int(request.form['year'])
    month = int(request.form['month'])
    monthly_time = database.calculate_monthly_time_spent(year, month, in_event_ids, out_event_ids)
    html = f"""
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Raport miesięczny</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>Raport miesięczny dla {year}-{month:02d}</h1>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Imię</th>
                        <th>Nazwisko</th>
                        <th>Spędzony czas</th>
                    </tr>
                </thead>
                <tbody>
    """
    for name, surname, mins in monthly_time:
        hours = int(mins // 60)
        minutes = int(mins % 60)
        time_str = f"{hours} godziny {minutes} minut"
        html += f"<tr><td>{name}</td><td>{surname}</td><td>{time_str}</td></tr>"
    html += f"""
                </tbody>
            </table>
            <a href='/' class="btn btn-secondary">Powrót</a>
            <a href='/monthly_report_pdf/{year}/{month}' class="btn btn-primary ms-2">Pobierz PDF</a>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/day_report_pdf/<date>')
def day_report_pdf(date):
    time_spent = database.calculate_time_spent(date, in_event_ids, out_event_ids)
    pdf_buffer = pdf.generate_daily_pdf(date, time_spent)
    return send_file(pdf_buffer, as_attachment=True, download_name=f'raport_dzienny_{date}.pdf', mimetype='application/pdf')

@app.route('/monthly_report_pdf/<int:year>/<int:month>')
def monthly_report_pdf(year, month):
    monthly_time = database.calculate_monthly_time_spent(year, month, in_event_ids, out_event_ids)
    pdf_buffer = pdf.generate_monthly_pdf(year, month, monthly_time)
    return send_file(pdf_buffer, as_attachment=True, download_name=f'raport_miesieczny_{year}_{month:02d}.pdf', mimetype='application/pdf')

@app.route('/process_data')
def process_data():
    try:
        logger.info("Manual data processing triggered from web interface")
        
        # Ensure archive folder exists
        files.ensure_archive_folder(archive_folder)
        
        # Initialize database
        database.init_db()
        
        # Read and process events
        logger.info(f"Reading events from {events_file}")
        event_list = events.read_events(events_file, event_ids)
        logger.info(f"Loaded {len(event_list)} events")
        
        for event in event_list:
            database.insert_event(event)
        logger.info("Inserted events into database")
        
        # Archive the processed events file
        logger.info(f"Archiving {events_file} to {archive_folder}")
        files.archive_file(events_file, archive_folder)
        logger.info("Manual data processing completed")
        
        # Redirect back to main page with success message
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Error in manual data processing: {e}")
        # Redirect back to main page even on error
        return redirect(url_for('index'))

if __name__ == '__main__':
    logger.add("logs/web.log", rotation="10 MB", retention="1 week")
    logger.info("Starting MINI RCP Web Server")
    app.run(host='0.0.0.0', port=5000, debug=False)