"""Dummy shell library plugin client implementation."""

from typing import Tuple

from shmgr.plugin import hookimpl


@hookimpl
def register_shell_libs() -> Tuple[str, str, Tuple[int, int, int]]:
    """We register the dummy shell library using this hook implementation."""
    return ("shmgr_dummy_lib", "dummy", (3, 0, 0))
