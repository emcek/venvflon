from pathlib import Path
from sys import platform
from unittest import mock

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
    assert sorted([venv.name for venv in venvs]) == ['.venv_310_11', '.venv_311_2', '.venv_312_5']


def test_success_deep_2_venv_list_in(resources):
    venvs = utils.venv_list_in(current_path=resources, max_depth=2)
    assert len(venvs) == 4
    assert sorted([venv.name for venv in venvs]) == ['.venv_310_11', '.venv_311_2', '.venv_312_5', '.venv_39_11']


def test_failure_venv_list_in(resources):
    venvs = utils.venv_list_in(current_path=resources / '.venv10', max_depth=1)
    assert len(venvs) == 0


@mark.parametrize('entry, expected', [
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


@mark.parametrize('entry, expected', [
    (['Resolved 65 packages in 2.61s', 'Prepared 3 packages in 4.40s', 'Uninstalled 3 packages in 188ms', 'Installed 3 packages in 29ms'], 3),
    (['Resolved 65 packages in 1ms', 'Audited 61 packages in 0.13ms'], 0),
])
def test_extract_installed_packages(entry, expected):
    assert utils.extract_installed_packages(entry=entry) == expected


@mark.parametrize('cmd_out', [
    'cpython-3.14.0a6+freethreaded-windows-x86_64-none    <download available>\ncpython-3.14.0a6-windows-x86_64-none                 <download available>\n',
    'cpython-3.14.0a6+freethreaded-linux-x86_64-gnu    <download available>\ncpython-3.14.0a6-linux-x86_64-gnu                 <download available>\n',
], ids=['Windows', 'Linux'])
def test_get_uv_pythons_dict(cmd_out):
    with mock.patch('venvflon.utils.get_command_output') as get_command_output_mock:
        get_command_output_mock.return_value = 0, '', cmd_out
        assert utils.get_uv_pythons_dict() == {
            'cpython-3.14.0a6+freethreaded': '<download available>',
            'cpython-3.14.0a6': '<download available>',
        }


def test_rename_venv_and_make_symlink_version_detection_fails(tmp_path, config):
    """Test error case when Python version cannot be detected."""
    # Change working directory to tmp_path
    with mock.patch('venvflon.utils.get_command_output') as mock_get_cmd:
        mock_get_cmd.return_value = (0, 'Invalid output', '')

        result = utils.rename_venv_and_make_symlink(config)

        assert result == 'Error: cannot detect Python version'
        mock_get_cmd.assert_called_once_with(cmd=[r'.venv\Scripts\python.exe', '-V'])


def test_rename_venv_and_make_symlink_success(tmp_path, config):
    """Test full successful flow with real filesystem operations."""
    project_dir = tmp_path / 'project'
    project_dir.mkdir()

    # Create fake .venv structure
    venv_dir = project_dir / '.venv'
    venv_dir.mkdir()

    with mock.patch('os.getcwd', return_value=str(project_dir)):
        with mock.patch('venvflon.utils.get_command_output') as mock_get_cmd:
            # Simulate Python 3.11 output
            mock_get_cmd.return_value = (0, '', 'Python 3.11.5')

            result = utils.rename_venv_and_make_symlink(config)
            assert result == ''

            assert not (project_dir / '.venv').exists()
            assert (project_dir / '.venv_311_5').exists()


def test_rename_venv_and_make_symlink_with_real_symlink(tmp_path, config):
    """Test with real symlink creation (Windows junction or symlink)."""
    project_dir = tmp_path / 'project'
    project_dir.mkdir()

    # Setup fake venv
    venv_dir = project_dir / '.venv'
    venv_dir.mkdir()
    (venv_dir / 'Scripts' / 'python.exe').mkdir(parents=True)

    config.timer = 1.2

    with mock.patch('os.getcwd', return_value=str(project_dir)):
        with mock.patch('venvflon.utils.get_command_output') as mock_get_cmd:
            mock_get_cmd.return_value = (0, '', 'Python 3.10.8')

            result = utils.rename_venv_and_make_symlink(config)

            assert result == ''

            # Verify structure
            assert (project_dir / '.venv_310_8').exists()
            assert (project_dir / '.venv').exists()  # symlink/junction

            # Verify it's a link
            venv_link = project_dir / '.venv'
            assert venv_link.is_symlink() or venv_link.is_junction()  # Windows support


def test_rename_venv_and_make_symlink_python_312(tmp_path, config):
    """Test with Python 3.12 version."""
    project_dir = tmp_path / 'project'
    project_dir.mkdir()
    (project_dir / '.venv' / 'Scripts').mkdir(parents=True)

    with mock.patch('os.getcwd', return_value=str(project_dir)):
        with mock.patch('venvflon.utils.get_command_output') as mock_get_cmd:
            mock_get_cmd.return_value = (0, '', 'Python 3.12.0')

            result = utils.rename_venv_and_make_symlink(config)
            assert result == ''
            assert (project_dir / '.venv_312_0').exists()
