import tkinter as tk
from tkinter import ttk
from ui.new_invoice import NewInvoiceWindow
from ui.edit_invoice import EditInvoiceWindow
from ui.manage_vendors import ManageVendorsWindow
from ui.manage_items import ManageItemsWindow
# Add imports for manage windows if needed later

def on_close_subwindow(window):
    window.destroy()
    root.deiconify()

def open_new_invoice():
    root.withdraw()
    win = NewInvoiceWindow(root, on_close=lambda: on_close_subwindow(win))
    win.protocol("WM_DELETE_WINDOW", lambda: on_close_subwindow(win))

def open_edit_invoice():
    root.withdraw()
    win = EditInvoiceWindow(root, on_close=lambda: on_close_subwindow(win))
    win.protocol("WM_DELETE_WINDOW", lambda: on_close_subwindow(win))

def open_manage_vendors():
    root.withdraw()
    win = ManageVendorsWindow(root, on_close=lambda: on_close_subwindow(win))
    win.protocol("WM_DELETE_WINDOW", lambda: on_close_subwindow(win))

def open_manage_items():
    root.withdraw()
    win = ManageItemsWindow(root, on_close=lambda: on_close_subwindow(win))
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

    root.mainloop()

if __name__ == "__main__":
    main()
