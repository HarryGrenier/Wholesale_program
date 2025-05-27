import tkinter as tk
from tkinter import ttk, messagebox
from models import get_all_invoices, get_invoice_items
from invoice_pdf import export_invoice_to_pdf
from datetime import datetime
import os

class ManageInvoicesWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Manage Invoices")
        self.geometry("600x400")
        
        ttk.Button(self, text="Export to PDF", command=self.export_selected_invoice).pack(pady=(0, 10))

        self.setup_ui()

    def setup_ui(self):
        # Top: list of invoices
        self.tree = ttk.Treeview(self, columns=("ID", "Date", "Total"), show="headings", height=10)
        self.tree.heading("ID", text="Invoice ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Total", text="Total ($)")
        self.tree.column("ID", width=80, anchor="center")
        self.tree.column("Date", width=120, anchor="center")
        self.tree.column("Total", width=100, anchor="center")
        self.tree.pack(fill=tk.BOTH, padx=10, pady=(10, 5), expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.load_invoice_details)

        # Bottom: details for selected invoice
        self.details = ttk.Treeview(self, columns=("Product", "Quantity", "Price", "Total"), show="headings", height=8)
        for col in ("Product", "Quantity", "Price", "Total"):
            self.details.heading(col, text=col)
            self.details.column(col, anchor="center")
        self.details.pack(fill=tk.BOTH, padx=10, pady=(0, 10), expand=True)

        self.populate_invoice_list()

    def populate_invoice_list(self):
        for row in get_all_invoices():
            invoice_id, date_str, total = row
            self.tree.insert("", "end", values=(invoice_id, date_str, f"{total:.2f}"))

    def load_invoice_details(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        invoice_id = self.tree.item(selected[0])['values'][0]

        self.details.delete(*self.details.get_children())
        for row in get_invoice_items(invoice_id):
            name, qty, price, total = row
            self.details.insert("", "end", values=(name, qty, f"{price:.2f}", f"{total:.2f}"))
            
    def export_selected_invoice(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select an invoice to export.")
            return

        invoice_id, invoice_date, _ = self.tree.item(selected[0])["values"]

        filename = f"invoice_{invoice_id}_{invoice_date.replace('-', '')}.pdf"
        path = os.path.join(os.getcwd(), filename)

        try:
            export_invoice_to_pdf(invoice_id, invoice_date, path)
            messagebox.showinfo("Success", f"Invoice exported as {filename}")
            os.startfile(path)  # Only works on Windows
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error: {e}")
