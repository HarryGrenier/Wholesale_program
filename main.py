import tkinter as tk
from tkinter import ttk
from ui.edit_invoice import EditInvoiceWindow
from ui.manage_vendors import ManageVendorsWindow
from ui.manage_items import ManageItemsWindow
from models.database import create_blank_invoice
from ui.settings import SettingsWindow
from models.cleanup_old_invoices import delete_old_invoices
from ui.saved_invoices_window import SavedInvoicesWindow

def open_saved_invoices_window():
    root.withdraw()
    win = SavedInvoicesWindow(root)
    win.protocol("WM_DELETE_WINDOW", lambda: on_close_subwindow(win))
    win.grab_set()  # Make sure the main window is not accessible while this is open

def on_close_subwindow(window):
    window.destroy()
    root.deiconify()
    
def open_new_invoice():
    invoice_id = create_blank_invoice()
    root.withdraw()
    win = EditInvoiceWindow(root, invoice_db_id=invoice_id)
    win.protocol("WM_DELETE_WINDOW", lambda: on_close_subwindow(win))
    

def open_edit_invoice():
    root.withdraw()
    win = EditInvoiceWindow(root)
    win.protocol("WM_DELETE_WINDOW", lambda: on_close_subwindow(win))

def open_manage_vendors():
    root.withdraw()
    win = ManageVendorsWindow(root, on_close=lambda: on_close_subwindow(win))
    win.protocol("WM_DELETE_WINDOW", lambda: on_close_subwindow(win))

def open_manage_items():
    root.withdraw()
    win = ManageItemsWindow(root, on_close=lambda: on_close_subwindow(win))
    win.protocol("WM_DELETE_WINDOW", lambda: on_close_subwindow(win))

def open_settings():
    root.withdraw()
    win = SettingsWindow(root)
    win.protocol("WM_DELETE_WINDOW", lambda: on_close_subwindow(win))
    
def main():
    global root
    root = tk.Tk()
    root.title("Wholesale Invoice Program")
    root.geometry("400x350")
    root.resizable(False, False)

    title = ttk.Label(root, text="Invoice Management System", font=("Arial", 16))
    title.pack(pady=20)

    ttk.Button(root, text="Create New Invoice", width=25, command=open_new_invoice).pack(pady=10)
    ttk.Button(root, text="Edit Existing Invoice", width=25, command=open_edit_invoice).pack(pady=10)
    ttk.Button(root, text="Manage Vendors", width=25, command=open_manage_vendors).pack(pady=10)
    ttk.Button(root, text="Manage Items", width=25, command=open_manage_items).pack(pady=10)
    ttk.Button(root, text="View Saved Invoices", width=25, command=open_saved_invoices_window).pack(pady=10)
    ttk.Button(root, text="Settings", width=25, command=open_settings).pack(pady=10)


    root.mainloop()

if __name__ == "__main__":
    try:
        delete_old_invoices()
    except Exception as e:
        print(f"Error during cleanup: {e}")
    main()
