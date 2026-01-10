import tkinter as tk
from tkinter import ttk
from view.widgets.action_row import ActionRow

class ActionSection(ttk.LabelFrame):
    def __init__(self, parent, controller, rule, on_dirty):
        super().__init__(parent, text="Then")
        self.controller = controller
        self.on_dirty = on_dirty
        self.action_rows = []

        self.action_container = tk.Frame(self, bg="#f9f9f9")
        self.action_container.pack(fill="x", padx=5, pady=5)

        ttk.Button(self, text="➕ Add Action", command=self.add_action_row).pack(anchor="w", padx=5, pady=(0, 5))

        if rule and "actions" in rule.config:
            for action_cfg in rule.config["actions"]:
                self.add_action_row(preset=action_cfg)
        else:
            self.add_action_row()

    def add_action_row(self, preset=None):
        row = ActionRow(self.action_container, controller=self.controller, preset=preset,
                on_delete=lambda: self.remove_action_row(row))
        self.action_rows.append(row)
        self.on_dirty()

    def remove_action_row(self, row):
        row.frame.destroy()
        if row in self.action_rows:
            self.action_rows.remove(row)
        self.on_dirty()

    def get_data(self):
        return [row.get_data() for row in self.action_rows]
