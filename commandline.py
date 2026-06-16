#!/usr/bin/env python3
"""Entry-point shim for JadivCommandline.

The implementation now lives in the ``jadivcli`` package. This script is kept so
that ``python3 commandline.py`` keeps working (and so Code Master can launch the
app via its metadata). All it does is start the shell.
"""

from jadivcli.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
