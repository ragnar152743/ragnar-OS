"""Graphical desktop shell for the Ragnar Mini OS."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

try:  # pragma: no cover - environment dependent
    import tkinter as tk
    from tkinter import ttk
except Exception:  # pragma: no cover - gracefully fallback when Tk is missing
    tk = None  # type: ignore[assignment]
    ttk = None  # type: ignore[assignment]

from .interfaces import resolve_app_icon

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from .all_in_one import MiniOS
    from .boot import BootReport
    from .interfaces import Widget


class MiniOSGui:
    """Provide a vivid Tk-based desktop for the Mini OS demo."""

    _support_checked: bool | None = None
    _support_available: bool = False

    def __init__(self, os_instance: "MiniOS", report: "BootReport") -> None:
        if not self.is_supported():
            raise RuntimeError(
                "Graphical mode is not available in this environment."
            )

        self.os = os_instance
        self.report = report
        self.root = tk.Tk()
        self.root.title("Ragnar MiniOS")
        self.root.geometry("1280x800")
        self.root.configure(bg="#050014")
        self.root.minsize(960, 600)

        self.status_var = tk.StringVar(value="Booting Ragnar MiniOS…")
        self.step_var = tk.StringVar(value="Preparing subsystems…")
        self._progress_index = 0

        self._style = ttk.Style(self.root)
        self._configure_style()

        self.splash_frame: tk.Frame | None = None
        self.desktop_frame: tk.Frame | None = None
        self.output_widget: tk.Text | None = None
        self.search_var = tk.StringVar()
        self._desktop_icon_container: tk.Frame | None = None
        self._start_menu_container: tk.Frame | None = None
        self._pinned_container: tk.Frame | None = None
        self._all_apps_frame: tk.Frame | None = None
        self._app_buttons: list[tk.Button] = []
        self._all_app_buttons: list[tk.Button] = []
        self._log_widget: tk.Text | None = None
        self._progress: ttk.Progressbar | None = None

        self._build_splash()

    # ------------------------------------------------------------------
    # Capability helpers

    @classmethod
    def is_supported(cls) -> bool:
        """Return True when Tkinter can open a window in this environment."""

        if tk is None or ttk is None:
            cls._support_checked = True
            cls._support_available = False
            return False

        if cls._support_checked:
            return cls._support_available

        try:  # pragma: no cover - requires UI capabilities
            probe = tk.Tk()
            probe.withdraw()
            probe.update_idletasks()
            probe.destroy()
        except tk.TclError:
            cls._support_available = False
        else:
            cls._support_available = True
        finally:
            cls._support_checked = True
        return cls._support_available

    # ------------------------------------------------------------------
    # UI construction

    def _configure_style(self) -> None:
        """Create the neon inspired theme for widgets."""

        try:
            self._style.theme_use("clam")
        except tk.TclError:  # pragma: no cover - fallback if theme missing
            pass

        accent = "#6f3bff"
        surface = "#14073d"
        self._style.configure(
            "Neon.Horizontal.TProgressbar",
            troughcolor="#0c0225",
            bordercolor="#0c0225",
            background=accent,
            lightcolor=accent,
            darkcolor=accent,
        )
        self._style.configure(
            "Neon.TEntry",
            fieldbackground="#0d0229",
            background="#0d0229",
            foreground="#f7f4ff",
            bordercolor=accent,
            insertcolor="#f7f4ff",
        )
        self._style.map(
            "Neon.TEntry",
            fieldbackground=[("disabled", surface), ("active", "#120630")],
        )
        self._style.configure(
            "Neon.Vertical.TScrollbar",
            troughcolor="#0d0229",
            bordercolor="#0d0229",
            background=accent,
            lightcolor=accent,
            darkcolor=accent,
            arrowcolor="#f7f4ff",
        )

    def _build_splash(self) -> None:
        """Show the animated boot splash before the desktop appears."""

        self.splash_frame = tk.Frame(self.root, bg="#050014")
        self.splash_frame.pack(fill="both", expand=True)

        logo = tk.Label(
            self.splash_frame,
            text="Ragnar MiniOS",
            font=("Segoe UI", 36, "bold"),
            fg="#f2e8ff",
            bg="#050014",
        )
        logo.pack(pady=(120, 10))

        subtitle = tk.Label(
            self.splash_frame,
            text="Initializing neon desktop shell",
            font=("Segoe UI", 16),
            fg="#bdb4ff",
            bg="#050014",
        )
        subtitle.pack()

        progress = ttk.Progressbar(
            self.splash_frame,
            style="Neon.Horizontal.TProgressbar",
            mode="determinate",
            length=520,
        )
        progress.pack(pady=(48, 12))
        self._progress = progress
        steps = max(len(self.report.steps), 1)
        progress.configure(maximum=steps, value=0)

        step_label = tk.Label(
            self.splash_frame,
            textvariable=self.step_var,
            font=("Segoe UI", 14),
            fg="#dfd7ff",
            bg="#050014",
        )
        step_label.pack(pady=(0, 24))

        self._log_widget = tk.Text(
            self.splash_frame,
            height=8,
            width=70,
            bg="#08001b",
            fg="#dcd6ff",
            relief="flat",
            font=("Consolas", 11),
        )
        self._log_widget.configure(state="disabled")
        self._log_widget.pack(pady=(0, 0))

        self._log_widget.tag_configure("fail", foreground="#ff8a9b")
        self._log_widget.tag_configure("pass", foreground="#7ef2c4")

        self.root.after(450, self._advance_boot_animation)

    # ------------------------------------------------------------------
    # Splash animation helpers

    def _append_log(self, message: str, tag: str | None = None) -> None:
        if self._log_widget is None:
            return
        self._log_widget.configure(state="normal")
        if tag:
            self._log_widget.insert("end", f"• {message}\n", tag)
        else:
            self._log_widget.insert("end", f"• {message}\n")
        self._log_widget.see("end")
        self._log_widget.configure(state="disabled")

    def _advance_boot_animation(self) -> None:
        if self._progress_index < len(self.report.steps):
            step = self.report.steps[self._progress_index]
            self.step_var.set(step)
            tag = None
            if "FAILED" in step.upper():
                tag = "fail"
            elif "PASS" in step.upper():
                tag = "pass"
            self._append_log(step, tag=tag)
            self._progress_index += 1
            if self._progress is not None:
                self._progress.configure(value=self._progress_index)
            self.root.after(420, self._advance_boot_animation)
            return

        summary = (
            "All systems ready."
            if self.report.ready
            else "Integrity verification failed – desktop in safe mode."
        )
        self.status_var.set(summary)
        self.step_var.set(summary)
        self._append_log(summary, tag="pass" if self.report.ready else "fail")
        self.root.after(600, self._show_desktop)

    # ------------------------------------------------------------------
    # Desktop construction

    def _show_desktop(self) -> None:
        if self.splash_frame is not None:
            self.splash_frame.destroy()
            self.splash_frame = None
        self._build_desktop()

    def _build_desktop(self) -> None:
        self.desktop_frame = tk.Frame(self.root, bg="#050014")
        self.desktop_frame.pack(fill="both", expand=True)

        top_bar = tk.Frame(self.desktop_frame, bg="#12063a", height=64)
        top_bar.pack(fill="x", side="top")

        title = tk.Label(
            top_bar,
            text="Ragnar MiniOS",
            font=("Segoe UI", 20, "bold"),
            fg="#f4f1ff",
            bg="#12063a",
        )
        title.pack(side="left", padx=(24, 12), pady=12)

        state_text = (
            "Integrity: PASS · Maintenance queue clear"
            if self.report.ready
            else "Integrity: FAIL · Recovery mode engaged"
        )
        state_label = tk.Label(
            top_bar,
            text=state_text,
            font=("Segoe UI", 11),
            fg="#c9c1ff",
            bg="#12063a",
        )
        state_label.pack(side="left", pady=12)

        search_entry = ttk.Entry(
            top_bar,
            textvariable=self.search_var,
            width=32,
            style="Neon.TEntry",
        )
        search_entry.pack(side="right", padx=24, pady=16)
        search_entry.insert(0, "Search apps and settings")
        search_entry.bind("<FocusIn>", self._clear_search_placeholder)
        search_entry.bind("<FocusOut>", self._restore_search_placeholder)
        search_entry.bind("<KeyRelease>", self._on_search_change)

        body = tk.Frame(self.desktop_frame, bg="#050014")
        body.pack(fill="both", expand=True, padx=24, pady=24)

        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)
        body.grid_columnconfigure(2, weight=1)
        body.grid_rowconfigure(0, weight=3)
        body.grid_rowconfigure(1, weight=2)

        self._build_start_menu(body)
        self._build_desktop_icons(body)
        self._build_widgets(body)
        self._build_app_console(body)

        status_bar = tk.Frame(self.desktop_frame, bg="#12063a", height=32)
        status_bar.pack(fill="x", side="bottom")

        status_label = tk.Label(
            status_bar,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            fg="#d6ceff",
            bg="#12063a",
        )
        status_label.pack(side="left", padx=16)

        system_label = tk.Label(
            status_bar,
            text="🕒 12:00  ·  🔔 No notifications",
            font=("Segoe UI", 10),
            fg="#d6ceff",
            bg="#12063a",
        )
        system_label.pack(side="right", padx=16)

    def _build_start_menu(self, parent: tk.Frame) -> None:
        container = tk.Frame(
            parent,
            bg="#10052f",
            highlightbackground="#3920a7",
            highlightthickness=2,
            bd=0,
        )
        container.grid(row=0, column=0, sticky="nsew", padx=(0, 16), pady=(0, 16))
        self._start_menu_container = container

        header = tk.Label(
            container,
            text="Start Menu",
            font=("Segoe UI", 16, "bold"),
            fg="#f4f1ff",
            bg="#10052f",
        )
        header.pack(anchor="w", padx=18, pady=(18, 10))

        pinned_label = tk.Label(
            container,
            text="Pinned",
            font=("Segoe UI", 12, "bold"),
            fg="#cfc7ff",
            bg="#10052f",
        )
        pinned_label.pack(anchor="w", padx=18, pady=(0, 6))

        self._pinned_container = tk.Frame(container, bg="#10052f")
        self._pinned_container.pack(fill="x", padx=18)

        ttk.Separator(container, orient="horizontal").pack(
            fill="x", padx=18, pady=16
        )

        apps_label = tk.Label(
            container,
            text="All Applications",
            font=("Segoe UI", 12, "bold"),
            fg="#cfc7ff",
            bg="#10052f",
        )
        apps_label.pack(anchor="w", padx=18, pady=(0, 6))

        scroll_frame = tk.Frame(container, bg="#10052f")
        scroll_frame.pack(fill="both", expand=True, padx=12, pady=(0, 18))

        canvas = tk.Canvas(
            scroll_frame,
            bg="#10052f",
            highlightthickness=0,
            relief="flat",
        )
        scrollbar = ttk.Scrollbar(
            scroll_frame,
            orient="vertical",
            command=canvas.yview,
            style="Neon.Vertical.TScrollbar",
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        frame_inner = tk.Frame(canvas, bg="#10052f")
        canvas.create_window((0, 0), window=frame_inner, anchor="nw")
        frame_inner.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        self._all_apps_frame = frame_inner
        self._populate_app_lists(self.os.list_app_names())

    def _build_desktop_icons(self, parent: tk.Frame) -> None:
        container = tk.Frame(
            parent,
            bg="#10052f",
            highlightbackground="#3920a7",
            highlightthickness=2,
            bd=0,
        )
        container.grid(row=0, column=1, sticky="nsew", padx=16, pady=(0, 16))
        self._desktop_icon_container = container

        header = tk.Label(
            container,
            text="Neon Desktop",
            font=("Segoe UI", 16, "bold"),
            fg="#f4f1ff",
            bg="#10052f",
        )
        header.pack(anchor="w", padx=18, pady=(18, 10))

        grid_frame = tk.Frame(container, bg="#10052f")
        grid_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        app_names = self.os.list_app_names()
        if not app_names:
            empty = tk.Label(
                grid_frame,
                text="No applications installed",
                font=("Segoe UI", 12),
                fg="#c9c1ff",
                bg="#10052f",
            )
            empty.pack(expand=True)
            return

        columns = 3
        for column in range(columns):
            grid_frame.grid_columnconfigure(column, weight=1)

        self._app_buttons.clear()
        for index, name in enumerate(app_names):
            row = index // columns
            column = index % columns
            icon = resolve_app_icon(name)
            button = tk.Button(
                grid_frame,
                text=f"{icon}\n{name}",
                font=("Segoe UI", 14, "bold"),
                fg="#fdfcff",
                bg="#291669",
                activebackground="#3b2193",
                activeforeground="#ffffff",
                relief="flat",
                bd=0,
                padx=12,
                pady=18,
                justify="center",
                wraplength=140,
                command=lambda app=name: self._launch_app(app),
            )
            button.grid(row=row, column=column, padx=12, pady=12, sticky="nsew")
            self._app_buttons.append(button)

    def _build_widgets(self, parent: tk.Frame) -> None:
        container = tk.Frame(
            parent,
            bg="#10052f",
            highlightbackground="#3920a7",
            highlightthickness=2,
            bd=0,
        )
        container.grid(row=0, column=2, sticky="nsew", padx=(16, 0), pady=(0, 16))

        header = tk.Label(
            container,
            text="Desktop Widgets",
            font=("Segoe UI", 16, "bold"),
            fg="#f4f1ff",
            bg="#10052f",
        )
        header.pack(anchor="w", padx=18, pady=(18, 10))

        widgets_container = tk.Frame(container, bg="#10052f")
        widgets_container.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        widgets = self.os.interface_manager.widgets
        if not widgets:
            empty = tk.Label(
                widgets_container,
                text="No widgets registered yet",
                font=("Segoe UI", 12),
                fg="#c9c1ff",
                bg="#10052f",
            )
            empty.pack(expand=True)
            return

        for widget in widgets:
            self._add_widget_card(widgets_container, widget)

    def _add_widget_card(self, parent: tk.Frame, widget: "Widget") -> None:
        card = tk.Frame(
            parent,
            bg="#1b0f4c",
            highlightbackground="#4f32d3",
            highlightthickness=1,
            bd=0,
        )
        card.pack(fill="x", pady=10)

        icon = f"{widget.icon} " if widget.icon else ""
        title = tk.Label(
            card,
            text=f"{icon}{widget.title}",
            font=("Segoe UI", 12, "bold"),
            fg="#f2ecff",
            bg="#1b0f4c",
        )
        title.pack(anchor="w", padx=14, pady=(12, 6))

        body = tk.Label(
            card,
            text=widget.body,
            font=("Segoe UI", 11),
            fg="#d0c8ff",
            bg="#1b0f4c",
            justify="left",
        )
        body.pack(fill="x", padx=14, pady=(0, 12))

    def _build_app_console(self, parent: tk.Frame) -> None:
        container = tk.Frame(
            parent,
            bg="#10052f",
            highlightbackground="#3920a7",
            highlightthickness=2,
            bd=0,
        )
        container.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="nsew",
            pady=(0, 0),
        )

        parent.grid_rowconfigure(1, weight=1)

        header = tk.Label(
            container,
            text="Application Console",
            font=("Segoe UI", 16, "bold"),
            fg="#f4f1ff",
            bg="#10052f",
        )
        header.pack(anchor="w", padx=18, pady=(18, 10))

        text_frame = tk.Frame(container, bg="#10052f")
        text_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        text_widget = tk.Text(
            text_frame,
            bg="#0d0229",
            fg="#f7f4ff",
            insertbackground="#f7f4ff",
            relief="flat",
            wrap="word",
            font=("Consolas", 11),
        )
        text_widget.pack(side="left", fill="both", expand=True)
        text_widget.configure(state="disabled")

        scrollbar = ttk.Scrollbar(
            text_frame,
            orient="vertical",
            command=text_widget.yview,
            style="Neon.Vertical.TScrollbar",
        )
        scrollbar.pack(side="right", fill="y")
        text_widget.configure(yscrollcommand=scrollbar.set)

        self.output_widget = text_widget

    # ------------------------------------------------------------------
    # Application interactions

    def _populate_app_lists(self, app_names: Iterable[str]) -> None:
        if self._pinned_container is None or self._all_apps_frame is None:
            return

        for child in self._pinned_container.winfo_children():
            child.destroy()
        for child in self._all_apps_frame.winfo_children():
            child.destroy()

        pinned = list(app_names)[:6]
        if not pinned:
            label = tk.Label(
                self._pinned_container,
                text="Nothing pinned yet",
                font=("Segoe UI", 11),
                fg="#c9c1ff",
                bg="#10052f",
            )
            label.pack(anchor="w", pady=6)
        else:
            for name in pinned:
                icon = resolve_app_icon(name)
                button = tk.Button(
                    self._pinned_container,
                    text=f"{icon}  {name}",
                    font=("Segoe UI", 12),
                    fg="#fdfcff",
                    bg="#281669",
                    activebackground="#3b2193",
                    activeforeground="#ffffff",
                    relief="flat",
                    bd=0,
                    padx=12,
                    pady=8,
                    anchor="w",
                    command=lambda app=name: self._launch_app(app),
                )
                button.pack(fill="x", pady=4)

        self._all_app_buttons.clear()
        for name in app_names:
            icon = resolve_app_icon(name)
            button = tk.Button(
                self._all_apps_frame,
                text=f"{icon}  {name}",
                font=("Segoe UI", 12),
                fg="#fdfcff",
                bg="#1e0d51",
                activebackground="#34187d",
                activeforeground="#ffffff",
                relief="flat",
                bd=0,
                padx=12,
                pady=8,
                anchor="w",
                command=lambda app=name: self._launch_app(app),
            )
            button.pack(fill="x", pady=4, padx=6)
            self._all_app_buttons.append(button)

    def _launch_app(self, app_name: str) -> None:
        output = self.os.open_application(app_name)
        self._write_console(f"▶ {app_name}\n{output}\n")
        self.status_var.set(f"Launched {app_name}")

    def _write_console(self, message: str) -> None:
        if not self.output_widget:
            return
        self.output_widget.configure(state="normal")
        self.output_widget.insert("end", message)
        self.output_widget.insert("end", "\n" + ("━" * 40) + "\n")
        self.output_widget.configure(state="disabled")
        self.output_widget.see("end")

    def _on_search_change(self, _event: object) -> None:
        query = self.search_var.get().strip().lower()
        if not query or query == "search apps and settings".lower():
            self._apply_search_filter(None)
            return
        self._apply_search_filter(query)

    def _apply_search_filter(self, query: str | None) -> None:
        app_names = self.os.list_app_names()
        if query:
            filtered = [name for name in app_names if query in name.lower()]
        else:
            filtered = app_names
        self._populate_app_lists(filtered if query else app_names)

    def _clear_search_placeholder(self, _event: object) -> None:
        if self.search_var.get() == "Search apps and settings":
            self.search_var.set("")

    def _restore_search_placeholder(self, _event: object) -> None:
        if not self.search_var.get():
            self.search_var.set("Search apps and settings")

    # ------------------------------------------------------------------
    # Lifecycle

    def run(self) -> None:
        """Enter the Tkinter main loop."""

        self.root.mainloop()


__all__ = ["MiniOSGui"]
