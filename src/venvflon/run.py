from __future__ import annotations

from argparse import ArgumentParser, Namespace
from os import environ
from pathlib import Path
from sys import base_prefix

from venvflon.flon import Gui

environ['TCL_LIBRARY'] = str(Path(base_prefix) / 'tcl' / 'tcl8.6')
environ['TK_LIBRARY'] = str(Path(base_prefix) / 'tcl' / 'tk8.6')
import tkinter as tk

__version__ = '0.2.1'


def run(cli_args=Namespace()):
    """
    Run the main GUI.

    :param cli_args: Namespace object containing command line arguments
    """
    root_tk = tk.Tk()
    width, height = 300, 150
    root_tk.title(f'venvflon - v{__version__}')
    root_tk.geometry(f'{width}x{height}')
    root_tk.iconphoto(False, tk.PhotoImage(file=Path(__file__).parent / 'img' / 'cannula_64.png'))
    gui = Gui(master=root_tk, cli_args=cli_args)
    gui.mainloop()


if __name__ == '__main__':
    parser = ArgumentParser(description='simple virtual environment switcher')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s version: ' + __version__)
    parser.add_argument('-p', '--pwsh', action='store', dest='link_mode', type=int, choices=[0, 5, 7], default=5,
                        help='0 - use Python, pwsh5 or pwsh7 to make symbolic link')
    args = parser.parse_args()
    print(args)
    run(cli_args=args)
