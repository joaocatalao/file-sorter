import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkFont
import json
import os
import copy

class Rule:
    def __init__(self, name, file_pattern, destination, include_subs=False):
        self.name = name
        self.file_pattern = file_pattern
        self.destination = destination
        self.include_subs = include_subs

    def to_dict(self):
        return {
            "name": self.name,
            "file_pattern": self.file_pattern,
            "destination": self.destination,
            "include_subs": self.include_subs,
            "condition_tree": getattr(self, "_condition_tree", {}),
            "action_list": getattr(self, "_action_list", [])
        }

    @staticmethod
    def from_dict(data):
        rule = Rule(
            data["name"],
            data["file_pattern"],
            data["destination"],
            data.get("include_subs", False)
        )
        rule._condition_tree = data.get("condition_tree", {})
        rule._action_list = data.get("action_list", [])
        return rule

class FileSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Sorter")
        self.root.iconbitmap("favicon.ico")
        self.unsaved_tabs = set()

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=16)
        self.root.option_add("*Font", default_font)

        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        self.rules_file = "data.json"
        self.load_rules()
        self.rule_count = 0
        self.rule_tabs = {}
        self.current_tab_name = None

        self.create_widgets()
        self.switch_tab("Rules")

    def create_widgets(self):
        self.tab_buttons = {}
        self.tab_labels = {}

        self.top_bar = tk.Frame(self.root, bg="#dcdcdc", bd=0)
        self.top_bar.pack(fill="x")

        self.tab_bar = tk.Frame(self.top_bar, bg="#dcdcdc", height=30)
        self.tab_bar.pack(side="left", fill="x", expand=True, padx=6, pady=(4, 0))

        self.settings_btn = ttk.Button(self.top_bar, text="⚙️", command=self.open_settings)
        self.settings_btn.pack(side="right", padx=6, pady=6)

        self.add_tab("Rules", fixed=True)
        self.add_tab("Logs", fixed=True)

        self.content_frame = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid")
        self.content_frame.pack(fill="both", expand=True)

        self.rules_tab = tk.Frame(self.content_frame, bg="#f8f8f8")
        self.logs_tab = tk.Frame(self.content_frame, bg="#f5f5f5")

        self.create_rules_header(self.rules_tab)

        self.rules_content = tk.Frame(self.rules_tab, bg="#f8f8f8")
        self.rules_content.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.populate_rules_list(self.rules_content)

    def add_tab(self, name, fixed=False):
        frame = tk.Frame(self.tab_bar, bg="#dcdcdc")
        frame.pack(side="left", padx=(0, 1))

        tab_label = tk.Label(
            frame,
            text=name,
            bg="#e0e0e0",
            padx=12,
            pady=4,
            bd=1,
            relief="raised"
        )
        tab_label.pack(side="left")
        tab_label.bind("<Button-1>", lambda e, n=name: self.switch_tab(n))
        tab_label.bind("<Enter>", lambda e: tab_label.config(bg="#e6e6e6"))
        tab_label.bind("<Leave>", lambda e: self.reset_tab_style(name))

        if not fixed:
            close_label = tk.Label(frame, text="×", bg="#e0e0e0", padx=6, pady=4, bd=1, relief="raised")
            close_label.pack(side="left")
            close_label.bind("<Button-1>", lambda e, f=frame, n=name: self.close_tab(f, n))
            close_label.bind("<Enter>", lambda e: close_label.config(bg="#ffdddd"))
            close_label.bind("<Leave>", lambda e: self.reset_tab_style(name))

        self.tab_buttons[name] = frame
        self.tab_labels[name] = tab_label

    def reset_tab_style(self, name):
        if name in self.tab_labels:
            if self.current_tab_name == name:
                self.tab_labels[name].config(bg="#ffffff", relief="flat", bd=0)
            else:
                self.tab_labels[name].config(bg="#e0e0e0", relief="raised", bd=1)

    def switch_tab(self, name):
        if self.current_tab_name:
            if self.current_tab_name == "Rules":
                self.rules_tab.pack_forget()
            elif self.current_tab_name == "Logs":
                self.logs_tab.pack_forget()
            elif self.current_tab_name in self.rule_tabs:
                self.rule_tabs[self.current_tab_name].pack_forget()

        self.current_tab_name = name

        for n in list(self.tab_labels.keys()):
            if str(self.tab_labels[n]) != "!label":  # avoid deleted widgets
                self.reset_tab_style(n)

        if name == "Rules":
            self.rules_tab.pack(fill="both", expand=True)
            self.current_tab = self.rules_tab
        elif name == "Logs":
            self.logs_tab.pack(fill="both", expand=True)
            self.current_tab = self.logs_tab
        elif name in self.rule_tabs:
            self.rule_tabs[name].pack(fill="both", expand=True)
            self.current_tab = self.rule_tabs[name]

    def close_tab(self, frame, name):
        if name not in self.rule_tabs:
            name = self.current_tab_name

        tab_frame = self.rule_tabs.get(name)
        if not tab_frame or not str(tab_frame):
            return  # Already destroyed or invalid

        def do_close():
            if name in self.rule_tabs:
                self.rule_tabs[name].destroy()
                del self.rule_tabs[name]
            if name in self.tab_buttons:
                del self.tab_buttons[name]
            if name in self.tab_labels:
                del self.tab_labels[name]
            if self.current_tab_name == name:
                self.switch_tab("Rules")
            self.unsaved_tabs.discard(name)
            self._closed_tabs = getattr(self, "_closed_tabs", set())
            self._closed_tabs.add(name)
            frame.destroy()

        if name in self.unsaved_tabs:
            confirm = messagebox.askyesnocancel("Unsaved Changes", f"Save changes to '{name}' before closing?")
            if confirm is None:
                return  # Cancelled
            elif confirm:
                # Trigger save button, then close only if successful
                save_btn = None
                try:
                    for widget in tab_frame.winfo_children():
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Button) and "Save" in child.cget("text"):
                                save_btn = child
                                break
                        if save_btn:
                            break
                except tk.TclError:
                    return  # Tab was closed already

                if save_btn:
                    # Set a flag and defer closing until after save
                    self._deferred_close_tab = (frame, name)
                    save_btn.invoke()
                    return

        # If not unsaved or after decline to save
        do_close()

    def create_rules_header(self, parent):
        header_frame = tk.Frame(parent, bg="#f0f0f0", height=50)
        header_frame.pack(fill='x', padx=0, pady=(0, 0))

        add_rule_btn = ttk.Button(header_frame, text="Add Rule", command=self.add_rule)
        add_group_btn = ttk.Button(header_frame, text="Add Rule Group", command=self.add_rule_group)

        add_rule_btn.pack(side='left', padx=10, pady=10)
        add_group_btn.pack(side='left', padx=5, pady=10)

        separator = tk.Frame(parent, height=2, bg="#a0a0a0")
        separator.pack(fill='x', pady=(0, 5))

    def populate_rules_list(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        if not self.rules:
            label = ttk.Label(parent, text="No rules yet.", background="#f8f8f8")
            label.pack(anchor='w', padx=10, pady=10)
            return

        for rule in self.rules:
            frame = ttk.Frame(parent, style="Card.TFrame")
            frame.pack(fill='x', padx=10, pady=5)
            
            dest = rule.destination or (rule._action_list[0]["path"] if getattr(rule, "_action_list", []) else "")

            label = ttk.Label(
                frame,
                text=f"{rule.name}: {rule.file_pattern} → {dest}",
                anchor='w',
                background="#f8f8f8"
            )
            label.pack(side='left', fill='x', expand=True, padx=5)

            clone_btn = ttk.Button(frame, text="📄", width=3, command=lambda r=rule: self.clone_existing_rule(r))
            clone_btn.pack(side='right', padx=2)
            self.create_tooltip(clone_btn, "Clone rule", left_align=True)

            edit_btn = ttk.Button(frame, text="✏️", width=3, command=lambda r=rule: self.edit_existing_rule(r))
            edit_btn.pack(side='right', padx=2)
            self.create_tooltip(edit_btn, "Edit rule", left_align=True)

            delete_btn = ttk.Button(frame, text="🗑️", width=3, command=lambda r=rule: self.delete_existing_rule(r))
            delete_btn.pack(side='right', padx=2)
            self.create_tooltip(delete_btn, "Delete rule", left_align=True)

    def clone_existing_rule(self, rule, existing_rule=None):
        base_name = rule.name + " (Copy"
        existing_titles = set(self.tab_labels.keys()) | set(self.rule_tabs.keys())
        index = 1
        title = f"{base_name})"
        while title in existing_titles:
            index += 1
            title = f"{base_name} {index})"


        self.add_tab(title)
        rule_tab = tk.Frame(self.content_frame, bg="#f9f9f9")
        self.rule_tabs[title] = rule_tab

        # Ensure it can be closed again
        if hasattr(self, "_closed_tabs") and title in self._closed_tabs:
            self._closed_tabs.remove(title)

        self.switch_tab(title)

        cloned_rule = copy.deepcopy(rule)
        self.build_rule_form(
            rule_tab=rule_tab,
            title=title,
            name=title,
            pattern=cloned_rule.file_pattern,
            include_subs=cloned_rule.include_subs,
            destination=cloned_rule.destination,
            existing_rule=cloned_rule,  # ✅ Let it populate UI
            rule_index=None,
            preset_rule=cloned_rule,
            is_cloning=True             # ✅ Force save as new
        )

    def edit_existing_rule(self, rule):
        existing_titles = set(self.tab_labels.keys()) | set(self.rule_tabs.keys())
        title = rule.name

        index = self.rules.index(rule)
        while title in existing_titles:
            title = f"{rule.name} (Edit {index})"
            index += 1

        self.add_tab(title)
        rule_tab = tk.Frame(self.content_frame, bg="#f9f9f9")
        self.rule_tabs[title] = rule_tab

        # Ensure it can be closed again
        if hasattr(self, "_closed_tabs") and title in self._closed_tabs:
            self._closed_tabs.remove(title)

        self.switch_tab(title)
        cloned_rule = copy.deepcopy(rule)

        self.build_rule_form(
            rule_tab=rule_tab,
            title=title,
            name=cloned_rule.name,
            pattern=cloned_rule.file_pattern,
            include_subs=cloned_rule.include_subs,
            destination=cloned_rule.destination,
            existing_rule=cloned_rule,
            rule_index=index
        )

    def delete_existing_rule(self, rule):
        confirm = messagebox.askyesno("Delete Rule", f"Are you sure you want to delete '{rule.name}'?")
        if confirm:
            self.rules.remove(rule)
            self.populate_rules_list(self.rules_content)
        
        self.save_rules()

    def save_rules(self):
        try:
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump([r.to_dict() for r in self.rules], f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save rules: {e}")

    def load_rules(self):
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    rule_dicts = json.load(f)
                    self.rules = [Rule.from_dict(d) for d in rule_dicts]
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load rules: {e}")

    def create_tooltip(self, widget, text, left_align=False):
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.withdraw()
        label = tk.Label(tooltip, text=text, background="#ffffcc", relief="solid", borderwidth=1,
                        font=("Segoe UI", 10), padx=6, pady=4)
        label.pack()

        def enter(event):
            widget.update_idletasks()
            screen_width = widget.winfo_screenwidth()
            label_width = label.winfo_reqwidth()
            widget_x = widget.winfo_rootx()
            if widget_x + label_width + 20 > screen_width:
                x_offset = -label_width - 10
            else:
                x_offset = 20
            x = widget_x + x_offset
            y = widget.winfo_rooty() + 20
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def leave(event):
            tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def build_rule_form(self, rule_tab, title, name, pattern, include_subs, destination, existing_rule=None, rule_index=None, preset_rule=None, is_cloning=False):
        rule_tab.pack(fill='both', expand=True)
        title_container = {'title': title}

        header_frame = tk.Frame(rule_tab, bg="#f0f0f0", height=50)
        header_frame.pack(fill='x', padx=0, pady=(0, 0))

        is_running = tk.BooleanVar(value=False)
        def toggle_rule():
            is_running.set(not is_running.get())
            update_status()

        def update_status():
            indicator_label.config(text="●" if is_running.get() else "○", foreground="green" if is_running.get() else "gray")
            start_stop_btn.config(text="■ Stop" if is_running.get() else "▶ Start")

        indicator_label = tk.Label(header_frame, text="○", font=("Segoe UI", 14), fg="gray", bg="#f0f0f0")
        indicator_label.pack(side='left', padx=(10, 0), pady=10)
        start_stop_btn = ttk.Button(header_frame, text="▶ Start", command=toggle_rule)
        start_stop_btn.pack(side='left', padx=5, pady=10)

        rule_name_var = tk.StringVar()
        rule_name_var.set(name)

        def update_tab_name(*args):
            old_title = title_container['title']
            new_name = rule_name_var.get().strip()
            if new_name and new_name != old_title and new_name not in self.tab_labels:
                if old_title in self.tab_labels:
                    self.tab_labels[new_name] = self.tab_labels.pop(old_title)
                if old_title in self.tab_buttons:
                    self.tab_buttons[new_name] = self.tab_buttons.pop(old_title)
                if old_title in self.rule_tabs:
                    self.rule_tabs[new_name] = self.rule_tabs.pop(old_title)
                self.tab_labels[new_name].config(text=new_name)
                title_container['title'] = new_name
                self.mark_tab_dirty(new_name)

                if old_title in self.unsaved_tabs:
                    self.unsaved_tabs.remove(old_title)
                    self.unsaved_tabs.add(new_name)

                self.current_tab_name = new_name


        def validate_and_save():
            folder = folder_var.get().strip()
            actions_data = [row.get_data() for row in self._action_rows]

            if root_condition_group:
                conditions_data = root_condition_group.get_data()
                if not conditions_data.get("children"):
                    messagebox.showerror("Error", "You must add at least one condition.")
                    return
            else:
                messagebox.showerror("Error", "You must add at least one condition.")
                return
            
            def check_conditions(children):
                for cond in children:
                    if "children" in cond:
                        if not check_conditions(cond["children"]):  # recurse
                            return False
                    else:
                        if not cond.get("value", "").strip():
                            return False
                return True

            if not check_conditions(conditions_data["children"]):
                messagebox.showerror("Error", "One or more conditions are incomplete (missing value).")
                return

            missing = []
            if not rule_name_var.get().strip():
                missing.append("Rule Name")
            if not folder:
                missing.append("Folder")
            if missing:
                messagebox.showerror("Error", "Missing fields: " + ", ".join(missing))
                return

            if not actions_data:
                messagebox.showerror("Error", "You must add at least one action.")
                return

            if any(not a["path"].strip() for a in actions_data):
                messagebox.showerror("Error", "One or more action paths are empty.")
                return

            self.save_rule_from_ui(
                title_container['title'],
                rule_name_var.get(),
                folder,
                include_subs_var.get(),
                existing_rule=existing_rule,
                conditions_data=conditions_data,
                actions_data=actions_data,
                rule_index=rule_index,
                is_cloning=is_cloning,
                close_after_save=True
            )
        
        ttk.Button(header_frame, text="📄 Copy", command=lambda: print("Copy rule UI state")).pack(side='right', padx=5)
        ttk.Button(header_frame, text="📅 Save", command=validate_and_save).pack(side='right', padx=10)

        separator = tk.Frame(rule_tab, height=2, bg="#a0a0a0")
        separator.pack(fill='x', pady=(0, 5))

        container = tk.Frame(rule_tab, bg="#f9f9f9")
        container.pack(fill='both', expand=True, padx=20, pady=20)

        rule_name_frame = tk.LabelFrame(container, text="Rule Name", bg="#f9f9f9")
        rule_name_frame.pack(fill='x', pady=10)
        tk.Entry(rule_name_frame, textvariable=rule_name_var).pack(fill='x', padx=5, pady=5)

        monitor_frame = tk.LabelFrame(container, text="Monitor", bg="#f9f9f9")
        monitor_frame.pack(fill='x', pady=10)
        folder_var = tk.StringVar(value=pattern)
        tk.Entry(monitor_frame, textvariable=folder_var).pack(side='left', fill='x', expand=True, padx=5, pady=5)
        ttk.Button(monitor_frame, text="...", command=lambda: folder_var.set(filedialog.askdirectory())).pack(side='left', padx=5)
        
        include_subs_var = tk.BooleanVar(value=include_subs)
        ttk.Checkbutton(monitor_frame, text="Include subfolders", variable=include_subs_var).pack(side='left', padx=10)

        condition_frame = tk.LabelFrame(container, text="If", bg="#f9f9f9")
        condition_frame.pack(fill='x', pady=10)

        root_condition_group = None  # delay assignment

        def init_root_condition_group():
            nonlocal root_condition_group
            if existing_rule and hasattr(existing_rule, "_condition_tree") and existing_rule._condition_tree:
                root_condition_group = ConditionGroup.from_data(condition_frame, existing_rule._condition_tree, controller=self, is_root=True, tab_name=title_container['title'])

        # Always initialize the appropriate layout
        init_root_condition_group()

        if not existing_rule and preset_rule:
            if hasattr(preset_rule, "_condition_tree") and preset_rule._condition_tree:
                root_condition_group = ConditionGroup(condition_frame, controller=self, tab_name=title_container['title'], is_root=True)

            if hasattr(preset_rule, "_action_list"):
                for preset in preset_rule._action_list:
                    add_action_row(preset)


        if root_condition_group is None:
            def create_top_level_group():
                nonlocal root_condition_group
                root_condition_group = ConditionGroup(condition_frame, controller=self, is_root=True)

            logic_cb = ttk.Combobox(condition_frame, values=["All of the following", "Any of the following", "None of the following"], state="readonly", width=22)
            logic_cb.set("All of the following")
            logic_cb.pack(anchor="w", padx=5, pady=(0, 5))

            button_frame = tk.Frame(condition_frame, bg="#f9f9f9")
            button_frame.pack(anchor="w", padx=5, pady=(0, 5))

            def handle_add_condition():
                create_top_level_group()
                button_frame.destroy()
                logic_cb.pack_forget()
                root_condition_group.logic_cb.set(logic_cb.get())
                root_condition_group.add_condition()

            def handle_add_group():
                create_top_level_group()
                button_frame.destroy()
                logic_cb.pack_forget()
                root_condition_group.logic_cb.set(logic_cb.get())
                root_condition_group.add_group()

            ttk.Button(button_frame, text="➕ Add Condition", command=handle_add_condition).pack(side="left", padx=2)
            ttk.Button(button_frame, text="➕ Add Group", command=handle_add_group).pack(side="left", padx=2)

        action_frame = tk.LabelFrame(container, text="Then", bg="#f9f9f9")
        action_frame.pack(fill='x', pady=10)

        action_rows = []
        self._action_rows = action_rows

        def add_action_row(preset=None, mark_dirty=True):
            row = ActionRow(action_frame, remove_action_row, controller=self, tab_name=title_container['title'], preset=preset)
            action_rows.append(row)
            if mark_dirty:
                self.mark_tab_dirty(title_container['title'])


        def remove_action_row(row):
            if row in action_rows:
                action_rows.remove(row)
            self.mark_tab_dirty(title_container['title'])

        ttk.Button(action_frame, text="➕ Add Action", command=lambda: add_action_row()).pack(anchor="w", padx=5, pady=(0, 5))

        # Add default action only if no preset
        if hasattr(existing_rule, "_action_list"):
            for preset in existing_rule._action_list:
                add_action_row(preset, mark_dirty=False)

        elif existing_rule is not None:
            add_action_row()

        def deferred_dirty_binding():
            rule_name_var.trace_add("write", update_tab_name)
            folder_var.trace_add("write", lambda *_: self.mark_tab_dirty(title_container['title']))
            include_subs_var.trace_add("write", lambda *_: self.mark_tab_dirty(title_container['title']))

        self.root.after_idle(deferred_dirty_binding)

    def add_rule(self):
        existing_titles = set(self.tab_labels.keys()) | set(self.rule_tabs.keys())
        index = 1
        while f"New Rule #{index}" in existing_titles:
            index += 1
        title = f"New Rule #{index}"

        self.add_tab(title)
        rule_tab = tk.Frame(self.content_frame, bg="#f9f9f9")
        self.rule_tabs[title] = rule_tab
        self.switch_tab(title)

        # Use the same form builder as "Edit" or "Clone"
        self.build_rule_form(
            rule_tab=rule_tab,
            title=title,
            name=title,
            pattern="",
            include_subs=False,
            destination=""
        )

    def save_rule_from_ui(self, tab_name, name, pattern, include_subs, existing_rule=None, conditions_data=None, actions_data=None, rule_index=None, is_cloning=False, close_after_save=True):
        if tab_name and pattern:
            if existing_rule and not is_cloning:
                existing_rule.name = name
                existing_rule.file_pattern = pattern
                existing_rule.destination = actions_data[0]["path"] if actions_data else ""  # ✅ INSERT THIS
                existing_rule.include_subs = include_subs
                existing_rule._condition_tree = conditions_data
                existing_rule._action_list = actions_data or []

                # Replace original rule in self.rules
                if rule_index is not None:
                    self.rules[rule_index] = existing_rule

            else:
                first_dest = actions_data[0]["path"] if actions_data else ""
                rule = Rule(name, pattern, first_dest, include_subs)
                rule._condition_tree = conditions_data
                rule._action_list = actions_data or []

                for existing in self.rules:
                    if existing.name == name:
                        messagebox.showwarning("Duplicate", f"A rule named '{name}' already exists.")
                        return

                self.rules.append(rule)

                self._closed_tabs = getattr(self, "_closed_tabs", set())
                if tab_name in self._closed_tabs:
                    self._closed_tabs.remove(tab_name)
            
            self.save_rules()
            self.populate_rules_list(self.rules_content)
            self._initial_condition_row = None
            self.mark_tab_clean(tab_name)

            if close_after_save:
                if tab_name in self.tab_buttons and tab_name not in getattr(self, "_closed_tabs", set()):
                    self.close_tab(self.tab_buttons[tab_name], tab_name)
                    self.switch_tab("Rules")

    def mark_tab_dirty(self, name):
        if name not in self.unsaved_tabs:
            self.unsaved_tabs.add(name)
            if name in self.tab_labels and not self.tab_labels[name]["text"].endswith(" *"):
                self.tab_labels[name]["text"] += " *"

    def mark_tab_clean(self, name):
        if name in self.unsaved_tabs:
            self.unsaved_tabs.remove(name)
            if name in self.tab_labels:
                self.tab_labels[name]["text"] = self.tab_labels[name]["text"].rstrip(" *")

        if hasattr(self, "_deferred_close_tab"):
            deferred_frame, deferred_name = self._deferred_close_tab
            del self._deferred_close_tab
            self.close_tab(deferred_frame, deferred_name)
            return

    def add_rule_group(self):
        print("Add Rule Group clicked")

    def open_settings(self):
        messagebox.showinfo("Settings", "Settings dialog would open here.")

class ConditionGroup:
    def __init__(self, master, remove_callback=None, controller=None, tab_name=None, is_root=False, preset=None):
        self._controller = controller
        self._tab_name = tab_name

        self.frame = tk.Frame(master, bg="#eaeaea", padx=8, pady=6, bd=1, relief="groove")
        self.frame.pack(fill="x", pady=5)

        logic_container = tk.Frame(self.frame, bg="#eaeaea")
        logic_container.pack(anchor="w", pady=(0, 5))  # use anchor to avoid spreading full width

        self.logic_cb = ttk.Combobox(
            logic_container,
            values=["All of the following", "Any of the following", "None of the following"],
            state="readonly",
            width=22
        )
        self.logic_cb.set("All of the following")
        self.logic_cb.pack(side="left", padx=(0, 5))
        self.logic_cb.bind("<<ComboboxSelected>>", lambda e: self._controller.mark_tab_dirty(self._tab_name))

        if remove_callback:
            remove_btn = ttk.Button(logic_container, text="❌", width=3, command=self.remove)
            remove_btn.pack(side="right", padx=(5, 0))

        self.children = []
        self.remove_callback = remove_callback

        button_frame = tk.Frame(self.frame, bg="#f0f0f0")
        button_frame.pack(anchor="w", pady=5)

        ttk.Button(button_frame, text="➕ Add Condition", command=self.add_condition).pack(side="left", padx=2)
        ttk.Button(button_frame, text="➕ Add Group", command=self.add_group).pack(side="left", padx=2)

    def add_condition(self):
        row = ConditionRow(self.frame, self.remove_child, controller=self._controller, tab_name=self._tab_name)
        self.children.append(row)
        self._controller.mark_tab_dirty(self._tab_name)

    def add_group(self):
        group = ConditionGroup(self.frame, remove_callback=self.remove_child, controller=self._controller, tab_name=self._tab_name)
        self.children.append(group)
        self._controller.mark_tab_dirty(self._tab_name)

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            self._controller.mark_tab_dirty(self._tab_name)

    def remove(self):
        self.frame.destroy()
        if self.remove_callback:
            self.remove_callback(self)
        self._controller.mark_tab_dirty(self._tab_name)

    def get_data(self):
        return {
            "logic": self.logic_cb.get(),
            "children": [child.get_data() for child in self.children]
        }
    
    @staticmethod
    def from_data(master, data, remove_callback=None, controller=None, tab_name=None, is_root=False):
        group = ConditionGroup(master, remove_callback=remove_callback, controller=controller, tab_name=tab_name, is_root=is_root)
        group.logic_cb.set(data.get("logic", "All of the following"))

        # remove auto-added first condition row
        for child in group.children:
            child.frame.destroy()
        group.children.clear()

        for child_data in data.get("children", []):
            if "children" in child_data:
                # it's a nested group
                subgroup = ConditionGroup.from_data(group.frame, child_data, remove_callback=group.remove_child, controller=controller, tab_name=tab_name)
                group.children.append(subgroup)
            else:
                row = ConditionRow(group.frame, group.remove_child, preset=child_data, controller=controller, tab_name=tab_name)
                group.children.append(row)

        return group

class ConditionRow:
    def __init__(self, master, remove_callback, controller, tab_name, is_first=False, preset=None):
        self.controller = controller
        self.tab_name = tab_name

        self.frame = tk.Frame(master, bg="#f9f9f9")
        self.frame.pack(fill="x", pady=3, padx=10)

        self.type_cb = ttk.Combobox(self.frame, values=["File name", "File extension", "File size", "File contents"], width=15)
        self.type_cb.set("File name")
        self.type_cb.pack(side="left", padx=5)

        self.compare_cb = ttk.Combobox(self.frame, values=["Is", "Is Not", "Contains", "Does Not Contain"], width=15)
        self.compare_cb.set("Contains")
        self.compare_cb.pack(side="left", padx=5)

        self.input_type_cb = ttk.Combobox(self.frame, values=["Text", "Regex", "Date", "Pattern"], width=12)
        self.input_type_cb.set("Text")
        self.input_type_cb.pack(side="left", padx=5)

        self.value_entry = tk.Entry(self.frame)
        self.value_entry.pack(side="left", fill="x", expand=True, padx=5)

        if preset:
            self.type_cb.set(preset.get("type", "File name"))
            self.compare_cb.set(preset.get("comparison", "Contains"))
            self.input_type_cb.set(preset.get("input_type", "Text"))
            self.value_entry.insert(0, preset.get("value", ""))

        if not is_first:
            remove_btn = ttk.Button(self.frame, text="❌", width=3, command=self.remove)
            remove_btn.pack(side="right", padx=5)

        for widget in (self.type_cb, self.compare_cb, self.input_type_cb):
            widget.bind("<<ComboboxSelected>>", lambda e: self.controller.mark_tab_dirty(self.tab_name))
        self.value_entry.bind("<KeyRelease>", lambda e: self.controller.mark_tab_dirty(self.tab_name))

        self.remove_callback = remove_callback

    def remove(self):
        self.frame.destroy()
        self.remove_callback(self)

    def get_data(self):
        return {
            "type": self.type_cb.get(),
            "comparison": self.compare_cb.get(),
            "input_type": self.input_type_cb.get(),
            "value": self.value_entry.get()
        }

class ActionRow:
    def __init__(self, master, remove_callback, controller, tab_name, preset=None):
        self.controller = controller
        self.tab_name = tab_name

        self.frame = tk.Frame(master, bg="#f9f9f9")
        self.frame.pack(fill="x", pady=3, padx=10)

        self.action_cb = ttk.Combobox(self.frame, values=["Move file", "Rename file", "Delete file", "Copy file"], width=15)
        self.action_cb.set("Move file")
        self.action_cb.pack(side="left", padx=5)

        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(self.frame, textvariable=self.path_var)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Bind to mark tab dirty
        self.action_cb.bind("<<ComboboxSelected>>", lambda e: self.controller.mark_tab_dirty(self.tab_name))
        self.path_var.trace_add("write", lambda *_: self.controller.mark_tab_dirty(self.tab_name))

        ttk.Button(self.frame, text="...", command=self.browse).pack(side="left", padx=5)
        ttk.Button(self.frame, text="❌", width=3, command=self.remove).pack(side="right", padx=5)

        self.remove_callback = remove_callback

        if preset:
            self.action_cb.set(preset.get("action", "Move file"))
            self.path_var.set(preset.get("path", ""))

    def browse(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)

    def remove(self):
        self.frame.destroy()
        self.remove_callback(self)
        self.controller.mark_tab_dirty(self.tab_name)

    def get_data(self):
        return {
            "action": self.action_cb.get(),
            "path": self.path_var.get()
        }

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSorterApp(root)

    try:
        root.state("zoomed")
    except:
        try:
            root.attributes('-zoomed', True)
        except:
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.geometry(f"{screen_width}x{screen_height}")

    root.minsize(800, 600)
    root.mainloop()
