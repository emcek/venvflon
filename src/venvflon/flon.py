from __future__ import annotations

from os import environ, getcwd
from pathlib import Path
from sys import base_prefix, executable
from time import sleep

from venvflon.utils import get_command_output, make_sym_link, rm_sym_link, venv_list_in

environ['TCL_LIBRARY'] = str(Path(base_prefix) / 'tcl' / 'tcl8.6')
environ['TK_LIBRARY'] = str(Path(base_prefix) / 'tcl' / 'tk8.6')
import tkinter as tk

print(executable)

class Gui(tk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master)
        self.master = master
        self.venv = tk.StringVar(value=' ')
        self.status_txt = tk.StringVar()
        self.cwd_entry = tk.StringVar()
        self.cwd = Path(getcwd())
        self.cwd_entry.set(str(self.cwd))
        self.venv_list = venv_list_in(current_path=self.cwd)
        new_width, new_height = len(str(self.venv_list[0])) + 300, len(self.venv_list) * 55
        self.master.geometry(f'{new_width}x{new_height}')
        self.master.minsize(width=new_width, height=new_height)
        self.init_widgets()
        self.update_status()

    def init_widgets(self) -> None:
        self.master.columnconfigure(index=0, weight=1)
        cwd_label = tk.Label(self.master, text='cwd:')
        cwd_label.grid(row=0, column=0, sticky=tk.W)
        cwd = tk.Entry(master=self.master, textvariable=self.cwd_entry, width=len(str(self.venv_list[0])) + 2)
        cwd.grid(row=0, column=1, sticky=tk.W)
        cwd.bind('<Return>', self.refresh_cwd)
        self.add_venvs()

    def add_venvs(self):
        venv_label = tk.Label(self.master, text='venv:')
        venv_label.grid(row=1, column=0, sticky=tk.W)
        frame = tk.Frame(master=self.master, relief=tk.GROOVE, borderwidth=2)
        frame.grid(row=1, column=1, columnspan=2, padx=2, pady=2, rowspan=len(self.venv_list))
        for i, text in enumerate(self.venv_list, 1):
            rb_venvs = tk.Radiobutton(master=frame, text=str(text), variable=self.venv, value=text, command=self.venv_selected)
            rb_venvs.grid(row=i, column=1, pady=0, padx=2, sticky=tk.W)
        status = tk.Label(master=self.master, textvariable=self.status_txt)
        status.grid(row=len(self.venv_list) + 1, column=0, columnspan=3, sticky=tk.E)

    def refresh_cwd(self, *args):
        self.venv_list = venv_list_in(current_path=self.cwd)
        self.add_venvs()

    def venv_selected(self):
        new_venv = self.venv.get()
        rm_sym_link(sym_link=Path(getcwd()) / '.venv')
        make_sym_link(to_path=Path(getcwd()) / '.venv', target=Path(new_venv))
        sleep(0.8)
        self.update_status()

    def update_status(self):
        out = get_command_output(cmd=['python', '-V'])
        self.status_txt.set(f'Current: {out[2].strip()}')
