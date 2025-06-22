import sqlite3
import csv

DB_PATH = "Data/invoice.db"
CSV_PATH = "Untitled spreadsheet - Sheet1.csv"

def get_connection():
    return sqlite3.connect(DB_PATH)

def insert_data():
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        vendors = set()
        items = []

        for row in reader:
            vendor_name = row.get("Vendor Name:", "").strip()
            item_name = row.get("Item:", "").strip()
            item_code = row.get("ProduceItemID", "").strip()

            if vendor_name:
                vendors.add(vendor_name)
            if item_name and item_code:
                items.append((item_name, item_code))

        with get_connection() as conn:
            cursor = conn.cursor()

            # Insert vendors
            for vname in vendors:
                cursor.execute("INSERT OR IGNORE INTO vendors (name) VALUES (?)", (vname,))

            # Insert items
            for name, code in items:
                cursor.execute("INSERT OR IGNORE INTO items (name, item_code) VALUES (?, ?)", (name, code))

            conn.commit()

if __name__ == "__main__":
    insert_data()
    print("Items and vendors imported successfully.")
