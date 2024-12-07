from pathlib import Path
from sys import platform

from pytest import mark, raises

from venvflon import utils
from venvflon.utils import LinkMode


@mark.slow
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
@mark.parametrize('cmd, result', [('Clear-Host', 0), ('bullshit', -1)])
def test_run_command(cmd, result):
    rc = utils.run_command(cmd=['powershell', cmd])
    assert rc == result

def test_get_command_output_success():
    rc, err, out = utils.get_command_output(cmd=['python', '-V', '-V'])
    assert rc == 0
    assert err == ''
    assert 'Python 3.' in out


def test_get_command_output_failure():
    rc, err, out = utils.get_command_output(cmd=['python', '-fake'])
    assert rc == 2
    assert 'Unknown option: -f' in err
    assert out == ''


@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_make_sym_link_windows_without_admin():
    with raises(OSError) as err:
        utils.make_sym_link(to_path=Path(__file__).parent / 'new', target=Path(__file__), mode=LinkMode.PYTHON)
    assert err.value.strerror == 'A required privilege is not held by the client'


@mark.skipif(condition=platform != 'linux', reason='Run only on Linux')
def test_make_and_remove_sym_link():
    new_sym_link = Path(__file__).parent / 'new'
    utils.make_sym_link(to_path=new_sym_link, target=Path(__file__), mode=LinkMode.PYTHON)
    assert new_sym_link.is_symlink()
    assert not new_sym_link.is_dir()
    assert new_sym_link.is_file()
    utils.rm_sym_link(sym_link=new_sym_link, mode=LinkMode.PYTHON)
    assert not new_sym_link.exists()


def test_success_deep_1_venv_list_in(resources):
    venvs = utils.venv_list_in(current_path=resources, max_depth=1)
    assert len(venvs) == 3
    assert sorted([venv.name for venv in venvs]) == ['.venv_310', '.venv_311', '.venv_312']


def test_success_deep_2_venv_list_in(resources):
    venvs = utils.venv_list_in(current_path=resources, max_depth=2)
    assert len(venvs) == 4
    assert sorted([venv.name for venv in venvs]) == ['.venv_310', '.venv_311', '.venv_312', '.venv_39']


def test_failure_venv_list_in(resources):
    venvs = utils.venv_list_in(current_path=resources / '.venv10', max_depth=1)
    assert len(venvs) == 0
