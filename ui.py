import tkinter as tk
from tkinter import ttk, messagebox
from models import create_invoice, search_product_across_vendors
from datetime import date
from manage_invoices_window import ManageInvoicesWindow

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Invoice Generator")

        self.create_menu()
        self.setup_ui()

    def create_menu(self):
        menubar = tk.Menu(self.root)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Invoice", command=self.clear_invoice)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Manage Menu
        manage_menu = tk.Menu(menubar, tearoff=0)
        manage_menu.add_command(label="Manage Invoices", command=self.manage_invoices)
        manage_menu.add_command(label="Manage Vendors", command=self.manage_vendors)
        menubar.add_cascade(label="Manage", menu=manage_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Wholesale Program v1.0"))
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")  # Use 'clam' or 'alt' for better default appearance
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))

        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(frame, text="Wholesale Invoice Builder", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=5, pady=(0, 15)
        )

        # Search bar
        ttk.Label(frame, text="Search Product:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(frame, textvariable=self.search_var)
        search_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        search_entry.bind("<KeyRelease>", self.perform_search_event)

        # Search results table
        self.search_results = ttk.Treeview(
            frame, columns=("ID", "Product", "Vendor", "Price"), show="headings", height=5
        )
        for col in ("ID", "Product", "Vendor", "Price"):
            self.search_results.heading(col, text=col)
            self.search_results.column(col, anchor="center")

        self.search_results.column("ID", width=60)
        self.search_results.column("Product", width=200)
        self.search_results.column("Vendor", width=160)
        self.search_results.column("Price", width=80)
        self.search_results.grid(row=2, column=0, columnspan=5, sticky="ew", padx=5, pady=(0, 10))

        # Quantity input and add button
        ttk.Label(frame, text="Quantity:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.qty_var = tk.IntVar(value=1)
        ttk.Entry(frame, textvariable=self.qty_var, width=6).grid(row=3, column=1, sticky="w", padx=5, pady=5)
        ttk.Button(frame, text="Add Product to Invoice", command=self.add_selected_product).grid(
            row=3, column=2, padx=5, pady=5
        )

        # Invoice table
        self.tree = ttk.Treeview(
            frame, columns=("Vendor", "Product", "Quantity", "Unit Price", "Total"), show="headings"
        )
        for col in ("Vendor", "Product", "Quantity", "Unit Price", "Total"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        self.tree.column("Vendor", width=160)
        self.tree.column("Product", width=200)
        self.tree.column("Quantity", width=80)
        self.tree.column("Unit Price", width=100)
        self.tree.column("Total", width=100)

        self.tree.grid(row=4, column=0, columnspan=5, sticky="nsew", padx=5, pady=10)
        self.tree.bind("<Double-1>", self.edit_cell)

        # Generate Invoice Button
        ttk.Button(frame, text="Generate Invoice", command=self.generate_invoice).grid(
            row=5, column=4, padx=5, pady=(10, 0), sticky="e"
        )

        # Layout resizing behavior
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)


    def clear_invoice(self):
        self.tree.delete(*self.tree.get_children())
        self.qty_var.set(1)
        self.search_var.set("")

    def manage_invoices(self):
        ManageInvoicesWindow(self.root)

    def manage_vendors(self):
        messagebox.showinfo("Manage Vendors", "This feature is not yet implemented.")

    def perform_search_event(self, event):
        self.perform_search()

    def perform_search(self):
        query = self.search_var.get().strip()
        self.search_results.delete(*self.search_results.get_children())
        if not query:
            return
        results = search_product_across_vendors(query)
        for pid, pname, price, vname in results:
            self.search_results.insert("", "end", values=(pid, pname, vname, f"{price:.2f}"), tags=(str(pid),))

    def add_selected_product(self):
        selected = self.search_results.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product from the search results.")
            return

        qty = self.qty_var.get()
        if qty <= 0:
            messagebox.showwarning("Invalid Quantity", "Quantity must be greater than 0.")
            return

        item = self.search_results.item(selected[0])
        pid, pname, vname, price_str = item["values"]
        pid = int(pid)
        price = float(price_str)
        total = qty * price

        self.tree.insert('', 'end', values=(vname, pname, qty, f"{price:.2f}", f"{total:.2f}"), tags=(str(pid),))

    def edit_cell(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        col_index = int(column.replace('#', '')) - 1
        if col_index not in [2, 3]:  # Only allow editing Quantity or Unit Price
            return

        old_val = self.tree.item(item, 'values')[col_index]
        x, y, width, height = self.tree.bbox(item, column)

        entry = ttk.Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, old_val)
        entry.focus()

        def save_edit(event):
            new_val = entry.get()
            values = list(self.tree.item(item, 'values'))

            try:
                if col_index == 2:  # Quantity
                    qty = int(new_val)
                    price = float(values[3])
                elif col_index == 3:  # Unit Price
                    qty = int(values[2])
                    price = float(new_val)
                else:
                    return
                values[2] = qty
                values[3] = f"{price:.2f}"
                values[4] = f"{qty * price:.2f}"
                self.tree.item(item, values=values)
            except ValueError:
                messagebox.showerror("Invalid Entry", "Please enter numeric values.")
            finally:
                entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    def generate_invoice(self):
        items = []

        for row_id in self.tree.get_children():
            vendor, name, qty_str, price_str, total_str = self.tree.item(row_id)['values']
            pid = self.tree.item(row_id)['tags'][0]  # Get product_id from tag
            qty = int(qty_str)
            price = float(price_str)
            items.append((int(pid), qty, price))

        if not items:
            messagebox.showwarning("Missing Data", "Add at least one product to the invoice.")
            return

        invoice_id = create_invoice("Internal", str(date.today()), items)
        messagebox.showinfo("Invoice Created", f"Invoice #{invoice_id} created.")
        self.clear_invoice()
