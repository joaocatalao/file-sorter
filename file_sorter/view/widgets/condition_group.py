import tkinter as tk
from tkinter import ttk
from view.widgets.condition_row import ConditionRow
import logging

logger = logging.getLogger(__name__)

class ConditionGroup:
    def __init__(self, master, controller):
        self.frame = tk.Frame(master, bg="#eaeaea", padx=8, pady=6, bd=1, relief="groove")
        self.frame.pack(fill="x", pady=5)

        self.logic_cb = ttk.Combobox(self.frame, values=["All Files", "All", "Any"], state="readonly", width=15)
        self.logic_cb.set("All")
        self.logic_cb.pack(anchor="w", padx=5, pady=5)

        self.logic_cb.bind("<<ComboboxSelected>>", self.update_button_state)

        self.children = []
        self.controller = controller

        self.button_frame = tk.Frame(self.frame, bg="#eaeaea")
        self.button_frame.pack(anchor="w", padx=5, pady=5)

        ttk.Button(self.button_frame, text="➕ Condition", command=self.add_condition).pack(side="left", padx=2)
        ttk.Button(self.button_frame, text="➕ Group", command=self.add_group).pack(side="left", padx=2)

        self.update_button_state()
        logger.debug("[ConditionGroup] Initialized")

    def update_button_state(self, *_):
        current_logic = self.logic_cb.get()
        logger.info(f"[ConditionGroup] Logic set to: {current_logic}")
        if current_logic == "All Files":
            for widget in self.button_frame.winfo_children():
                widget.configure(state="disabled")
            self.clear_conditions()
            if hasattr(self.controller, "current_rule") and hasattr(self.controller.current_rule, "set_all_files_mode"):
                self.controller.current_rule.set_all_files_mode()
        else:
            for widget in self.button_frame.winfo_children():
                widget.configure(state="normal")

    def add_condition(self, preset=None):
        row = ConditionRow(self.frame, controller=self.controller, preset=preset, on_delete=lambda: self.remove_child(row))
        self.children.append(row)
        logger.debug(f"[ConditionGroup] Added condition row (preset: {bool(preset)})")

    def add_group(self, preset=None):
        group = ConditionGroup(self.frame, controller=self.controller)
        self.children.append(group)
        logger.debug("[ConditionGroup] Added nested condition group")
        if preset:
            group.load_data(preset)

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            logger.debug("[ConditionGroup] Removed child condition/group")

    def get_data(self):
        logic = self.logic_cb.get().strip().lower().replace(" ", "_")
        result = {
            "logic": logic,
            "children": [child.get_data() for child in self.children]
        }
        logger.debug(f"[ConditionGroup] get_data() → logic: {logic}, children: {len(result['children'])}")
        return result

    def load_data(self, data):
        logic_map = {
            "all": "All",
            "any": "Any",
            "none": "None",
            "all_files": "All Files"
        }
        logic_str = data.get("logic", "").lower()
        self.logic_cb.set(logic_map.get(logic_str, "All"))
        self.logic_cb.event_generate("<<ComboboxSelected>>")
        logger.info(f"[ConditionGroup] Loading data with logic: {logic_str}")

        for child in data.get("children", []):
            if "children" in child:
                self.add_group(preset=child)
            else:
                self.add_condition(preset=child)

    def clear_conditions(self):
        for child in self.children:
            child.frame.destroy()
        self.children.clear()
        logger.debug("[ConditionGroup] Cleared all children")
