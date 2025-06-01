import tkinter as tk
from tkinter import ttk, messagebox
from models import database

class ManageItemsWindow(tk.Toplevel):
    def __init__(self, master, on_close=None):
        super().__init__(master)
        self.title("Manage Items")
        self.geometry("600x500")
        self.on_close = on_close

        self.selected_item_id = None
        self.setup_widgets()
        self.refresh_vendor_filter()
        self.refresh_item_list()

    def setup_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(top_frame, text="Filter by Vendor:").pack(side="left")
        self.vendor_filter_var = tk.StringVar()
        self.vendor_list = database.get_all_vendors()
        self.vendor_menu = ttk.Combobox(top_frame, textvariable=self.vendor_filter_var, state="readonly")
        self.vendor_menu.pack(side="left", padx=5)
        self.vendor_menu['values'] = ["All"] + [v[1] for v in self.vendor_list]
        self.vendor_menu.current(0)
        self.vendor_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_item_list())

        self.item_listbox = tk.Listbox(self, height=15)
        self.item_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.item_listbox.bind("<<ListboxSelect>>", self.on_select_item)

        entry_frame = ttk.Frame(self)
        entry_frame.pack(pady=10)

        # Item Name
        ttk.Label(entry_frame, text="Item Name:").pack(side="left", padx=(0, 2))
        self.item_name_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.item_name_var, width=30).pack(side="left", padx=(0, 10))

        # Item Code
        ttk.Label(entry_frame, text="Item Code:").pack(side="left", padx=(0, 2))
        self.item_code_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.item_code_var, width=15).pack(side="left", padx=(0, 10))

        # Vendor
        ttk.Label(entry_frame, text="Vendor:").pack(side="left", padx=(0, 2))
        self.vendor_select_var = tk.StringVar()
        self.vendor_select_menu = ttk.Combobox(entry_frame, textvariable=self.vendor_select_var, state="readonly", width=20)
        self.vendor_select_menu['values'] = [v[1] for v in self.vendor_list]
        self.vendor_select_menu.pack(side="left", padx=(0, 10))

        button_frame = ttk.Frame(self)
        button_frame.pack()

        ttk.Button(button_frame, text="Add", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Rename", command=self.rename_item).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_item).pack(side="left", padx=5)

    def refresh_vendor_filter(self):
        self.vendor_list = database.get_all_vendors()
        self.vendor_menu['values'] = ["All"] + [v[1] for v in self.vendor_list]
        self.vendor_select_menu['values'] = [v[1] for v in self.vendor_list]

    def refresh_item_list(self):
        self.item_listbox.delete(0, tk.END)
        self.items = database.get_all_items()

        selected_vendor_name = self.vendor_filter_var.get()
        if selected_vendor_name and selected_vendor_name != "All":
            selected_vendor_id = next((v[0] for v in self.vendor_list if v[1] == selected_vendor_name), None)
            self.filtered_items = [item for item in self.items if item[2] == selected_vendor_id]
        else:
            self.filtered_items = self.items

        for i in self.filtered_items:
            vendor_name = next((v[1] for v in self.vendor_list if v[0] == i[2]), "")
            self.item_listbox.insert(tk.END, f"{i[1]} ({vendor_name})")

        self.selected_item_id = None
        self.item_name_var.set("")
        self.vendor_select_var.set("")

    def on_select_item(self, event=None):
        selection = self.item_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        item = self.filtered_items[index]
        self.selected_item_id = item[0]
        self.item_name_var.set(item[1])
        vendor_name = next((v[1] for v in self.vendor_list if v[0] == item[2]), "")
        self.vendor_select_var.set(vendor_name)

        if len(item) > 3:
            self.item_code_var.set(item[3])
        else:
            self.item_code_var.set("")  # Clear field if no code


    def add_item(self):
        name = self.item_name_var.get().strip()
        vendor_name = self.vendor_select_var.get().strip()
        if not name or not vendor_name:
            messagebox.showwarning("Missing Info", "Enter item name and select a vendor.")
            return
        vendor_id = next((v[0] for v in self.vendor_list if v[1] == vendor_name), None)
        if vendor_id is None:
            messagebox.showerror("Error", "Invalid vendor selected.")
            return
        try:
            item_code = self.item_code_var.get().strip()
            if not item_code:
                messagebox.showwarning("Missing Code", "Enter an item code.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Could not add item: {e}")
        try:
            database.add_item(name, vendor_id, item_code)
            self.refresh_item_list()
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not add item: {e}")

    def rename_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("No Selection", "Select an item to rename.")
            return
        name = self.item_name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Enter a new name.")
            return
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE items SET name = ? WHERE id = ?", (name, self.selected_item_id))
            conn.commit()
            conn.close()
            self.refresh_item_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not rename item: {e}")

    def delete_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("No Selection", "Select an item to delete.")
            return

        # Check if used in any invoice
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM invoice_items WHERE item_id = ?", (self.selected_item_id,))
        count = cursor.fetchone()[0]
        conn.close()

        if count > 0:
            messagebox.showerror("Blocked", "Cannot delete item used in invoices.")
            return

        confirm = messagebox.askyesno("Confirm", "Delete this item?")
        if not confirm:
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM items WHERE id = ?", (self.selected_item_id,))
            conn.commit()
            conn.close()
            self.refresh_item_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete item: {e}")

    def destroy(self):
        if self.on_close:
            callback = self.on_close
            self.on_close = None  # prevent loop
            callback()
        else:
            super().destroy()

