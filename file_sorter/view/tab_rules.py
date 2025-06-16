from model.dynamic_rule import DynamicRule
from utils.tooltip import Tooltip
from view.widgets.toolbar import Toolbar
import tkinter as tk
from tkinter import ttk
import copy

class RulesTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f8f8f8")
        self.controller = controller
        self.pack_propagate(0)

        self.build_header()
        self.build_rules_list()

    def build_header(self):
            def add_btn(text, cmd, tooltip):
                return {"text": text, "command": cmd, "tooltip": tooltip}

            toolbar = Toolbar(
                self,
                left_buttons=[
                    add_btn("➕ Add Rule", self.add_rule, "Create a new rule"),
                    add_btn("📁 Add Rule Group", self.add_group, "Create a new group")
                ]
            )
            toolbar.pack(fill="x")

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
            if getattr(rule, "is_group", False):
                self.render_group(rule)
            else:
                self.render_rule(rule, index)

    def render_group(self, group):
        frame = ttk.LabelFrame(self.list_frame, text=f"📁 {group.name}", padding=10)
        frame.pack(fill="x", pady=8)

        ttk.Label(frame, text="(No rules in this group yet)", foreground="#888888").pack(anchor="w", padx=10)

    def render_rule(self, rule, index):
        container = ttk.Frame(self.list_frame)
        container.pack(fill="x", pady=6, padx=5, anchor="w")

        is_expanded = tk.BooleanVar(value=False)

        title_frame = ttk.Frame(container)
        title_frame.pack(fill="x")

        toggle_btn = ttk.Label(title_frame, text="▶", width=2)
        toggle_btn.pack(side="left")

        name_label = ttk.Label(title_frame, text=f"📄 {rule.name}", font=("Segoe UI", 10))
        name_label.pack(side="left", anchor="w")

        btns = ttk.Frame(title_frame)
        btns.pack(side="right")

        btn_edit = ttk.Button(btns, text="🖊️", width=3, command=lambda r=rule, i=index: self.controller.open_rule_editor(rule=r, index=i))
        btn_edit.pack(side="right", padx=2)
        Tooltip(btn_edit, "Edit Rule")

        btn_delete = ttk.Button(btns, text="🗑️", width=3, command=lambda r=rule: self.delete_rule(r))
        btn_delete.pack(side="right", padx=2)
        Tooltip(btn_delete, "Delete Rule")

        btn_duplicate = ttk.Button(btns, text="📑", width=3, command=lambda r=rule: self.controller.duplicate_rule(r))
        btn_duplicate.pack(side="right", padx=2)
        Tooltip(btn_duplicate, "Duplicate Rule")
        
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
    
    def delete_rule(self, rule):
        confirm = tk.messagebox.askyesno("Delete Rule", f"Are you sure you want to delete '{rule.name}'?")
        if confirm:
            if rule in self.controller.rule_manager.rules:
                self.controller.rule_manager.rules.remove(rule)
                self.controller.rule_manager.save_rules()
                self.controller.view.show_rules(self.controller.rule_manager.rules)

    def add_group(self):
        def on_submit():
            name = name_var.get().strip()
            if name:
                self.controller.rule_manager.create_group(name)
                self.controller.view.show_rules(self.controller.rule_manager.rules)
                popup.destroy()

        popup = tk.Toplevel(self)
        popup.title("New Rule Group")
        popup.geometry("300x180")
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(popup, text="Group name:", font=("Segoe UI", 10)).pack(pady=(15, 5))
        name_var = tk.StringVar(value=f"Group #{len(self.controller.rule_manager.rules) + 1}")
        name_entry = ttk.Entry(popup, textvariable=name_var, width=30)
        name_entry.pack()

        # Future options (disabled for now)
        options_frame = ttk.LabelFrame(popup, text="Group Options (coming soon)", padding=10)
        options_frame.pack(fill="x", padx=10, pady=10)

        tk.Checkbutton(options_frame, text="Enable/Disable group", state="disabled").pack(anchor="w")

        btns = ttk.Frame(popup)
        btns.pack(pady=10)

        ttk.Button(btns, text="Create", command=on_submit).pack(side="left", padx=5)
        ttk.Button(btns, text="Cancel", command=popup.destroy).pack(side="left", padx=5)

        name_entry.focus_set()
