from copy import deepcopy
import re
from itertools import count
from geometry import Grid

def transform(transforms, layers):
    # print transforms

    for i, layer in enumerate(layers):
        a = layer.rows
        b = layer.rows
        left = transforms
        for t in transforms:
            count, cmd = t
            if cmd in ('d', 'u'): # z-up/z-down handled in next loop
                break
            left = left[1:]
            if cmd == '!':
                # update original blueprint memory slot
                a = deepcopy(b)
            elif cmd in ('n', 's', 'e', 'w'):
                # print 'calling transform %s,%s with this:' % t
                # print 'A:'
                # print Grid.print_cells(a)
                # print 'B:'
                # print Grid.print_cells(b)
                new = apply_transform(t, a, b)
                a, b = new, deepcopy(new)
            else:
                # print 'calling transform %s,%s with this:' % t
                # 'B:'
                # print Grid.print_cells(b)
                # print
                new = apply_transform(t, b)
                b = new
            layers[i].rows = b
            # layers[i].grid.height = len(layers[i].grid.cells)
            # layers[i].grid.width = len(layers[i].grid.cells[0])
            # print
            # print layers[i].grid
            # print '--- ^b ---'

    # do remaining zup/zdown transforms, if any
    for t in left:
        count, cmd = t
        if cmd not in ('d', 'u'):
            raise Exception, "Transform sequence contains invalid transformation %s%s" % t
        # clone z-layers
        addlayers = deepcopy(layers)

        # determine z-level offset after drawing layers
        zoffset = sum(
            sum(1 if x == '>' else -1 if x == '<' else 0
                for x in layer.onexit
                )
            for layer in addlayers
            )

        # print 'zoffset %d' % zoffset
        # add appropriate z-up/down chars for transitioning
        # between zlevels
        if cmd == 'd':
            if zoffset >= 0:
                zfix = ['>']
            else:
                zfix = ['>'] * ((abs(zoffset) * 2) + 1)
        else: # 'u'
            if zoffset <= 0:
                zfix = ['<']
            else:
                zfix = ['<'] * ((zoffset * 2) + 1)
        # print 'layercount at %d' % len(layers)

        for i in xrange(1, count):
            layers[-1].onexit += zfix
            layers.extend(deepcopy(addlayers))

    # print 'done with xform:'
    # print layers[0].grid
    # print '---------------'
    return layers

def apply_transform(transform, a, b=None):
    """
    Apply the requested transformation to 2D lists [[]] a and possibly b,
    and return the result.
    """
    count, action = transform
    if b and (len(a) != len(b) or len(a[0]) != len(b[0])):
        raise Exception, (
            "Cannot apply '%d%s' because " % transform +
            "grids to combine have differing dimensions.\n\n"
            "To use e.g. 'rotcw 2e', ensure your blueprint is perfectly square.\n\n"
            "To use e.g. 'rotcw 2e rotcw 2s', instead use "
            "'rotcw 2e fliph flipv 2s'."
            )
    # a, b = deepcopy(a), deepcopy(b)
    # print 'applying %s %d' % (action, count)
    # print 'A:'
    # print Grid.print_cells(a)
    # if b:
    #     print 'B:'
    #     print Grid.print_cells(b)

    if action == 'flipv':
        # flip a vertically
        a.reverse()
        # print 'flipv:'
        # print Grid.print_cells(a)
        return a
    elif action == 'fliph':
        # flip a horizontally
        for row in a:
            row.reverse()
        # print 'fliph:'
        # print Grid.print_cells(a)
        return a
    elif action in ('rotcw', 'rotccw'):
        rot = [list(x) for x in zip(*a)]
        # print 'rot:'
        # print Grid.print_cells(rot)
        if action == 'rotcw':
            return apply_transform((1, 'fliph'), rot)
        if action == 'rotccw':
            return apply_transform((1, 'flipv'), rot)
    elif action in ('n', 's', 'e', 'w'):
        # repeat (a+b) in given direction the requested number
        # of times:
        #   with only a, action 3e would produce aaa
        #   with both a and b, action 3e would produce aba
        if not b:
            series = [a] * count
        else:
            series = ([a, b] * (count // 2)) + \
                ([a] if count % 2 == 1 else [])

        # reverse series for negative directions
        if action in ('n', 'w'): series.reverse()

        # repeat series in direction
        if action in ('n', 's'):
            out = []
            for s in series:
                out.extend(s)
        else: # 'e', 'w'
            # combine each row of each series item
            # into a new row
            rows = zip(*series)
            out = []
            for r in rows:
                newrow = []
                for s in r:
                    newrow.extend(s)
                out.append(newrow)
        return out

    else:
        raise Exception, 'Unknown transformation type: %d %s' % transform

def parse_transform_str(transform_str):
    transforms = transform_str.lower().split(' ')
    readies = []
    for t in transforms:
        m = re.match(r'(\d+)?(\w+|!)', t)
        try:
            (count, cmd) = m.group(1, 2)
        except:
            raise Exception, 'Syntax error in transform sequence.\n' + transform_str
        count = int(count) if count else 1
        readies.append((count, cmd))

    # put zup/zdown transforms at the end so we do x/y transforms first
    readies.sort(cmp=lambda x, y: compare_transforms(x, y))
    return readies


def compare_transforms(t, u):
    tz = t[1][0] in ('u', 'd')
    uz = u[1][0] in ('u', 'd')

    if tz and uz:
        return 0
    if tz:
        return 1
    if uz:
        return -1
    return 0
