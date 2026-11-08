from argparse import Namespace
from pathlib import Path
from sys import platform

from pytest import fixture

from venvflon import utils


@fixture()
def resources():
    """
    Path to tests/resources directory.

    :return: Path to tests/resources directory
    """
    return Path(__file__).resolve().with_name('resources')


@fixture
def config():
    """Default test config."""
    if platform == 'win32':
        return Namespace(link_mode=utils.LinkMode.PWSH5, timer=False)
    elif platform == 'linux':
        return Namespace(link_mode=utils.LinkMode.PYTHON, timer=4)
    else:
        return Namespace(link_mode=utils.LinkMode.PWSH7, timer=False)
