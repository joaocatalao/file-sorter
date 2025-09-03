import tkinter as tk
from tkinter import ttk
from view.widgets.condition_group import ConditionGroup


class ConditionSection(ttk.LabelFrame):
    def __init__(self, parent, controller, rule=None, on_dirty=None):
        super().__init__(parent, text="If")
        self.controller = controller
        self.on_dirty = on_dirty

        self.pack(fill="x", pady=(0, 10))  # consistent spacing

        # Internal ConditionGroup widget
        self.condition_group = ConditionGroup(self, controller=self.controller)

        if rule and "conditions" in rule.config:
            # Preload when editing existing rule
            self.condition_group.load_data(rule.config["conditions"])
        else:
            # New rule → default to "All Files"
            self.condition_group.logic_cb.set("All Files")
            self.condition_group.update_button_state()

    def get_data(self):
        return self.condition_group.get_data()
