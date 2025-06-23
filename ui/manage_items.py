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
        self.refresh_item_list()

    def setup_widgets(self):
        self.item_listbox = tk.Listbox(self, height=15)
        self.item_listbox.pack(fill="both", expand=True, padx=10, pady=10)
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

        button_frame = ttk.Frame(self)
        button_frame.pack()

        ttk.Button(button_frame, text="Add", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Rename", command=self.rename_item).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_item).pack(side="left", padx=5)

    def refresh_item_list(self):
        self.item_listbox.delete(0, tk.END)
        self.items = database.get_all_items()
        self.filtered_items = self.items

        for i in self.filtered_items:
            self.item_listbox.insert(tk.END, i[1])  # Item name only

        self.selected_item_id = None
        self.item_name_var.set("")
        self.item_code_var.set("")

    def on_select_item(self, event=None):
        selection = self.item_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        item = self.filtered_items[index]
        self.selected_item_id = item[0]
        self.item_name_var.set(item[1])
        self.item_code_var.set(item[2])

    def add_item(self):
        name = self.item_name_var.get().strip()
        item_code = self.item_code_var.get().strip()

        if not name:
            messagebox.showwarning("Missing Info", "Enter item name.")
            return
        if not item_code:
            messagebox.showwarning("Missing Code", "Enter an item code.")
            return
        try:
            database.add_item(name, item_code)
            self.refresh_item_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add item: {e}")

    def rename_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("No Selection", "Select an item to rename.")
            return
        name = self.item_name_var.get().strip()
        item_code = self.item_code_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Enter a new name.")
            return
        if not item_code:
            messagebox.showwarning("Missing Code", "Enter an item code.")
            return
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE items SET name = ?, item_code = ? WHERE id = ?", (name, item_code, self.selected_item_id))
            conn.commit()
            conn.close()
            self.refresh_item_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not rename item: {e}")

    
    
        
    def delete_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("No Selection", "Select an item to delete.")
            return

        # Optional: confirm soft deletion
        confirm = messagebox.askyesno("Confirm", "Mark this item as inactive?")
        if not confirm:
            return

        try:
            database.soft_delete_item(self.selected_item_id)
            self.refresh_item_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not deactivate item: {e}")

    def destroy(self):
        if self.on_close:
            callback = self.on_close
            self.on_close = None
            callback()
        else:
            super().destroy()
