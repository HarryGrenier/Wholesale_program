

from collections import defaultdict

def group_invoice_items(items):
    combined = defaultdict(lambda: {
        "vendor_name": "",
        "item_code": "",
        "item_name": "",
        "optional_info": "",
        "quantity": 0,
        "unit_price": 0.0
    })
    for item in items:
        key = (item["vendor_name"], item["item_code"], item["unit_price"])
        combined[key]["vendor_name"] = item["vendor_name"]
        combined[key]["item_code"] = item["item_code"]
        combined[key]["item_name"] = item["item_name"]
        combined[key]["optional_info"] = item.get("optional_info", "")
        combined[key]["unit_price"] = item["unit_price"]
        combined[key]["quantity"] += item["quantity"]

    grouped = defaultdict(list)
    for (vendor, _, _), combined_item in combined.items():
        grouped[vendor].append(combined_item)

    return grouped
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from collections import defaultdict
import os

def generate_pdf_invoice(invoice_id, order_date, invoice_items, filename="invoice_report.pdf"):
    """
    Generate a PDF invoice with subtotals per vendor and grand totals.
    invoice_items = list of dicts:
        {
            "vendor_name": str,
            "item_id": str or int,
            "item_name": str,
            "optional_info": str,
            "quantity": int,
            "unit_price": float
        }
    """
    c = canvas.Canvas(filename, pagesize=LETTER)
    width, height = LETTER

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, height - 1 * inch, "Wholesale Invoices - Accounting Report")

    # Metadata
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, height - 1.25 * inch, f"Invoice ID: {invoice_id}")
    c.drawString(4 * inch, height - 1.25 * inch, f"Order Date: {order_date}")

    # Table headers
    headers = ["Vendor", "Item Code", "Item Name", "Info", "Qty", "Unit $", "Ext. Cost"]
    col_widths = [1.2, 0.8, 1.5, 1.5, 0.5, 0.7, 0.8]
    y = height - 1.75 * inch

    def draw_table_header(y):
        c.setFont("Helvetica-Bold", 9)
        x = 0.5 * inch
        for i, h in enumerate(headers):
            c.drawString(x, y, h)
            x += col_widths[i] * inch
        return y - 0.2 * inch

    def draw_row(y, row_data, font="Helvetica", size=9):
        c.setFont(font, size)
        x = 0.5 * inch
        for i, val in enumerate(row_data):
            c.drawString(x, y, str(val))
            x += col_widths[i] * inch
        return y - 0.2 * inch

    y = draw_table_header(y)


    def group_invoice_items(items):
        combined = defaultdict(lambda: {
            "vendor_name": "",
            "item_code": "",
            "item_name": "",
            "optional_info": "",
            "quantity": 0,
            "unit_price": 0.0
        })
        for item in items:
            key = (item["vendor_name"], item["item_code"], item["unit_price"])
            combined[key]["vendor_name"] = item["vendor_name"]
            combined[key]["item_code"] = item["item_code"]
            combined[key]["item_name"] = item["item_name"]
            combined[key]["optional_info"] = item.get("optional_info", "")
            combined[key]["unit_price"] = item["unit_price"]
            combined[key]["quantity"] += item["quantity"]
        grouped = defaultdict(list)
        for (vendor, _, _), combined_item in combined.items():
            grouped[vendor].append(combined_item)
        return grouped

    grouped = group_invoice_items(invoice_items)
    grand_total_qty = 0
    grand_total_cost = 0
    for vendor in sorted(grouped.keys()):
        items = grouped[vendor]
        subtotal_qty = 0
        subtotal_cost = 0
        for item in items:
            ext_cost = item["quantity"] * item["unit_price"]
            row = [
                vendor,
                item["item_code"],
                item["item_name"],
                item["optional_info"],
                item["quantity"],
                f"{item['unit_price']:.2f}",
                f"{ext_cost:.2f}"
            ]
            y = draw_row(y, row)
            subtotal_qty += item["quantity"]
            subtotal_cost += ext_cost
            if y < 1 * inch:
                c.showPage()
                y = height - 1 * inch
                y = draw_table_header(y)
        # Subtotal row
        y = draw_row(y, ["", "", "", "Subtotal:", subtotal_qty, "", f"{subtotal_cost:.2f}"], font="Helvetica-Bold")
        # Underline to separate vendors
        c.line(0.5 * inch, y + 0.15 * inch, 7.5 * inch, y + 0.15 * inch)
        y -= 0.2 * inch
        grand_total_qty += subtotal_qty
        grand_total_cost += subtotal_cost
        
    # Grand total
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5 * inch, y, f"GRAND TOTAL: ")
    c.line(0.5 * inch, y - 0.05 * inch, 7.5 * inch, y - 0.05 * inch)
    c.drawString(5.5 * inch, y, f"Quantity: {grand_total_qty}  Total: ${grand_total_cost:.2f}")
    c.save()
    return os.path.abspath(filename)
