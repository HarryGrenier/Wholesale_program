import sqlite3

def connect_db():
    return sqlite3.connect("invoice.db")

def init_db():
    conn = connect_db()
    cur = conn.cursor()

    # Vendors table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )""")

    # Items table (formerly products)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        vendor_id INTEGER,
        FOREIGN KEY (vendor_id) REFERENCES vendors(id)
    )""")

    # Invoices table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id TEXT NOT NULL,
        date TEXT NOT NULL
    )""")

    # Invoice Items (manually entered prices, item info)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER,
        vendor_name TEXT,
        item_name TEXT,
        item_info TEXT,
        quantity INTEGER,
        unit_price REAL,
        FOREIGN KEY (invoice_id) REFERENCES invoices(id)
    )""")

    conn.commit()
    conn.close()


def populate_test_data():
    conn = connect_db()
    cur = conn.cursor()

    # Clear old data
    cur.execute("DELETE FROM invoice_items")
    cur.execute("DELETE FROM invoices")
    cur.execute("DELETE FROM items")
    cur.execute("DELETE FROM vendors")

    # Insert vendors
    vendors = ["Fresh Foods", "Global Supply", "Office Mart"]
    for name in vendors:
        cur.execute("INSERT INTO vendors (name) VALUES (?)", (name,))

    # Get vendor IDs
    cur.execute("SELECT id, name FROM vendors")
    vendor_map = {name: vid for vid, name in cur.fetchall()}

    # Insert items
    items = [
        ("Apples", vendor_map["Fresh Foods"]),
        ("Bananas", vendor_map["Fresh Foods"]),
        ("Paper", vendor_map["Office Mart"]),
        ("Stapler", vendor_map["Office Mart"]),
        ("Cleaning Wipes", vendor_map["Global Supply"]),
    ]

    for name, vendor_id in items:
        cur.execute("INSERT INTO items (name, vendor_id) VALUES (?, ?)", (name, vendor_id))

    conn.commit()
    conn.close()
    print("✅ Test data inserted.")


if __name__ == "__main__":
    init_db()
    populate_test_data()