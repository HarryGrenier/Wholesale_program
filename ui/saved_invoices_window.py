import os
import platform
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import subprocess
from ui.settings import load_settings

class SavedInvoicesWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("📁 Saved Invoices")
        self.geometry("800x500")
        self.settings = load_settings()

        self.pdf_dir = self.settings.get("pdf_output_directory", "")
        if not os.path.isdir(self.pdf_dir):
            messagebox.showerror("Directory Error", "The saved invoice directory does not exist.")
            self.destroy()
            return

        self.create_widgets()
        self.load_pdf_files()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("filename", "modified"), show="headings")
        self.tree.heading("filename", text="Filename")
        self.tree.heading("modified", text="Last Modified")
        self.tree.column("filename", width=500)
        self.tree.column("modified", width=200, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Open", command=self.open_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_pdf_files).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side="right", padx=5)

    def load_pdf_files(self):
        self.tree.delete(*self.tree.get_children())
        try:
            files = [
                f for f in os.listdir(self.pdf_dir)
                if f.lower().endswith(".pdf")
            ]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(self.pdf_dir, x)), reverse=True)
            for f in files:
                path = os.path.join(self.pdf_dir, f)
                modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")
                self.tree.insert("", "end", values=(f, modified))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load files:\n{e}")

    def open_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a file to open.")
            return

        filename = self.tree.item(selected[0])["values"][0]
        filepath = os.path.join(self.pdf_dir, filename)
        try:
            if platform.system() == 'Darwin':
                subprocess.call(('open', filepath))
            elif platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Linux':
                subprocess.call(('xdg-open', filepath))
        except Exception as e:
            messagebox.showerror("Open Failed", f"Could not open file:\n{e}")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a file to delete.")
            return

        filename = self.tree.item(selected[0])["values"][0]
        filepath = os.path.join(self.pdf_dir, filename)
        confirm = messagebox.askyesno("Confirm Delete", f"Delete '{filename}'?")
        if confirm:
            try:
                os.remove(filepath)
                self.load_pdf_files()
                messagebox.showinfo("Deleted", f"'{filename}' was deleted.")
            except Exception as e:
                messagebox.showerror("Delete Failed", f"Could not delete file:\n{e}")
