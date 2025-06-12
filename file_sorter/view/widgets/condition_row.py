import tkinter as tk
from tkinter import ttk

class ConditionRow:
    def __init__(self, master, controller, preset=None, on_delete=None):
        self.frame = tk.Frame(master, bg="#f9f9f9")
        self.frame.pack(fill="x", pady=3, padx=10)

        self.type_cb = ttk.Combobox(self.frame, values=["File name", "Extension", "Size", "Content"], width=15)
        self.type_cb.set("File name")
        self.type_cb.pack(side="left", padx=5)

        self.compare_cb = ttk.Combobox(self.frame, values=["Is", "Is Not", "Contains", "Does Not Contain"], width=15)
        self.compare_cb.set("Contains")
        self.compare_cb.pack(side="left", padx=5)

        self.value_entry = tk.Entry(self.frame)
        self.value_entry.pack(side="left", fill="x", expand=True, padx=5)

        self.on_delete = on_delete

        if preset:
            self.type_cb.set(preset.get("type", "File name"))
            self.compare_cb.set(preset.get("comparison", "Contains"))
            self.value_entry.insert(0, preset.get("value", ""))

        ttk.Button(self.frame, text="❌", command=self.delete).pack(side="right", padx=5)

    def get_data(self):
        return {
            "type": self.type_cb.get(),
            "comparison": self.compare_cb.get(),
            "value": self.value_entry.get()
        }

    def delete(self):
        self.frame.destroy()
        if self.on_delete:
            self.on_delete()
