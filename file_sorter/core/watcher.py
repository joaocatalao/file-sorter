import logging
import time
import threading

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class FileEventHandler:
    def __init__(self, watch_path):
        self.watch_path = watch_path

    def on_created(self, file_path):
        logger.info(f"[WATCHER] Detected new file created: {file_path}")

    def on_modified(self, file_path):
        logger.info(f"[WATCHER] Detected file modified: {file_path}")

    def on_deleted(self, file_path):
        logger.info(f"[WATCHER] Detected file deleted: {file_path}")

def start_watching(path, stop_event):
    logger.info(f"[WATCHER] Would start watching directory: {path}")
    handler = FileEventHandler(path)

    # Simulated watcher loop
    while not stop_event.is_set():
        # Simulate detecting a file event
        handler.on_created(f"{path}/example.txt")
        time.sleep(5)  # Simulate interval

def stop_watching():
    logger.info("[WATCHER] Would stop watching directory")
