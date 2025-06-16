import tkinter as tk
from tkinter import ttk, filedialog
import logging

logger = logging.getLogger(__name__)

class ActionRow:
    def __init__(self, master, controller, preset=None, on_delete=None):
        self.controller = controller
        self.on_delete = on_delete

        self.frame = tk.Frame(master, bg="#f9f9f9")
        self.frame.pack(fill="x", pady=3, padx=10)

        self.action_cb = ttk.Combobox(self.frame, values=["Move", "Copy", "Delete", "Rename"], width=15)
        self.action_cb.set("Move")
        self.action_cb.pack(side="left", padx=5)

        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(self.frame, textvariable=self.path_var)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=5)

        ttk.Button(self.frame, text="...", command=self.browse).pack(side="left", padx=5)

        if preset:
            self.action_cb.set(preset.get("action", "Move"))
            self.path_var.set(preset.get("path", ""))
            logger.debug(f"[ActionRow] Initialized with preset: {preset}")
        else:
            logger.debug("[ActionRow] Initialized with default values")

        ttk.Button(self.frame, text="❌", command=self.delete).pack(side="right", padx=5)

    def browse(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)
            logger.info(f"[ActionRow] Path selected: {path}")

    def get_data(self):
        action = self.action_cb.get()
        path = self.path_var.get()
        logger.debug(f"[ActionRow] get_data() → action: {action}, path: {path}")
        return {
            "action": action,
            "path": path
        }

    def delete(self):
        logger.info(f"[ActionRow] Deleted row: action={self.action_cb.get()}, path={self.path_var.get()}")
        self.frame.destroy()
        if self.on_delete:
            self.on_delete()
