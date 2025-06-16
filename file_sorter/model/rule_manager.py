import os
import json
import importlib
import shutil
import logging

from model.rule_base import BaseRule
from model.rule_group import RuleGroup
from model.dynamic_rule import DynamicRule

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "rules.json")

class RuleManager:
    def __init__(self, plugin_dir=None, data_file=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.plugin_dir = plugin_dir or os.path.join(base_dir, "..", "plugins")
        self.data_file = data_file or os.path.join(base_dir, "..", "data", "rules.json")
        self.available_rule_classes = {
            "DynamicRule": DynamicRule
        }
        self.rules = []

    def load_plugins(self):
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"[PluginLoader] Plugin directory missing: {self.plugin_dir}")
            return

        for file in os.listdir(self.plugin_dir):
            if file.endswith(".py") and not file.startswith("_"):
                modname = file[:-3]
                plugin_path = os.path.join(self.plugin_dir, f"{modname}.py")
                try:
                    spec = importlib.util.spec_from_file_location(modname, plugin_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for item in dir(module):
                        obj = getattr(module, item)
                        if isinstance(obj, type) and issubclass(obj, BaseRule) and obj is not BaseRule:
                            self.available_rule_classes[obj.__name__] = obj
                            logger.info(f"[PluginLoader] Registered rule class: {obj.__name__}")
                except Exception as e:
                    logger.error(f"[PluginLoader] Failed to load plugin {modname}: {e}")

    def load_rules(self):
        if not os.path.exists(RULES_PATH) or os.path.getsize(RULES_PATH) == 0:
            logger.info(f"[RuleLoader] No rules found at {RULES_PATH}")
            self.rules = []
            return

        try:
            with open(RULES_PATH, "r") as f:
                rule_dicts = json.load(f)
        except Exception as e:
            logger.error(f"[RuleLoader] Failed to load rules.json: {e}")
            self.rules = []
            return

        self.rules = []
        for rd in rule_dicts:
            rule_type = rd.get("type")

            if rule_type == "group":
                try:
                    self.rules.append(RuleGroup.from_dict(rd))
                    logger.info(f"[RuleLoader] Loaded group rule: {rd.get('name', '?')}")
                except Exception as e:
                    logger.warning(f"[RuleLoader] Failed to load group {rd.get('name', '?')}: {e}")
            else:
                rule_type = rd.get("rule_type")
                if rule_type and rule_type in self.available_rule_classes:
                    rule_cls = self.available_rule_classes[rule_type]
                    rule = rule_cls(rd["name"], rd.get("config", {}))
                    self.rules.append(rule)
                    logger.info(f"[RuleLoader] Loaded rule: {rd['name']}")
                else:
                    logger.warning(f"[RuleLoader] Unknown rule type: {rule_type}")

    def save_rules(self):
        if os.path.exists(RULES_PATH):
            try:
                shutil.copy(RULES_PATH, RULES_PATH + ".bak")
                logger.info(f"[RuleSaver] Backup created at {RULES_PATH}.bak")
            except Exception as e:
                logger.warning(f"[RuleSaver] Could not create backup: {e}")

        def safe_to_dict(r):
            try:
                return r.to_dict()
            except Exception as e:
                logger.warning(f"[RuleSaver] Could not serialize rule {getattr(r, 'name', '?')}: {e}")
                return None

        safe_list = [safe_to_dict(r) for r in self.rules]
        valid_rules = [r for r in safe_list if r is not None]

        try:
            with open(RULES_PATH, "w") as f:
                json.dump(valid_rules, f, indent=4)
            logger.info(f"[RuleSaver] Saved {len(valid_rules)} rules to {RULES_PATH}")
        except Exception as e:
            logger.error(f"[RuleSaver] Failed to write rules file: {e}")

    def create_group(self, name):
        logger.info(f"[RuleManager] Creating new group: {name}")
        group = RuleGroup(name)
        self.rules.append(group)
        self.save_rules()
        return group
