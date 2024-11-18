from __future__ import annotations

from os import walk, sep
from pathlib import Path
from subprocess import run, CalledProcessError
from typing import Sequence


def run_command(cmd: Sequence[str], cwd: Path | None = None) -> int:
    """
    Run command in shell as a subprocess.

    :param cmd: The command to be executed as a sequence of strings
    :param cwd: current working directory
    :return: The return code of command
    """
    try:
        proc = run(cmd, check=True, shell=False, cwd=cwd)
        return proc.returncode
    except CalledProcessError as e:
        print(f'Result: {e}')
        return -1

def get_command_output(cmd: Sequence[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """
    Execute command and return its output.

    :param cmd: The command to be executed as a sequence of strings
    :param cwd: current working directory
    :return: Tuple with return code, stderr and stdout
    """
    try:
        result = run(cmd, capture_output=True, check=True, cwd=cwd)
        return result.returncode, result.stderr.decode('utf-8'), result.stdout.decode('utf-8')
    except CalledProcessError as e:
        print(f'Result: {e}')
        return e.returncode, e.stderr.decode('utf-8'), e.stdout.decode('utf-8')


def make_sym_link(to_path: Path, target: Path) -> None:
    cmd_symlink = f'"New-Item -ItemType SymbolicLink -Path \\"{to_path}\\" -Target \\"{target}\\"'
    ps_command = f"Start-Process powershell.exe -ArgumentList '-Command {cmd_symlink}' -Verb RunAs"
    print(f'Make symbolic link: {ps_command}')
    run_command(cmd=['powershell.exe', '-Command', ps_command])


def rm_sym_link(sym_link: Path) -> None:
    rm_symlink = f"(Get-Item '{sym_link}').Delete()"
    ps_command = f'Start-Process powershell.exe -ArgumentList "-Command {rm_symlink}" -Verb RunAs'
    print(f'Execute: {ps_command}')
    run_command(cmd=['powershell.exe', '-Command', ps_command])


def venv_list_in(current_path: Path, max_depth: int = 1) -> Sequence[Path]:
    result = []
    for dirpath, dirnames, _ in walk(current_path, topdown=True):
        for dirname in dirnames:
            if '.venv' in dirname:
                result.append(Path(dirpath) / dirname)
        if dirpath.count(sep) - str(current_path).count(sep) == max_depth - 1:
            del dirnames[:]
    return result
