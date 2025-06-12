from view.main_window import MainWindow
from model.rule_manager import RuleManager
from view.rule_editor import RuleEditor
import tkinter as tk

class AppController:
    def __init__(self, root):
        self.root = root
        self.rule_manager = RuleManager()
        self.rule_manager.load_plugins()
        self.rule_manager.load_rules()

        self.view = MainWindow(root, controller=self)
        self.view.show_rules(self.rule_manager.rules)

    def open_rule_editor(self, rule=None, index=None):
        title = rule.name if rule else f"New Rule #{len(self.rule_manager.rules) + 1}"

        if title in self.view.tabs:
            self.view.show_tab(title)
            return

        # Don't create RuleEditor here — just pass context
        self.view.open_rule_tab(title, rule=rule, index=index)

    def create_or_update_rule(self, name, config, index=None):
        rule_cls = next(iter(self.rule_manager.available_rule_classes.values()))
        new_rule = rule_cls(name, config)

        if index is not None:
            self.rule_manager.rules[index] = new_rule
        else:
            self.rule_manager.rules.append(new_rule)

        self.rule_manager.save_rules()
        self.view.show_rules(self.rule_manager.rules)

        # Close current tab after save
        self.view.close_tab(name)
        return new_rule
