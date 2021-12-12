"""Tests the shmgr project's CLI."""

from shmgr import main


def test_main() -> None:
    """Tests main() function."""
    assert main([""]) == 0
