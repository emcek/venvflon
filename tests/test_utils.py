from pathlib import Path
from sys import platform

from pytest import mark

from venvflon import utils


@mark.slow
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
@mark.parametrize('cmd, result', [('Clear-Host', 0), ('bullshit', -1)])
def test_run_command(cmd, result):
    rc = utils.run_command(cmd=['powershell', cmd])
    assert rc == result


def test_success_deep_1_venv_list_in(resources):
    venvs = utils.venv_list_in(current_path=resources, max_depth=1)
    assert len(venvs) == 3
    assert sorted([venv.name for venv in venvs]) == ['.venv_310', '.venv_311', '.venv_312']


def test_success_deep_2_venv_list_in(resources):
    venvs = utils.venv_list_in(current_path=resources, max_depth=2)
    assert len(venvs) == 4
    assert sorted([venv.name for venv in venvs]) == ['.venv_310', '.venv_311', '.venv_312', '.venv_39']


def test_failure_venv_list_in():
    venvs = utils.venv_list_in(current_path=Path('..'), max_depth=1)
    assert len(venvs) == 0
