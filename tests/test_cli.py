"""Integration tests for the `shmgr` tool."""

from importlib.resources import read_text
import os
from pathlib import Path
import subprocess as sp
from textwrap import dedent
from typing import Iterator

from _pytest.capture import CaptureFixture
from pytest import fixture
from rich.console import Console
from rich.text import Text
from typing_extensions import Final

from shmgr import cli


console = Console(stderr=True)

CACHE_DIR_ENVVAR: Final = "SHMGR_CACHE_DIR"


@fixture(name="cache_dir")
def cache_dir_fixture(tmp_path: Path) -> Iterator[Path]:
    """Setup a temp cache dir to be used with tests."""
    result = tmp_path / "cache"
    result.mkdir()

    old_shmgr_cache_dir = os.getenv(CACHE_DIR_ENVVAR)
    os.environ[CACHE_DIR_ENVVAR] = str(result)

    yield result

    if old_shmgr_cache_dir is not None:
        os.environ[CACHE_DIR_ENVVAR] = old_shmgr_cache_dir
    else:
        del os.environ[CACHE_DIR_ENVVAR]


@fixture(name="dummy_lib_contents")
def dummy_lib_setup() -> Iterator[str]:
    """Install dummy plugin client to be used with tests."""
    TEXT_STATUS = "<<<<<   {}   >>>>>     ".format
    this_dir = Path(__file__).resolve().parent
    with console.status(
        Text(
            TEXT_STATUS("PIP INSTALL SHMGR_DUMMY_LIB......."),
            style="bold #004e00",
        )
    ):
        popen = sp.Popen(
            f"python -m pip install -e {this_dir}/data/shmgr_dummy_lib",
            shell=True,
        )
        popen.communicate()
        ec = popen.returncode
        assert ec == 0, "Failed to install 'dummy' shell library."

    result = read_text("shmgr_dummy_lib.data.dummy", "latest.sh")

    yield result

    with console.status(
        Text(
            TEXT_STATUS("PIP UNINSTALL SHMGR_DUMMY_LIB......."),
            style="bold #ff9500",
        )
    ):
        popen = sp.Popen("python -m pip uninstall -y shmgr_dummy_lib", shell=True)
        popen.communicate()
        ec = popen.returncode
        assert ec == 0, "Failed to uninstall 'dummy' shell library."


def test_first_load(
    dummy_lib_contents: str, cache_dir: Path, capsys: CaptureFixture
) -> None:
    """Tests that we can load a shell library for the first time.

    The library should be able to be successfully loaded AND should be cached
    for later.
    """
    assert not list(
        cache_dir.rglob("*")
    ), "The fake cache directory should initially be empty."

    assert cli.main(["", "load", "dummy:3"]) == 0

    captured = capsys.readouterr()
    assert captured.out == dummy_lib_contents, (
        "The `shmgr load test:3` command should output the contents of version"
        " 3.0.0 of the 'test' shell library."
    )

    actual_cached_libs = list(cache_dir.rglob("*.sh"))
    assert len(actual_cached_libs) == 3, (
        "After invoking `shmgr load test:3`, we should have one cached"
        " version of the test shell library per major version available (e.g."
        " test/1.0.1.sh, test/2.3.4.sh, test/3.0.0.sh)  | "
        f" actual_cached_libs={actual_cached_libs}"
    )

    v3_lib_path = cache_dir / "test/3.0.0.sh"
    assert v3_lib_path.read_text() == dummy_lib_contents, (
        "The test/3.0.0.sh file should contain the cached contents of version"
        " 3.0.0 of the 'test' shell library."
    )


def test_cached_load(cache_dir: Path) -> None:
    """Tests that we load cached shell libraries properly."""
    foo_lib_contents = dedent(
        """
        #!/bin/bash

        function foo() {
            echo "KUNG FOOOOOO!"
        }
    """
    ).strip()

    v1_foo_lib_path = cache_dir / "foo/1.2.3.sh"
    v1_foo_lib_path.parent.mkdir(parents=True)
    v1_foo_lib_path.write_text(foo_lib_contents)

    assert os.system("shmgr load foo:1") == 0

    popen = sp.Popen(["shmgr", "load", "foo:1"], stdout=sp.PIPE)
    stdout, _stderr = popen.communicate()

    assert stdout.decode().strip() == foo_lib_contents, (
        "The `shmgr load foo:1` command should output the cached contents of"
        " v1.* of the 'foo' shell library."
    )
