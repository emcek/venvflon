from pathlib import Path

from pytest import fixture


@fixture()
def resources():
    """
    Path to tests/resources directory.

    :return: Path to tests/resources directory
    """
    return Path(__file__).resolve().with_name('resources')
