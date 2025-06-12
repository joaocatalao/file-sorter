import os
import json
import importlib
from model.rule_base import BaseRule

class RuleManager:
    def __init__(self, plugin_dir=None, data_file=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.plugin_dir = plugin_dir or os.path.join(base_dir, "..", "plugins")
        self.data_file = data_file or os.path.join(base_dir, "..", "data", "rules.json")
        self.available_rule_classes = {}
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
        if not os.path.exists(self.data_file):
            return []
        with open(self.data_file, 'r', encoding='utf-8') as f:
            rule_dicts = json.load(f)
        self.rules.clear()
        for r in rule_dicts:
            rule_type = r.get("rule_type")
            rule_cls = self.available_rule_classes.get(rule_type)
            if rule_cls:
                rule = rule_cls.from_dict(r)
                self.rules.append(rule)
        return self.rules

    def save_rules(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump([r.to_dict() for r in self.rules], f, indent=4)
