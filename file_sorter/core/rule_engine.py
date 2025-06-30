import logging
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import List, Dict

from model.dynamic_rule import DynamicRule
from core.action_executor import execute_actions

logger = logging.getLogger(__name__)


class _RuleHandler(FileSystemEventHandler):
    def __init__(self, rule: DynamicRule):
        super().__init__()
        self.rule = rule

    def on_created(self, event):
        if not event.is_directory:
            self._process(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._process(event.dest_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._process(event.src_path)

    def _process(self, path: str):
        try:
            if self.rule.match(path):
                logger.info(f"[Engine] Matched {path} for rule {self.rule.name}")
                execute_actions(path, self.rule.config.get("actions", []))
        except Exception as e:
            logger.error(f"[Engine] Error processing {path}: {e}")


class RuleEngine:
    """Simple runtime engine that watches folders and executes actions."""

    def __init__(self):
        self.observers: Dict[str, List[Observer]] = {}

    def start_rule(self, rule: DynamicRule):
        self.stop_rule(rule.name)
        observers = []
        for folder in rule.config.get("folders", []):
            path = folder.get("path", "")
            if not path or not os.path.isdir(path):
                logger.warning(f"[Engine] Skipping invalid folder: {path}")
                continue
            include_subs = folder.get("include_subs", False)
            handler = _RuleHandler(rule)
            observer = Observer()
            observer.schedule(handler, path, recursive=include_subs)
            observer.start()
            observers.append(observer)
            logger.info(
                f"[Engine] Started watching {path} ({'recursive' if include_subs else 'non-recursive'})"
            )
        if observers:
            self.observers[rule.name] = observers

    def stop_rule(self, name: str):
        obs_list = self.observers.pop(name, [])
        for obs in obs_list:
            obs.stop()
            obs.join()
        if obs_list:
            logger.info(f"[Engine] Stopped watchers for rule {name}")

    def stop_all(self):
        for name in list(self.observers.keys()):
            self.stop_rule(name)

