import tkinter as tk
from tkinter import ttk, messagebox , simpledialog
from models import database

class ManageVendorsWindow(tk.Toplevel):
    def __init__(self, master, on_close=None):
        super().__init__(master)
        self.title("Manage Vendors")
        self.geometry("600x400")
        self.on_close = on_close

        self.selected_vendor_id = None
        self.setup_widgets()
        self.refresh_vendor_list()

    def setup_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.vendor_listbox = tk.Listbox(frame, height=15)
        self.vendor_listbox.pack(fill="both", expand=True)
        self.vendor_listbox.bind("<<ListboxSelect>>", self.on_select_vendor)

        entry_frame = ttk.Frame(self)
        entry_frame.pack(pady=10)
        ttk.Label(entry_frame, text="Vendor Name:").pack(side="left", padx=(0, 5))
        self.vendor_name_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.vendor_name_var, width=30).pack(side="left", padx=5)

        ttk.Button(entry_frame, text="Add", command=self.add_vendor).pack(side="left", padx=5)
        ttk.Button(entry_frame, text="Rename", command=self.rename_vendor).pack(side="left", padx=5)
        ttk.Button(entry_frame, text="Delete", command=self.delete_vendor).pack(side="left", padx=5)

    def refresh_vendor_list(self):
        self.vendor_listbox.delete(0, tk.END)
        self.vendors = database.get_all_vendors()
        for v in self.vendors:
            self.vendor_listbox.insert(tk.END, v[1])
        self.selected_vendor_id = None
        self.vendor_name_var.set("")

    def on_select_vendor(self, event=None):
        selection = self.vendor_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        vendor = self.vendors[index]
        self.selected_vendor_id = vendor[0]
        self.vendor_name_var.set(vendor[1])

    def add_vendor(self):
        name = self.vendor_name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a vendor name.")
            return
        try:
            database.add_vendor(name)
            self.refresh_vendor_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add vendor: {e}")

    def rename_vendor(self):
        if self.selected_vendor_id is None:
            messagebox.showwarning("No Selection", "Select a vendor to rename.")
            return
        name = self.vendor_name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Enter a new name.")
            return
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE vendors SET name = ? WHERE id = ?", (name, self.selected_vendor_id))
            conn.commit()
            conn.close()
            self.refresh_vendor_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not rename vendor: {e}")

    def delete_vendor(self):
        if self.selected_vendor_id is None:
            messagebox.showwarning("No Selection", "Select a vendor to delete.")
            return

        confirm = messagebox.askyesno("Confirm", "Mark this vendor as inactive?")
        if not confirm:
            return

        try:
            database.soft_delete_vendor(self.selected_vendor_id)
            self.refresh_vendor_list()
            messagebox.showinfo("Vendor Deactivated", "Vendor has been marked as inactive.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not deactivate vendor: {e}")


    
    def destroy(self):
        if self.on_close:
            callback = self.on_close
            self.on_close = None  # prevent loop
            callback()
        else:
            super().destroy()
