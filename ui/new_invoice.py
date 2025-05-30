import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import uuid

from models import database

class NewInvoiceWindow(tk.Toplevel):
    def __init__(self, master, on_close=None):
        super().__init__(master)
        self.title("Create New Invoice")
        self.geometry("1200x600")
        self.on_close = on_close

        self.vendor_options = database.get_all_vendors()
        self.items_data = []

        self.setup_header()
        self.setup_form()
        self.setup_table()
        self.setup_footer()

    def setup_header(self):
        frame = ttk.Frame(self)
        frame.pack(fill='x', padx=10, pady=10)

        invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
        date = datetime.now().strftime("%Y-%m-%d")

        ttk.Label(frame, text="Invoice ID:").grid(row=0, column=0, sticky='e')
        self.invoice_id_var = tk.StringVar(value=invoice_id)
        ttk.Entry(frame, textvariable=self.invoice_id_var, state='readonly').grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Date:").grid(row=0, column=2, sticky='e')
        self.date_var = tk.StringVar(value=date)
        ttk.Entry(frame, textvariable=self.date_var, state='readonly').grid(row=0, column=3, padx=5)

    def setup_form(self):
        frame = ttk.Frame(self)
        frame.pack(fill='x', padx=10)

        # Vendor dropdown
        ttk.Label(frame, text="Vendor:").grid(row=0, column=0, sticky='e')
        self.vendor_var = tk.StringVar()
        self.vendor_menu = ttk.Combobox(frame, textvariable=self.vendor_var, state="readonly")
        self.vendor_menu['values'] = [v[1] for v in self.vendor_options]
        self.vendor_menu.grid(row=0, column=1, padx=5)
        self.vendor_menu.bind("<<ComboboxSelected>>", self.update_items_menu)

        # Item dropdown
        ttk.Label(frame, text="Item:").grid(row=0, column=2, sticky='e')
        self.item_var = tk.StringVar()
        self.item_menu = ttk.Combobox(frame, textvariable=self.item_var, state="readonly")
        self.item_menu.grid(row=0, column=3, padx=5)

        # Quantity
        ttk.Label(frame, text="Quantity:").grid(row=1, column=0, sticky='e')
        self.quantity_var = tk.IntVar()
        ttk.Entry(frame, textvariable=self.quantity_var).grid(row=1, column=1, padx=5)

        # Unit Price
        ttk.Label(frame, text="Unit Price:").grid(row=1, column=2, sticky='e')
        self.price_var = tk.DoubleVar()
        ttk.Entry(frame, textvariable=self.price_var).grid(row=1, column=3, padx=5)

        # Optional Info
        ttk.Label(frame, text="Optional Item Info:").grid(row=2, column=0, sticky='e')
        self.info_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.info_var, width=60).grid(row=2, column=1, columnspan=3, sticky='we', padx=5)

        # Add Button
        ttk.Button(frame, text="Add Item", command=self.add_item).grid(row=3, column=3, pady=10, sticky='e')

    def setup_table(self):
        columns = ("vendor", "item", "quantity", "price", "info")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        self.tree.tag_configure('oddrow', background='#f0f0ff')
        self.tree.tag_configure('evenrow', background='#ffffff')
        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, stretch=True)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.on_double_click)


    def setup_footer(self):
        frame = ttk.Frame(self)
        frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(frame, text="Delete Selected Row", command=self.delete_selected_row).pack(side="left")
        ttk.Button(frame, text="Save Invoice", command=self.save_invoice).pack(side="right")

    def update_items_menu(self, event=None):
        selected_vendor = self.vendor_var.get()
        vendor_id = next((v[0] for v in self.vendor_options if v[1] == selected_vendor), None)
        if vendor_id:
            items = database.get_items_by_vendor(vendor_id)
            self.item_menu['values'] = [i[1] for i in items]
            self.item_menu.filtered_items = items

    def add_item(self):
        vendor_name = self.vendor_var.get()
        item_name = self.item_var.get()
        quantity = self.quantity_var.get()
        unit_price = self.price_var.get()
        info = self.info_var.get()

        if not vendor_name or not item_name:
            messagebox.showwarning("Missing Info", "Vendor and Item must be selected.")
            return

        vendor_id = next((v[0] for v in self.vendor_options if v[1] == vendor_name), None)
        item_id = next((i[0] for i in self.item_menu.filtered_items if i[1] == item_name), None)

        self.items_data.append({
            "vendor_id": vendor_id,
            "item_id": item_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "optional_info": info
        })

        self.tree.insert("", "end", values=(vendor_name, item_name, quantity, f"${unit_price:.2f}", info))

        # Clear inputs for next row
        self.item_var.set("")
        self.quantity_var.set(0)
        self.price_var.set(0.0)
        self.info_var.set("")

    def save_invoice(self):
        if not self.items_data:
            messagebox.showwarning("No Items", "Add at least one item before saving.")
            return

        try:
            invoice_items = [
                {
                    "vendor_id": item["vendor_id"],
                    "item_id": item["item_id"],
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"]
                    # optional_info not stored in DB yet
                }
                for item in self.items_data
            ]

            database.create_invoice(
                self.invoice_id_var.get(),
                self.date_var.get(),
                "",  # user_info replaced by nothing here
                invoice_items
            )
            messagebox.showinfo("Success", "Invoice saved successfully.")
            if self.on_close:
                self.on_close()
            else:
                self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save invoice: {e}")


    def on_double_click(self, event):
        region = self.tree.identify('region', event.x, event.y)
        if region != 'cell':
            return
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        col = int(col_id.replace('#', '')) - 1
        if col not in [2, 3, 4]:
            return  # Only quantity, price, info

        x, y, w, h = self.tree.bbox(row_id, col_id)
        value = self.tree.item(row_id)['values'][col]
        entry = tk.Entry(self.tree)
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, value)
        entry.focus()

        def save_edit(event):
            new_val = entry.get()
            values = list(self.tree.item(row_id)['values'])
            values[col] = new_val
            self.tree.item(row_id, values=values)

            # Update items_data — match by row index
            index = self.tree.index(row_id)
            if col == 2:
                self.items_data[index]["quantity"] = int(new_val)
            elif col == 3:
                self.items_data[index]["unit_price"] = float(new_val.replace('$', '').strip())
            elif col == 4:
                self.items_data[index]["optional_info"] = new_val

            entry.destroy()

        entry.bind('<Return>', save_edit)
        entry.bind('<FocusOut>', lambda e: entry.destroy())


    def delete_selected_row(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a row to delete.")
            return

        confirm = messagebox.askyesno("Confirm", "Delete selected row?")
        if not confirm:
            return

        for row_id in selected:
            index = self.tree.index(row_id)
            if index < len(self.items_data):
                del self.items_data[index]
            self.tree.delete(row_id)

