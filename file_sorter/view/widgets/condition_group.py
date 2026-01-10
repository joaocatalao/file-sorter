import tkinter as tk
from tkinter import ttk
from view.widgets.condition_row import ConditionRow
import logging

logger = logging.getLogger(__name__)

class ConditionGroup:
    def __init__(self, master, controller, preset=None, on_delete=None):
        self.controller = controller
        self.on_delete = on_delete
        self.children = []

        self.frame = tk.Frame(master, bg="#eaeaea", padx=8, pady=6, bd=1, relief="groove")
        self.frame.pack(fill="x", pady=5)

        # Top controls (logic dropdown + delete button)
        top = tk.Frame(self.frame, bg="#eaeaea")
        top.pack(fill="x")

        logic_controls = tk.Frame(top, bg="#eaeaea")
        logic_controls.pack(side="left", padx=5, pady=5)

        self.logic_cb = ttk.Combobox(logic_controls, values=["All Files", "All", "Any"], state="readonly", width=15)
        self.logic_cb.set("All")
        self.logic_cb.bind("<<ComboboxSelected>>", self._on_logic_changed)
        self.logic_cb.pack(side="left")

        if self.on_delete:
            ttk.Button(logic_controls, text="❌", width=3, command=self.delete).pack(side="left", padx=(5, 0))

        # Add buttons
        self.button_frame = tk.Frame(self.frame, bg="#eaeaea")
        self.button_frame.pack(anchor="w", padx=5, pady=5)

        self.btn_add_condition = ttk.Button(self.button_frame, text="➕ Condition", command=self.add_condition)
        self.btn_add_condition.pack(side="left", padx=2)

        self.btn_add_group = ttk.Button(self.button_frame, text="➕ Group", command=self.add_group)
        self.btn_add_group.pack(side="left", padx=2)

        self.update_button_state()

        if preset:
            self.load_data(preset)
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
    
    def _on_logic_changed(self, event=None):
        self.update_button_state()
        if self.logic_cb.get() == "All Files":
            self.clear_conditions()

    def add_condition(self, preset=None):
        row = ConditionRow(self.frame, controller=self.controller, preset=preset, on_delete=lambda: self.remove_child(row))
        self.children.append(row)
        logger.info(f"[ConditionGroup] Condition added (preset: {bool(preset)})")

    def add_group(self, preset=None):
        group = ConditionGroup(self.frame, controller=self.controller, preset=preset, on_delete=lambda: self.remove_child(group))
        self.children.append(group)
        logger.info("[ConditionGroup] Nested group added")

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.frame.destroy()
            logger.info("[ConditionGroup] Removed child condition/group")

    def delete(self):
        logger.info("[ConditionGroup] Deleted entire group")
        self.frame.destroy()
        if self.on_delete:
            self.on_delete()

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
