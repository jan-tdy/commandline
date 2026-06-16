"""Allow ``python -m jadivcli`` to launch the shell."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
