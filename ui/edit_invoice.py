import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from models import database
from models.generate_pdf import generate_pdf_invoice
from ui.settings import load_settings
from datetime import datetime
import os
import subprocess
import platform

class EditInvoiceWindow(tk.Toplevel):
    def __init__(self, master, invoice_db_id=None):
        super().__init__(master)
        self.settings = load_settings()

        self.title("📋 Edit Invoice - Wholesale Manager")
        if self.settings.get("window_mode", "zoomed") == "zoomed":
            self.state("zoomed")

        default_font = ('Segoe UI', 10)
        self.option_add("*Font", default_font)

        style = ttk.Style()
        style.configure("Treeview", rowheight=28, font=default_font)
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        style.map("Treeview", background=[("selected", "#cce5ff")], foreground=[("selected", "black")])

        self.even_color = self.settings["row_colors"].get("even", "#f4f4f4")
        self.odd_color = self.settings["row_colors"].get("odd", "#ffffff")

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
            ttk.Label(frame, text=f"Invoice ID: {self.selected_invoice_id}").pack(side="left")
            return
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

        # Row colors
        self.tree.tag_configure('evenrow', background=self.even_color)
        self.tree.tag_configure('oddrow', background=self.odd_color)

    # In-place editing on double-click
        def on_double_click(event):
            region = self.tree.identify('region', event.x, event.y)
            if region != 'cell':
                return

            row_id = self.tree.identify_row(event.y)
            col_id = self.tree.identify_column(event.x)
            col = int(col_id.replace('#', '')) - 1

            if col not in [2, 3, 4]:  # Only allow editing Quantity, Price, Info
                return

            x, y, width, height = self.tree.bbox(row_id, col_id)
            current_val = self.tree.item(row_id)['values'][col]

            entry = tk.Entry(self.tree)
            entry.place(x=x, y=y, width=width, height=height)
            entry.insert(0, current_val)
            entry.focus()

            def save_edit(event):
                new_val = entry.get()
                values = list(self.tree.item(row_id)['values'])

                try:
                    # Validate input for quantity and price
                    if col == 2:
                        new_val_cast = int(new_val)
                        self.tree_full_data[row_id]['quantity'] = new_val_cast
                    elif col == 3:
                        new_val_cast = float(new_val)
                        self.tree_full_data[row_id]['unit_price'] = new_val_cast
                    else:
                        new_val_cast = new_val
                        self.tree_full_data[row_id]['optional_info'] = new_val_cast

                    values[col] = new_val_cast
                    self.tree.item(row_id, values=values)

                except ValueError:
                    messagebox.showerror("Invalid Input", f"Please enter a valid number for {columns[col]}.")

                entry.destroy()

            entry.bind("<Return>", save_edit)
            entry.bind("<FocusOut>", lambda e: entry.destroy())

        self.tree.bind("<Double-1>", on_double_click)

    def setup_new_row_entry(self):
        frame = ttk.LabelFrame(self, text="➕ Add New Item")
        frame.pack(fill='x', padx=10, pady=5)
        self.new_vendor_var = tk.StringVar()
        self.new_item_var = tk.StringVar()
        self.new_quantity_var = tk.IntVar(value=self.settings["defaults"].get("quantity", 1))
        self.new_price_var = tk.DoubleVar(value=self.settings["defaults"].get("unit_price", 0.0))
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
            "vendor_id": vendor_id, "item_id": item_id, "quantity": qty,
            "unit_price": price, "optional_info": info, "existing_id": None
        }

    def update_item_dropdown(self, event=None):
        selected_vendor = self.new_vendor_var.get()
        vendor_id = next((v[0] for v in self.vendor_list if v[1] == selected_vendor), None)
        if vendor_id:
            items = database.get_items_by_vendor(vendor_id)
            self.new_item_menu['values'] = [i[1] for i in items]
            self.new_item_menu.filtered_items = items

    def delete_selected_row(self):
        if not self.tree.selection():
            messagebox.showwarning("No Selection", "Please select a row to delete.")
            return
        if self.settings.get("confirmations", {}).get("on_delete", True):
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected row?")
            if not confirm:
                return
        for row_id in self.tree.selection():
            if row_id in self.tree_full_data:
                existing_id = self.tree_full_data[row_id].get("existing_id")
                if existing_id is not None:
                    self.deleted_ids.add(existing_id)
                del self.tree_full_data[row_id]
            self.tree.delete(row_id)

        self.reapply_row_tags()
    
    def save_changes(self):
        if not self.selected_invoice_id:
            return

        if self.settings.get("confirmations", {}).get("on_save", True):
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
            if not updated_items and not self.tree.get_children():
                confirm_delete = messagebox.askyesno("Delete Empty Invoice", "There are no items left. Delete the invoice?")
                if confirm_delete:
                    database.delete_invoice(self.selected_invoice_id)
                    messagebox.showinfo("Invoice Deleted", "The empty invoice has been deleted.")

                    # ⬇️ OPTIONAL: show or refresh main window
                    if hasattr(self.master, 'deiconify'):  # for Tk root
                        self.master.deiconify()
                    elif hasattr(self.master, 'refresh'):  # for main window callback
                        self.master.refresh()

                    self.destroy()
                    return
                else:
                    return

            database.update_invoice(self.selected_invoice_id, items=updated_items, deleted_ids=self.deleted_ids)
            self.load_invoice_items_from_id(self.selected_invoice_id)
            messagebox.showinfo("Success", "Invoice updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update invoice: {e}")


    def load_invoice_items_from_id(self, invoice_id):
        self.tree.delete(*self.tree.get_children())
        self.tree_full_data.clear()
        self.invoice_items = database.get_invoice_items(invoice_id)
        self.selected_invoice_id = invoice_id
        for index, item in enumerate(self.invoice_items):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            row_id = self.tree.insert("", "end", values=(item[1], item[2], item[3], item[4], item[5]), tags=(tag,))
            self.tree_full_data[row_id] = {
                "existing_id": item[0],
                "quantity": item[3],
                "unit_price": item[4],
                "optional_info": item[5]
            }

    def load_invoice_items(self, event=None):
        selection = self.invoice_menu.get()
        if not selection:
            return
        invoice_index = self.invoice_menu.current()
        self.selected_invoice_id = self.invoices[invoice_index][0]
        self.load_invoice_items_from_id(self.selected_invoice_id)
        
    def reapply_row_tags(self):
        children = self.tree.get_children()
        for i, row_id in enumerate(children):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.item(row_id, tags=(tag,))

    def export_to_pdf(self):
        if not self.selected_invoice_id:
            messagebox.showerror("No Invoice", "Please select an invoice to export.")
            return
        default_dir = self.settings.get("pdf_output_directory", "")
        order_date = database.get_invoice_details(self.selected_invoice_id)["date"]
        formatted_date = datetime.strptime(order_date, "%Y-%m-%d").strftime("%Y%m%d")
        filename_template = self.settings.get("pdf_filename_format", "invoice_{id}_{date}")
        default_filename = filename_template.format(id=self.selected_invoice_id, date=formatted_date)
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save PDF Invoice",
            initialdir=default_dir,
            initialfile=default_filename
        )
        if not filepath:
            return
        raw_items = database.get_invoice_items(self.selected_invoice_id)
        invoice_items = [{
            "vendor_name": row["vendor_name"],
            "item_code": row["item_code"],
            "item_name": row["item_name"],
            "optional_info": row["optional_info"],
            "quantity": row["quantity"],
            "unit_price": row["unit_price"]
        } for row in raw_items]
        generate_pdf_invoice(self.selected_invoice_id, order_date, invoice_items, filepath)
        messagebox.showinfo("Success", f"PDF saved to:{filepath}")
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', filepath))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(filepath)
            elif platform.system() == 'Linux':  # Linux
                subprocess.call(('xdg-open', filepath))
            else:
                messagebox.showwarning("Unsupported OS", f"Cannot open PDF on {platform.system()}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF: {e}")
