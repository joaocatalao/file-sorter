from model.rule_base import BaseRule
import os
import shutil

class DynamicRule(BaseRule):
    def match(self, file_path):
        def eval_condition(cond, path):
            prop = cond.get("property")
            comparison = cond.get("comparison")
            value = cond.get("value", "")

            if prop == "File name":
                target = os.path.basename(path)
            elif prop == "Extension":
                target = os.path.splitext(path)[1][1:]  # remove dot
            else:
                return False

            if comparison == "Contains":
                return value.lower() in target.lower()
            elif comparison == "Is":
                return value.lower() == target.lower()
            elif comparison == "Starts with":
                return target.lower().startswith(value.lower())
            elif comparison == "Ends with":
                return target.lower().endswith(value.lower())
            else:
                return False

        def eval_logic_group(group, path):
            logic = group.get("logic", "All")
            children = group.get("children", [])

            results = []
            for child in children:
                if "property" in child:
                    results.append(eval_condition(child, path))
                elif "logic" in child:
                    results.append(eval_logic_group(child, path))

            return all(results) if logic == "All" else any(results)

        return eval_logic_group(self.config.get("conditions", {}), file_path)

    def action(self, file_path):
        for act in self.config.get("actions", []):
            if act.get("action") == "Move":
                dest = act.get("path", "")
                if os.path.isdir(dest):
                    shutil.move(file_path, os.path.join(dest, os.path.basename(file_path)))
