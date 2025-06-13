import tkinter as tk
from tkinter import ttk

class SettingsTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f8f8f8")
        self.controller = controller
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text="Settings", font=("Segoe UI", 14), bg="#f8f8f8").pack(anchor="w", padx=20, pady=(20, 10))

        # Close tab after save
        self.close_on_save = tk.BooleanVar(value=self.controller.settings.get("close_tab_after_save", False))
        ttk.Checkbutton(self, text="Close rule tab after save", variable=self.close_on_save, command=self.toggle_close_tab).pack(anchor="w", padx=30, pady=5)

        # Start with Windows (placeholder)
        self.start_with_windows = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="Start with Windows (coming soon)", variable=self.start_with_windows, state="disabled").pack(anchor="w", padx=30, pady=5)

        # Minimize to tray
        self.minimize_to_tray = tk.BooleanVar(value=self.controller.settings.get("minimize_to_tray", False))
        ttk.Checkbutton(self, text="Minimize to system tray", variable=self.minimize_to_tray, command=self.toggle_tray).pack(anchor="w", padx=30, pady=5)

    def toggle_close_tab(self):
        self.controller.settings["close_tab_after_save"] = self.close_on_save.get()

    def toggle_tray(self):
        self.controller.settings["minimize_to_tray"] = self.minimize_to_tray.get()
