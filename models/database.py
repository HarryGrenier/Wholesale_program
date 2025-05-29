import sqlite3
from datetime import datetime

DB_NAME = "invoice.db"

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

def add_item(name, vendor_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (name, vendor_id) VALUES (?, ?)", (name, vendor_id))
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

def get_invoice_items(invoice_db_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ii.id, v.name AS vendor_name, i.name AS item_name,
                   ii.quantity, ii.unit_price, ii.optional_info
            FROM invoice_items ii
            JOIN vendors v ON ii.vendor_id = v.id
            JOIN items i ON ii.item_id = i.id
            WHERE ii.invoice_id = ?
        ''', (invoice_db_id,))
        return cursor.fetchall()

def update_invoice(invoice_db_id, user_info, items):
    with get_connection() as conn:
        cursor = conn.cursor()
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
