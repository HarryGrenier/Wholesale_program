from models import database
from datetime import datetime

def test_database():
    print("Adding vendors...")
    try:
        database.add_vendor("Vendor A")
        database.add_vendor("Vendor B")
    except Exception:
        print("Vendors already exist or duplicate entries ignored.")

    vendors = database.get_all_vendors()
    print("Vendors:", vendors)

    print("\nAdding items...")
    for vendor in vendors:
        vendor_id = vendor[0]
        try:
            database.add_item(f"Item 1 from {vendor[1]}", vendor_id)
            database.add_item(f"Item 2 from {vendor[1]}", vendor_id)
        except Exception:
            print(f"Items for {vendor[1]} may already exist.")

    items = database.get_all_items()
    print("Items:", items)

    print("\nCreating an invoice...")
    invoice_id = f"INV-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    date = datetime.now().strftime("%Y-%m-%d")
    user_info = "Test invoice with optional info"

    invoice_items = [
        {
            "vendor_id": vendors[0][0],
            "item_id": items[0][0],
            "quantity": 3,
            "unit_price": 9.99,
            "optional_info": "Urgent delivery"
        },
        {
            "vendor_id": vendors[1][0],
            "item_id": items[2][0],
            "quantity": 1,
            "unit_price": 15.50,
            "optional_info": "Gift-wrapped"
        }
    ]

    database.create_invoice(invoice_id, date, user_info, invoice_items)

    print("\nAll Invoices:")
    invoices = database.get_all_invoices()
    for inv in invoices:
        print(f"\nInvoice: {inv}")
        inv_items = database.get_invoice_items(inv[0])
        for item in inv_items:
            print(" -", item)

if __name__ == "__main__":
    test_database()
