import tkinter as tk
from tkinter import ttk

class Toolbar(ttk.Frame):
    def __init__(self, parent, left_buttons=None, right_buttons=None, height=50, padding=(6, 4)):
        super().__init__(parent)

        # Create fixed-height container
        container = tk.Frame(self, height=height, bg="#f9f9f9")
        container.pack(fill="x")
        container.pack_propagate(False)

        # Inner frame for layout
        inner = ttk.Frame(container, padding=padding)
        inner.pack(fill="both", expand=True)

        # Left-aligned area
        self.left_area = ttk.Frame(inner)
        self.left_area.pack(side="left", fill="y")

        # Right-aligned area
        self.right_area = ttk.Frame(inner)
        self.right_area.pack(side="right", fill="y")

        # Populate buttons
        if left_buttons:
            self._add_buttons(self.left_area, left_buttons)

        if right_buttons:
            self._add_buttons(self.right_area, right_buttons)

    def _add_buttons(self, area, buttons):
        for btn in buttons:
            if "custom" in btn:
                btn["custom"].pack(in_=area, side="left", padx=4)
            else:
                b = ttk.Button(area, text=btn["text"], command=btn["command"])
                b.pack(side="left", padx=4)
                if "tooltip" in btn:
                    try:
                        from utils.tooltip import Tooltip
                        Tooltip(b, btn["tooltip"])
                    except ImportError:
                        pass
