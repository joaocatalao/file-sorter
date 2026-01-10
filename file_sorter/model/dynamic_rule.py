import os
import shutil
import logging
from model.rule_base import BaseRule
from core.condition_evaluator import evaluate_conditions
from core.action_executor import execute_actions

logger = logging.getLogger(__name__)

class DynamicRule(BaseRule):
    def __init__(self, name, config, enabled=True):
        super().__init__(name, config, enabled)

    def set_all_files_mode(self):
        """Clear all conditions and set the rule to match all files."""
        self.config["conditions"] = {
            "logic": "all_files",
            "children": []
        }

    def match(self, file_path):
        return evaluate_conditions(file_path, self.config.get("conditions", {}))

    def action(self, file_path):
        execute_actions(file_path, self.config.get("actions", []))