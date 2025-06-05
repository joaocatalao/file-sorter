import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkFont

class Rule:
    def __init__(self, name, file_pattern, destination):
        self.name = name
        self.file_pattern = file_pattern
        self.destination = destination

class FileSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Sorter")
        self.root.iconbitmap("favicon.ico")

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=16)
        self.root.option_add("*Font", default_font)

        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        self.rules = []
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
        frame.destroy()
        if name in self.rule_tabs:
            self.rule_tabs[name].destroy()
            del self.rule_tabs[name]
        if name in self.tab_buttons:
            del self.tab_buttons[name]
        if name in self.tab_labels:
            del self.tab_labels[name]

        if self.current_tab_name == name:
            self.switch_tab("Rules")

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

            label = ttk.Label(
                frame,
                text=f"{rule.name}: {rule.file_pattern} → {rule.destination}",
                anchor='w',
                background="#f8f8f8"
            )
            label.pack(side='left', fill='x', expand=True, padx=5)

            clone_btn = ttk.Button(frame, text="🗌", width=3, command=lambda r=rule: self.clone_existing_rule(r))
            clone_btn.pack(side='right', padx=2)
            self.create_tooltip(clone_btn, "Clone rule", left_align=True)

            edit_btn = ttk.Button(frame, text="✏️", width=3, command=lambda r=rule: self.edit_existing_rule(r))
            edit_btn.pack(side='right', padx=2)
            self.create_tooltip(edit_btn, "Edit rule", left_align=True)

            delete_btn = ttk.Button(frame, text="🗑️", width=3, command=lambda r=rule: self.delete_existing_rule(r))
            delete_btn.pack(side='right', padx=2)
            self.create_tooltip(delete_btn, "Delete rule", left_align=True)

    def clone_existing_rule(self, rule):
        existing_titles = set(self.tab_labels.keys()) | set(self.rule_tabs.keys())
        index = 1
        base_name = rule.name + " #"
        while f"{base_name}{index}" in existing_titles:
            index += 1
        title = f"{base_name}{index}"

        self.add_tab(title)
        rule_tab = tk.Frame(self.content_frame, bg="#f9f9f9")
        self.rule_tabs[title] = rule_tab
        self.switch_tab(title)
        self.build_rule_form(rule_tab, title, rule.name + f" #{index}", rule.file_pattern, False, rule.destination)

    def edit_existing_rule(self, rule):
        existing_titles = set(self.tab_labels.keys()) | set(self.rule_tabs.keys())
        title = rule.name
        index = 1
        while title in existing_titles:
            title = f"{rule.name} (Edit {index})"
            index += 1

        self.add_tab(title)
        rule_tab = tk.Frame(self.content_frame, bg="#f9f9f9")
        self.rule_tabs[title] = rule_tab
        self.switch_tab(title)
        self.build_rule_form(rule_tab, title, rule.name, rule.file_pattern, False, rule.destination)

    def delete_existing_rule(self, rule):
        confirm = messagebox.askyesno("Delete Rule", f"Are you sure you want to delete '{rule.name}'?")
        if confirm:
            self.rules.remove(rule)
            self.populate_rules_list(self.rules_content)

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

    def build_rule_form(self, rule_tab, title, name, pattern, include_subs, destination):
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

        rule_name_var = tk.StringVar(value=name)
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
                self.current_tab_name = new_name

        rule_name_var.trace_add("write", update_tab_name)

        def validate_and_save():
            folder = folder_var.get().strip()
            value = value_entry.get().strip()
            dest = dest_var.get().strip()
            missing = []
            if not rule_name_var.get().strip():
                missing.append("Rule Name")
            if not folder:
                missing.append("Folder")
            if not value or (value == "pdf" and value_entry.cget("foreground") == "#a0a0a0"):
                missing.append("Condition Value")
            if not dest:
                missing.append("Destination")
            if missing:
                messagebox.showerror("Error", "Missing fields: " + ", ".join(missing))
                return
            self.save_rule_from_ui(title_container['title'], rule_name_var.get(), folder, value, dest)

        ttk.Button(header_frame, text="📄 Copy", command=lambda: print("Copy rule UI state")).pack(side='right', padx=5)
        ttk.Button(header_frame, text="📅 Save", command=validate_and_save).pack(side='right', padx=10)

        separator = tk.Frame(rule_tab, height=2, bg="#a0a0a0")
        separator.pack(fill='x', pady=(0, 5))

        container = tk.Frame(rule_tab, bg="#f9f9f9")
        container.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(container, text="Rule Name:", bg="#f9f9f9").pack(anchor='w')
        tk.Entry(container, textvariable=rule_name_var).pack(fill='x', pady=5)

        monitor_frame = tk.LabelFrame(container, text="Monitor", bg="#f9f9f9")
        monitor_frame.pack(fill='x', pady=10)
        folder_var = tk.StringVar(value=pattern)
        folder_entry = tk.Entry(monitor_frame, textvariable=folder_var)
        folder_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        ttk.Button(monitor_frame, text="...", command=lambda: folder_var.set(filedialog.askdirectory())).pack(side='left', padx=5)
        include_subs_var = tk.BooleanVar(value=include_subs)
        ttk.Checkbutton(monitor_frame, text="Include subfolders", variable=include_subs_var).pack(side='left', padx=10)

        condition_frame = tk.LabelFrame(container, text="If", bg="#f9f9f9")
        condition_frame.pack(fill='x', pady=10)
        condition_row = tk.Frame(condition_frame, bg="#f9f9f9")
        condition_row.pack(fill='x', padx=5, pady=5)
        type_cb = ttk.Combobox(condition_row, values=["File extension", "File contents"])
        type_cb.set("File extension")
        type_cb.pack(side='left', padx=5)
        compare_cb = ttk.Combobox(condition_row, values=["Is", "Contains"])
        compare_cb.set("Is")
        compare_cb.pack(side='left', padx=5)
        input_type_cb = ttk.Combobox(condition_row, values=["Text"])
        input_type_cb.set("Text")
        input_type_cb.pack(side='left', padx=5)

        value_entry = tk.Entry(condition_row, foreground="#a0a0a0")
        value_entry.insert(0, "pdf")
        def on_focus_in(event):
            if value_entry.get() == "pdf" and value_entry.cget("foreground") == "#a0a0a0":
                value_entry.delete(0, tk.END)
                value_entry.config(foreground="#000000")
        def on_focus_out(event):
            if value_entry.get() == "":
                value_entry.insert(0, "pdf")
                value_entry.config(foreground="#a0a0a0")
        value_entry.bind("<FocusIn>", on_focus_in)
        value_entry.bind("<FocusOut>", on_focus_out)
        value_entry.pack(side='left', fill='x', expand=True, padx=5)

        action_frame = tk.LabelFrame(container, text="Then", bg="#f9f9f9")
        action_frame.pack(fill='x', pady=10)
        action_row = tk.Frame(action_frame, bg="#f9f9f9")
        action_row.pack(fill='x', padx=5, pady=5)
        action_cb = ttk.Combobox(action_row, values=["Move file", "Rename file"])
        action_cb.set("Move file")
        action_cb.pack(side='left', padx=5)
        dest_var = tk.StringVar(value=destination)
        tk.Entry(action_row, textvariable=dest_var).pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(action_row, text="...", command=lambda: dest_var.set(filedialog.askdirectory())).pack(side='left', padx=5)

    def add_rule(self):
        existing_titles = set(self.tab_labels.keys()) | set(self.rule_tabs.keys())
        index = 1
        while f"New Rule #{index}" in existing_titles:
            index += 1
        initial_title = f"New Rule #{index}"
        title_container = {'title': initial_title}

        self.add_tab(initial_title)

        rule_tab = tk.Frame(self.content_frame, bg="#f9f9f9")
        self.rule_tabs[initial_title] = rule_tab
        self.switch_tab(initial_title)

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

        rule_name_var = tk.StringVar(value=initial_title)

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
                if new_name in self.tab_labels:
                    self.tab_labels[new_name].config(text=new_name)
                title_container['title'] = new_name
                self.current_tab_name = new_name

        rule_name_var.trace_add("write", update_tab_name)

        def validate_and_save():
            name = rule_name_var.get().strip()
            folder = folder_var.get().strip()
            value = value_entry.get().strip()
            dest = action_target_var.get().strip()

            missing = []
            if not name:
                missing.append("Rule Name")
            if not folder:
                missing.append("Folder")
            if not value or (value == "pdf" and value_entry.cget("foreground") == "#a0a0a0"):
                missing.append("Condition Value")
            if not dest:
                missing.append("Destination")

            if missing:
                messagebox.showerror("Error", "Missing fields: " + ", ".join(missing))
                return

            self.save_rule_from_ui(title_container['title'], name, folder, value, dest)

        ttk.Button(header_frame, text="💾 Save", command=validate_and_save).pack(side='right', padx=10)

        def copy_rule():
            self.copy_rule_ui(title_container['title'], rule_name_var.get(), folder_var.get(), include_subs.get(),
                            type_cb.get(), compare_cb.get(), input_type_cb.get(),
                            value_entry.get(), action_cb.get(), action_target_var.get())

        ttk.Button(header_frame, text="📋 Copy", command=copy_rule).pack(side='right', padx=5)

        separator = tk.Frame(rule_tab, height=2, bg="#a0a0a0")
        separator.pack(fill='x', pady=(0, 5))

        container = tk.Frame(rule_tab, bg="#f9f9f9")
        container.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(container, text="Rule Name:", bg="#f9f9f9").pack(anchor='w')
        tk.Entry(container, textvariable=rule_name_var).pack(fill='x', pady=5)

        monitor_frame = tk.LabelFrame(container, text="Monitor", bg="#f9f9f9")
        monitor_frame.pack(fill='x', pady=10)

        folder_var = tk.StringVar()
        folder_entry = tk.Entry(monitor_frame, textvariable=folder_var)
        folder_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        ttk.Button(monitor_frame, text="...", command=lambda: folder_var.set(filedialog.askdirectory())).pack(side='left', padx=5)
        include_subs = tk.BooleanVar(value=False)
        ttk.Checkbutton(monitor_frame, text="Include subfolders", variable=include_subs).pack(side='left', padx=10)

        condition_frame = tk.LabelFrame(container, text="If", bg="#f9f9f9")
        condition_frame.pack(fill='x', pady=10)

        condition_row = tk.Frame(condition_frame, bg="#f9f9f9")
        condition_row.pack(fill='x', padx=5, pady=5)

        type_cb = ttk.Combobox(condition_row, values=["File extension", "File contents"])
        type_cb.set("File extension")
        type_cb.pack(side='left', padx=5)

        compare_cb = ttk.Combobox(condition_row, values=["Is", "Contains"])
        compare_cb.set("Is")
        compare_cb.pack(side='left', padx=5)

        input_type_cb = ttk.Combobox(condition_row, values=["Text"])
        input_type_cb.set("Text")
        input_type_cb.pack(side='left', padx=5)

        value_entry = tk.Entry(condition_row, foreground="#a0a0a0")
        value_entry.insert(0, "pdf")
        def on_focus_in(event):
            if value_entry.get() == "pdf" and value_entry.cget("foreground") == "#a0a0a0":
                value_entry.delete(0, tk.END)
                value_entry.config(foreground="#000000")
        def on_focus_out(event):
            if value_entry.get() == "":
                value_entry.insert(0, "pdf")
                value_entry.config(foreground="#a0a0a0")
        value_entry.bind("<FocusIn>", on_focus_in)
        value_entry.bind("<FocusOut>", on_focus_out)
        value_entry.pack(side='left', fill='x', expand=True, padx=5)

        action_frame = tk.LabelFrame(container, text="Then", bg="#f9f9f9")
        action_frame.pack(fill='x', pady=10)

        action_row = tk.Frame(action_frame, bg="#f9f9f9")
        action_row.pack(fill='x', padx=5, pady=5)

        action_cb = ttk.Combobox(action_row, values=["Move file", "Rename file"])
        action_cb.set("Move file")
        action_cb.pack(side='left', padx=5)

        action_target_var = tk.StringVar()
        action_target_entry = tk.Entry(action_row, textvariable=action_target_var)
        action_target_entry.pack(side='left', fill='x', expand=True, padx=5)

        ttk.Button(action_row, text="...", command=lambda: action_target_var.set(filedialog.askdirectory())).pack(side='left', padx=5)

    def save_rule_from_ui(self, tab_name, name, pattern, content_filter, destination):
        if tab_name and pattern and destination:
            rule = Rule(name, pattern, destination)
            self.rules.append(rule)
            self.populate_rules_list(self.rules_content)
            self.close_tab(self.tab_buttons[tab_name], tab_name)
            self.switch_tab("Rules")

    def copy_rule_ui(self, tab_name, name, pattern, include_subs, type_filter, compare, input_type, value, action, target):
        existing_titles = set(self.tab_labels.keys()) | set(self.rule_tabs.keys())
        index = 1
        while f"New Rule #{index}" in existing_titles:
            index += 1
        title = f"New Rule #{index}"

        self.add_tab(title)
        rule_tab = tk.Frame(self.content_frame, bg="#f9f9f9")
        self.rule_tabs[title] = rule_tab
        self.switch_tab(title)

        # TODO: Copy fields exactly as in add_rule with the provided values
        # For brevity, you can extract the rule form into a reusable function later

    def add_rule_group(self):
        print("Add Rule Group clicked")

    def open_settings(self):
        messagebox.showinfo("Settings", "Settings dialog would open here.")

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
