from tkinter import ttk, filedialog, messagebox
from view.widgets.condition_group import ConditionGroup
from view.widgets.action_row import ActionRow

import tkinter as tk
from tkinter import messagebox
import sys
import os
import glob

class RuleEditor(tk.Frame):
    def __init__(self, parent, controller, rule=None, rule_index=None):
        print("[RuleEditor] __init__ called")

        super().__init__(parent, bg="#f9f9f9")
        self.controller = controller
        self.rule = rule
        self.rule_index = rule_index
        self.action_rows = []

        self.rule_name = tk.StringVar(value=self.rule.name if self.rule else "")
        self.tab_name = self.rule_name.get()  # ✅ Use the current input name as tab_name
        self.monitor_mode = tk.StringVar(value=self.rule.config.get("monitor_mode", "watchdog") if self.rule else "watchdog")
        self.poll_interval = tk.StringVar(value=self.rule.config.get("poll_interval", "10") if self.rule else "10")
        self.poll_unit = tk.StringVar(value=self.rule.config.get("poll_unit", "Minutes") if self.rule else "Minutes")
        
        def on_rule_name_change(*_):
            new_name = self.rule_name.get().strip()

            if not new_name:
                return  # Don’t rename to empty string

            if new_name != self.tab_name:
                # Save old reference and rename tab
                self.controller.view.rename_tab(self.tab_name, new_name)
                self.tab_name = new_name

            # Always mark as dirty even if name matches
            self.mark_dirty()

        self.rule_name.trace_add("write", on_rule_name_change)

        self.folder_rows = []  # holds dicts: {path_var, subs_var, frame}

        self.is_dirty = False  # ✅ Set early

        self.build_ui()  # ✅ After trace bindings

    def mark_dirty(self):
        if not self.tab_name:
            self.tab_name = self.rule_name.get()  # fallback for any future use
        if not self.is_dirty:
            self.is_dirty = True
            if self.tab_name:
                self.controller.view.mark_tab_dirty(self.tab_name)

    def toggle_monitor_options(self):
        if self.monitor_options.winfo_ismapped():
            self.monitor_options.pack_forget()
        else:
            self.monitor_options.pack(fill="x", padx=5, pady=(0, 10))

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
        ttk.Entry(header, textvariable=self.rule_name).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(header, text="👁 Preview", command=self.preview_rule).pack(side="right", padx=5)
        ttk.Button(header, text="💾 Save", command=self.save_rule).pack(side="right", padx=5)

        content = tk.Frame(self.scrollable_frame, bg="#f9f9f9")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        folder_frame = ttk.LabelFrame(content, text="Monitor Folders")
        folder_frame.pack(fill="x", pady=10)

        self.folder_container = ttk.Frame(folder_frame)
        self.folder_container.pack(fill="x")

        self.add_folder_row(
            preset_path=self.rule.config.get("pattern", "") if self.rule else "",
            preset_include=self.rule.config.get("include_subs", False) if self.rule else False
        )

        ttk.Button(folder_frame, text="➕ Add Folder", command=self.add_folder_row).pack(anchor="w", padx=5, pady=5)

        self.monitor_options = ttk.Frame(folder_frame)
        self.monitor_options.pack(fill="x", padx=5, pady=(2, 5))
        self.monitor_options.pack_forget()

        ttk.Radiobutton(self.monitor_options, text="React on file changes", variable=self.monitor_mode, value="watchdog").pack(anchor="w", pady=(0, 2))
        poll_row = ttk.Frame(self.monitor_options)
        poll_row.pack(anchor="w")

        ttk.Radiobutton(poll_row, text="Check every", variable=self.monitor_mode, value="poll").pack(side="left")
        ttk.Entry(poll_row, textvariable=self.poll_interval, width=5).pack(side="left", padx=(5, 2))
        ttk.Combobox(poll_row, textvariable=self.poll_unit, values=["Seconds", "Minutes", "Hours"], width=8, state="readonly").pack(side="left")

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

    def remove_folder_row(self, row_frame):
        for row in self.folder_rows:
            if row["frame"] == row_frame:
                row_frame.destroy()
                self.folder_rows.remove(row)
                break
        self.mark_dirty()

    def browse_folder_dialog(self, path_var):
        path = filedialog.askdirectory()
        if path:
            path_var.set(path)
            self.mark_dirty()

    def add_folder_row(self, preset_path="", preset_include=False):
        path_var = tk.StringVar(value=preset_path)
        subs_var = tk.BooleanVar(value=preset_include)
        mode_var = tk.StringVar(value="watchdog")
        poll_interval = tk.StringVar(value="10")
        poll_unit = tk.StringVar(value="Minutes")

        # Container frame for full folder block
        outer = ttk.Frame(self.folder_container)
        outer.pack(fill="x", padx=5, pady=3)

        # Row with entry + buttons
        top = ttk.Frame(outer)
        top.pack(fill="x")

        ttk.Entry(top, textvariable=path_var).pack(side="left", fill="x", expand=True)
        ttk.Button(top, text="...", command=lambda: self.browse_folder_dialog(path_var)).pack(side="left", padx=5)

        # Monitor options toggle (this row only)
        def toggle():
            if monitor_frame.winfo_ismapped():
                monitor_frame.pack_forget()
            else:
                monitor_frame.pack(fill="x", padx=5, pady=(2, 5))

        ttk.Button(top, text="⚙️", width=3, command=toggle).pack(side="left", padx=(0, 2))
        ttk.Button(top, text="❌", width=3, command=lambda: self.remove_folder_row(outer)).pack(side="left", padx=(0, 2))

        # Include subfolders checkbox
        ttk.Checkbutton(outer, text="Include subfolders", variable=subs_var).pack(anchor="w", pady=(2, 0))

        # Folder-specific monitor settings frame (with visual border)
        monitor_frame = ttk.LabelFrame(outer, text="Monitor Options")
        monitor_frame.pack_forget()

        ttk.Radiobutton(monitor_frame, text="React on file changes", variable=mode_var, value="watchdog").pack(anchor="w", pady=(0, 2))
        poll_row = ttk.Frame(monitor_frame)
        poll_row.pack(anchor="w")

        ttk.Radiobutton(poll_row, text="Check every", variable=mode_var, value="poll").pack(side="left")
        ttk.Entry(poll_row, textvariable=poll_interval, width=5).pack(side="left", padx=(5, 2))
        ttk.Combobox(poll_row, textvariable=poll_unit, values=["Seconds", "Minutes", "Hours"], width=8, state="readonly").pack(side="left")

        self.folder_rows.append({
            "frame": outer,
            "path": path_var,
            "subs": subs_var,
            "mode": mode_var,
            "interval": poll_interval,
            "unit": poll_unit,
        })

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

        actions_data = [row.get_data() for row in self.action_rows]
        conditions_data = self.condition_group.get_data()

        new_name = self.rule_name.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Rule name is required.")
            return
        
        old_tab_name = self.tab_name

        # Auto-rename if name exists and it's a new rule or renaming another
        existing_names = {r.name for r in self.controller.rule_manager.rules}
        base_name = new_name
        suffix = 1

        def rules_match(r1, r2):
            return r1.name == r2.name and r1.config == r2.config

        existing_names = {r.name for r in self.controller.rule_manager.rules}
        base_name = new_name
        suffix = 1

        def rules_match(r1, name, config):
            return r1.name == name and r1.config == config

        existing_names = {r.name for r in self.controller.rule_manager.rules}
        base_name = new_name
        suffix = 1

        # Check if any *other* rule already has this name and config
        is_duplicate = any(
            rules_match(r, new_name, {
                "folders": [
                    {
                        "path": row["path"].get().strip(),
                        "include_subs": row["subs"].get(),
                        "monitor_mode": row["mode"].get(),
                        "poll_interval": row["interval"].get(),
                        "poll_unit": row["unit"].get(),
                    } for row in self.folder_rows
                ],

                "conditions": self.condition_group.get_data(),
                "actions": [row.get_data() for row in self.action_rows]
            })
            for r in self.controller.rule_manager.rules
            if r is not self.rule
        )

        # Apply (Copy), (Copy 2), etc only if truly duplicated
        while new_name in existing_names and is_duplicate:
            suffix_text = "" if suffix == 1 else f" {suffix}"
            new_name = f"{base_name} (Copy{suffix_text})"
            suffix += 1

        # Ensure it updates the UI and internal name tracking
        if new_name != self.tab_name:
            self.controller.view.rename_tab(self.tab_name, new_name)
            self.tab_name = new_name

        self.rule_name.set(new_name)  # ✅ UI field last
        
        rule_data = {
            "folders": [
                {
                    "path": row["path"].get().strip(),
                    "include_subs": row["subs"].get(),
                    "monitor_mode": row["mode"].get(),
                    "poll_interval": row["interval"].get(),
                    "poll_unit": row["unit"].get(),
                } for row in self.folder_rows
            ],

            "conditions": conditions_data,
            "actions": actions_data,
            "monitor_mode": self.monitor_mode.get(),
            "poll_interval": self.poll_interval.get(),
            "poll_unit": self.poll_unit.get(),

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
        
    def preview_rule(self):

        folders = [
            {
                "path": row["path"].get().strip(),
                "include_subs": row["subs"].get()
            }
            for row in self.folder_rows if row["path"].get().strip()
        ]

        if not folders:
            messagebox.showerror("Missing Folder", "Please choose at least one folder.")
            return

        print(f"[📂 Preview Triggered] For {len(folders)} folder(s)")

        rule_obj = self.controller.rule_manager.available_rule_classes["DynamicRule"](
            self.rule_name.get(),
            {
                "folders": folders,
                "conditions": self.condition_group.get_data(),
                "actions": [row.get_data() for row in self.action_rows],
            },
        )

        matched = set()

        # Normalize and filter duplicates from nested paths
        normalized = []
        for f in folders:
            f_path = os.path.abspath(f["path"])
            f["abs_path"] = f_path
            normalized.append(f)

        # Skip subfolders already covered by a parent with include_subs=True
        def is_covered(f, others):
            return any(
                o["include_subs"] and f["abs_path"].startswith(o["abs_path"] + os.sep)
                for o in others if o != f
            )

        filtered_folders = [f for f in normalized if not is_covered(f, normalized)]

        for folder in filtered_folders:
            root = folder["abs_path"]
            include_subs = folder.get("include_subs", False)

            if include_subs:
                for dirpath, _, filenames in os.walk(root):
                    for f in filenames:
                        path = os.path.join(dirpath, f)
                        if rule_obj.match(path):
                            matched.add(path)
            else:
                try:
                    for f in os.listdir(root):
                        path = os.path.join(root, f)
                        if os.path.isfile(path) and rule_obj.match(path):
                            matched.add(path)
                except Exception as e:
                    print(f"[⚠️ Preview Error] Failed to list {root}: {e}")

        # UI display (no changes here)
        popup = tk.Toplevel(self)
        popup.title("Preview Rule Matches")
        popup.resizable(False, False)
        popup.geometry("600x400")

        popup.update_idletasks()
        w, h = 600, 400
        x = (popup.winfo_screenwidth() // 2) - (w // 2)
        y = (popup.winfo_screenheight() // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")
        popup.transient(self.winfo_toplevel())
        popup.grab_set()

        ttk.Label(popup, text=f"{len(matched)} file(s) matched:", font=("Segoe UI", 10, "bold")).pack(pady=10)
        frame = ttk.Frame(popup)
        frame.pack(fill="both", expand=True, padx=10)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Segoe UI", 9))
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        for path in sorted(matched):
            listbox.insert("end", path)

        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)
