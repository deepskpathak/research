"""Command line entry point. Subcommands are added by the CLI task."""
from __future__ import annotations

import sys
from typing import Sequence

from . import __version__


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] in ("-V", "--version"):
        print(f"kgrag {__version__}")
        return 0
    print("kgrag: no commands available yet (see README).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
