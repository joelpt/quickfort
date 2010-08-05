"""General utility stuff."""

import string

def convert_line_endings(temp, mode=0):
    """
    Convert line endings to desired OS dialect (mode).
    modes:  0 - Unix, 1 - Mac, 2 - DOS
    http://code.activestate.com/recipes/66434-change-line-endings/
    """
    if mode == 0:
        temp = string.replace(temp, '\r\n', '\n')
        temp = string.replace(temp, '\r', '\n')
    elif mode == 1:
        temp = string.replace(temp, '\r\n', '\r')
        temp = string.replace(temp, '\n', '\r')
    elif mode == 2:
        import re
        temp = re.sub("\r(?!\n)|(?<!\r)\n", "\r\n", temp)
    return temp


def flatten(l):
    """Flatten a list of elements and/or lists recursively."""
    out = []
    for item in l:
        if isinstance(item, (list, tuple)):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out


def uniquify(seq, idfun=None):
    """Deduplicate elements of list based on value of id function idfun."""
    # order preserving
    if idfun is None:
        idfun = lambda x: x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result


class Bunch:
    """
    Like a dynamic struct. Usage:
    >>> point = Bunch(datum=y, squared=y*y, coord=x)
    >>> if point.squared > threshold:
    >>>     point.isok =
    """
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

