from model.rule_manager import RuleManager
from model.dynamic_rule import DynamicRule
from view.main_window import MainWindow
from view.rule_editor import RuleEditor
from config.settings import load_settings, save_settings

import tkinter as tk
import random
import copy
import os

class AppController:
    def __init__(self, root):
        self.root = root
        self.rule_manager = RuleManager()
        self.rule_manager.load_plugins()
        self.rule_manager.load_rules()

        self.settings = load_settings()
        
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
        rule_cls = self.rule_manager.available_rule_classes.get("DynamicRule")
        new_rule = rule_cls(name, config)

        if index is not None:
            self.rule_manager.rules[index] = new_rule
        else:
            self.rule_manager.rules.append(new_rule)

        self.rule_manager.save_rules()
        self.view.show_rules(self.rule_manager.rules)

        return new_rule
    
    def duplicate_rule(self, rule):
        new_config = copy.deepcopy(rule.config)
        base_name = f"{rule.name} (Copy)"
        existing_names = {r.name for r in self.rule_manager.rules}
        count = 1
        new_name = base_name

        while new_name in existing_names:
            count += 1
            new_name = f"{base_name} {count}"

        duplicate = DynamicRule(new_name, new_config)
        internal_tab_id = f"{new_name} ({random.randint(1000,9999)})"

        def build_editor(parent):
            editor = RuleEditor(parent, controller=self, rule=duplicate, rule_index=None)
            editor.tab_name = internal_tab_id  # ✅ Set to internal ID, not rule name
            editor.is_dirty = True
            self.root.after(0, lambda: self.view.mark_tab_dirty(internal_tab_id))
            return editor

        self.view.open_rule_tab(internal_tab_id, build_editor, display_name=new_name)

    def preview_rule(self, rule, folder):

        # Normalize first!
        folder = os.path.abspath(folder)
        print(f"[📂 Preview] Walking folder: {folder}")
        print(f"[👓 Rule Type] {type(rule).__name__}")

        include_subs = rule.config.get("include_subs", False)

        matches = []

        if not os.path.isdir(folder):
            print(f"[❌] Folder does not exist → {folder}")
            return []

        for root, dirs, files in os.walk(folder):
            if not include_subs:
                dirs[:] = []  # prevent os.walk from descending into subfolders

            for fname in files:
                path = os.path.join(root, fname)
                print(f"[🧾] Checking file: {path}")
                try:
                    if rule.match(path):
                        print(f"[✅ MATCHED] → {path}")
                        matches.append(path)
                    else:
                        print(f"[❌ NO MATCH] → {path}")
                except Exception as e:
                    print(f"[⚠️ ERROR] while checking {path}: {e}")

        print(f"[🎯 Preview Result] {len(matches)} match(es)")
        return matches
        
