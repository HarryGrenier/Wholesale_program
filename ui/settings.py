
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
import json
import os
from models.database_creation import create_tables


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "Data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "invoice_retention": {
        "years": 2,
        "months": 0
    },
    "row_colors": {
        "even": "#f4f4f4",
        "odd": "#ffffff"
    },
    "pdf_output_directory": "",
    "defaults": {
        "quantity": 1,
        "unit_price": 0.0
    },
    "window_mode": "zoomed",
    "confirmations": {
        "on_save": True,
        "on_delete": True
    },
    "pdf_filename_format": "invoice_{id}_{date}"
}


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

class SettingsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("⚙️ Settings")
        self.geometry("500x480")
        self.resizable(False, False)

        self.settings = load_settings()

        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="both", expand=True)

        # Even Row Color
        ttk.Label(frame, text="Even Row Color:").grid(row=0, column=0, sticky="w")
        self.even_color_entry = ttk.Entry(frame, width=15)
        self.even_color_entry.insert(0, self.settings["row_colors"]["even"])
        self.even_color_entry.grid(row=0, column=1)
        ttk.Button(frame, text="Pick", command=lambda: self.pick_color(self.even_color_entry)).grid(row=0, column=2)
        ttk.Button(frame, text="Reset", command=lambda: self.even_color_entry.delete(0, tk.END) or self.even_color_entry.insert(0, DEFAULT_SETTINGS["row_colors"]["even"])).grid(row=0, column=3)


        # Odd Row Color
        ttk.Label(frame, text="Odd Row Color:").grid(row=1, column=0, sticky="w")
        self.odd_color_entry = ttk.Entry(frame, width=15)
        self.odd_color_entry.insert(0, self.settings["row_colors"]["odd"])
        self.odd_color_entry.grid(row=1, column=1)
        ttk.Button(frame, text="Pick", command=lambda: self.pick_color(self.odd_color_entry)).grid(row=1, column=2)
        ttk.Button(frame, text="Reset", command=lambda: self.odd_color_entry.delete(0, tk.END) or self.odd_color_entry.insert(0, DEFAULT_SETTINGS["row_colors"]["odd"])).grid(row=1, column=3)


        # PDF Output Directory
        ttk.Label(frame, text="PDF Output Directory:").grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 0))
        self.output_dir_entry = ttk.Entry(frame, width=45)
        self.output_dir_entry.insert(0, self.settings["pdf_output_directory"])
        self.output_dir_entry.grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_output_dir).grid(row=3, column=2)

        # Default Quantity and Price
        ttk.Label(frame, text="Default Quantity:").grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.default_qty_entry = ttk.Entry(frame, width=10)
        self.default_qty_entry.insert(0, str(self.settings["defaults"]["quantity"]))
        self.default_qty_entry.grid(row=4, column=1, sticky="w")

        ttk.Label(frame, text="Default Unit Price:").grid(row=5, column=0, sticky="w")
        self.default_price_entry = ttk.Entry(frame, width=10)
        self.default_price_entry.insert(0, str(self.settings["defaults"]["unit_price"]))
        self.default_price_entry.grid(row=5, column=1, sticky="w")

        # Window Mode
        ttk.Label(frame, text="Window Mode:").grid(row=6, column=0, sticky="w", pady=(10, 0))
        self.window_mode_var = tk.StringVar(value=self.settings.get("window_mode", "zoomed"))
        ttk.Combobox(frame, textvariable=self.window_mode_var, values=["zoomed", "normal"], state="readonly", width=15).grid(row=6, column=1)

        # Confirmations
        self.confirm_save_var = tk.BooleanVar(value=self.settings["confirmations"].get("on_save", True))
        self.confirm_delete_var = tk.BooleanVar(value=self.settings["confirmations"].get("on_delete", True))
        ttk.Checkbutton(frame, text="Confirm on Save", variable=self.confirm_save_var).grid(row=7, column=0, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Checkbutton(frame, text="Confirm on Delete", variable=self.confirm_delete_var).grid(row=8, column=0, columnspan=2, sticky="w")

        # PDF Filename Format
        ttk.Label(frame, text="PDF Filename Format:").grid(row=10, column=0, sticky="w", pady=(10, 0))
        self.filename_format_entry = ttk.Entry(frame, width=30)
        self.filename_format_entry.insert(0, self.settings.get("pdf_filename_format", "invoice_{id}_{date}"))
        self.filename_format_entry.grid(row=10, column=1, columnspan=2, sticky="w")

        # Save and Reset Buttons
        ttk.Button(frame, text="Save Settings", command=self.save).grid(row=11, column=0, columnspan=3, pady=15)
        ttk.Button(frame, text="Reset to Defaults", command=self.reset_defaults).grid(row=12, column=0, columnspan=3)
        ttk.Button(frame, text="Generate Database Schema", command=self.run_schema_creation).grid(row=15, column=0, columnspan=3, pady=(0, 10))
        


    def pick_color(self, entry_widget):
        color = colorchooser.askcolor()[1]
        if color:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, color)

    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, directory)

    def save(self):
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)
        self.settings["row_colors"]["even"] = self.even_color_entry.get()
        self.settings["row_colors"]["odd"] = self.odd_color_entry.get()
        self.settings["pdf_output_directory"] = self.output_dir_entry.get()
        self.settings["defaults"]["quantity"] = int(self.default_qty_entry.get())
        self.settings["defaults"]["unit_price"] = float(self.default_price_entry.get())
        self.settings["window_mode"] = self.window_mode_var.get()
        self.settings["confirmations"]["on_save"] = self.confirm_save_var.get()
        self.settings["confirmations"]["on_delete"] = self.confirm_delete_var.get()
        self.settings["pdf_filename_format"] = self.filename_format_entry.get()

        save_settings(self.settings)
        messagebox.showinfo("Settings", "Settings saved successfully!")

    def reset_defaults(self):
        global DEFAULT_SETTINGS
        self.settings = DEFAULT_SETTINGS.copy()
        save_settings(self.settings)
        self.destroy()
        SettingsWindow(self.master)

    def run_schema_creation(self):
        db_path = "Data/invoice.db"

        if os.path.exists(db_path):
            confirm = messagebox.askyesno(
                "Database Exists",
                "The database already exists.\nAre you sure you want to run the schema creation?\n(This will not delete any data but may modify the structure.)"
            )
            if not confirm:
                return

        try:
            create_tables()
            messagebox.showinfo("Success", "Database schema created successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create database schema:\n{e}")