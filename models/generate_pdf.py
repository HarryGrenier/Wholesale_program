from collections import defaultdict

from requests import options
from ui.settings import load_settings
from models.pricing import price_with_fee, markup_price, margin_pct_on_sale


def money(x):
    try:
        return f"${float(x):,.2f}"
    except Exception:
        return ""

def pct(x):
    try:
        return f"{float(x) * 100:.1f}%"
    except Exception:
        return ""

def compute_pricing_fields(item, case_fee, wholesale_markup, retail_markup):
    unit_price = float(item["unit_price"])
    qty = int(item["quantity"])

    unit_cost_fee = round(unit_price + float(case_fee), 2)          # cost + case fee
    wholesale_price = round(unit_cost_fee * (1 + float(wholesale_markup)), 2)
    retail_price = round(unit_cost_fee * (1 + float(retail_markup)), 2)

    # margin on SELL price: (sale - cost) / sale
    def margin(cost, sale):
        return 0.0 if sale <= 0 else (sale - cost) / sale

    return {
        **item,
        "case_fee": float(case_fee),
        "unit_cost_with_fee": unit_cost_fee,
        "wholesale_price": wholesale_price,
        "retail_price": retail_price,
        "wholesale_margin": margin(unit_cost_fee, wholesale_price),
        "retail_margin": margin(unit_cost_fee, retail_price),
        "ext_cost_with_fee": round(qty * unit_cost_fee, 2)
    }

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



 # --- Helper functions ---
def money(x):
    try:
        return f"${float(x):,.2f}"
    except Exception:
        return ""

def pct(x):
    try:
        return f"{float(x) * 100:.1f}%"
    except Exception:
        return ""

def price_with_fee(unit_price, fee):
    return round(float(unit_price) + float(fee), 2)

def markup_price(cost, markup_rate):
    return round(float(cost) * (1 + float(markup_rate)), 2)




##############################################################
# Main PDF Generation Function
##############################################################

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from collections import defaultdict
import os



def generate_pdf_invoice(invoice_id, order_date, invoice_items, filename="invoice_report.pdf", options=0):
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
    c = canvas.Canvas(filename, pagesize=LETTER)
    width, height = LETTER

    def draw_main_header():
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, "Wholesale Invoices - Accounting Report")

        c.setFont("Helvetica", 10)
        c.drawString(1 * inch, height - 1.25 * inch, f"Invoice ID: {invoice_id}")
        c.drawString(4 * inch, height - 1.25 * inch, f"Order Date: {order_date}")

    
    # ============================
    # PAGE 1: Itemized Invoice with subtotals & grand totals
    # ============================
    if (options == 1) or (options == 0):
        draw_main_header()
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
        
        
        grand_total_qty = 0
        grand_total_cost = 0
        for vendor in sorted(grouped.keys(), key=lambda v: v.lower()):
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
    
    
    
    # ============================
    # PAGE 2: Pricing & Margin Summary (vendor-grouped) with pagination
    # ============================
    if (options == 2) or (options == 0):
        # Get settings
        settings = load_settings()
        case_fee = float(settings.get("case_fee", 0.0))
        Wholesale_Markup = float(settings.get("Wholesale_Markup", 0.22))  # 22% markup for wholesale price calculation
        Retail_Markup = float(settings.get("Retail_Markup", 0.50))     # 50% markup for retail price calculation
        
        # --- Page 2 column setup ---
        headers2 = ["Vendor", "Item", "Qty", "Base Cost", "Unit + Fee", "22% Markup", "50% Markup"]
        col_widths2 = [1.5, 1.5, 0.5, 0.7, 0.8, 0.8, 0.8]  # 7 widths for 7 headers

        LEFT_X = 0.5 * inch
        RIGHT_X = 7.5 * inch
        BOTTOM_Y = 1.0 * inch                      # bottom margin cutoff

        row_h = 0.20 * inch
        vendor_h = 0.20 * inch
        header_h = 0.22 * inch
        underline_h = 0.10 * inch

        def draw_page2_header():
            """
            Draw page-2 title/meta BELOW the main header/meta and
            return the y position where the table header should start.
            """
            w, h = LETTER

            c.setFont("Helvetica-Bold", 13)
            c.drawString(1 * inch, h - 1.55 * inch, "Pricing & Margin Summary")

            c.setFont("Helvetica", 9)
            c.drawString(
                1 * inch,
                h - 1.75 * inch,
                f"Case Fee: {money(case_fee)}   |   Wholesale Markup: {pct(Wholesale_Markup)}   |   Retail Markup: {pct(Retail_Markup)}"
            )

            # table should start under the page2 meta line
            return h - 2.05 * inch

        def draw_table_header2(y):
            c.setFont("Helvetica-Bold", 9)
            x = LEFT_X
            for i, htxt in enumerate(headers2):
                c.drawString(x, y, htxt)
                x += col_widths2[i] * inch
            c.line(LEFT_X, y - 0.05 * inch, RIGHT_X, y - 0.05 * inch)
            return y - header_h

        def draw_row2(y, row_data, font="Helvetica", size=9):
            c.setFont(font, size)
            x = LEFT_X
            for i, val in enumerate(row_data):
                c.drawString(x, y, str(val))
                x += col_widths2[i] * inch
            return y - row_h

        # This will hold our current y position for page 2
        y2 = None

        def start_page2(on_new_page: bool):
            nonlocal y2
            if on_new_page:
                c.showPage()

            draw_main_header()

            table_top_y = draw_page2_header()
            y2 = draw_table_header2(table_top_y)

        def ensure_room(height_needed):
            nonlocal y2
            if (y2 - height_needed) < BOTTOM_Y:
                c.showPage()
                draw_main_header()
                table_top_y = draw_page2_header()
                y2 = draw_table_header2(table_top_y)


        append_mode = (options == 0)  # if both reports, append pricing to a new page
        start_page2(on_new_page=append_mode)

        grouped2 = group_invoice_items(invoice_items)

        for vendor in sorted(grouped2.keys(), key=lambda v: v.lower()):
            items = grouped2[vendor]

            # Need room for vendor label at least
            ensure_room(vendor_h)

            # Vendor header row
            y2 = draw_row2(y2, [vendor, "", "", "", "", "", ""], font="Helvetica-Bold")

            for it in items:
                # Need room for one row
                ensure_room(row_h)

                unit_price = float(it["unit_price"])
                qty = int(it["quantity"])

                cost_fee = price_with_fee(unit_price, case_fee)
                wholesale_sale = markup_price(cost_fee, Wholesale_Markup)
                retail_sale = markup_price(cost_fee, Retail_Markup)

                row2 = [
                    "",  # vendor already printed above
                    it.get("item_name", ""),
                    qty,
                    money(unit_price),
                    money(cost_fee),
                    money(wholesale_sale),
                    money(retail_sale),
                ]
                y2 = draw_row2(y2, row2)

            # Need room for underline line
            ensure_room(underline_h)
            c.line(LEFT_X, y2 + 0.10 * inch, RIGHT_X, y2 + 0.10 * inch)
            y2 -= underline_h
    c.save()
    return os.path.abspath(filename)