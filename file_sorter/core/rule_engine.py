import logging
import os
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import List, Dict, Union

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


class _PollThread(threading.Thread):
    """Background thread that polls a folder at intervals."""

    def __init__(self, rule: DynamicRule, folder: dict):
        super().__init__(daemon=True)
        self.rule = rule
        self.folder = folder
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        path = self.folder.get("path", "")
        include_subs = self.folder.get("include_subs", False)
        interval = int(self.folder.get("poll_interval", 10))
        unit = self.folder.get("poll_unit", "minutes")
        factor = {"seconds": 1, "minutes": 60, "hours": 3600}.get(unit, 60)
        delay = max(1, interval * factor)
        logger.info(f"[Engine] Polling {path} every {interval} {unit}")

        seen = set()
        while not self.stop_event.is_set():
            for root_dir, dirs, files in os.walk(path):
                for fname in files:
                    fpath = os.path.join(root_dir, fname)
                    if fpath in seen:
                        continue
                    seen.add(fpath)
                    try:
                        if self.rule.match(fpath):
                            logger.info(
                                f"[Engine] Matched {fpath} for rule {self.rule.name}"
                            )
                            execute_actions(fpath, self.rule.config.get("actions", []))
                    except Exception as e:
                        logger.error(f"[Engine] Error processing {fpath}: {e}")
                if not include_subs:
                    break
            self.stop_event.wait(delay)


class RuleEngine:
    """Simple runtime engine that watches folders and executes actions."""

    def __init__(self):
        self.observers: Dict[str, List[Union[Observer, threading.Thread]]] = {}

    def start_rule(self, rule: DynamicRule):
        self.stop_rule(rule.name)
        observers = []
        for folder in rule.config.get("folders", []):
            path = folder.get("path", "")
            if not path or not os.path.isdir(path):
                logger.warning(f"[Engine] Skipping invalid folder: {path}")
                continue

            mode = folder.get("monitor_mode", "watchdog")
            include_subs = folder.get("include_subs", False)

            if mode == "poll":
                poller = _PollThread(rule, folder)
                poller.start()
                observers.append(poller)
                logger.info(
                    f"[Engine] Started polling {path} ({'recursive' if include_subs else 'non-recursive'})"
                )
            else:
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

