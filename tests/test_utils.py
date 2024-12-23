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


def test_get_command_output_success():
    rc, err, out = utils.get_command_output(cmd=['python', '-V', '-V'])
    assert rc == 0
    assert err == ''
    assert 'Python 3.' in out


def test_get_command_output_call_process_error():
    rc, err, out = utils.get_command_output(cmd=['python', '-fake'])
    assert rc == 2
    assert 'Unknown option: -f' in err
    assert out == ''


def test_get_command_output_file_not_found_error():
    rc, err, out = utils.get_command_output(cmd=['fake', '-fake'])
    assert rc == 255
    assert err == 'None of venv were detected'
    assert out == ''


@mark.ci
def test_make_and_remove_sym_link():
    new_sym_link = Path(__file__).parent / 'new'
    utils.make_sym_link(to_path=new_sym_link, target=Path(__file__), mode=utils.LinkMode.PYTHON)
    assert new_sym_link.is_symlink()
    assert not new_sym_link.is_dir()
    if platform == 'linux':
        assert new_sym_link.is_file()
    elif platform == 'win32':
        assert not new_sym_link.is_file()
    utils.rm_sym_link(sym_link=new_sym_link, mode=utils.LinkMode.PYTHON)
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


@mark.parametrize("entry, expected", [
    ('2s', 2000.0),
    ('2.5s', 2500.0),
    ('150ms', 150.0),
    ('0.5s', 500.0),
    ('0s', 0.0),
    ('0ms', 0.0),
    ('not time at all', 0.0),
])
def test_extract_time_valid_values(entry, expected):
    assert utils.extract_time(entry=entry) == expected
