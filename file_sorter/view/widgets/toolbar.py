import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)

class Toolbar(ttk.Frame):
    def __init__(self, parent, left_buttons=None, right_buttons=None, height=50, padding=(6, 4)):
        super().__init__(parent)

        container = tk.Frame(self, height=height, bg="#f9f9f9")
        container.pack(fill="x")
        container.pack_propagate(False)

        inner = ttk.Frame(container, padding=padding)
        inner.pack(fill="both", expand=True)

        self.left_area = ttk.Frame(inner)
        self.left_area.pack(side="left", fill="y")

        self.right_area = ttk.Frame(inner)
        self.right_area.pack(side="right", fill="y")

        if left_buttons:
            self._add_buttons(self.left_area, left_buttons, label="left")

        if right_buttons:
            self._add_buttons(self.right_area, right_buttons, label="right")

        logger.debug("[Toolbar] Initialized with buttons")

    def add_status_indicator(self, textvariable, is_running=False):
        frame = ttk.Frame(self.left_area)
        dot = tk.Canvas(frame, width=10, height=10, highlightthickness=0)
        dot.pack(side="left", padx=(0, 5))
        dot.create_oval(2, 2, 10, 10, fill="#4caf50" if is_running else "#ccc", tags="dot")

        label = ttk.Label(frame, textvariable=textvariable, foreground="#555")
        label.pack(side="left")

        frame.pack(side="left", padx=4)
        logger.debug("[Toolbar] Status indicator added")

        return dot  # return canvas so editor can update dot color

    def _add_buttons(self, area, buttons, label=""):
        for btn in buttons:
            if "custom" in btn:
                btn["custom"].pack(in_=area, side="left", padx=4, pady=4)
                btn["custom"].update_idletasks()
                logger.debug(f"[Toolbar] Added custom widget to {label} area")
            else:
                b = ttk.Button(area, text=btn["text"], command=btn["command"])
                b.pack(side="left", padx=4)
                logger.debug(f"[Toolbar] Added button '{btn['text']}' to {label} area")

                if "tooltip" in btn:
                    try:
                        from utils.tooltip import Tooltip
                        Tooltip(b, btn["tooltip"])
                        logger.debug(f"[Toolbar] Added tooltip to '{btn['text']}': {btn['tooltip']}")
                    except ImportError:
                        logger.warning(f"[Toolbar] Tooltip failed to load for: {btn['text']}")
