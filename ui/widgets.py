import tkinter as tk
from tkinter import ttk

class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)
        self['values'] = self._completion_list
        self.bind('<KeyRelease>', self._on_keyrelease)

    def _on_keyrelease(self, event):
        # Don't interfere with navigation keys
        if event.keysym in ("Up", "Down", "Left", "Right", "Return", "Tab"):
            return

        typed = self.get().lower()

        if typed == "":
            filtered = self._completion_list
        else:
            filtered = [item for item in self._completion_list if item.lower().startswith(typed)]

        # Save cursor position so user can keep typing
        current_pos = self.index(tk.INSERT)

        self['values'] = filtered

        # Re-set typed text to maintain what user typed
        self.delete(0, tk.END)
        self.insert(0, typed)
        self.icursor(current_pos)

        if len(typed) >= 2 and self['values']:
            self.event_generate('<Down>')