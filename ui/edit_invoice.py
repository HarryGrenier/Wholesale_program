
import tkinter as tk
from tkinter import ttk, messagebox
from models import database
from models.generate_pdf import generate_pdf_invoice
import tkinter.filedialog as filedialog

class EditInvoiceWindow(tk.Toplevel):
    def __init__(self, master, invoice_db_id=None):
        super().__init__(master)
        self.title("📋 Edit Invoice - Wholesale Manager")
        self.state("zoomed")

        default_font = ('Segoe UI', 10)
        self.option_add("*Font", default_font)

        style = ttk.Style()
        style.configure("Treeview", rowheight=28, font=default_font)
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        style.map("Treeview",
            background=[("selected", "#cce5ff")],
            foreground=[("selected", "black")]
        )

        self.selected_invoice_id = invoice_db_id
        self.invoice_items = []
        self.tree_full_data = {}
        self.deleted_ids = set()

        if invoice_db_id is None:
            self.invoices = database.get_all_invoices()
        else:
            self.invoices = []

        self.setup_invoice_selector()
        ttk.Separator(self, orient="horizontal").pack(fill='x', padx=10, pady=5)
        self.setup_treeview()
        ttk.Separator(self, orient="horizontal").pack(fill='x', padx=10, pady=5)
        self.setup_new_row_entry()
        ttk.Separator(self, orient="horizontal").pack(fill='x', padx=10, pady=5)
        self.setup_buttons()

        if invoice_db_id:
            self.load_invoice_items_from_id(invoice_db_id)

    def setup_invoice_selector(self):
        frame = ttk.LabelFrame(self, text="📄 Invoice Selection")
        frame.pack(fill='x', padx=10, pady=5)

        if self.selected_invoice_id:
            Id_string = f"Invoice ID: {self.selected_invoice_id}"
            ttk.Label(frame, text=Id_string).pack(side="left")
            return

        ttk.Label(frame, text="Select Invoice:").pack(side="left")
        self.invoice_var = tk.StringVar()
        invoice_options = [f"{inv[1]} | Invoice ID: {inv[0]}" for inv in self.invoices]
        self.invoice_menu = ttk.Combobox(frame, textvariable=self.invoice_var, values=invoice_options, state="readonly", width=40)
        self.invoice_menu.pack(side="left", padx=10)
        self.invoice_menu.bind("<<ComboboxSelected>>", self.load_invoice_items)

    def setup_treeview(self):
        tree_frame = ttk.LabelFrame(self, text="📦 Line Items")
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ("vendor", "item", "quantity", "price", "optional_info")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=18)
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, anchor="center")
        self.tree.pack(fill='both', expand=True)

        self.tree.tag_configure('evenrow', background='#eaf3fc')  # Very light blue
        self.tree.tag_configure('oddrow', background='#ffffff')   # White


        def on_double_click(event):
            region = self.tree.identify('region', event.x, event.y)
            if region != 'cell': return
            row_id = self.tree.identify_row(event.y)
            col_id = self.tree.identify_column(event.x)
            col = int(col_id.replace('#', '')) - 1
            if col not in [2, 3, 4]: return
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
                if row_id in self.tree_full_data:
                    if col == 2:
                        self.tree_full_data[row_id]['quantity'] = int(new_val)
                    elif col == 3:
                        self.tree_full_data[row_id]['unit_price'] = float(new_val)
                    elif col == 4:
                        self.tree_full_data[row_id]['optional_info'] = new_val
                entry.destroy()

            entry.bind('<Return>', save_edit)
            entry.bind('<FocusOut>', lambda e: entry.destroy())

        self.tree.bind("<Double-1>", on_double_click)

    def setup_new_row_entry(self):
        frame = ttk.LabelFrame(self, text="➕ Add New Item")
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
        frame = ttk.LabelFrame(self, text="🛠 Actions")
        frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(frame, text="Delete Selected Row", command=self.delete_selected_row).pack(side="left", padx=5)
        ttk.Button(frame, text="Save Changes", command=self.save_changes).pack(side="right")
        ttk.Button(frame, text="Export to PDF", command=self.export_to_pdf).pack(side="right", padx=5)


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

        index = len(self.tree.get_children())
        tag = 'evenrow' if index % 2 == 0 else 'oddrow'

        row_id = self.tree.insert("", "end", values=(vendor_name, item_name, qty, price, info), tags=(tag,))
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

    
    def load_invoice_items_from_id(self, invoice_id):
        self.tree.delete(*self.tree.get_children())
        self.tree_full_data.clear()
        self.invoice_items = database.get_invoice_items(invoice_id)
        self.selected_invoice_id = invoice_id

        for index, item in enumerate(self.invoice_items):
            item_id = item[0]
            vendor_name = item[1]
            item_name = item[2]
            quantity = item[3]
            unit_price = item[4]
            optional_info = item[5]

            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            row_id = self.tree.insert("", "end", values=(vendor_name, item_name, quantity, unit_price, optional_info), tags=(tag,))
            self.tree_full_data[row_id] = {
                "existing_id": item_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "optional_info": optional_info
            }
    def load_invoice_items(self, event=None):
        selection = self.invoice_menu.get()
        if not selection:
            return

        invoice_index = self.invoice_menu.current()
        self.selected_invoice_id = self.invoices[invoice_index][0]

        self.tree.delete(*self.tree.get_children())
        self.tree_full_data.clear()
        self.invoice_items = database.get_invoice_items(self.selected_invoice_id)

        for index, item in enumerate(self.invoice_items):
            item_id = item[0]
            vendor_name = item[1]
            item_name = item[2]
            quantity = item[3]
            unit_price = item[4]
            optional_info = item[5]

            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            row_id = self.tree.insert("", "end", values=(vendor_name, item_name, quantity, unit_price, optional_info), tags=(tag,))
            self.tree_full_data[row_id] = {
                "existing_id": item_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "optional_info": optional_info
            }

        first = self.tree.get_children()
        if first:
            self.tree.selection_set(first[0])
            self.tree.focus(first[0])


    def delete_selected_row(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a row to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected row?")
        if not confirm:
            return

        for row_id in selected:
            if row_id in self.tree_full_data:
                existing_id = self.tree_full_data[row_id].get("existing_id")
                if existing_id is not None:
                    self.deleted_ids.add(existing_id)
                del self.tree_full_data[row_id]
            self.tree.delete(row_id)

    def save_changes(self):
        if not self.selected_invoice_id:
            return

        confirm = messagebox.askyesno("Save Changes", "Are you sure you want to save all changes to this invoice?")
        if not confirm:
            return

        updated_items = []

        for row_id in self.tree.get_children():
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
            database.update_invoice(self.selected_invoice_id, items=updated_items, deleted_ids=self.deleted_ids)
            self.load_invoice_items_from_id(self.selected_invoice_id)  # 🔁 Reload contents
            messagebox.showinfo("Success", "Invoice updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update invoice: {e}")
    def export_to_pdf(self):
        if not self.selected_invoice_id:
            messagebox.showerror("No Invoice", "Please select an invoice to export.")
            return

        # Ask where to save the file
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save PDF Invoice"
        )
        if not filepath:
            return

        # Fetch invoice date and items from database
        from models.database import get_invoice_details, get_invoice_items

        order_date = get_invoice_details(self.selected_invoice_id)["date"]
        raw_items = get_invoice_items(self.selected_invoice_id)

        # Ensure each row has item_id, item_name, vendor_name, quantity, unit_price, optional_info
        invoice_items = []
        for row in raw_items:
            invoice_items.append({
                "vendor_name": row["vendor_name"],
                "item_code": row["item_code"],
                "item_name": row["item_name"],
                "optional_info": row["optional_info"],
                "quantity": row["quantity"],
                "unit_price": row["unit_price"]
            })

        # Call PDF generator
        generate_pdf_invoice(self.selected_invoice_id, order_date, invoice_items, filepath)
        messagebox.showinfo("Success", f"PDF saved to:\n{filepath}")

    def export_invoice(self):
        if not self.selected_invoice_id:
            messagebox.showwarning("No Invoice", "Please select an invoice to export.")
            return

        items = self.tree.get_children()
        if not items:
            messagebox.showinfo("Empty", "There are no items to export.")
            return

        lines = []
        lines.append(f"Invoice Export{'='*40}")
        lines.append(f"Invoice ID: {self.selected_invoice_id}")
        lines.append("")

        for row_id in items:
            values = self.tree.item(row_id)['values']
            lines.append(f"{values[0]} - {values[1]} | Qty: {values[2]} | ${values[3]:.2f} | Info: {values[4]}")

        file_name = f"invoice_{self.selected_invoice_id}.pdf"
        with open(file_name, "w") as f:
            f.write("\n".join(lines))

        messagebox.showinfo("Export Complete", f"Invoice exported to {file_name}")
