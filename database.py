import sqlite3

def connect_db():
    return sqlite3.connect("invoice.db")

def init_db():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        vendor_id INTEGER,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (vendor_id) REFERENCES vendors(id)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY,
        customer_name TEXT,
        date TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY,
        invoice_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price_each REAL,
        FOREIGN KEY (invoice_id) REFERENCES invoices(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )""")

    conn.commit()
    conn.close()
