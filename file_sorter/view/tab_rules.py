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
            container = ttk.Frame(self.list_frame)
            container.pack(fill="x", pady=6, padx=5, anchor="w")

            is_expanded = tk.BooleanVar(value=False)

            # Title row
            title_frame = ttk.Frame(container)
            title_frame.pack(fill="x")

            toggle_btn = ttk.Label(title_frame, text="▶", width=2)
            toggle_btn.pack(side="left")

            name_label = ttk.Label(title_frame, text=f"📄 {rule.name}", font=("Segoe UI", 10))
            name_label.pack(side="left", anchor="w")

            # Buttons
            btns = ttk.Frame(title_frame)
            btns.pack(side="right")
            ttk.Button(btns, text="✏️", width=3, command=lambda r=rule, i=index: self.controller.open_rule_editor(rule=r, index=i)).pack(side="right", padx=2)
            ttk.Button(btns, text="🗑", width=3, command=lambda r=rule: self.delete_rule(r)).pack(side="right", padx=2)

            # Details (must come first before lambda binds)
            details_frame = ttk.Frame(container)

            folder = rule.config.get("pattern") or rule.config.get("destination") or "(no folder)"
            ttk.Label(details_frame, text=f"📁 Folder: {folder}", font=("Segoe UI", 9)).pack(anchor="w")

            cond_block = rule.config.get("conditions", {})
            logic = cond_block.get("logic", "All")
            children = cond_block.get("children", [])
            cond_descs = []

            for cond in children:
                if isinstance(cond, dict) and "type" in cond:
                    cond_descs.append(f"{cond['type']} {cond['comparison']} \"{cond['value']}\"")
                elif isinstance(cond, dict) and "logic" in cond:
                    cond_descs.append(f"[{cond['logic']} group]")

            cond_summary = ", ".join(cond_descs) if cond_descs else "(none)"
            ttk.Label(details_frame, text=f"📌 Conditions: {logic} | {cond_summary}", font=("Segoe UI", 9)).pack(anchor="w")

            actions = rule.config.get("actions", [])
            action_descs = []
            for a in actions:
                action = a.get("action", "?")
                path = a.get("path", "")
                action_descs.append(f"{action} → {path}")
            action_summary = ", ".join(action_descs) if action_descs else "(none)"
            ttk.Label(details_frame, text=f"⚙️ Actions: {action_summary}", font=("Segoe UI", 9)).pack(anchor="w")

            # Toggle function — now after details_frame exists
            def toggle(frame, flag, btn):
                flag.set(not flag.get())
                if flag.get():
                    btn.config(text="▼")
                    frame.pack(fill="x", padx=20)
                else:
                    btn.config(text="▶")
                    frame.forget()

            toggle_btn.bind("<Button-1>", lambda e, df=details_frame, exp=is_expanded, tb=toggle_btn: toggle(df, exp, tb))
            name_label.bind("<Button-1>", lambda e, df=details_frame, exp=is_expanded, tb=toggle_btn: toggle(df, exp, tb))

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
