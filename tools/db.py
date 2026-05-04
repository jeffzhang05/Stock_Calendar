import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'events.db')

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            date TEXT,
            title TEXT,
            type TEXT,
            region TEXT,
            description TEXT,
            related_tickers TEXT,
            last_updated TEXT
        )
    ''')
    conn.commit()
    conn.close()

def upsert_events(events_list):
    """
    Takes a list of event dicts and upserts them into the SQLite database.
    """
    if not events_list:
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    
    for e in events_list:
        tickers_str = json.dumps(e.get('related_tickers', []))
        cursor.execute('''
            INSERT OR REPLACE INTO events 
            (id, date, title, type, region, description, related_tickers, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            e['id'], 
            e['date'], 
            e['title'], 
            e['type'], 
            e['region'], 
            e.get('description', ''), 
            tickers_str, 
            now
        ))
    
    conn.commit()
    conn.close()

def get_events(start_date=None, end_date=None, regions=None, types=None):
    """
    Reads events from the DB with optional filtering.
    regions and types should be lists of strings if provided.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM events WHERE 1=1"
    params = []
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
        
    if regions:
        placeholders = ','.join('?' for _ in regions)
        query += f" AND region IN ({placeholders})"
        params.extend(regions)
        
    if types:
        placeholders = ','.join('?' for _ in types)
        query += f" AND type IN ({placeholders})"
        params.extend(types)
        
    query += " ORDER BY date ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    events = []
    for r in rows:
        events.append({
            "id": r['id'],
            "date": r['date'],
            "title": r['title'],
            "type": r['type'],
            "region": r['region'],
            "description": r['description'],
            "related_tickers": json.loads(r['related_tickers']) if r['related_tickers'] else []
        })
        
    conn.close()
    return events
