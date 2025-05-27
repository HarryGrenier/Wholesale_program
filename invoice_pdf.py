# invoice_pdf.py
from fpdf import FPDF
from models import get_invoice_items_grouped

class InvoicePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, f"Invoice", ln=True, align="C")

    def add_invoice(self, invoice_id, invoice_date, items_grouped):
        self.set_font("Arial", size=11)
        self.ln(5)
        self.cell(0, 10, f"Invoice ID: {invoice_id}", ln=True)
        self.cell(0, 10, f"Date: {invoice_date}", ln=True)
        self.ln(5)

        current_vendor = None
        total_amount = 0

        for vendor, product, qty, price, total in items_grouped:
            if vendor != current_vendor:
                self.set_font("Arial", "B", 11)
                self.cell(0, 10, f"Vendor: {vendor}", ln=True)
                current_vendor = vendor
            self.set_font("Arial", "", 11)
            self.cell(0, 10,
                f"  {product:<20}  Qty: {qty:<2}  @ ${price:.2f}  = ${total:.2f}",
                ln=True
            )
            total_amount += total

        self.ln(5)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, f"Total: ${total_amount:.2f}", ln=True)

def export_invoice_to_pdf(invoice_id, invoice_date, output_path="invoice.pdf"):
    items = get_invoice_items_grouped(invoice_id)
    pdf = InvoicePDF()
    pdf.add_page()
    pdf.add_invoice(invoice_id, invoice_date, items)
    pdf.output(output_path)
    return output_path
