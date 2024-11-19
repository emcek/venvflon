from sys import platform

from pytest import mark

from venvflon import utils


@mark.slow
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
@mark.parametrize('cmd, result', [('Clear-Host', 0), ('bullshit', -1)])
def test_run_command(cmd, result):
    rc = utils.run_command(cmd=['powershell', cmd])
    assert rc == result
