# ui.py

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import models
import viewer


class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice Manager")
        self.current_invoice_id = None
        self.unsaved_changes = False
        self.vendors = models.get_all_vendors()
        self.items = models.get_all_items()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_home_screen()

    def show_home_screen(self):
        self.clear_window()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Welcome to the Invoice Manager", font=("Arial", 16)).pack(pady=10)
        ttk.Button(frame, text="New Invoice", command=self.new_invoice).pack(pady=5)
        ttk.Button(frame, text="View Invoices", command=self.open_invoice_viewer).pack(pady=5)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def new_invoice(self):
        self.clear_window()
        self.unsaved_changes = False
        self.current_invoice_id = None
        self.vendors = models.get_all_vendors()
        self.items = models.get_all_items()
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Invoice ID:").grid(row=0, column=0, sticky="w")
        self.invoice_id_entry = ttk.Entry(frame)
        self.invoice_id_entry.insert(0, "AUTO")
        self.invoice_id_entry.grid(row=0, column=1, padx=5, sticky="ew")

        ttk.Label(frame, text="Date:").grid(row=0, column=2, sticky="w")
        self.date_entry = ttk.Entry(frame)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=3, padx=5, sticky="ew")

        columns = ("Vendor", "Item", "Item Info", "Quantity", "Unit Price")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=10)
        self.tree.bind("<Double-1>", self.edit_cell)

        for i in range(10):
            self.tree.insert("", "end", values=("Select Vendor", "Select Item", "", "", ""))
            if i % 2 == 0:
                self.tree.tag_configure("evenrow", background="#f0f0ff")
                self.tree.item(self.tree.get_children()[-1], tags=("evenrow",))

        ttk.Button(frame, text="Save Invoice", command=self.save_invoice).grid(row=2, column=2, sticky="e", pady=5)
        ttk.Button(frame, text="Cancel Invoice", command=self.show_home_screen).grid(row=2, column=3, sticky="e", pady=5)

        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)
        frame.rowconfigure(1, weight=1)

    def edit_cell(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        col_index = int(col.replace("#", "")) - 1

        x, y, width, height = self.tree.bbox(row_id, col)
        value = self.tree.set(row_id, self.tree["columns"][col_index])

        def save_edit(new_value):
            self.tree.set(row_id, self.tree["columns"][col_index], new_value)
            widget.destroy()

        if col_index == 0:
            widget = ttk.Combobox(self.tree, values=self.vendors, state="readonly")
            widget.set(value)
            widget.place(x=x, y=y, width=width, height=height)
            widget.bind("<<ComboboxSelected>>", lambda e: (self.update_vendor_and_filter_items(row_id, widget.get()), widget.destroy()))
        elif col_index == 1:
            vendor = self.tree.set(row_id, "Vendor")
            items = models.get_items_for_vendor(vendor) if vendor != "Select Vendor" else self.items
            widget = ttk.Combobox(self.tree, values=items, state="readonly")
            widget.set(value)
            widget.place(x=x, y=y, width=width, height=height)
            widget.bind("<<ComboboxSelected>>", lambda e: (save_edit(widget.get()), widget.destroy()))
        else:
            widget = ttk.Entry(self.tree)
            widget.insert(0, value)
            widget.place(x=x, y=y, width=width, height=height)
            widget.focus()
            widget.bind("<Return>", lambda e: save_edit(widget.get()))
            widget.bind("<FocusOut>", lambda e: save_edit(widget.get()))

    def update_vendor_and_filter_items(self, row_id, vendor_name):
        self.tree.set(row_id, "Vendor", vendor_name)
        current_item = self.tree.set(row_id, "Item")
        valid_items = models.get_items_for_vendor(vendor_name)
        if current_item not in valid_items:
            self.tree.set(row_id, "Item", "Select Item")

    def save_invoice(self):
        invoice_id = self.invoice_id_entry.get().strip()
        date = self.date_entry.get().strip()

        if not date:
            messagebox.showerror("Error", "Date is required.")
            return

        if invoice_id == "AUTO":
            invoice_id = models.generate_next_invoice_id()
            self.invoice_id_entry.delete(0, tk.END)
            self.invoice_id_entry.insert(0, invoice_id)

        items = []
        for row_id in self.tree.get_children():
            vendor, item, info, qty, price = self.tree.item(row_id)["values"]
            if vendor == "Select Vendor" or item == "Select Item":
                continue
            try:
                qty = int(qty)
                price = float(price)
                items.append((vendor, item, info, qty, price))
            except:
                messagebox.showerror("Error", "Invalid quantity or price.")
                return

        if not items:
            messagebox.showwarning("Empty Invoice", "Please add at least one item.")
            return

        if models.invoice_exists(invoice_id):
            if not messagebox.askyesno("Overwrite?", f"Invoice {invoice_id} exists. Overwrite?"):
                return
            models.update_invoice(invoice_id, date, items)
        else:
            models.save_invoice_to_db(invoice_id, date, items)

        messagebox.showinfo("Success", f"Invoice {invoice_id} saved successfully.")
        self.show_home_screen()

    def open_invoice_viewer(self):
        viewer.open(self)

    def on_close(self):
        if self.unsaved_changes:
            if not messagebox.askyesno("Quit", "You have unsaved changes. Quit anyway?"):
                return
        self.root.destroy()
        
    def edit_invoice(self, invoice_id):
        self.clear_window()
        self.current_invoice_id = invoice_id
        self.unsaved_changes = False

        invoice = models.get_invoice_by_id(invoice_id)
        items = models.get_invoice_items(invoice_id)

        self.vendors = models.get_all_vendors()
        self.items = models.get_all_items()

        self.setup_ui()

        self.invoice_id_entry.delete(0, tk.END)
        self.invoice_id_entry.insert(0, invoice_id)

        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, invoice[1])  # Assuming invoice is (id, date)

        self.tree.delete(*self.tree.get_children())
        for i, (vendor, item, info, qty, price) in enumerate(items):
            self.tree.insert("", "end", values=(vendor, item, info, qty, price),
                             tags=("evenrow",) if i % 2 == 0 else ())

        # Fill remaining rows to get to 10 total rows
        for i in range(len(items), 10):
            self.tree.insert("", "end", values=("Select Vendor", "Select Item", "", "", ""),
                             tags=("evenrow",) if i % 2 == 0 else ())
