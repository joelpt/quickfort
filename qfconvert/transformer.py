"""
Transforms/repeats blueprint layers based on a sequence of transformation
commands.
"""

from copy import deepcopy
import re
from geometry import GridLayer, Point

def transform(transforms, start, layers):
    """Transforms start, layers using the given transforms."""

    for i, layer in enumerate(layers):
        a = layer.rows # aka the memory bucket
        b = layer.rows # aka the current bucket
        left = transforms
        for t in transforms:
            count, cmd = t
            if cmd in ('d', 'u'): # z-up/z-down handled in next loop
                break
            left = left[1:]
            if cmd == '!':
                # The ! command just updates A to match B
                a = deepcopy(b)
            else:
                a, b = apply_transform(t, a, b) # do the transform

                # adjust start pos for 'n' and 'w' commands
                if cmd == 'n':
                    start += Point(0, layers[0].height() * (count - 1))
                elif cmd == 'w':
                    start += Point(layers[0].width() * (count - 1), 0)

            # we'll return the result in b
            layers[i].rows = b

    # do remaining zup/zdown transforms, if any
    for t in left:
        count, cmd = t

        if cmd not in ('d', 'u'):
            raise Exception, \
                "Transform sequence contains invalid transformation %s%s" % t

        # clone z-layers
        addlayers = deepcopy(layers)

        # determine z-level offset after drawing layers
        dz = GridLayer.zoffset(addlayers)

        # add appropriate z-up/down chars for transitioning between zlevels
        if cmd == 'd':
            if dz >= 0:
                zfix = ['>']
            else:
                zfix = ['>'] * ((abs(dz) * 2) + 1)
        else: # 'u'
            if dz <= 0:
                zfix = ['<']
            else:
                zfix = ['<'] * ((dz * 2) + 1)

        # add new layers with appropriate onexit transitions
        for i in xrange(1, count):
            layers[-1].onexit += zfix
            layers.extend(deepcopy(addlayers))

    return start, layers


def apply_transform(trans, a, b):
    """
    Apply the requested transformation to 2D lists [[]] a and possibly b,
    and return the result.
    """
    b = deepcopy(b) # ensure a and b are different objects
    count, action = trans
    if b and (len(a) != len(b) or len(a[0]) != len(b[0])):
        raise Exception, (
            "Cannot apply '%d%s' because " % trans +
            "grids to combine have differing dimensions "
            "(%dx%d vs %dx%d).\n" % (len(a[0]), len(a), len(b[0]), len(b)) +
            "For 'rotcw 2e', ensure your blueprint is perfectly square.\n"
            "For 'rotcw 2e rotcw 2s', instead use 'rotcw 2e fliph flipv 2s'."
            )

    if action == 'flipv':
        # flip b vertically
        b.reverse()
        return a, b

    elif action == 'fliph':
        # flip b horizontally
        for row in b:
            row.reverse()
        return a, b

    elif action in ('rotcw', 'rotccw'):
        # rotate a clockwise or counterclockwise 90 degrees
        rot = [list(x) for x in zip(*b)] # pivot the grid (cols become rows)
        if action == 'rotcw':
            return apply_transform((1, 'fliph'), a, rot)
        if action == 'rotccw':
            return apply_transform((1, 'flipv'), a, rot)

    elif action in ('n', 's', 'e', 'w'):
        # repeat (a+b) in given direction the requested number of times
        #   4e yields ABAB pattern; 3e yields ABA
        series = ([a, b] * (count // 2)) + \
            ([a] if count % 2 == 1 else [])

        # reverse series for negative directions
        if action in ('n', 'w'):
            series.reverse()

        # repeat series in direction
        if action in ('n', 's'):
            out = []
            for s in series:
                out.extend(s)
        else: # 'e', 'w'
            # combine each row of each series item into a new row
            rows = zip(*series)
            out = []
            for r in rows:
                newrow = []
                for s in r:
                    newrow.extend(s)
                out.append(newrow)
        return out, deepcopy(out) # must be treated as two different objects

    else:
        raise Exception, 'Unknown transformation type: %d %s' % trans


def parse_transform_str(transform_str):
    """
    Converts space separated transform string e.g. '2e rotcw' into list
    of tuples, e.g. [(2, 'e'), (1, 'rotcw')]
    Returns the conversion result as a list of tuples.
    """
    transforms = transform_str.lower().strip().split(' ')
    readies = []
    for t in transforms:
        m = re.match(r'(\d+)?(\w+|!)', t)
        try:
            (count, cmd) = m.group(1, 2)
        except:
            raise Exception, \
                "Syntax error in transform sequence.\n" + transform_str
        count = int(count) if count else 1
        readies.append((count, cmd))

    # put zup/zdown transforms at the end so we do x/y transforms first
    readies.sort(key=lambda x: 1 if x[1][0] in ('u', 'd') else 0)
    return readies

