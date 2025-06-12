import tkinter as tk
from tkinter import ttk
from view.tab_rules import RulesTab
from view.tab_logs import LogsTab
import os

class MainWindow:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Document Sorter")

        icon_path = os.path.join(os.path.dirname(__file__), "..", "favicon.ico")
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

    def open_settings(self):
        from tkinter import messagebox
        messagebox.showinfo("Settings", "Settings dialog would open here.")

    def open_rule_tab(self, title, editor_widget):
        if title in self.tabs:
            self.show_tab(title)
            return

        container = tk.Frame(self.tab_bar, bg="#dcdcdc")
        container.pack(side="left")

        label = tk.Label(container, text=title, bg="#e0e0e0", padx=12, pady=4, bd=1, relief="raised")
        label.pack(side="left")
        label.bind("<Button-1>", lambda e, n=title: self.show_tab(n))
        label.bind("<Enter>", lambda e, n=title: label.config(bg="#e6e6e6"))
        label.bind("<Leave>", lambda e, n=title: label.config(bg="#e0e0e0" if self.current_tab != n else "#ffffff"))

        close_btn = tk.Label(container, text="×", bg="#e0e0e0", padx=6, pady=4, bd=1, relief="raised")
        close_btn.pack(side="left")
        close_btn.bind("<Button-1>", lambda e, n=title: self.close_tab(n))
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#ffdddd"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg="#e0e0e0"))

        frame = tk.Frame(self.content_frame, bg="#ffffff")
        frame.place(relwidth=1, relheight=1)

        editor_widget.master = frame
        editor_widget.pack(fill="both", expand=True)

        self.tabs[title] = {
            "label": label,
            "close": close_btn,
            "frame": frame,
            "container": container
        }

        self.show_tab(title)

    def close_tab(self, name):
        if name not in self.tabs:
            return

        tab = self.tabs[name]

        # Safely destroy all widgets
        tab["label"].destroy()
        if "close" in tab:
            tab["close"].destroy()
        if "frame" in tab:
            tab["frame"].destroy()
        if "container" in tab:
            tab["container"].destroy()  # <- this is the actual tab bar space

        del self.tabs[name]

        fallback = "Rules" if "Rules" in self.tabs else next(iter(self.tabs), None)
        if fallback:
            self.show_tab(fallback)
