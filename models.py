from database import connect_db

def get_vendors():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM vendors")
    return cur.fetchall()

def get_products_by_vendor(vendor_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price FROM products WHERE vendor_id = ?", (vendor_id,))
    return cur.fetchall()

def get_all_invoices():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT invoices.id, invoices.date, SUM(invoice_items.quantity * invoice_items.price_each) AS total
        FROM invoices
        LEFT JOIN invoice_items ON invoices.id = invoice_items.invoice_id
        GROUP BY invoices.id
        ORDER BY invoices.date DESC
    """)
    return cur.fetchall()

def get_invoice_items(invoice_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT products.name, invoice_items.quantity, invoice_items.price_each,
               invoice_items.quantity * invoice_items.price_each AS total
        FROM invoice_items
        JOIN products ON invoice_items.product_id = products.id
        WHERE invoice_items.invoice_id = ?
    """, (invoice_id,))
    return cur.fetchall()

def get_invoice_items_grouped(invoice_id):
    """
    Return [(vendor_name, product_name, qty, price_each, line_total)] sorted by vendor.
    """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT v.name,
               p.name,
               ii.quantity,
               ii.price_each,
               ii.quantity * ii.price_each     AS line_total
        FROM   invoice_items  AS ii
        JOIN   products       AS p ON ii.product_id = p.id
        JOIN   vendors        AS v ON p.vendor_id   = v.id
        WHERE  ii.invoice_id = ?
        ORDER  BY v.name, p.name
        """,
        (invoice_id,)
    )
    return cur.fetchall()





def search_product_across_vendors(product_query):
    conn = connect_db()
    cur = conn.cursor()
    search_term = f"%{product_query}%"
    cur.execute("""
        SELECT products.id, products.name, products.price, vendors.name AS vendor_name
        FROM products
        JOIN vendors ON products.vendor_id = vendors.id
        WHERE products.name LIKE ? OR CAST(products.id AS TEXT) LIKE ?
    """, (search_term, search_term))
    return cur.fetchall()

def create_invoice(customer_name, date, items):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO invoices (customer_name, date) VALUES (?, ?)", (customer_name, date))
    invoice_id = cur.lastrowid

    for product_id, quantity, price in items:
        cur.execute("""
            INSERT INTO invoice_items (invoice_id, product_id, quantity, price_each)
            VALUES (?, ?, ?, ?)""", (invoice_id, product_id, quantity, price))

    conn.commit()
    conn.close()
    return invoice_id
