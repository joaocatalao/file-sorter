import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from view.widgets.condition_group import ConditionGroup
from view.widgets.action_row import ActionRow

class RuleEditor(tk.Frame):
    def __init__(self, parent, controller, rule=None, rule_index=None):
        print("[RuleEditor] __init__ called")

        super().__init__(parent, bg="#f9f9f9")
        self.controller = controller
        self.rule = rule
        self.rule_index = rule_index
        self.action_rows = []

        self.rule_name = tk.StringVar(value=self.rule.name if self.rule else "")
        self.folder_path = tk.StringVar(value=self.rule.config.get("pattern", "") if self.rule else "")
        self.include_subs = tk.BooleanVar(value=self.rule.config.get("include_subs", False) if self.rule else False)

        self.build_ui()

        self.is_dirty = False
        self.tab_name = rule.name if rule else None

        self.rule_name.trace_add("write", lambda *_: self.mark_dirty())
        self.folder_path.trace_add("write", lambda *_: self.mark_dirty())
        self.include_subs.trace_add("write", lambda *_: self.mark_dirty())

    def mark_dirty(self):
        if not self.is_dirty:
            self.is_dirty = True
            if self.tab_name:
                self.controller.view.mark_tab_dirty(self.tab_name)

    def build_ui(self):
        print("[RuleEditor] build_ui() called")

        # --- Canvas + Scrollable Frame Wrapper ---
        canvas = tk.Canvas(self, bg="#f9f9f9", borderwidth=0, highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scrollbar.set)

        v_scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame = tk.Frame(canvas, bg="#f9f9f9")
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        def on_frame_resize(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_resize(event):
            canvas.itemconfig(canvas_window, width=event.width)

        self.scrollable_frame.bind("<Configure>", on_frame_resize)
        canvas.bind("<Configure>", on_canvas_resize)

        # Optional: scroll with mouse wheel
        self.scrollable_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda ev: canvas.yview_scroll(-1*(ev.delta//120), "units")))
        self.scrollable_frame.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # --- Everything below goes inside scrollable_frame ---
        header = tk.Frame(self.scrollable_frame, bg="#f0f0f0", height=50)
        header.pack(fill='x')

        ttk.Label(header, text="Rule Name:").pack(side="left", padx=5)
        ttk.Entry(header, textvariable=self.rule_name).pack(side="left", padx=5)
        ttk.Button(header, text="💾 Save", command=self.save_rule).pack(side="right", padx=10)

        content = tk.Frame(self.scrollable_frame, bg="#f9f9f9")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        folder_frame = ttk.LabelFrame(content, text="Monitor Folder")
        folder_frame.pack(fill="x", pady=10)
        ttk.Entry(folder_frame, textvariable=self.folder_path).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(folder_frame, text="...", command=self.browse_folder).pack(side="left", padx=5)
        ttk.Checkbutton(folder_frame, text="Include subfolders", variable=self.include_subs).pack(side="left", padx=10)

        self.cond_frame = ttk.LabelFrame(content, text="If")
        self.cond_frame.pack(fill="x", pady=10)
        self.condition_group = ConditionGroup(self.cond_frame, controller=self.controller)
        if self.rule and "conditions" in self.rule.config:
            self.condition_group.load_data(self.rule.config["conditions"])

        action_frame = ttk.LabelFrame(content, text="Then")
        action_frame.pack(fill="x", pady=10)

        self.action_container = tk.Frame(action_frame, bg="#f9f9f9")
        self.action_container.pack(fill="x", padx=5, pady=5)

        ttk.Button(action_frame, text="➕ Add Action", command=self.add_action_row).pack(anchor="w", padx=5, pady=(0, 5))

        if self.rule and "actions" in self.rule.config:
            for action_cfg in self.rule.config["actions"]:
                self.add_action_row(preset=action_cfg)
        else:
            self.add_action_row()

        print("[RuleEditor] UI built successfully")

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path.set(path)

    def add_action_row(self, preset=None):
        row = ActionRow(self.action_container, controller=self.controller, preset=preset, on_delete=lambda: self.remove_action_row(row))
        self.action_rows.append(row)

    def remove_action_row(self, row):
        row.frame.destroy()
        if row in self.action_rows:
            self.action_rows.remove(row)

    def save_rule(self):
        if not self.rule_name.get().strip():
            messagebox.showerror("Error", "Rule name is required.")
            return

        actions_data = [row.get_data() for row in self.action_rows]
        conditions_data = self.condition_group.get_data()

        rule_data = {
            "pattern": self.folder_path.get().strip(),
            "include_subs": self.include_subs.get(),
            "conditions": conditions_data,
            "actions": actions_data
        }

        rule = self.controller.create_or_update_rule(
            name=self.rule_name.get().strip(),
            config=rule_data,
            index=self.rule_index
        )

        self.rule = rule  # ✅ Needed for later edits
        self.is_dirty = False  # ✅ Reset dirty flag

        # If we should close the tab after save
        if self.controller.settings.get("close_tab_after_save", False):
            self.controller.view.close_tab(self.tab_name)
        else:
            self.controller.view.mark_tab_clean(self.tab_name)  # ✅ Remove *

        messagebox.showinfo("Saved", f"Rule '{rule.name}' saved successfully.")
        
