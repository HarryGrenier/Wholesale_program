
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
    headers = ["Vendor", "Item ID", "Item Name", "Info", "Qty", "Unit $", "Ext. Cost"]
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

    grouped = defaultdict(list)
    for item in invoice_items:
        grouped[item["vendor_name"]].append(item)

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
                item["item_id"],
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
        y -= 0.1 * inch

        grand_total_qty += subtotal_qty
        grand_total_cost += subtotal_cost

    # Grand total
    y -= 0.1 * inch
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5 * inch, y, f"GRAND TOTAL: Qty = {grand_total_qty}, Cost = ${grand_total_cost:.2f}")

    c.save()
    return os.path.abspath(filename)
