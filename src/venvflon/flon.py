from __future__ import annotations

from argparse import Namespace
from os import chdir, environ, getcwd
from pathlib import Path
from sys import base_prefix

from tkinterdnd2 import DND_FILES, TkinterDnD

from venvflon import utils

environ['TCL_LIBRARY'] = str(Path(base_prefix) / 'tcl' / 'tcl8.6')
environ['TK_LIBRARY'] = str(Path(base_prefix) / 'tcl' / 'tk8.6')
import tkinter as tk

__version__ = '0.5.0'


class Gui(tk.Frame):
    """Tkinter GUI for venvflon."""

    def __init__(self, master: tk.Tk, cli_args: Namespace) -> None:
        """
        Tkinter  GUI for venvflon.

        :param master: Tkinter root
        :param cli_args: CLI arguments
        """
        super().__init__(master)
        self.master: tk.Tk = master
        self.config: Namespace = cli_args  # type: ignore[assignment]
        self.config.link_mode = utils.LINK_MODE_MAP[cli_args.link_mode]
        self.venv = tk.StringVar(value=' ')
        self.status_txt = tk.StringVar()
        self.cwd_entry = tk.StringVar()
        self.cwd_entry.set(getcwd())
        self.venv_list = utils.venv_list_in(current_path=Path(getcwd()))
        self.frame = tk.Frame(master=self.master, relief=tk.GROOVE, borderwidth=2)
        self.status = tk.Label(master=self.master, textvariable=self.status_txt)
        self.cwd = tk.Entry(master=self.master, textvariable=self.cwd_entry, width=20, relief=tk.SUNKEN, font=('Arial', 9))
        self.frame = tk.Frame(master=self.master, relief=tk.GROOVE, borderwidth=2, bg='white')
        self.status = tk.Label(master=self.master, textvariable=self.status_txt, font=('Arial', 9, 'italic'))
        self.cwd.drop_target_register(DND_FILES)   # type: ignore[attr-defined]
        self.init_widgets()

    def init_widgets(self) -> None:
        """Initialize widgets."""
        cwd_label = tk.Label(self.master, text='cwd:', font=('Arial', 9))
        cwd_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cwd.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.cwd.bind('<Return>', self.refresh_cwd)
        self.cwd.dnd_bind('<<Drop>>', self.drop_in_cwd)  # type: ignore[attr-defined]
        self.add_venvs()
        self.resize_window()

    def add_venvs(self) -> None:
        """Add venvs as radio buttons to the GUI."""
        self._remove_old_radiobuttons()
        if len(self.venv_list):
            self.frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
            for i, text in enumerate(self.venv_list, 1):
                rb_venvs = tk.Radiobutton(master=self.frame, text=str(text), variable=self.venv, value=text,
                                          bg='white', font=('Arial', 9), anchor=tk.W, justify=tk.LEFT)
                self._select_current_venv(venv_path=str(text))
                rb_venvs.configure(command=self.venv_selected)
                rb_venvs.grid(row=i, column=1, pady=0, padx=2, sticky=tk.W)
        self.status.grid(row=3, column=0, columnspan=3, sticky=tk.W, padx=5, pady=10)
        self.update_status()

    def _remove_old_radiobuttons(self) -> None:
        """Remove old Radio buttons for venvs."""
        for venv_rb in self.frame.grid_slaves():
            venv_rb.destroy()

    def _select_current_venv(self, venv_path: str) -> None:
        """
        Select the radio button for venv which symlink point to.

        :param venv_path: Path to the venv as string
        """
        sym_link = Path(getcwd()) / '.venv'
        if sym_link.exists() and sym_link.resolve().name in venv_path:
            self.venv.set(venv_path)

    def refresh_cwd(self, *args: tk.Event[tk.Entry]) -> None:
        """
        Refresh the current working directory.

        :param args: Internal tkinter arguments
        """
        new_cwd = Path(self.cwd_entry.get())
        self.cwd.configure(width=len(str(new_cwd)))
        chdir(new_cwd)
        self.master.title(f'venvflon - {new_cwd.name}')
        self.venv_list = utils.venv_list_in(current_path=new_cwd)
        self.add_venvs()
        self.resize_window()

    def drop_in_cwd(self, event: TkinterDnD.DnDEvent) -> None:
        """
        Insert dropped directory into cwd entry.

        :param event: Drop and Drag event
        """
        self.cwd.delete(0, tk.END)
        self.cwd.insert(tk.END, event.data)
        self.refresh_cwd()

    def venv_selected(self) -> None:
        """Set the selected venv as the active one."""
        new_venv = self.venv.get()
        sym_link = Path(getcwd()) / '.venv'
        utils.rm_sym_link(sym_link=sym_link, mode=self.config.link_mode)
        utils.make_sym_link(to_path=sym_link, target=Path(new_venv), mode=self.config.link_mode, timer=self.config.timer)
        self.update_status()

    def resize_window(self) -> None:
        """Resize the window based on the venv list length."""
        venv_txt_length = 30 if not len(self.venv_list) else len(str(self.venv_list[0]))
        venv_txt_height = 2 if not len(self.venv_list) else len(self.venv_list)
        new_width, new_height = venv_txt_length + 300, venv_txt_height * 55 + 17
        self.cwd.configure(width=len(self.cwd_entry.get()))
        self.master.geometry(f'{new_width}x{new_height}')
        self.master.minsize(width=new_width, height=new_height)

    def update_status(self) -> None:
        """Update the status text."""
        _, err, out = utils.get_command_output(cmd=[r'.venv\Scripts\python.exe', '-V'])
        if out:
            self.status_txt.set(f'v{__version__}   /   Current: {out.strip()}')
        elif err:
            self.status_txt.set(f'v{__version__}   /   Error: {err.strip()}')
