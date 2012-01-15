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


def is_substring_in_list(needle, haystack):
    """
    Determine if any string in haystack:list contains the specified
    needle:string as a substring.
    """
    for e in haystack:
        if needle in e:
            return True
    return False


# Abstract struct class
class Struct:
    def __init__(self, *argv, **argd):
        if len(argd):
            # Update by dictionary
            self.__dict__.update(argd)
        else:
            # Update by position
            attrs = filter(lambda x: x[0:2] != "__", dir(self))
            for n in range(len(argv)):
                setattr(self, attrs[n], argv[n])
