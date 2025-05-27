import sqlite3

def populate_test_data():
    conn = sqlite3.connect("invoice.db")
    cur = conn.cursor()

    # Clear previous test data
    cur.execute("DELETE FROM invoice_items")
    cur.execute("DELETE FROM invoices")
    cur.execute("DELETE FROM products")
    cur.execute("DELETE FROM vendors")
    conn.commit()

    # Add vendors
    vendors = [("Fresh Foods Inc.",), ("Global Distributors",)]
    cur.executemany("INSERT INTO vendors (name) VALUES (?)", vendors)
    conn.commit()

    # Get vendor IDs
    cur.execute("SELECT id, name FROM vendors")
    vendor_map = {name: vid for vid, name in cur.fetchall()}

    # Add products for each vendor
    products = [
        # For Fresh Foods Inc.
        (vendor_map["Fresh Foods Inc."], "Apples", 1.20),
        (vendor_map["Fresh Foods Inc."], "Bananas", 0.60),
        (vendor_map["Fresh Foods Inc."], "Carrots", 0.80),
        # For Global Distributors
        (vendor_map["Global Distributors"], "Paper Towels", 2.50),
        (vendor_map["Global Distributors"], "Toilet Paper", 4.00),
        (vendor_map["Global Distributors"], "Cleaning Spray", 3.75),
    ]

    cur.executemany("INSERT INTO products (vendor_id, name, price) VALUES (?, ?, ?)", products)
    conn.commit()

    print("✅ Test data populated successfully.")
    conn.close()

if __name__ == "__main__":
    populate_test_data()
