import tkinter as tk
from tkinter import ttk, filedialog
import logging

logger = logging.getLogger(__name__)


class MonitorList(ttk.LabelFrame):
    def __init__(self, master, paths, on_dirty=None):
        super().__init__(master, text="Monitor Folders")
        self.paths = paths  # list of dicts
        self.on_dirty = on_dirty
        self.rows = []

        if not self.paths:
            self.paths.append({
                "path": "",
                "include_subs": False,
                "mode": "watchdog",
                "interval": "10",
                "unit": "minutes"
            })

        self.pack(fill="x", pady=(3, 10))

        self.container = ttk.Frame(self)
        self.container.pack(fill="x", padx=10, pady=(4, 4))

        for path in self.paths:
            self._add_path_row(path)

        self._render_buttons()

    def _render_buttons(self):
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=(0, 5))
        ttk.Button(btn_frame, text="➕ Add Folder", command=self._add_new_path).pack(side="left")

    def _add_new_path(self):
        new_path = {
            "path": "",
            "include_subs": False,
            "mode": "watchdog",
            "interval": "10",
            "unit": "minutes"
        }
        logger.info(f"[MonitorList] Added empty folder slot")
        self.paths.append(new_path)
        self._add_path_row(new_path)
        if self.on_dirty:
            self.on_dirty()

    def _add_path_row(self, path_data):
        outer = ttk.Frame(self.container)
        outer.pack(fill="x", pady=4)

        if not self.container.winfo_ismapped():
            self.container.pack(fill="x", padx=10, pady=(4, 4))

        row_top = ttk.Frame(outer)
        row_top.pack(fill="x")

        var_path = tk.StringVar(value=path_data["path"])
        entry = ttk.Entry(row_top, textvariable=var_path)
        entry.pack(side="left", fill="x", expand=True)
        entry.focus_set()
        var_path.trace_add("write", lambda *_: self._update_field(path_data, "path", var_path.get()))

        ttk.Button(row_top, text="📂", width=3, command=lambda: self._browse_path(var_path)).pack(side="left", padx=2)
        btn_gear = ttk.Button(row_top, text="⚙️", width=3, command=lambda: self._toggle_options(options_frame))
        btn_gear.pack(side="left", padx=2)
        ttk.Button(row_top, text="✖", width=3, command=lambda: self._remove_row(outer, path_data)).pack(side="left", padx=(4, 0))

        # Include subfolders
        sub_var = tk.BooleanVar(value=path_data.get("include_subs", True))
        cb = ttk.Checkbutton(outer, text="Include subfolders", variable=sub_var)
        cb.pack(anchor="w", padx=(2, 0), pady=(2, 0))
        sub_var.trace_add("write", lambda *_: self._update_field(path_data, "include_subs", sub_var.get()))

        # Hidden options frame
        options_frame = ttk.LabelFrame(outer, text="Monitor Options")
        options_frame.pack(fill="x", padx=4, pady=(4, 0))
        options_frame.pack_forget()

        # Monitor mode radio buttons
        mode_var = tk.StringVar(value=path_data.get("mode", "watchdog"))
        path_data["_mode_var"] = mode_var

        frame_radio = ttk.Frame(options_frame)
        frame_radio.pack(anchor="w", padx=6, pady=(6, 2))

        rb_watchdog = ttk.Radiobutton(
            frame_radio, text="React on file changes", variable=mode_var, value="watchdog",
            command=lambda: _set_mode("watchdog")
        )
        rb_watchdog.pack(anchor="w")

        # Polling row container
        frame_poll = ttk.Frame(options_frame)
        frame_poll.pack(anchor="w", padx=6, pady=(0, 4))

        rb_poll = ttk.Radiobutton(
            frame_poll, text="Check every", variable=mode_var, value="poll",command=lambda: _set_mode("poll")
        )
        rb_poll.grid(row=0, column=0, sticky="w")

        interval_var = tk.StringVar()
        interval_var.set(path_data.get("interval", "10") or "10")
        path_data["_interval_var"] = interval_var

        entry_interval = ttk.Entry(frame_poll, textvariable=interval_var, width=6)
        entry_interval.grid(row=0, column=1, padx=(4, 2))

        unit_cb = ttk.Combobox(
            frame_poll, values=["seconds", "minutes", "hours"], state="readonly", width=10
        )
        unit_value = path_data.get("unit")
        unit_cb.set(unit_value if unit_value else "minutes")
        unit_cb.grid(row=0, column=2, padx=(2, 0))

        # Radio mode setter (also disables poll controls when needed)
        def _set_mode(mode):
            self._update_field(path_data, "mode", mode)
            is_poll = mode == "poll"
            entry_interval.config(state="normal" if is_poll else "disabled")
            unit_cb.config(state="readonly" if is_poll else "disabled")

        def delayed_mode_init():
            # Temporarily enable to let value render
            entry_interval.config(state="normal")
            entry_interval.update_idletasks()  # Force visual update before disabling
            _set_mode(mode_var.get())

        self.after(0, delayed_mode_init)

    def _browse_path(self, path_var):
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(folder)

    def _toggle_options(self, frame):
        if frame.winfo_ismapped():
            frame.pack_forget()
        else:
            frame.pack(fill="x", pady=(4, 0))
        if self.on_dirty:
            self.on_dirty()

    def _remove_row(self, frame, path_data):
        if path_data in self.paths:
            self.paths.remove(path_data)
        frame.destroy()

        if not self.paths:
            self.container.pack_forget()
        else:
            self.container.pack(fill="x", padx=10, pady=(4, 4))

        if self.on_dirty:
            self.on_dirty()

    def _update_field(self, path_data, key, value):
        path_data[key] = value
        if self.on_dirty:
            self.on_dirty()
