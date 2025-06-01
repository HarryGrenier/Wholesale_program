import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
import json
import os

SETTINGS_FILE = "../Data/settings.json"
DEFAULT_SETTINGS = {
    "row_colors": {
        "even": "#f4f4f4",
        "odd": "#ffffff"
    },
    "pdf_output_directory": ""
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
        self.geometry("400x250")
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

        # Odd Row Color
        ttk.Label(frame, text="Odd Row Color:").grid(row=1, column=0, sticky="w")
        self.odd_color_entry = ttk.Entry(frame, width=15)
        self.odd_color_entry.insert(0, self.settings["row_colors"]["odd"])
        self.odd_color_entry.grid(row=1, column=1)
        ttk.Button(frame, text="Pick", command=lambda: self.pick_color(self.odd_color_entry)).grid(row=1, column=2)

        # PDF Output Directory
        ttk.Label(frame, text="PDF Output Directory:").grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 0))
        self.output_dir_entry = ttk.Entry(frame, width=45)
        self.output_dir_entry.insert(0, self.settings["pdf_output_directory"])
        self.output_dir_entry.grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_output_dir).grid(row=3, column=2)

        # Reset to Defaults Button
        ttk.Button(frame, text="Reset to Defaults", command=self.reset_to_defaults).grid(row=5, column=0, columnspan=3, pady=5)

        # Save Button
        ttk.Button(frame, text="Save Settings", command=self.save).grid(row=4, column=0, columnspan=3, pady=15)

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
    
    def reset_to_defaults(self):
        self.even_color_entry.delete(0, tk.END)
        self.even_color_entry.insert(0, DEFAULT_SETTINGS["row_colors"]["even"])

        self.odd_color_entry.delete(0, tk.END)
        self.odd_color_entry.insert(0, DEFAULT_SETTINGS["row_colors"]["odd"])

        self.output_dir_entry.delete(0, tk.END)
        self.output_dir_entry.insert(0, DEFAULT_SETTINGS["pdf_output_directory"])

        save_settings(DEFAULT_SETTINGS)
        messagebox.showinfo("Settings", "Settings reset to defaults.")

    def save(self):
        self.settings["row_colors"]["even"] = self.even_color_entry.get()
        self.settings["row_colors"]["odd"] = self.odd_color_entry.get()
        self.settings["pdf_output_directory"] = self.output_dir_entry.get()
        save_settings(self.settings)
        messagebox.showinfo("Settings", "Settings saved successfully!")
        self.destroy()
