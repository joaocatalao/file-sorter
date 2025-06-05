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
        self.current_tab_name = "Rules"

        self.create_widgets()

    def create_widgets(self):
        self.tab_buttons = {}
        self.tab_labels = {}

        # === Header with Tabs + Settings ===
        self.top_bar = tk.Frame(self.root, bg="#dcdcdc", bd=0)
        self.top_bar.pack(fill="x")

        self.tab_bar = tk.Frame(self.top_bar, bg="#dcdcdc", height=30)
        self.tab_bar.pack(side="left", fill="x", expand=True, padx=6, pady=(4, 0))

        self.settings_btn = ttk.Button(self.top_bar, text="⚙️", command=self.open_settings)
        self.settings_btn.pack(side="right", padx=6, pady=6)

        self.add_tab("Rules", fixed=True)
        self.add_tab("Logs", fixed=True)

        # === Tab Content Area ===
        self.content_frame = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid")
        self.content_frame.pack(fill="both", expand=True)

        self.rules_tab = tk.Frame(self.content_frame, bg="#f8f8f8")
        self.logs_tab = tk.Frame(self.content_frame, bg="#f5f5f5")

        self.rules_tab.pack(fill="both", expand=True)
        self.current_tab = self.rules_tab

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
        if self.current_tab_name == name:
            self.tab_labels[name].config(bg="#ffffff", relief="flat", bd=0)
        else:
            self.tab_labels[name].config(bg="#e0e0e0", relief="raised", bd=1)

    def switch_tab(self, name):
        self.current_tab.pack_forget()
        self.current_tab_name = name

        for n, tab in self.tab_labels.items():
            if n == name:
                tab.config(bg="#ffffff", relief="flat", bd=0)
            else:
                tab.config(bg="#e0e0e0", relief="raised", bd=1)

        if name == "Rules":
            self.rules_tab.pack(fill="both", expand=True)
            self.current_tab = self.rules_tab
        elif name == "Logs":
            self.logs_tab.pack(fill="both", expand=True)
            self.current_tab = self.logs_tab
        else:
            self.rule_tabs[name].pack(fill="both", expand=True)
            self.current_tab = self.rule_tabs[name]

    def close_tab(self, frame, name):
        frame.destroy()
        if name in self.rule_tabs:
            self.rule_tabs[name].destroy()
            del self.rule_tabs[name]
        if self.current_tab == self.rule_tabs.get(name):
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
            frame = ttk.Frame(parent)
            frame.pack(fill='x', padx=10, pady=5)

            label = ttk.Label(
                frame,
                text=f"{rule.name}: {rule.file_pattern} → {rule.destination}",
                anchor='w'
            )
            label.pack(side='left', fill='x', expand=True)

    def add_rule(self):
        self.rule_count += 1
        title = f"New Rule #{self.rule_count}"
        self.add_tab(title)

        rule_tab = tk.Frame(self.content_frame, bg="#f9f9f9")
        self.rule_tabs[title] = rule_tab
        self.switch_tab(title)

        container = tk.Frame(rule_tab, bg="#f9f9f9")
        container.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(container, text="Rule Name:", bg="#f9f9f9").pack(anchor='w')
        name_entry = tk.Entry(container)
        name_entry.pack(fill='x', pady=5)

        tk.Label(container, text="File Pattern (e.g. *.pdf):", bg="#f9f9f9").pack(anchor='w')
        pattern_entry = tk.Entry(container)
        pattern_entry.pack(fill='x', pady=5)

        tk.Label(container, text="Destination Folder:", bg="#f9f9f9").pack(anchor='w')
        dest_var = tk.StringVar()
        dest_entry = tk.Entry(container, textvariable=dest_var)
        dest_entry.pack(fill='x', pady=5)

        def choose_folder():
            folder = filedialog.askdirectory()
            if folder:
                dest_var.set(folder)

        ttk.Button(container, text="Browse...", command=choose_folder).pack(anchor='w', pady=5)

        def save_rule():
            name = name_entry.get()
            pattern = pattern_entry.get()
            destination = dest_var.get()

            if name and pattern and destination:
                rule = Rule(name, pattern, destination)
                self.rules.append(rule)
                self.populate_rules_list(self.rules_content)
                self.close_tab(self.tab_buttons[title], title)
                self.switch_tab("Rules")

        ttk.Button(container, text="Save Rule", command=save_rule).pack(pady=20)

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
