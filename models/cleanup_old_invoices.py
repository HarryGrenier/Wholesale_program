import sqlite3
import json
from datetime import datetime, timedelta
import os

SETTINGS_PATH = "Data/settings.json"
DB_PATH = "Data/invoice.db"

def load_retention_period():
    with open(SETTINGS_PATH, "r") as f:
        settings = json.load(f)
    
    retention = settings.get("invoice_retention", {})
    years = retention.get("years", 0)
    months = retention.get("months", 0)
    
    total_days = (years * 12 + months) * 30
    return timedelta(days=total_days)

def delete_old_invoices():
    cutoff_date = (datetime.now() - load_retention_period()).date()  # <-- `.date()` drops time
    cutoff_str = cutoff_date.strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Delete invoice items first
    cursor.execute('''
        DELETE FROM invoice_items
        WHERE invoice_id IN (
            SELECT id FROM invoices WHERE date < ?
        )
    ''', (cutoff_str,))

    # Delete the invoices themselves
    cursor.execute('''
        DELETE FROM invoices WHERE date < ?
    ''', (cutoff_str,))

    conn.commit()
    conn.close()
    
def delete_empty_invoices():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Delete invoices that have no corresponding items
    cursor.execute('''
        DELETE FROM invoices
        WHERE id NOT IN (
            SELECT DISTINCT invoice_id FROM invoice_items
        )
    ''')

    conn.commit()
    conn.close()
if __name__ == "__main__":
    delete_old_invoices()
