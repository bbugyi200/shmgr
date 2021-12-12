"""Contains the shmgr package's main entry point.

This tool is primarily used to dynamically source bash libraries.

Examples:
    # Load v1.* of the "foo" shell library...
    eval "$(shmgr load foo:1)"

    # Load v2.* of the "foo" shell library. Exit with a non-zero exit code
    # if no version >=2.0.0 can be found...
    eval "$(shmgr load foo:2)"

    # Load v2.* of the "foo" shell library. Exit with a non-zero exit
    # code if no version >=2.1.0 can be found...
    eval "$(shmgr load foo:2.1)"

    # Load v3.* of the "bar" shell library. Exit with a non-zero exit code
    # if no version >=3.2.1 can be found...
    eval "$(shmgr load bar:3.2.1)"

    # Load v2.* of the "foo" shell library and v3.* of the "bar" shell library.
    # Exit with a non-zero exit code if no version >=2.1.0 can be found for the
    # "foo" library OR if no version >=3.2.1 can be found for the "bar"
    # library...
    eval "$(shmgr load foo:2.1 bar:3.2.1)"

    # List all available shell libraries...
    shmgr list
"""

from importlib.resources import read_text
from typing import Sequence

import clap
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Arguments(clap.Arguments):
    """Command-line arguments."""

    library_name: str


def parse_cli_args(argv: Sequence[str]) -> Arguments:
    """Parses command-line arguments."""
    parser = clap.Parser()
    parser.add_argument(
        "library_name",
        help="The name of the shell library that you want to load.",
    )

    args = parser.parse_args(argv[1:])
    kwargs = vars(args)

    return Arguments(**kwargs)


def run(args: Arguments) -> int:
    """This function acts as this tool's main entry point."""
    if "." not in args.library_name:
        libname = args.library_name + ".sh"
    else:
        libname = args.library_name

    print(read_text("shmgr._data.libs", libname))
    return 0


main = clap.main_factory(parse_cli_args, run)
if __name__ == "__main__":
    main()
