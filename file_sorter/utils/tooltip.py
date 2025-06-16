import tkinter as tk

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _=None):
        if self.tipwindow or not self.text:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        # Create invisible top-level first
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.withdraw()
        tw.wm_overrideredirect(True)

        label = tk.Label(tw, text=self.text, background="#ffffe0", relief="solid", borderwidth=1, font=("Segoe UI", 9))
        label.pack(ipadx=6, ipady=2)

        tw.update_idletasks()
        screen_w = tw.winfo_screenwidth()
        screen_h = tw.winfo_screenheight()
        width = tw.winfo_width()
        height = tw.winfo_height()

        # Clamp to bottom-right of screen
        x = min(x, screen_w - width - 10)
        y = min(y, screen_h - height - 10)

        tw.geometry(f"+{x}+{y}")
        tw.deiconify()

    def hide(self, _=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None
