from model.rule_base import BaseRule
from model.rule_group import RuleGroup
from model.dynamic_rule import DynamicRule

import os
import json
import importlib
import shutil

RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "rules.json")

class RuleManager:
    def __init__(self, plugin_dir=None, data_file=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.plugin_dir = plugin_dir or os.path.join(base_dir, "..", "plugins")
        self.data_file = data_file or os.path.join(base_dir, "..", "data", "rules.json")
        self.available_rule_classes = {}

        self.available_rule_classes = {
                    "DynamicRule": DynamicRule   # ✅ Register it up front
                }

        self.rules = []

    def load_plugins(self):
        for file in os.listdir(self.plugin_dir):
            if file.endswith(".py") and not file.startswith("_"):
                modname = file[:-3]

                import importlib.util
                plugin_path = os.path.join(self.plugin_dir, f"{modname}.py")
                spec = importlib.util.spec_from_file_location(modname, plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for item in dir(module):
                    obj = getattr(module, item)
                    if isinstance(obj, type) and issubclass(obj, BaseRule) and obj is not BaseRule:
                        self.available_rule_classes[obj.__name__] = obj

    def load_rules(self):
        if not os.path.exists(RULES_PATH) or os.path.getsize(RULES_PATH) == 0:
            self.rules = []
            return

        try:
            with open(RULES_PATH, "r") as f:
                rule_dicts = json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load rules.json: {e}")
            self.rules = []
            return

        self.rules = []
        for rd in rule_dicts:
            rule_type = rd.get("type")

            if rule_type == "group":
                try:
                    self.rules.append(RuleGroup.from_dict(rd))
                except Exception as e:
                    print(f"⚠️ Failed to load group: {rd.get('name', '?')} ({e})")
            else:
                rule_type = rd.get("rule_type")
                if rule_type and rule_type in self.available_rule_classes:
                    rule_cls = self.available_rule_classes[rule_type]
                    rule = rule_cls(rd["name"], rd.get("config", {}))
                    self.rules.append(rule)
                else:
                    print(f"⚠️ Unknown rule type: {rule_type}")

    def save_rules(self):
        if os.path.exists(RULES_PATH):
            shutil.copy(RULES_PATH, RULES_PATH + ".bak")

        def safe_to_dict(r):
            try:
                return r.to_dict()
            except Exception as e:
                print(f"⚠️ Could not serialize rule: {getattr(r, 'name', '?')} ({e})")
                return None

        safe_list = [safe_to_dict(r) for r in self.rules]
        valid_rules = [r for r in safe_list if r is not None]

        with open(RULES_PATH, "w") as f:
            json.dump(valid_rules, f, indent=4)

    def create_group(self, name):
        group = RuleGroup(name)
        self.rules.append(group)
        self.save_rules()
        return group
