import sqlite3



def invoice_exists(invoice_id):
    conn = sqlite3.connect('invoice.db')
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM invoices WHERE id = ?", (invoice_id,))
    result = cur.fetchone()
    conn.close()
    return result is not None

def connect_db():
    return sqlite3.connect("invoice.db")

#retrieves all vendors from the database
def get_all_vendors():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT name FROM vendors ORDER BY name")
    return [row[0] for row in cur.fetchall()]

# retrieves all items for a specific vendor
def get_items_for_vendor(vendor_name):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT items.name
        FROM items
        JOIN vendors ON items.vendor_id = vendors.id
        WHERE vendors.name = ?
        ORDER BY items.name
    """, (vendor_name,))
    return [row[0] for row in cur.fetchall()]

# retrieves all items from the database
def get_all_items():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT name FROM items ORDER BY name")
    return [row[0] for row in cur.fetchall()]


def update_invoice(invoice_id, date, items):
    conn = connect_db()
    cur = conn.cursor()

    # Get the DB ID
    cur.execute("SELECT id FROM invoices WHERE invoice_id = ?", (invoice_id,))
    result = cur.fetchone()
    if not result:
        conn.close()
        raise ValueError("Invoice not found")

    db_invoice_id = result[0]

    # Update date
    cur.execute("UPDATE invoices SET date = ? WHERE id = ?", (date, db_invoice_id))

    # Delete old line items
    cur.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (db_invoice_id,))

    # Insert updated line items
    for vendor, item, info, qty, price in items:
        cur.execute("""
            INSERT INTO invoice_items (invoice_id, vendor_name, item_name, item_info, quantity, unit_price)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (db_invoice_id, vendor, item, info, qty, price))

    conn.commit()
    conn.close()


# saves the invoice data to the database
def save_invoice_to_db(invoice_id, date, items):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO invoices (invoice_id, date) VALUES (?, ?)", (invoice_id, date))
    db_invoice_id = cur.lastrowid

    for vendor, item, info, qty, price in items:
        cur.execute(
            """INSERT INTO invoice_items (invoice_id, vendor_name, item_name, item_info, quantity, unit_price)
            VALUES (?, ?, ?, ?, ?, ?)""", 
            (db_invoice_id, vendor, item, info, qty, price)
        )

    conn.commit()
    conn.close()


def get_invoice_by_id(invoice_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT invoice_id, date FROM invoices WHERE invoice_id = ?", (invoice_id,))
    return cur.fetchone()


def get_invoice_items(invoice_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT vendor_name, item_name, item_info, quantity, unit_price
        FROM invoice_items
        JOIN invoices ON invoice_items.invoice_id = invoices.id
        WHERE invoices.invoice_id = ?
    """, (invoice_id,))
    return cur.fetchall()


def get_all_invoice_summaries():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT invoice_id, date FROM invoices ORDER BY date DESC")
    return cur.fetchall()


def generate_next_invoice_id():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT invoice_id FROM invoices ORDER BY id DESC LIMIT 1")
    last = cur.fetchone()
    if last:
        try:
            num = int(last[0].replace("INV-", ""))
            return f"INV-{num + 1:05d}"
        except:
            pass
    return "INV-00001"
