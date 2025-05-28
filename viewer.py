# viewer.py
import tkinter as tk
from tkinter import ttk, messagebox
import models

def open(app):
    """
    Opens a new window for selecting and editing saved invoices.
    Accepts an instance of the main app to enable populating the form.
    """
    top = tk.Toplevel(app.root)
    top.title("Select Invoice")

    ttk.Label(top, text="Select an Invoice:").grid(row=0, column=0, padx=10, pady=5)

    invoice_options = models.get_all_invoice_summaries()
    if not invoice_options:
        messagebox.showinfo("No Invoices", "There are no saved invoices to display.")
        top.destroy()
        return

    selected_invoice = tk.StringVar()
    invoice_dropdown = ttk.Combobox(top, textvariable=selected_invoice, state="readonly")
    invoice_dropdown['values'] = [f"{inv_id} - {date}" for inv_id, date in invoice_options]
    invoice_dropdown.grid(row=0, column=1, padx=10, pady=5)

    preview_tree = ttk.Treeview(top, columns=("Vendor", "Item", "Info", "Qty", "Unit Price"), show="headings", height=8)
    for col in ("Vendor", "Item", "Info", "Qty", "Unit Price"):
        preview_tree.heading(col, text=col)
        preview_tree.column(col, anchor="center")
    preview_tree.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10))

    def load_preview():
        selected = selected_invoice.get()
        if not selected:
            return

        invoice_id = selected.split(" - ")[0]
        items = models.get_invoice_items(invoice_id)

        preview_tree.delete(*preview_tree.get_children())
        for vendor, item, info, qty, price in items:
            preview_tree.insert("", "end", values=(vendor, item, info, qty, price))

    def edit_invoice():
        selected = selected_invoice.get()
        if not selected:
            messagebox.showwarning("Missing", "Please select an invoice.")
            return

        invoice_id = selected.split(" - ")[0]
        app.edit_invoice(invoice_id)
        top.destroy()

    invoice_dropdown.bind("<<ComboboxSelected>>", lambda e: load_preview())
    ttk.Button(top, text="Edit Invoice", command=edit_invoice).grid(row=2, column=1, pady=10, sticky='e')
