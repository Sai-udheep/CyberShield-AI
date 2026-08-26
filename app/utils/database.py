import sqlite3
import os
import pandas as pd
from datetime import datetime

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database"))
DB_PATH = os.path.join(DB_DIR, "scans.db")

def get_db_connection():
    """Returns a connection to the SQLite database."""
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initializes the database and creates the scans history table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            scan_type TEXT NOT NULL,
            input_data TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            risk_score INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("Database and 'scans' table initialized successfully.")

def log_scan(scan_type, input_data, prediction, confidence, risk_score):
    """
    Logs a new scan record into the database.
    
    Parameters:
        scan_type (str): 'URL' or 'Email'
        input_data (str): The raw URL or email text
        prediction (str): 'Safe' or 'Phishing' (URL), 'Ham' or 'Spam' (Email)
        confidence (float): Probability score (0.0 to 1.0)
        risk_score (int): Score on a 0 to 100 scale
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO scans (timestamp, scan_type, input_data, prediction, confidence, risk_score)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, scan_type, input_data, prediction, float(confidence), int(risk_score)))
    conn.commit()
    conn.close()

def get_history():
    """
    Retrieves all history records sorted by latest first.
    
    Returns:
        pd.DataFrame: DataFrame containing all scans
    """
    conn = get_db_connection()
    query = "SELECT id, timestamp, scan_type, input_data, prediction, confidence, risk_score FROM scans ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_stats():
    """
    Computes summary statistics for the dashboard.
    
    Returns:
        dict: Stats including total scans, threat count, safe count, and threat percentage.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total counts
    cursor.execute("SELECT COUNT(*) FROM scans")
    total_scans = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM scans WHERE scan_type = 'URL'")
    total_urls = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM scans WHERE scan_type = 'Email'")
    total_emails = cursor.fetchone()[0]
    
    # Threat counts (where prediction is 'Phishing' or 'Spam')
    cursor.execute("SELECT COUNT(*) FROM scans WHERE prediction IN ('Phishing', 'Spam')")
    threat_scans = cursor.fetchone()[0]
    
    safe_scans = total_scans - threat_scans
    threat_rate = (threat_scans / total_scans * 100) if total_scans > 0 else 0.0
    
    conn.close()
    
    return {
        "total_scans": total_scans,
        "total_urls": total_urls,
        "total_emails": total_emails,
        "threat_scans": threat_scans,
        "safe_scans": safe_scans,
        "threat_rate": round(threat_rate, 2)
    }

def clear_history():
    """Deletes all logged records in the scans table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scans")
    conn.commit()
    conn.close()
    print("Database scan history cleared.")

if __name__ == "__main__":
    init_db()
