from __future__ import annotations

from os import environ
from pathlib import Path
from sys import base_prefix

from venvflon.flon import Gui

environ['TCL_LIBRARY'] = str(Path(base_prefix) / 'tcl' / 'tcl8.6')
environ['TK_LIBRARY'] = str(Path(base_prefix) / 'tcl' / 'tk8.6')
import tkinter as tk

__version__ = '0.1.0'


def run():
    """Run the main GUI."""
    root_tk = tk.Tk()
    width, height = 300, 150
    root_tk.title(f'venvflon - v{__version__}')
    root_tk.geometry(f'{width}x{height}')
    root_tk.iconphoto(False, tk.PhotoImage(file=Path(__file__).parent / 'img' / 'cannula_64.png'))
    gui = Gui(master=root_tk)
    gui.mainloop()


if __name__ == '__main__':
    run()
