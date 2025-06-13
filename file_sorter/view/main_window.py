from view.tab_rules import RulesTab
from view.tab_logs import LogsTab
from view.tab_settings import SettingsTab

import tkinter as tk
from tkinter import ttk
import os

class MainWindow:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Document Sorter")

        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "favicon.ico"))
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self.tabs = {}
        self.current_tab = None

        self.build_ui()
        self.show_tab("Rules")

    def build_ui(self):
        self.top_bar = tk.Frame(self.root, bg="#dcdcdc")
        self.top_bar.pack(fill="x")

        self.tab_bar = tk.Frame(self.top_bar, bg="#dcdcdc", height=30)
        self.tab_bar.pack(side="left", fill="x", expand=True, padx=6, pady=(4, 0))

        self.settings_btn = ttk.Button(self.top_bar, text="⚙️", command=self.open_settings)
        self.settings_btn.pack(side="right", padx=6, pady=6)

        self.content_frame = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid")
        self.content_frame.pack(fill="both", expand=True)

        self.add_tab("Rules", RulesTab)
        self.add_tab("Logs", LogsTab)

    def add_tab(self, name, view_class):
        label = tk.Label(self.tab_bar, text=name, bg="#e0e0e0", padx=12, pady=4, bd=1, relief="raised")
        label.pack(side="left")
        label.bind("<Button-1>", lambda e, n=name: self.show_tab(n))
        label.bind("<Enter>", lambda e: label.config(bg="#e6e6e6"))
        label.bind("<Leave>", lambda e, n=name: label.config(bg="#e0e0e0" if self.current_tab != n else "#ffffff"))

        frame = view_class(self.content_frame, controller=self.controller)
        frame.place(relwidth=1, relheight=1)
        frame.lower()

        self.tabs[name] = {
            "label": label,
            "frame": frame
        }

    def show_tab(self, name):
        if self.current_tab and self.current_tab in self.tabs:
            self.tabs[self.current_tab]["label"].config(bg="#e0e0e0")
            self.tabs[self.current_tab]["frame"].lower()

        self.current_tab = name
        if name in self.tabs:
            self.tabs[name]["label"].config(bg="#ffffff")
            self.tabs[name]["frame"].lift()

    def show_rules(self, rules):
        self.tabs["Rules"]["frame"].display_rules(rules)

    def mark_tab_dirty(self, name):
        if name in self.tabs:
            label = self.tabs[name]["label"]
            if not label.cget("text").endswith("*"):
                label.config(text=label.cget("text") + " *")

    def mark_tab_clean(self, name):
        if name in self.tabs:
            label = self.tabs[name]["label"]
            if label.cget("text").endswith("*"):
                label.config(text=label.cget("text")[:-2])  # remove ' *'

    def open_settings(self):
        if "Settings" in self.tabs:
            self.show_tab("Settings")
            return

        def build_settings(parent):
            from view.tab_settings import SettingsTab
            return SettingsTab(parent, controller=self.controller)

        self.open_rule_tab("Settings", build_settings)

    def open_rule_tab(self, name, widget_factory, display_name=None):
        if name in self.tabs:
            self.show_tab(name)
            return

        print(f"[MainWindow] Creating new tab for: {name}")

        container = tk.Frame(self.tab_bar, bg="#dcdcdc")
        container.pack(side="left")
        print(f"[MainWindow] Tab '{name}' content packed.")

        label_name = display_name or name

        label = tk.Label(container, text=label_name, bg="#e0e0e0", padx=12, pady=4, bd=1, relief="raised")
        label.pack(side="left")
        label.bind("<Button-1>", lambda e, n=name: self.show_tab(n))
        label.bind("<Enter>", lambda e, n=name: label.config(bg="#e6e6e6"))
        label.bind("<Leave>", lambda e, n=name: label.config(bg="#e0e0e0" if self.current_tab != n else "#ffffff"))

        close_btn = tk.Label(container, text="×", bg="#e0e0e0", padx=6, pady=4, bd=1, relief="raised")
        close_btn.pack(side="left")
        close_btn.bind("<Button-1>", lambda e, n=name: self.close_tab(n))
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#ffdddd"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg="#e0e0e0"))

        frame = tk.Frame(self.content_frame, bg="#ffffff")
        frame.place(relwidth=1, relheight=1)

        editor_widget = widget_factory(frame)
        editor_widget.pack(fill="both", expand=True)
        editor_widget.tab_name = name

        self.tabs[name] = {
            "label": label,
            "close": close_btn,
            "frame": frame,
            "container": container
        }

        self.show_tab(name)

    def close_tab(self, name):
        if name not in self.tabs:
            return

        tab = self.tabs[name]
        widget_frame = tab["frame"]
        
        # Check if this frame has children and is a RuleEditor
        if widget_frame.winfo_children():
            editor = widget_frame.winfo_children()[0]
            if hasattr(editor, "is_dirty") and editor.is_dirty:
                from tkinter import messagebox
                confirm = messagebox.askyesnocancel("Unsaved Changes", f"Do you want to save changes to '{name}' before closing?")
                if confirm is None:
                    return  # cancel
                elif confirm:
                    if hasattr(editor, "save_rule"):
                        editor.save_rule()

        # Proceed to destroy
        tab["label"].destroy()
        if "close" in tab:
            tab["close"].destroy()
        if "frame" in tab:
            tab["frame"].destroy()
        if "container" in tab:
            tab["container"].destroy()

        if name in self.tabs:
            del self.tabs[name]
        else:
            print(f"[⚠️ close_tab] Tried to close unknown tab: '{name}'")
            print("🔎 Available tabs:", list(self.tabs.keys()))

        fallback = "Rules" if "Rules" in self.tabs else next(iter(self.tabs), None)
        if fallback:
            self.show_tab(fallback)

    def rename_tab(self, old_name, new_name):
        if old_name in self.tabs:
            tab = self.tabs.pop(old_name)
            self.tabs[new_name] = tab

            current_text = tab["label"].cget("text")
            is_dirty = current_text.endswith("*")
            tab["label"].config(text=new_name + (" *" if is_dirty else ""))

            if "close" in tab:
                tab["close"].bind("<Button-1>", lambda e, n=new_name: self.close_tab(n))

            # Ensure we update current_tab
            if self.current_tab == old_name:
                self.current_tab = new_name

