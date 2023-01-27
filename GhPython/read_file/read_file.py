"""Reads the contents of a file.
    How to use:
        This file should be included in a GhPython Component.
    Inputs:
        Path: The absolute path of the file to read
        PerLine: By default True to output the data line by line, or False
        Empty: By default True, or False to remove empty lines
    Output:
        Data: The file content"""

__author__ = "Zhitong Cui"
__version__ = "2021-7-23"

## -----------------------------------------------------------------------------

ghenv.Component.Name = "Read File"
ghenv.Component.NickName = "ReadFile"

import Grasshopper as gh
import os

def read_lines(fpath, empty=True):
    """Reads the contents of a file line by line.

    Args:
      fpath: An absolute path to a file to read
      empty: By default True to remove empty lines

    Raises:
      OSError: '<fpath>' is not a valid file path
      RuntimeError: Unable to read 'fname'

    Returns:
      The individual lines of data in a list.
    """
    lines = []
    if not os.path.exists(fpath) or not os.path.isfile(fpath):
        raise OSError("'{}' is not a valid file path".format(fpath))

    try:
        with open(fpath) as f:
            for line in f:
                if not empty and (line == '\n' or line == '\r\n'):
                    continue
                lines.append(line)
    except:
        basedir, fname = os.path.split(fpath)
        raise RuntimeError("Unable to read '{}'".format(fname))

    return lines

## -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Manage path input
    if Path is None:
        e = "Input parameter Path failed to collect data"
        ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Warning, e)

    if PerLine is None:
        Perline = True

    if Empty is None:
        Empty = True

    if Path is not None:
        # Read data from file
        lines = []
        try:
            lines = read_lines(Path, Empty)
        except Exception as e:
            ghenv.Component.AddRuntimeMessage(gh.Kernel.GH_RuntimeMessageLevel.Error, str(e))
        # Output data
        if PerLine:
            Data = lines
        else:
            Data = "".join(lines)
