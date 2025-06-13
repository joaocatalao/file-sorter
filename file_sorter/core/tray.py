import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image
import os
import sys

class TrayManager:
    def __init__(self, root, on_restore):
        self.root = root
        self.icon = None
        self.on_restore = on_restore
        self.running = False

    def _create_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "favicon.ico")
        icon_image = Image.open(icon_path)

        self.icon = Icon("FileSorter", icon_image, "File Sorter", menu=Menu(
            MenuItem("Restore", lambda: self._restore(), default=True),
            MenuItem("Exit", lambda: self._exit())
        ))

    def _restore(self):
        if self.icon:
            self.icon.stop()
        self.root.after(0, self._restore_main_window)

    def _restore_main_window(self):
        self.root.deiconify()
        try:
            self.root.state("zoomed")  # Windows / cross-platform full screen
        except:
            try:
                self.root.attributes('-zoomed', True)  # macOS/Linux fallback
            except:
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.focus_force()

    def _exit(self):
        self.running = False
        if self.icon:
            self.icon.stop()
        self.root.quit()

    def run(self):
        self._create_icon()
        self.running = True
        threading.Thread(target=self.icon.run, daemon=True).start()
