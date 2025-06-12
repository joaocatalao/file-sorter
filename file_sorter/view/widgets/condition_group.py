import tkinter as tk
from tkinter import ttk
from view.widgets.condition_row import ConditionRow

class ConditionGroup:
    def __init__(self, master, controller):
        self.frame = tk.Frame(master, bg="#eaeaea", padx=8, pady=6, bd=1, relief="groove")
        self.frame.pack(fill="x", pady=5)

        self.logic_cb = ttk.Combobox(self.frame, values=["All", "Any", "None"], state="readonly", width=15)
        self.logic_cb.set("All")
        self.logic_cb.pack(anchor="w", padx=5, pady=5)

        self.children = []
        self.controller = controller

        button_frame = tk.Frame(self.frame, bg="#eaeaea")
        button_frame.pack(anchor="w", padx=5, pady=5)

        ttk.Button(button_frame, text="➕ Condition", command=self.add_condition).pack(side="left", padx=2)
        ttk.Button(button_frame, text="➕ Group", command=self.add_group).pack(side="left", padx=2)

    def add_condition(self):
        row = ConditionRow(self.frame, controller=self.controller)
        self.children.append(row)

    def add_group(self):
        group = ConditionGroup(self.frame, controller=self.controller)
        self.children.append(group)

    def get_data(self):
        return {
            "logic": self.logic_cb.get(),
            "children": [child.get_data() for child in self.children]
        }
