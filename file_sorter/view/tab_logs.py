import tkinter as tk
from tkinter import ttk

class LogsTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f5f5")
        ttk.Label(self, text="Log output goes here").pack(padx=20, pady=20)
