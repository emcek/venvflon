from os import path, walk, remove, readlink, symlink, environ, getcwd
from pathlib import Path
from sys import base_prefix, executable

environ["TCL_LIBRARY"] = str(Path(base_prefix) / "tcl" / "tcl8.6")
environ["TK_LIBRARY"] = str(Path(base_prefix) / "tcl" / "tk8.6")
import tkinter as tk
print(executable)

class Gui(tk.Frame):
    def __init__(self, master: tk.Tk, ) -> None:
        super().__init__(master)
        self.master = master
        self.venv = tk.StringVar()
        self.status_txt = tk.StringVar()
        self.venv_list = [Path(dirpath) / dirname for dirpath, dirnames, _ in walk(Path(getcwd()).parents[1])
                          for dirname in dirnames if '.venv' in dirname.lower()]
        self.init_widgets()
        self.update_status()

    def init_widgets(self) -> None:
        self.master.columnconfigure(index=0, weight=1)
        frame = tk.Frame(master=self.master, relief=tk.GROOVE, borderwidth=2)
        frame.grid(row=0, column=0, padx=2, pady=2, rowspan=len(self.venv_list))
        for i, text in enumerate(self.venv_list):
            rb_venvs = tk.Radiobutton(master=frame, text=str(text), variable=self.venv, value=text, command=self.key_selected)
            rb_venvs.grid(row=i, column=0, pady=0, padx=2, sticky=tk.W)
        status = tk.Label(master=self.master, textvariable=self.status_txt)
        status.grid(row=len(self.venv_list) + 1, column=0, sticky=tk.W)

    def key_selected(self):
        key = self.venv.get()
        # remove(path.join(Path.home(), '.ssh/id_rsa'))
        # remove(path.join(Path.home(), '.ssh/id_rsa.pub'))
        # symlink(key, path.join(Path.home(), '.ssh/id_rsa'))
        # symlink(f'{key}.pub', path.join(Path.home(), '.ssh/id_rsa.pub'))
        self.update_status()

    def update_status(self):
        # out = readlink(path.join(Path.home(), '.ssh/id_rsa'))
        out = ''
        self.status_txt.set(out.split('/')[-1])


if __name__ == '__main__':
    root_tk = tk.Tk()
    width, height = 250, 120
    root_tk.title('venvflon')
    root_tk.geometry(f'{width}x{height}')
    root_tk.minsize(width=width, height=height)
    here = path.abspath(path.dirname(__file__))
    root_tk.iconphoto(False, tk.PhotoImage(file='img/cannula_64.png'))
    gui = Gui(master=root_tk)
    gui.mainloop()
