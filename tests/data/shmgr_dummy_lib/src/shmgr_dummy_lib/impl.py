"""Dummy shell library plugin client implementation."""

from typing import Tuple

# from shmgr.plugin import hookimpl


VERSION = "3.0.0"


# @hookimpl
def register_shell_libs() -> Tuple[str, str, Tuple[int, int, int]]:
    """We register the dummy shell library using this hook implementation."""
    major, minor, patch = [int(v) for v in VERSION.split(".")]
    return ("shmgr_dummy_lib", "dummy", (major, minor, patch))
