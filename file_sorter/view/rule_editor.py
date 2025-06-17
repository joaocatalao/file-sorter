from view.widgets.condition_group import ConditionGroup
from view.widgets.action_row import ActionRow
from view.widgets.toolbar import Toolbar
from view.widgets.rule_name_section import RuleNameSection
from view.widgets.monitor_list import MonitorList
from view.widgets.condition_section import ConditionSection

import tkinter as tk
from tkinter import messagebox
from collections import defaultdict
from tkinter import ttk, filedialog, messagebox
import os
import logging

class RuleEditor(tk.Frame):
    def __init__(self, parent, controller, rule=None, rule_index=None):

        super().__init__(parent, bg="#f9f9f9")
        self.controller = controller
        self.rule = rule
        self.rule_index = rule_index
        self.action_rows = []

        logger = logging.getLogger(__name__)
        logger.debug(f"[RuleEditor] Initialized with rule: {self.rule.name if self.rule else 'New'}")

        self.rule_status = tk.StringVar(value="Stopped")
        self.is_running = False

        self.rule_name = tk.StringVar(value=self.rule.name if self.rule else "")
        self.tab_name = self.rule_name.get()  # ✅ Use the current input name as tab_name
    
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

        self.is_dirty = False  # ✅ Set early

        self.build_ui()  # ✅ After trace bindings

    def mark_dirty(self):
        if not self.tab_name:
            self.tab_name = self.rule_name.get()  # fallback for any future use
        if not self.is_dirty:
            self.is_dirty = True
            if self.tab_name:
                self.controller.view.mark_tab_dirty(self.tab_name)

    def build_ui(self):
        def toggle_start():
            self.is_running = not self.is_running
            self.rule_status.set("Running" if self.is_running else "Stopped")
            self.indicator.itemconfig("dot", fill="#4caf50" if self.is_running else "#ccc")
            self.start_button.config(text="⏹ Stop" if self.is_running else "▶ Start")

        status_frame = ttk.Frame(self)

        self.indicator = tk.Canvas(status_frame, width=10, height=10, highlightthickness=0)
        self.indicator.pack(side="left", padx=(0, 5))

        self.indicator.create_oval(2, 2, 10, 10, fill="#ccc", outline="#888", tags="dot")

        status_label = ttk.Label(status_frame, textvariable=self.rule_status, foreground="#555")
        status_label.pack(side="left")

        # --- Toolbar (above scrollable area) ---
        self.toolbar = Toolbar(
            self,
            left_buttons=[
                {"text": "▶ Start", "command": toggle_start, "tooltip": "Start or stop rule"},
                # No status_frame passed here
            ],
            right_buttons=[
                {"text": "👁 Preview", "command": self.preview_rule, "tooltip": "Preview matching files"},
                {"text": "💾 Save", "command": self.save_rule, "tooltip": "Save rule"}
            ]
        )
        self.indicator = self.toolbar.add_status_indicator(self.rule_status, is_running=self.is_running)
        self.toolbar.pack(fill="x", pady=(0, 10))

        self.start_button = self.toolbar.left_area.winfo_children()[0]  # Keep ref

        # --- Scrollable Content ---
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
        
        # Main content wrapper
        content = tk.Frame(self.scrollable_frame, bg="#f9f9f9")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Rule name section
        RuleNameSection(
            content,
            controller=self.controller,
            name_var=self.rule_name,
            on_rename=lambda old, new: self.controller.view.rename_tab(old, new),
            on_dirty=self.mark_dirty
        )

        # Folder section
        self.monitor_section = MonitorList(
            content,
            paths=self.rule.config.get("folders", []) if self.rule else [],
            on_dirty=self.mark_dirty
        )

        # Condition section
        self.condition_section = ConditionSection(
            content,
            controller=self.controller,
            rule=self.rule,
            on_dirty=self.mark_dirty
        )

        # Action section
        action_frame = ttk.LabelFrame(content, text="Then")
        action_frame.pack(fill="x", pady=(0, 10))  # ✅ consistent

        self.action_container = tk.Frame(action_frame, bg="#f9f9f9")
        self.action_container.pack(fill="x", padx=5, pady=5)

        ttk.Button(action_frame, text="➕ Add Action", command=self.add_action_row).pack(anchor="w", padx=5, pady=(0, 5))

        if self.rule and "actions" in self.rule.config:
            for action_cfg in self.rule.config["actions"]:
                self.add_action_row(preset=action_cfg)
        else:
            self.add_action_row()

        logger = logging.getLogger(__name__)
        logger.debug("[RuleEditor] UI built successfully")

    def add_action_row(self, preset=None):
        row = ActionRow(self.action_container, controller=self.controller, preset=preset, on_delete=lambda: self.remove_action_row(row))
        self.action_rows.append(row)

    def remove_action_row(self, row):
        row.frame.destroy()
        if row in self.action_rows:
            self.action_rows.remove(row)

    def save_rule(self):

        actions_data = [row.get_data() for row in self.action_rows]
        conditions_data = self.condition_section.get_data()

        new_name = self.rule_name.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Rule name is required.")
            return
        
        old_tab_name = self.tab_name

        # Auto-rename if name exists and it's a new rule or renaming another
        existing_names = {r.name for r in self.controller.rule_manager.rules}
        base_name = new_name
        suffix = 1

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
                "folders": self.monitor_section.get_config(),
                "conditions": self.condition_section.get_data(),
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
            "folders": self.monitor_section.get_config(),
            "conditions": self.condition_section.get_data(),
            "actions": [row.get_data() for row in self.action_rows],
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
        logger = logging.getLogger(__name__)
        folders = [
            {
                "path": row["path"].strip(),
                "include_subs": row["include_subs"]
            }
            for row in self.monitor_section.get_rows() if row["path"].strip()
        ]

        if not folders:
            messagebox.showerror("Missing Folder", "Please choose at least one folder.")
            return

        logger.info(f"[Preview] Triggered for rule '{self.rule_name.get()}' on {len(folders)} folder(s)")

        rule_obj = self.controller.rule_manager.available_rule_classes["DynamicRule"](
            self.rule_name.get(),
            {
                "folders": folders,
                "conditions": self.condition_section.get_data(),
                "actions": [row.get_data() for row in self.action_rows],
            },
        )

        def nested_dict():
            return defaultdict(nested_dict)

        grouped_tree = nested_dict()

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
                            relative_path = os.path.relpath(path, root)
                            # Group by declared root path (not dirpath), keeping relative subfolder structure
                            parts = os.path.relpath(path, root).split(os.sep)
                            node = grouped_tree[os.path.normpath(root)]
                            for part in parts[:-1]:  # all folders
                                node = node[part]
                            node.setdefault("_files", []).append(parts[-1])

            else:
                try:
                    for f in os.listdir(root):
                        path = os.path.join(root, f)
                        if os.path.isfile(path) and rule_obj.match(path):
                            relative_path = os.path.relpath(path, root)
                            # Group by declared root path (not dirpath), keeping relative subfolder structure
                            parts = os.path.relpath(path, root).split(os.sep)
                            node = grouped_tree[os.path.normpath(root)]
                            for part in parts[:-1]:  # all folders
                                node = node[part]
                            node.setdefault("_files", []).append(parts[-1])

                except Exception as e:
                    logger.error(f"[Preview] Failed to list {root}: {e}")

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

        def count_files(node):
            count = 0
            for key, value in node.items():
                if key == "_files":
                    count += len(value)
                else:
                    count += count_files(value)
            return count

        total_files = sum(count_files(tree) for tree in grouped_tree.values())

        ttk.Label(popup, text=f"{total_files} file(s) matched:", font=("Segoe UI", 10, "bold")).pack(pady=10)

        frame = ttk.Frame(popup)
        frame.pack(fill="both", expand=True, padx=10)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Segoe UI", 9))
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        expanded_state = {}  # full path -> bool
        index_map = {}

        def render_node(node, prefix="", full_path=""):
            for key, child in sorted(node.items()):
                if key == "_files":
                    for f in sorted(child):
                        listbox.insert("end", f"{prefix}  - {f}")
                else:
                    path = f"{full_path}/{key}" if full_path else key
                    is_open = expanded_state.get(path, False)
                    icon = "▼" if is_open else "▶"
                    idx = listbox.size()
                    listbox.insert("end", f"{prefix}{icon} 📁 {key}")
                    index_map[idx] = ("folder", path, child, prefix + "    ")
                    if is_open:
                        render_node(child, prefix + "    ", path)

        def on_click(event):
            widget = event.widget
            idx = widget.nearest(event.y)
            if idx in index_map:
                kind, path, node, prefix = index_map[idx]
                if kind == "folder":
                    # Toggle open/close
                    expanded_state[path] = not expanded_state.get(path, False)
                    # Re-render the full list
                    listbox.delete(0, "end")
                    index_map.clear()
                    for root in grouped_tree:
                        listbox.insert("end", f"📁 {root}")
                        render_node(grouped_tree[root], prefix="    ", full_path=root)
                        listbox.insert("end", "")

        # Insert folder groups
        for root in grouped_tree:
            listbox.insert("end", f"📁 {root}")
            render_node(grouped_tree[root], prefix="    ", full_path=root)
            listbox.insert("end", "")  # spacer

        # Bind folder toggle
        listbox.bind("<Button-1>", on_click)

        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

    def destroy(self):
        logger = logging.getLogger(__name__)
        logger.debug("[RuleEditor] destroy() called — cleaning up toolbar")
        if hasattr(self, "toolbar"):
            self.toolbar.destroy()
        super().destroy()
