import os
import shutil
import logging

logger = logging.getLogger(__name__)

def execute_actions(file_path, actions):
    for act in actions:
        action_type = act.get("action", "").lower()
        path = act.get("path", "").strip()

        try:
            if action_type == "move" and path:
                os.makedirs(path, exist_ok=True)
                target = os.path.join(path, os.path.basename(file_path))
                shutil.move(file_path, target)
                logger.info(f"[ActionExecutor] Moved: {file_path} → {target}")

            elif action_type == "delete":
                os.remove(file_path)
                logger.info(f"[ActionExecutor] Deleted: {file_path}")

            elif action_type == "rename" and path:
                new_path = os.path.join(os.path.dirname(file_path), path)
                os.rename(file_path, new_path)
                logger.info(f"[ActionExecutor] Renamed: {file_path} → {new_path}")

            else:
                logger.warning(f"[ActionExecutor] Skipped unsupported action: {act}")

        except Exception as e:
            logger.error(f"[ActionExecutor] Failed: {action_type.upper()} {file_path} → {path or ''} ({e})")
