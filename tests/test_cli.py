"""Integration tests for the `shmgr` tool."""

from importlib.resources import read_text
from pathlib import Path
from textwrap import dedent

from _pytest.capture import CaptureFixture

from shmgr import cli


def test_first_load(tmp_path: Path, capsys: CaptureFixture) -> None:
    """Tests that we can load a shell library for the first time.

    The library should be able to be successfully loaded AND should be cached
    for later.

    WARNING: This test depends on the shmgr-test-lib package (which is a test
    plugin client for this package) being listed in this project's development
    requirements.
    """
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    assert not list(
        cache_dir.rglob("*")
    ), "The fake cache directory should initially be empty."

    assert cli.main(["", "load", f"--cache-dir={cache_dir}", "test:3"]) == 0

    captured = capsys.readouterr()
    test_lib_contents = read_text("shmgr_test_lib.data", "3.0.0.sh")
    assert captured.out == test_lib_contents, (
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
    assert v3_lib_path.read_text() == test_lib_contents, (
        "The test/3.0.0.sh file should contain the cached contents of version"
        " 3.0.0 of the 'test' shell library."
    )


def test_cached_load(tmp_path: Path, capsys: CaptureFixture) -> None:
    """Tests that we load cached shell libraries properly."""
    cache_dir = tmp_path / "cache"

    foo_lib_contents = dedent(
        """
        #!/bin/bash

        function foo() {
            echo "KUNG FOOOOOO!"
        }
    """
    )

    v1_foo_lib_path = cache_dir / "foo/1.2.3.sh"
    v1_foo_lib_path.parent.mkdir(parents=True)
    v1_foo_lib_path.write_text(foo_lib_contents)

    assert cli.main(["", "load", f"--cache-dir={cache_dir}", "foo:1"]) == 0

    captured = capsys.readouterr()
    assert captured.out == foo_lib_contents, (
        "The `shmgr load foo:1` command should output the cached contents of"
        " v1.* of the 'foo' shell library."
    )
