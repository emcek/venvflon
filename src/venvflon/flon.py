from __future__ import annotations

import tkinter as tk
from argparse import Namespace
from os import chdir, getcwd, rename
from pathlib import Path
from re import match
from tkinter import ttk

import yaml
from tkinterdnd2 import DND_FILES, TkinterDnD

from venvflon import utils

__version__ = '0.7.1'
KEYWORDS = ('Resolved', 'Installed', 'Audited', 'Prepared', 'Uninstalled')
LATEST_PYTHON = '3.13'


class Gui(tk.Frame):
    """Tkinter GUI for venvflon."""

    def __init__(self, master: tk.Tk, cli_args: Namespace) -> None:
        """
        Tkinter GUI for venvflon.

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
        self.master.columnconfigure(1, weight=1)
        self.master.columnconfigure(2, weight=1)
        self.master.rowconfigure(2, weight=1)
        self.frame = tk.Frame(master=self.master, relief=tk.GROOVE, borderwidth=2)
        self.status = tk.Label(master=self.master, textvariable=self.status_txt, font=('Arial', 9, 'italic'))
        self.cwd = tk.Entry(master=self.master, textvariable=self.cwd_entry, width=20, relief=tk.SUNKEN, font=('Arial', 9))
        self.btn_sync = tk.Button(master=self.master, text='Sync', command=self.sync, font=('Arial', 9))
        self.btn_create = tk.Button(master=self.master, text='Create', command=self.create, font=('Arial', 9))
        pythons_list = utils.get_uv_pythons_list()
        self.combo_py_ver = ttk.Combobox(master=self.master, values=pythons_list, state='readonly')
        index_of_element = next((i for i, item in enumerate(pythons_list) if item.startswith(LATEST_PYTHON)), 0)
        self.combo_py_ver.current(int(index_of_element))
        self.init_widgets()

    def init_widgets(self) -> None:
        """Initialize widgets."""
        self.cwd.drop_target_register(DND_FILES)  # type: ignore[attr-defined]
        cwd_label = tk.Label(self.master, text='cwd:', font=('Arial', 9))
        cwd_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cwd.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        self.cwd.bind('<Return>', self.refresh_cwd)
        self.cwd.dnd_bind('<<Drop>>', self.drop_in_cwd)  # type: ignore[attr-defined]
        combo_label = tk.Label(self.master, text='python:', font=('Arial', 9))
        combo_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.combo_py_ver.grid(row=3, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        self.btn_sync.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        self.btn_create.grid(row=4, column=2, sticky=tk.EW, padx=5, pady=5)
        self.sync_btn_state()
        self.add_venvs()

    def add_venvs(self) -> None:
        """Add venvs as radio buttons to the GUI."""
        self._remove_old_radiobuttons()
        if len(self.venv_list):
            self.frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.NSEW)
            self.frame.columnconfigure(1, weight=1)
            for i, text in enumerate(self.venv_list, 1):
                rb_venvs = tk.Radiobutton(master=self.frame, text=str(text), variable=self.venv, value=text,
                                          font=('Arial', 9), anchor=tk.W, justify=tk.LEFT)
                self._select_current_venv(venv_path=str(text))
                rb_venvs.configure(command=self.venv_selected)
                rb_venvs.grid(row=i, column=1, pady=0, padx=2, sticky=tk.W)
        self.status.grid(row=5, column=0, columnspan=3, sticky=tk.W, padx=5, pady=10)
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
        self.sync_btn_state()

    def drop_in_cwd(self, event: TkinterDnD.DnDEvent) -> None:
        """
        Insert dropped directory into cwd entry.

        :param event: Drop and Drag event
        """
        self.cwd.delete(0, tk.END)
        self.cwd.insert(tk.END, event.data)
        self.refresh_cwd()

    def sync(self) -> None:
        """Run sync command from configuration YAML."""
        self.btn_sync.configure(text='Syncing...')
        with open(file='.venvflon.yaml', encoding='utf-8') as yaml_file:
            data = yaml.load(yaml_file, Loader=yaml.SafeLoader)
        all_out = []
        for cmd in data['sync_cmd']:
            _, err, _ = utils.get_command_output(cmd=cmd.split(' '))
            parsed_lines = [line for line in err.split('\n') if any(keyword in line for keyword in KEYWORDS)]
            all_out.extend(parsed_lines)
        time_ms = sum(utils.extract_time(entry=entry) for entry in all_out)
        packages = utils.extract_installed_packages(entry=all_out)
        total_time = f'{time_ms / 1000:.2f} s' if time_ms > 1000 else f'{time_ms:.2f} ms'
        desc = f'Installed {packages} in {total_time}' if packages else f'Sync in {total_time}'
        self.btn_sync.configure(text=desc)

    def venv_selected(self) -> None:
        """Set the selected venv as the active one."""
        new_venv = self.venv.get()
        sym_link = Path(getcwd()) / '.venv'
        utils.rm_sym_link(sym_link=sym_link, mode=self.config.link_mode)
        utils.make_sym_link(to_path=sym_link, target=Path(new_venv), mode=self.config.link_mode, timer=self.config.timer)
        self.update_status()

    def update_status(self) -> None:
        """Update the status text."""
        _, err, out = utils.get_command_output(cmd=[r'.venv\Scripts\python.exe', '-V'])
        if out:
            self.status_txt.set(f'v{__version__}   /   Current: {out.strip()}')
        elif err:
            self.status_txt.set(f'v{__version__}   /   Error: {err.strip()}')

    def sync_btn_state(self) -> None:
        """Check if a config YAML file exists and change a button status."""
        if Path(getcwd(), '.venvflon.yaml').exists():
            self.btn_sync.configure(state=tk.ACTIVE)
        else:
            self.btn_sync.configure(state=tk.DISABLED)

    def _rename_venv_and_make_symlink(self):
        """Rename existing venv and make symlink to it."""
        *_, out = utils.get_command_output(cmd=[r'.venv\Scripts\python.exe', '-V'])
        py_ver = match(r'Python\s+(\d+)\.(\d+)\.\d+', out.strip())
        if py_ver is None:
            self.status_txt.set('Error: cannot detect Python version')
            return
        venv_with_ver = f'.venv_{py_ver.group(1)}{py_ver.group(2)}'
        rename('.venv', venv_with_ver)
        sym_link = Path(getcwd()) / '.venv'
        new_venv = Path(getcwd()) / venv_with_ver
        utils.make_sym_link(to_path=sym_link, target=Path(new_venv), mode=self.config.link_mode, timer=self.config.timer)

    def create(self) -> None:
        """Create a new virtual environment."""
        venv = Path(self.cwd_entry.get()) / '.venv'
        if venv.is_symlink():
            self.status_txt.set('Symlink already set')
            return
        if venv.exists():
            self._rename_venv_and_make_symlink()
        else:
            uv_py_ver = self.combo_py_ver.get()
            utils.get_command_output(cmd=['uv', 'venv', '--python', uv_py_ver])
            self._rename_venv_and_make_symlink()
        self.refresh_cwd()
