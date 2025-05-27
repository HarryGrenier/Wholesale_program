from tkinter import Tk
from database import init_db
from ui import InvoiceApp

if __name__ == "__main__":
    init_db()
    root = Tk()
    app = InvoiceApp(root)
    root.mainloop()
