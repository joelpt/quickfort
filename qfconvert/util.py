"""General utility stuff."""

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

