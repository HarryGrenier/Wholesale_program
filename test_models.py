from models import database
from datetime import datetime, timedelta
import random

def seed_large_test_data():
    print("Seeding vendors...")
    for i in range(1, 6):
        try:
            database.add_vendor(f"Vendor {chr(64 + i)}")
        except Exception:
            continue

    vendors = database.get_all_vendors()
    print("Vendors:", vendors)

    print("Seeding items...")
    for vendor in vendors:
        vendor_id = vendor[0]
        for i in range(5):  # 5 items per vendor
            try:
                database.add_item(f"Item {i+1} from {vendor[1]}", vendor_id)
            except Exception:
                continue

    items = database.get_all_items()
    print(f"{len(items)} total items.")

    print("Seeding invoices...")
    base_date = datetime.now() - timedelta(days=30)
    for n in range(20):  # 20 invoices
        invoice_id = f"INV-AUTO-{n+1:04d}"
        date = (base_date + timedelta(days=n)).strftime("%Y-%m-%d")
        user_info = f"Bulk test invoice {n+1}"

        invoice_items = []
        for _ in range(random.randint(5, 15)):  # 5-15 line items
            item = random.choice(items)
            invoice_items.append({
                "vendor_id": item[2],  # assuming item[2] = vendor_id
                "item_id": item[0],
                "quantity": random.randint(1, 20),
                "unit_price": round(random.uniform(5.0, 150.0), 2),
                "optional_info": random.choice(["", "Priority", "Promo", "Backorder", ""])
            })

        try:
            database.create_invoice(invoice_id, date, user_info, invoice_items)
        except Exception as e:
            print(f"Skipping {invoice_id}: {e}")

    print("Seeding complete.")

if __name__ == "__main__":
    seed_large_test_data()