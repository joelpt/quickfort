"""
Transforms/repeats blueprint layers based on a sequence of transformation
commands.
"""

import re
from copy import deepcopy

from log import log_routine, logmsg, loglines
from filereader import FileLayer
from geometry import add_points

from errors import ParametersError


def parse_transform_str(transform_str):
    """
    Converts space separated transform string e.g. '2e valign=top rotcw'
    into list of tuples, e.g. [(2, 'e'), ('t', 'valign'), (1, 'rotcw')].

    Transforms of format s/pat/repl/ are stored as (('pat', 'repl'), 'sub')

    Commit sequences of the form 'rotcw ! 2e' can be entered as 'rotcw; 2e'
    and will be translated to the former form here.

    Returns the conversion result as follows:
        ('newphase', (x/y transforms), (z-level transforms))
    """
    if transform_str == '':
        return (None, None, None)

    transform_str = re.sub('\s*;\s*', ' ! ', transform_str)  # 2e;2e -> 2e ! 2e
    transform_str = re.sub('\s+', ' ', transform_str)        # cleanup spaces
    transforms = transform_str.strip().split(' ')
    readies = []
    newphase = None
    for t in transforms:
        lt = t.lower()
        try:
            # matches halign=(left|middle|right) or 1 letter equiv. l|m|r
            m = re.match(r'^(halign)=(l|m|r)\w*$', lt)
            if m is not None:
                readies.append(m.group(2, 1))
                continue

            # matches valign=(top|middle|bottom) or 1 letter equiv. t|m|b
            m = re.match(r'^(valign)=(t|m|b)\w*$', lt)
            if m is not None:
                readies.append(m.group(2, 1))
                continue

            # matches phase=(build|dig|place|query) or 1 letter equiv. b|d|p|q
            m = re.match(r'^(phase)=(b|d|p|q)\w*$', lt)
            if m is not None:
                newphase = m.group(2)
                continue

            # matches s/pattern/replacement/, allows escaping / as \/
            m = re.match(r'^(s)/(\S*?)(?<!\\)/(([^\s/]|\\/)*)(?<!\\)/?$', t)
            if m is not None:
                # internally the command is called 'sub' to avoid
                # ambiguity vs. 's' (repeat south) command
                readies.append((m.group(2, 3), 'sub'))
                continue

            # matches #D repeaters, rotcw/rotccw, fliph/flipv, and ! sequence separator
            m = re.match(r'^(\d+)?(n|s|e|w|u|d|rotcw|rotccw|fliph|flipv|!)$', lt)
            if m is not None:
                count = int(m.group(1)) if m.group(1) else 1
                readies.append((count, m.group(2)))
                continue
        except:
            # error while match one of the permitted patterns
            raise ParametersError(
                "Syntax error in transform sequence.\n" + \
                "Transform string: %s\nError occurred on: %s" % (transform_str, t)
                )

        # failed to match any of the permitted patterns
        raise ParametersError(
            "Did not recognize transform command.\n" + \
            "Transform string: %s\nDid not recognize: %s" % (transform_str, t)
            )

    # separate zup/zdown transforms from x/y transforms
    xys = [t for t in readies if t[1][0] not in ('u', 'd')]
    zs = [t for t in readies if t[1][0] in ('u', 'd')]

    return newphase, xys, zs


class Transformer:
    """Handles transformation of a blueprint based on a series of commands."""

    def __init__(self, layers, start):
        self.layers = layers
        self.start = start
        self.valign = 'b'  # bottom is default vertical alignment
        self.halign = 'r'  # right is default horizontal alignment

    @log_routine('transform', 'TRANSFORMER')
    def transform(self, transforms):
        """Transforms start, layers using the given transforms."""
        layers = self.layers
        start = self.start

        # loop through all single-layer transformations to all layers
        for i, layer in enumerate(layers):
            a = layer.rows  # aka the memory bucket
            b = layer.rows  # aka the current bucket

            logmsg('transform', 'Transformation buckets before layer %d:' % i)
            loglines('transform', lambda: self.str_buckets(a, b))

            left = transforms
            for t in transforms:
                param, cmd = t
                left = left[1:]  # remove this cmd from the remaining cmds

                if cmd == 'halign':
                    self.halign = param
                elif cmd == 'valign':
                    self.valign = param
                elif cmd == '!':
                    # The ! command just updates A to match B
                    a = b
                else:
                    a, b = self.apply_transform(t, a, b)  # do the transform

                    # adjust start pos for 'n' and 'w' commands
                    if cmd == 'n':
                        start = add_points(start, (0, layers[0].height() * (param - 1)))
                    elif cmd == 'w':
                        start = add_points(start, (layers[0].width() * (param - 1), 0))

                if cmd in ('halign', 'valign'):
                    logmsg('transform', 'Set %s=%s' % (t[1], t[0]))
                else:
                    logmsg('transform', 'Buckets after command %s%s:' % t)
                    loglines('transform', lambda: self.str_buckets(a, b))

                # we'll return the result in b
                layers[i].rows = b

        self.start, self.layers = start, layers
        return

    def str_buckets(self, a, b):
        """Make a printable string showing bucket contents A and B."""
        return '\n'.join([
            '---------------- BUCKET A ----------------',
            FileLayer.str_rows(a),
            '---------------- BUCKET B ----------------',
            FileLayer.str_rows(b),
            '------------------------------------------'])

    def apply_transform(self, trans, a, b):
        """
        Apply the requested transformation to 2D lists [[]] a and possibly b,
        and return the result.
        """
        #b = deepcopy(b)  # ensure a and b are different objects
        count, action = trans

        if action == 'sub':
            # do regex search-and-replace against every cell in B
            (pattern, replacement) = count

            # handle 'empty' patterns for the user by matching empty cells
            if pattern == '':
                pattern = '^$'
            elif pattern == '~':
                pattern = '~^$'  # matches any NON empty cell

            if len(pattern) > 0 and pattern[0] == '~':
                # "negate" the pattern - s/~d/x/ turns all non-d cells to x
                pattern = pattern[1:]
                b = [[replacement if re.search(pattern, cell) is None
                        else cell
                        for cell in row]
                    for row in b]
                return a, b

            # do normal by-cell search and replace
            b = [[re.sub(pattern, replacement, cell)
                    for cell in row]
                for row in b]
            return a, b

        if action == 'flipv':
            # flip b vertically
            b.reverse()
            return a, b

        if action == 'fliph':
            # flip b horizontally
            for row in b:
                row.reverse()
            return a, b

        if action in ('rotcw', 'rotccw'):
            # rotate a clockwise or counterclockwise 90 degrees
            rot = [list(x) for x in zip(*b)]  # pivot the grid (cols <-> rows)

            if action == 'rotcw':
                return self.apply_transform((1, 'fliph'), a, rot)  # clockwise

            return self.apply_transform((1, 'flipv'), a, rot)  # counterclockwise

        if action in ('n', 's', 'e', 'w'):
            # heights and widths
            ha, hb, wa, wb = len(a), len(b), len(a[0]), len(b[0])

            # handle alignment issues when a and b have differing dimensions
            if action in ('e', 'w'):
                if ha < hb:
                    a = self.expand_height(a, hb, self.valign)
                elif hb < ha:
                    b = self.expand_height(b, ha, self.valign)
            elif action in ('n', 's'):
                if wa < wb:
                    a = self.expand_width(a, wb, self.halign)
                elif wb < wa:
                    b = self.expand_width(b, wa, self.halign)

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
            else:  # 'e', 'w'
                # combine each row of each series item into a new row
                rows = zip(*series)
                out = []
                for r in rows:
                    newrow = []
                    for s in r:
                        newrow.extend(s)
                    out.append(newrow)
            return out, out  # must be treated as two different objects

        raise ParametersError('Unknown transformation type: %d %s' % trans)

    def expand_width(self, rows, targetwidth, alignment):
        """Expand rows to requested targetwidth, aligning according to alignment param."""
        width = len(rows[0])
        if alignment == 'l':
            # align left: add columns to the right
            left, right = 0, (targetwidth - width)
        elif alignment == 'r':
            # align right: add columns to the left
            left, right = (targetwidth - width), 0
        elif alignment == 'm':
            # align middle: add columns to both left and right evenly
            left = (targetwidth - width) / 2
            right = targetwidth - width - left
        else:
            raise ParametersError(
                "Unrecognized horizontal alignment code %s" % alignment)

        for i, r in enumerate(rows):
            r = [''] * left + r + [''] * right
            rows[i] = r
        return rows

    def expand_height(self, rows, targetheight, alignment):
        """Expand rows to requested targetheight, aligning according to alignment param."""
        height = len(rows)
        if alignment == 't':
            # align top: add rows to the bottom
            top, bottom = 0, (targetheight - height)
        elif alignment == 'b':
            # align bottom: add rows to the top
            top, bottom = (targetheight - height), 0
        elif alignment == 'm':
            # align middle: add rows to both top and bottom evenly
            top = (targetheight - height) / 2
            bottom = targetheight - height - top
        else:
            raise ParametersError(
                "Unrecognized vertical alignment code %s" % alignment)

        width = len(rows[0])
        rows = [[''] * width] * top + rows + [[''] * width] * bottom

        return rows
