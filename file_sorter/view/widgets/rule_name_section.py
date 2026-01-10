import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)

class RuleNameSection(ttk.LabelFrame):
    def __init__(self, master, controller, name_var, on_rename=None, on_dirty=None):
        super().__init__(master, text="Rule Name")
        self.controller = controller
        self.name_var = name_var
        self.on_rename = on_rename
        self.on_dirty = on_dirty

        self.pack(fill="x", pady=(3, 10))

        self.entry = ttk.Entry(self, textvariable=self.name_var)
        self.entry.pack(fill="x", padx=10, pady=10)

        self.previous_name = self.name_var.get()

        self.entry.bind("<FocusOut>", self._on_name_change)
        logger.debug("[RuleNameSection] Initialized")

    def _on_name_change(self, event=None):
        new_name = self.name_var.get().strip()
        if not new_name or new_name == self.previous_name:
            return

        if self.on_rename:
            self.on_rename(self.previous_name, new_name)

        # Check if the visible label actually changed
        tab = self.controller.view.tabs.get(new_name)
        if tab:
            current_text = tab["label"].cget("text").rstrip(" *")
            if current_text == new_name:
                logger.info(f"[RuleNameSection] Name changed: '{self.previous_name}' → '{new_name}'")
                self.previous_name = new_name

        if self.on_dirty:
            self.on_dirty()
