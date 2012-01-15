"""
Used to determine if script is running as a script (./qfconvert.py) or as a
py2exe-compiled exe file (./qfconvert.exe). Also gets the script/exe's path.
"""

import imp
import os
import sys


def main_is_frozen():
    """Returns True when running as an exe."""
    return (hasattr(sys, "frozen") or   # new py2exe
        hasattr(sys, "importers")       # old py2exe
        or imp.is_frozen("__main__"))   # tools/freeze


def get_main_dir():
    """Returns the path to the currently executing script or exe."""
    if main_is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(sys.argv[0])
