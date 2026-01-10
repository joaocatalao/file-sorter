import tkinter as tk
from tkinter import ttk

class LogsTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f5f5")
        self.controller = controller

        self.build_ui()

    def build_ui(self):
        # Title
        ttk.Label(self, text="Live Logs", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        # Frame with scrollbar + Text
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.scrollbar = ttk.Scrollbar(container)
        self.scrollbar.pack(side="right", fill="y")

        self.text = tk.Text(container, wrap="word", yscrollcommand=self.scrollbar.set, bg="#ffffff", relief="solid", borderwidth=1)
        self.text.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.text.yview)

        self.text.insert("end", "Log output will appear here.\n")
        self.text.config(state="disabled")

    def log(self, message: str):
        self.text.config(state="normal")
        self.text.insert("end", message + "\n")
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete(1.0, "end")
        self.text.config(state="disabled")
