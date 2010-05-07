# does not work?!
def flatten(ob):
    if isinstance(ob, basestring) or not isinstance(ob, Iterable):
        yield ob
    else:
        for o in ob:
            for ob in flatten(o):
                yield ob


def uniquify(seq, idfun=None):
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

def sign(n):
    if n > 0:
        return 1
    elif n == 0:
        return 0
    else:
        return -1