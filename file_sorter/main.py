from controller.app_controller import AppController
from core.tray import TrayManager
from config.settings import save_settings

import tkinter as tk
import os
import platform
import tkinter.font as tkFont

# Enable DPI Awareness (Windows only)
if platform.system() == "Windows":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)  # Windows 8.1 or later
    except Exception:
        try:
            windll.user32.SetProcessDPIAware()   # Fallback for older versions
        except:
            pass

from controller.app_controller import AppController

if __name__ == "__main__":
    root = tk.Tk()
    controller = AppController(root)

    tray_manager = TrayManager(root, on_restore=lambda: root.deiconify())

    def on_close():
        if controller.settings.get("minimize_to_tray"):
            root.withdraw()
            tray_manager.run()
        else:
            controller.stop_all()
            root.destroy()

        save_settings(controller.settings)

    root.protocol("WM_DELETE_WINDOW", on_close)

    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(family="Segoe UI", size=10)
    root.option_add("*Font", default_font)

    try:
        root.state("zoomed")
    except:
        try:
            root.attributes('-zoomed', True)
        except:
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.geometry(f"{screen_width}x{screen_height}")

    root.minsize(800, 600)

    root.mainloop()
