import sqlite3 as sql
import json
import os
from datetime import date, datetime
from loguru import logger

    
def init_db():
    logger.info("Initializing database")
    db_path = 'events.db'
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            date TEXT,
            name TEXT,
            surname TEXT,
            id_point INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Database initialized")

def insert_event(event):
    logger.debug(f"Inserting event: {event}")
    db_path = 'events.db'
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (time, date, name, surname, id_point)
        VALUES (?, ?, ?, ?, ?)
    ''', (event.time, event.date, event.name, event.surname, event.id_point))
    conn.commit()
    conn.close()
    logger.debug("Event inserted")

def get_users_on_site(in_event_ids, out_event_ids, target_date=None):
    if target_date is None:
        target_date = date.today().isoformat()
    logger.info(f"Getting users on site for date {target_date}")
    db_path = 'events.db'
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT name, surname, id_point FROM events WHERE date = ? ORDER BY name, surname, time DESC', (target_date,))
    rows = cursor.fetchall()
    conn.close()
    logger.debug(f"Found {len(rows)} events for date {target_date}")
    
    on_site = []
    current_person = None
    for row in rows:
        name, surname, id_point = row
        person = (name, surname)
        if person != current_person:
            current_person = person
            if id_point in in_event_ids:
                on_site.append(person)
    logger.info(f"Users on site: {on_site}")
    return on_site


def get_all_events():
    logger.info("Getting all events")
    db_path = 'events.db'
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT time, date, name, surname, id_point FROM events ORDER BY date, time')
    rows = cursor.fetchall()
    conn.close()
    logger.info(f"Retrieved {len(rows)} events")
    return rows

def calculate_time_spent(target_date, in_event_ids, out_event_ids):
    logger.info(f"Calculating time spent on site for date {target_date}")
    db_path = 'events.db'
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT name, surname, time, id_point FROM events WHERE date = ? ORDER BY name, surname, time', (target_date,))
    rows = cursor.fetchall()
    conn.close()
    logger.debug(f"Found {len(rows)} events for date {target_date}")
    
    from collections import defaultdict
    person_events = defaultdict(list)
    for row in rows:
        name, surname, time_str, id_point = row
        person = (name, surname)
        person_events[person].append((time_str, id_point))
    
    time_spent = []
    date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
    
    for person, events in person_events.items():
        first_in = None
        last_out = None
        for time_str, id_point in events:
            time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
            if id_point in in_event_ids:
                if first_in is None:
                    first_in = time_obj
            if id_point in out_event_ids:
                last_out = time_obj
        
        if first_in and last_out and last_out > first_in:
            diff = datetime.combine(date_obj, last_out) - datetime.combine(date_obj, first_in)
            minutes = diff.total_seconds() / 60
            time_spent.append((person[0], person[1], minutes))
            logger.debug(f"{person}: {minutes} minutes")
    
    logger.info(f"Calculated time spent for {len(time_spent)} users")
    return time_spent

def calculate_monthly_time_spent(year, month, in_event_ids, out_event_ids):
    logger.info(f"Calculating monthly time spent for {year}-{month:02d}")
    db_path = 'events.db'
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    month_str = f"{year}-{month:02d}"
    cursor.execute('SELECT name, surname, date, time, id_point FROM events WHERE date LIKE ? ORDER BY name, surname, date, time', (month_str + '-%',))
    rows = cursor.fetchall()
    conn.close()
    logger.debug(f"Found {len(rows)} events for month {month_str}")
    
    from collections import defaultdict
    person_events = defaultdict(list)
    for row in rows:
        name, surname, date_str, time_str, id_point = row
        person = (name, surname)
        person_events[person].append((date_str, time_str, id_point))
    
    monthly_time = []
    for person, events in person_events.items():
        # Find earliest in and latest out
        earliest_in = None
        latest_out = None
        for date_str, time_str, id_point in events:
            dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
            if id_point in in_event_ids:
                if earliest_in is None or dt < earliest_in:
                    earliest_in = dt
            elif id_point in out_event_ids:
                if latest_out is None or dt > latest_out:
                    latest_out = dt
        
        if earliest_in and latest_out and latest_out > earliest_in:
            diff = latest_out - earliest_in
            total_minutes = diff.total_seconds() / 60
            monthly_time.append((person[0], person[1], total_minutes))
            logger.debug(f"{person}: {total_minutes} minutes in month")
    
    logger.info(f"Calculated monthly time for {len(monthly_time)} users")
    return monthly_time

