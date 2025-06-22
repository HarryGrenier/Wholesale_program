import sqlite3
from datetime import datetime

DB_NAME = "Data/invoice.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

# -------------------
# Vendor Operations
# -------------------

def add_vendor(name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO vendors (name) VALUES (?)", (name,))
        conn.commit()

def get_all_vendors():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM vendors ORDER BY name")
        return cursor.fetchall()




# -------------------
# Item Operations
# -------------------

def add_item(name, item_code):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (name, item_code) VALUES (?, ?)", (name, item_code))
        conn.commit()

def get_all_items():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, item_code FROM items ORDER BY name")
        return cursor.fetchall()
    
def get_item_id_by_name(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM items WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# -------------------
# Invoice Operations
# -------------------

def get_all_invoices():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, date FROM invoices ORDER BY id DESC")
        return cursor.fetchall()

def get_invoice_items(invoice_id):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ii.id as item_id,
                v.name as vendor_name,
                i.item_code,
                i.name as item_name,
                ii.quantity,
                ii.unit_price,
                ii.optional_info
            FROM invoice_items ii
            JOIN items i ON ii.item_id = i.id
            JOIN vendors v ON ii.vendor_id = v.id
            WHERE ii.invoice_id = ?
""", (invoice_id,))
        return cursor.fetchall()

def update_invoice(invoice_db_id, items, deleted_ids=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if deleted_ids:
            for item_id in deleted_ids:
                cursor.execute("DELETE FROM invoice_items WHERE id = ?", (item_id,))

        for item in items:
            if item.get("existing_id"):
                cursor.execute(
                    '''UPDATE invoice_items
                       SET quantity = ?, unit_price = ?, optional_info = ?
                       WHERE id = ?''',
                    (item["quantity"], item["unit_price"], item.get("optional_info", ""), item["existing_id"])
                )
            else:
                cursor.execute(
                    '''INSERT INTO invoice_items (invoice_id, vendor_id, item_id, quantity, unit_price, optional_info)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (
                        invoice_db_id,
                        item["vendor_id"],
                        item["item_id"],
                        item["quantity"],
                        item["unit_price"],
                        item.get("optional_info", "")
                    )
                )
        conn.commit()


def get_invoice_details(invoice_id):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, date FROM invoices WHERE id = ?", (invoice_id,))
        row = cursor.fetchone()
        return dict(row) if row else None




def create_blank_invoice():
    with get_connection() as conn:
        cursor = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO invoices (date) VALUES (?)", (date,))
        conn.commit()
        return cursor.lastrowid
    
def delete_invoice(invoice_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
        conn.commit()
