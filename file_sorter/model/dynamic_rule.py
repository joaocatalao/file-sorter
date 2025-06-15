import os
import shutil
from model.rule_base import BaseRule

class DynamicRule(BaseRule):
    def __init__(self, name, config):
        super().__init__(name, config)

    def set_all_files_mode(self):
        """Clear all conditions and set the rule to match all files."""
        self.config["conditions"] = {
            "logic": "all_files",
            "children": []
        }

    def match(self, file_path):
        """Evaluate if the file matches all configured conditions."""
        print(f"[🔍 MATCH] Checking file: {file_path}")

        conditions = self.config.get("conditions", {})
        logic = conditions.get("logic", "All").lower()

        if logic == "all_files":
            print("[🔄 All Files Mode] Matching all files without conditions.")
            return True

        children = conditions.get("children", [])

        if not children:
            print("[🟡] No conditions defined.")
            return False

        type_map = {
            "extension": "extension",
            "file name": "name",
            "size": "size"
        }

        comparison_map = {
            "is": "eq",
            "is not": "eq",
            "contains": "contains",
            "greater than": "gt"
        }

        results = []

        for cond in children:
            if not isinstance(cond, dict):
                continue

            raw_type = cond.get("type", "").strip().lower()
            raw_comp = cond.get("comparison", "").strip().lower()
            value = cond.get("value", "").strip()

            cond_type = type_map.get(raw_type)
            comparison = comparison_map.get(raw_comp)
            invert = raw_comp == "is not"

            result = False
            reason = ""

            try:
                if cond_type == "extension" and comparison == "eq":
                    file_ext = os.path.splitext(file_path)[1].lower().lstrip(".")
                    result = file_ext == value.lower()
                    reason = f"Expected '.{value.lower()}', got '.{file_ext}'"

                elif cond_type == "name" and comparison == "contains":
                    result = value.lower() in os.path.basename(file_path).lower()
                    reason = f"Name check: contains '{value.lower()}'"

                elif cond_type == "size" and comparison == "gt":
                    size = os.path.getsize(file_path)
                    result = size > int(value)
                    reason = f"Size {size} > {value}"

                else:
                    reason = "Unsupported condition"

            except Exception as e:
                print(f"[⚠️ Error] Condition error: {raw_type} {raw_comp} {value} – {e}")
                result = False

            if invert:
                result = not result

            op = raw_comp
            print(f"[🧪 Condition] {cond_type} {op} '{value}' → {result} ({reason})")
            results.append(result)

        if logic == "any":
            final_result = any(results)
        elif logic == "none":
            final_result = not any(results)
        else:  # default to "all"
            final_result = all(results)

        print(f"[✅ MATCH RESULT] → {final_result}")
        return final_result

    def action(self, file_path):
        """Perform all configured actions on the file."""
        actions = self.config.get("actions", [])

        for act in actions:
            action_type = act.get("action", "").lower()
            path = act.get("path", "").strip()

            try:
                if action_type == "move" and path:
                    os.makedirs(path, exist_ok=True)
                    target_path = os.path.join(path, os.path.basename(file_path))
                    shutil.move(file_path, target_path)

                elif action_type == "delete":
                    os.remove(file_path)

                elif action_type == "rename" and path:
                    folder = os.path.dirname(file_path)
                    new_path = os.path.join(folder, path)
                    os.rename(file_path, new_path)

                # Add more actions here

            except Exception as e:
                print(f"[❌ Action Failed] {action_type.upper()} {file_path} → {path or ''} ({e})")
