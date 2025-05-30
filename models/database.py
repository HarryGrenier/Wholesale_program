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

def add_item(name, vendor_id, item_code):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (name, vendor_id, item_code) VALUES (?, ?, ?)", (name, vendor_id, item_code))
        conn.commit()

def get_items_by_vendor(vendor_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM items WHERE vendor_id = ? ORDER BY name", (vendor_id,))
        return cursor.fetchall()

def get_all_items():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, vendor_id FROM items")
        return cursor.fetchall()

# -------------------
# Invoice Operations
# -------------------

def create_invoice(invoice_id, date, user_info, items):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO invoices (invoice_id, date, user_info) VALUES (?, ?, ?)",
            (invoice_id, date, user_info)
        )
        invoice_db_id = cursor.lastrowid
        for item in items:
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

def get_all_invoices():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, invoice_id, date, user_info FROM invoices ORDER BY date DESC")
        return cursor.fetchall()

def get_invoice_items(invoice_id):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ii.id as item_id,
                   vendors.name as vendor_name,
                   items.name as item_name,
                   ii.quantity,
                   ii.unit_price,
                   ii.optional_info,
                   items.item_code as item_code
            FROM invoice_items ii
            JOIN items ON ii.item_id = items.id
            JOIN vendors ON items.vendor_id = vendors.id
            WHERE ii.invoice_id = ?
        """, (invoice_id,))
        return cursor.fetchall()

def update_invoice(invoice_db_id, user_info, items, deleted_ids=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if deleted_ids:
            for item_id in deleted_ids:
                cursor.execute("DELETE FROM invoice_items WHERE id = ?", (item_id,))
        cursor.execute("UPDATE invoices SET user_info = ? WHERE id = ?", (user_info, invoice_db_id))

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


def add_item_code_column():
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE items ADD COLUMN item_code TEXT UNIQUE")
            conn.commit()
        except Exception:
            pass  # Already added
