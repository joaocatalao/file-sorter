from view.main_window import MainWindow
from model.rule_manager import RuleManager
from view.rule_editor import RuleEditor

import tkinter as tk
import random

class AppController:
    def __init__(self, root):
        self.root = root
        self.rule_manager = RuleManager()
        self.rule_manager.load_plugins()
        self.rule_manager.load_rules()

        self.settings = {
            "close_tab_after_save": True,  # 🧩 will use later
            "minimize_to_tray": False
        }
        
        self.view = MainWindow(root, controller=self)
        self.view.show_rules(self.rule_manager.rules)

    def _generate_unique_rule_title(self):
        base = "New Rule"
        # Get saved rule names
        rule_names = {r.name for r in self.rule_manager.rules}
        # Get displayed tab names
        tab_names = {tab["label"].cget("text").rstrip(" *") for tab in self.view.tabs.values()}
        used = rule_names.union(tab_names)

        for i in range(1, 1000):
            name = f"{base} #{i}"
            if name not in used:
                return name

        return f"{base} #{len(used) + 1}"  # fallback

    def open_rule_editor(self, rule=None, index=None):
        if rule:
            title = rule.name
            internal_id = title
        else:
            title = self._generate_unique_rule_title()
            internal_id = f"{title} ({random.randint(1000,9999)})"

        print(f"[AppController] Opening RuleEditor tab: {title}")

        if title in self.view.tabs:
            self.view.show_tab(title)
            return

        def build_editor(parent):
            print("[AppController] Instantiating RuleEditor in container")
            return RuleEditor(parent, controller=self, rule=rule, rule_index=index)

        self.view.open_rule_tab(internal_id, build_editor, display_name=title)

    def create_or_update_rule(self, name, config, index=None):
        rule_cls = next(iter(self.rule_manager.available_rule_classes.values()))
        new_rule = rule_cls(name, config)

        if index is not None:
            self.rule_manager.rules[index] = new_rule
        else:
            self.rule_manager.rules.append(new_rule)

        self.rule_manager.save_rules()
        self.view.show_rules(self.rule_manager.rules)

        return new_rule
