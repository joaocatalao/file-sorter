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

        self.button_frame = tk.Frame(self.frame, bg="#eaeaea")
        self.button_frame.pack(anchor="w", padx=5, pady=5)

        ttk.Button(self.button_frame, text="➕ Condition", command=self.add_condition).pack(side="left", padx=2)
        ttk.Button(self.button_frame, text="➕ Group", command=self.add_group).pack(side="left", padx=2)

    def add_condition(self, preset=None):
        row = ConditionRow(self.frame, controller=self.controller, preset=preset, on_delete=lambda: self.remove_child(row))
        self.children.append(row)

    def add_group(self, preset=None):
        group = ConditionGroup(self.frame, controller=self.controller)
        self.children.append(group)
        if preset:
            group.load_data(preset)

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)

    def get_data(self):
        return {
            "logic": self.logic_cb.get(),
            "children": [child.get_data() for child in self.children]
        }

    def load_data(self, data):
        self.logic_cb.set(data.get("logic", "All"))
        for child in data.get("children", []):
            if "children" in child:
                self.add_group(preset=child)
            else:
                self.add_condition(preset=child)
