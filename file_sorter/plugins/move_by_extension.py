import os
import shutil
from model.rule_base import BaseRule

class MoveByExtensionRule(BaseRule):
    def match(self, file_path):
        return file_path.endswith(self.config.get("extension", ""))

    def action(self, file_path):
        dest_dir = self.config.get("destination")
        if dest_dir and os.path.exists(file_path):
            dest_path = os.path.join(dest_dir, os.path.basename(file_path))
            shutil.move(file_path, dest_path)
