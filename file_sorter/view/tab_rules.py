import tkinter as tk
from tkinter import ttk

class RulesTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f8f8f8")
        self.controller = controller
        self.pack_propagate(0)

        self.build_header()
        self.build_rules_list()

    def build_header(self):
        header_frame = tk.Frame(self, bg="#f0f0f0", height=50)
        header_frame.pack(fill='x')

        ttk.Button(header_frame, text="Add Rule", command=self.add_rule).pack(side='left', padx=10, pady=10)
        ttk.Button(header_frame, text="Add Rule Group", command=self.add_group).pack(side='left', padx=5, pady=10)

        separator = tk.Frame(self, height=2, bg="#a0a0a0")
        separator.pack(fill='x')

    def build_rules_list(self):
        self.list_frame = tk.Frame(self, bg="#f8f8f8")
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def display_rules(self, rules):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not rules:
            ttk.Label(self.list_frame, text="No rules yet.", background="#f8f8f8").pack(anchor="w", padx=10, pady=10)
            return

        for index, rule in enumerate(rules):
            frame = ttk.Frame(self.list_frame)
            frame.pack(fill="x", pady=5)

            dest = rule.config.get("destination") or rule.config.get("pattern") or ""
            label = ttk.Label(frame, text=f"{rule.name} → {dest}", anchor="w")
            label.pack(side="left", expand=True, fill="x")

            ttk.Button(frame, text="Edit", command=lambda r=rule, i=index: self.controller.open_rule_editor(rule=r, index=i)).pack(side="right", padx=2)
            ttk.Button(frame, text="Delete", command=lambda r=rule: self.delete_rule(r)).pack(side="right", padx=2)

    def add_rule(self):
        self.controller.open_rule_editor()

    def add_group(self):
        print("Add Rule Group clicked")

    def delete_rule(self, rule):
        from tkinter import messagebox
        confirm = messagebox.askyesno("Delete Rule", f"Delete rule '{rule.name}'?")
        if confirm:
            self.controller.rule_manager.rules.remove(rule)
            self.controller.rule_manager.save_rules()
            self.controller.view.show_rules(self.controller.rule_manager.rules)
