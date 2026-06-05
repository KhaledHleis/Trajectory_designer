"""
main.py
-------
Entry point — run this file to launch the application.

    python main.py
"""

import tkinter as tk
from tkinter import ttk

from ui import WaypointGeneratorApp
from ui.theme import Theme as T


def _apply_ttk_style(root: tk.Tk):
    """Apply a dark theme to ttk widgets (Combobox, etc.)."""
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        "TCombobox",
        fieldbackground=T.ENTRY_BG,
        background=T.ENTRY_BG,
        foreground=T.TEXT,
        selectbackground=T.ACCENT,
        selectforeground=T.DARK_BG,
        bordercolor=T.SEP,
        arrowcolor=T.ACCENT,
    )


if __name__ == "__main__":
    root = tk.Tk()
    _apply_ttk_style(root)
    app = WaypointGeneratorApp(root)
    root.mainloop()
