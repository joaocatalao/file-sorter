import os
import logging

logger = logging.getLogger(__name__)

def evaluate_conditions(file_path, config):
    logic = config.get("logic", "all").lower()
    children = config.get("children", [])

    if logic == "all_files":
        return True

    if not children:
        logger.warning("[ConditionEvaluator] No conditions defined.")
        return False

    results = []

    for cond in children:
        result, reason = _evaluate_single_condition(file_path, cond)
        results.append(result)
        logger.debug(f"[ConditionEvaluator] {reason} → {result}")

    if logic == "any":
        return any(results)
    elif logic == "none":
        return not any(results)
    else:
        return all(results)

def _evaluate_single_condition(file_path, cond):
    raw_type = cond.get("type", "").strip().lower()
    raw_comp = cond.get("comparison", "").strip().lower()
    value = cond.get("value", "").strip()

    try:
        if raw_type == "extension":
            ext = os.path.splitext(file_path)[1].lower().lstrip(".")
            match = ext == value.lower()
            if raw_comp == "is not":
                match = not match
            return match, f"Extension match: {ext} vs {value}"

        elif raw_type == "file name":
            name = os.path.basename(file_path).lower()
            contains = value.lower() in name
            return contains, f"Name contains: '{value}' in '{name}'"

        elif raw_type == "size":
            size = os.path.getsize(file_path)
            match = size > int(value)
            return match, f"Size {size} > {value}"

    except Exception as e:
        logger.error(f"[ConditionEvaluator] Error on condition {cond}: {e}")
        return False, f"Error on condition {cond}"

    return False, f"Unsupported condition {cond}"
