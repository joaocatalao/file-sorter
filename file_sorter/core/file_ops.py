import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def move_file(src, dest):
    logger.info(f"[MOVE] Would move file from '{src}' to '{dest}'")

def copy_file(src, dest):
    logger.info(f"[COPY] Would copy file from '{src}' to '{dest}'")

def rename_file(src, new_name):
    logger.info(f"[RENAME] Would rename file '{src}' to '{new_name}'")

def delete_file(path):
    logger.info(f"[DELETE] Would delete file at '{path}'")

def create_folder_if_not_exists(path):
    if not os.path.exists(path):
        logger.info(f"[MKDIR] Would create folder: {path}")
    else:
        logger.info(f"[MKDIR] Folder already exists: {path}")
