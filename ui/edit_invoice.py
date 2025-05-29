import tkinter as tk
from tkinter import ttk, messagebox
from models import database

class EditInvoiceWindow(tk.Toplevel):
    def __init__(self, master, on_close=None):
        super().__init__(master)
        self.title("Edit Invoice")
        self.geometry("1200x650")
        self.on_close = on_close

        self.invoices = database.get_all_invoices()
        self.selected_invoice_id = None
        self.invoice_items = []
        self.tree_full_data = {}  # row_id -> item dict

        self.setup_invoice_selector()
        self.setup_treeview()
        self.setup_edit_fields()
        self.setup_new_row_entry()
        self.setup_buttons()

    def setup_invoice_selector(self):
        frame = ttk.Frame(self)
        frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame, text="Select Invoice:").pack(side="left")
        self.invoice_var = tk.StringVar()
        invoice_options = [f"{inv[1]} | {inv[2]}" for inv in self.invoices]
        self.invoice_menu = ttk.Combobox(frame, textvariable=self.invoice_var, values=invoice_options, state="readonly", width=40)
        self.invoice_menu.pack(side="left", padx=10)
        self.invoice_menu.bind("<<ComboboxSelected>>", self.load_invoice_items)

    def setup_treeview(self):
        columns = ("vendor", "item", "quantity", "price", "optional_info")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, anchor="center")
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

    def setup_edit_fields(self):
        frame = ttk.Frame(self)
        frame.pack(fill='x', padx=10, pady=5)

        self.quantity_var = tk.IntVar()
        self.price_var = tk.DoubleVar()
        self.info_var = tk.StringVar()

        ttk.Label(frame, text="Quantity:").grid(row=0, column=0)
        ttk.Entry(frame, textvariable=self.quantity_var, width=10).grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Unit Price:").grid(row=0, column=2)
        ttk.Entry(frame, textvariable=self.price_var, width=10).grid(row=0, column=3, padx=5)

        ttk.Label(frame, text="Optional Info:").grid(row=0, column=4)
        ttk.Entry(frame, textvariable=self.info_var, width=40).grid(row=0, column=5, padx=5)

        ttk.Button(frame, text="Update Selected Row", command=self.update_selected_row).grid(row=0, column=6, padx=5)

    def setup_new_row_entry(self):
        frame = ttk.LabelFrame(self, text="Add New Item")
        frame.pack(fill='x', padx=10, pady=5)

        self.new_vendor_var = tk.StringVar()
        self.new_item_var = tk.StringVar()
        self.new_quantity_var = tk.IntVar()
        self.new_price_var = tk.DoubleVar()
        self.new_info_var = tk.StringVar()

        self.vendor_list = database.get_all_vendors()
        ttk.Label(frame, text="Vendor:").grid(row=0, column=0)
        self.new_vendor_menu = ttk.Combobox(frame, textvariable=self.new_vendor_var, values=[v[1] for v in self.vendor_list], state="readonly", width=20)
        self.new_vendor_menu.grid(row=0, column=1, padx=5)
        self.new_vendor_menu.bind("<<ComboboxSelected>>", self.update_item_dropdown)

        ttk.Label(frame, text="Item:").grid(row=0, column=2)
        self.new_item_menu = ttk.Combobox(frame, textvariable=self.new_item_var, state="readonly", width=20)
        self.new_item_menu.grid(row=0, column=3, padx=5)

        ttk.Label(frame, text="Qty:").grid(row=0, column=4)
        ttk.Entry(frame, textvariable=self.new_quantity_var, width=5).grid(row=0, column=5)

        ttk.Label(frame, text="Unit $:").grid(row=0, column=6)
        ttk.Entry(frame, textvariable=self.new_price_var, width=7).grid(row=0, column=7)

        ttk.Label(frame, text="Info:").grid(row=0, column=8)
        ttk.Entry(frame, textvariable=self.new_info_var, width=30).grid(row=0, column=9)

        ttk.Button(frame, text="Add Row", command=self.add_new_row_to_table).grid(row=0, column=10, padx=10)

    def setup_buttons(self):
        frame = ttk.Frame(self)
        frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(frame, text="Delete Selected Row", command=self.delete_selected_row).pack(side="left", padx=5)
        ttk.Button(frame, text="Export Invoice", command=self.export_invoice).pack(side="left", padx=5)
        ttk.Button(frame, text="Save Changes", command=self.save_changes).pack(side="right")

    def load_invoice_items(self, event=None):
        selection = self.invoice_menu.get()
        if not selection:
            return

        invoice_index = self.invoice_menu.current()
        self.selected_invoice_id = self.invoices[invoice_index][0]

        self.tree.delete(*self.tree.get_children())
        self.tree_full_data.clear()
        self.invoice_items = database.get_invoice_items(self.selected_invoice_id)

        for item in self.invoice_items:
            visible = item[1:]
            row_id = self.tree.insert("", "end", values=visible)
            self.tree_full_data[row_id] = {
                "existing_id": item[0],
                "quantity": item[3],
                "unit_price": item[4],
                "optional_info": item[5]
            }

    def update_item_dropdown(self, event=None):
        selected_vendor = self.new_vendor_var.get()
        vendor_id = next((v[0] for v in self.vendor_list if v[1] == selected_vendor), None)
        if vendor_id:
            items = database.get_items_by_vendor(vendor_id)
            self.new_item_menu['values'] = [i[1] for i in items]
            self.new_item_menu.filtered_items = items

    def add_new_row_to_table(self):
        vendor_name = self.new_vendor_var.get()
        item_name = self.new_item_var.get()
        qty = self.new_quantity_var.get()
        price = self.new_price_var.get()
        info = self.new_info_var.get()

        if not vendor_name or not item_name:
            messagebox.showwarning("Missing Info", "Please select both vendor and item.")
            return

        vendor_id = next((v[0] for v in self.vendor_list if v[1] == vendor_name), None)
        item_id = next((i[0] for i in self.new_item_menu.filtered_items if i[1] == item_name), None)

        row_id = self.tree.insert("", "end", values=(vendor_name, item_name, qty, price, info))
        self.tree_full_data[row_id] = {
            "vendor_id": vendor_id,
            "item_id": item_id,
            "quantity": qty,
            "unit_price": price,
            "optional_info": info,
            "existing_id": None
        }

        self.new_vendor_var.set("")
        self.new_item_var.set("")
        self.new_quantity_var.set(0)
        self.new_price_var.set(0.0)
        self.new_info_var.set("")

    def update_selected_row(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a row to update.")
            return

        try:
            quantity = self.quantity_var.get()
            price = self.price_var.get()
            info = self.info_var.get()

            if quantity < 0 or price < 0:
                raise ValueError

            row_id = selected[0]
            values = self.tree.item(row_id, "values")
            updated = (values[0], values[1], quantity, price, info)
            self.tree.item(row_id, values=updated)
            self.tree_full_data[row_id]["quantity"] = quantity
            self.tree_full_data[row_id]["unit_price"] = price
            self.tree_full_data[row_id]["optional_info"] = info

        except Exception:
            messagebox.showerror("Invalid Input", "Enter valid quantity and unit price.")

    def delete_selected_row(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a row to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected row?")
        if not confirm:
            return

        for row_id in selected:
            self.tree.delete(row_id)
            if row_id in self.tree_full_data:
                del self.tree_full_data[row_id]

    def save_changes(self):
        if not self.selected_invoice_id:
            return

        confirm = messagebox.askyesno("Save Changes", "Are you sure you want to save all changes to this invoice?")
        if not confirm:
            return

        updated_items = []

        for row_id in self.tree.get_children():
            values = self.tree.item(row_id)["values"]
            data = self.tree_full_data[row_id]

            if data.get("existing_id") is not None:
                updated_items.append({
                    "existing_id": data["existing_id"],
                    "quantity": data["quantity"],
                    "unit_price": data["unit_price"],
                    "optional_info": data["optional_info"]
                })
            else:
                updated_items.append({
                    "vendor_id": data["vendor_id"],
                    "item_id": data["item_id"],
                    "quantity": data["quantity"],
                    "unit_price": data["unit_price"],
                    "optional_info": data["optional_info"]
                })

        try:
            database.update_invoice(self.selected_invoice_id, user_info="", items=updated_items)
            messagebox.showinfo("Success", "Invoice updated successfully.")
            if self.on_close:
                self.on_close()
            else:
                self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update invoice: {e}")

    def export_invoice(self):
        if not self.selected_invoice_id:
            messagebox.showwarning("No Invoice", "Please select an invoice to export.")
            return

        items = self.tree.get_children()
        if not items:
            messagebox.showinfo("Empty", "There are no items to export.")
            return

        lines = []
        lines.append(f"Invoice Export\n{'='*40}")
        lines.append(f"Invoice ID: {self.invoice_var.get().split('|')[0].strip()}")
        lines.append("")

        for row_id in items:
            values = self.tree.item(row_id)['values']
            lines.append(f"{values[0]} - {values[1]} | Qty: {values[2]} | ${values[3]:.2f} | Info: {values[4]}")

        file_name = f"invoice_{self.selected_invoice_id}.txt"
        with open(file_name, "w") as f:
            f.write("\n".join(lines))

        messagebox.showinfo("Export Complete", f"Invoice exported to {file_name}")
