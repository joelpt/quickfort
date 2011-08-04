"""
Transforms/repeats blueprint layers based on a sequence of transformation
commands.
"""

from copy import deepcopy
import re
from geometry import Point
from grid import Grid, GridLayer
from filereader import FileLayer

def parse_transform_str(transform_str):
    """
    Converts space separated transform string e.g. '2e valign=top rotcw' 
    into list of tuples, e.g. [(2, 'e'), ('t', 'valign'), (1, 'rotcw')].
    
    Transforms of format s/pat/repl/ are stored as (('pat', 'repl'), 'sub')

    Returns the conversion result as follows:
        ('newphase', (x/y transforms), (z-level transforms))
    """
    transforms = transform_str.strip().split(' ')
    readies = []
    newphase = None
    for t in transforms:
        lt = t.lower()
        try:
            m = re.match(r'^(halign)=(l|m|r)\w*$', lt)
            if m is not None:
                readies.append(m.group(2, 1))
                continue
            
            m = re.match(r'^(valign)=(t|m|b)\w*$', lt)
            if m is not None:
                readies.append(m.group(2, 1))
                continue

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

            m = re.match(r'^(\d+)?(n|s|e|w|u|d|rotcw|rotccw|fliph|flipv|!)$', lt)
            if m is not None:
                count = int(m.group(1)) if m.group(1) else 1
                readies.append( (count, m.group(2)) )
                continue
        except:
            # error while match one of the permitted patterns
            raise Exception, \
                "Syntax error in transform sequence.\n" + \
                "Transform string: %s\nError occurred on: %s" % (transform_str, t)

        # failed to match any of the permitted patterns
        raise Exception, \
            "Did not recognize transform command.\n" + \
            "Transform string: %s\nDid not recognize: %s" % (transform_str, t)

    # separate zup/zdown transforms from x/y transforms
    xys = [t for t in readies if t[1][0] not in ('u', 'd')]
    zs = [t for t in readies if t[1][0] in ('u', 'd')]

    return newphase, xys, zs


class Transformer:
    """Handles transformation of a blueprint based on a series of commands."""

    def __init__(self, layers, start, debug):
        self.layers = layers
        self.start = start
        self.debug = debug
        self.valign = 'b' # bottom default vertical alignment
        self.halign = 'r' # right default horizontal alignment

    def transform(self, transforms):
        """Transforms start, layers using the given transforms."""

        layers = self.layers
        start = self.start

        if self.debug:
            print ">>>> BEGIN TRANSFORMATION"

        # loop through all single-layer transformations to all layers
        for i, layer in enumerate(layers):
            a = layer.rows # aka the memory bucket
            b = layer.rows # aka the current bucket

            if self.debug:
                print "#### Transformation buckets before transforming layer %d:" % i
                self.print_buckets(a, b)

            left = transforms
            for t in transforms:
                param, cmd = t
                left = left[1:] # remove this cmd from the remaining cmds

                if cmd == 'halign':
                    self.halign = param
                elif cmd == 'valign':
                    self.valign = param
                elif cmd == '!':
                    # The ! command just updates A to match B
                    a = deepcopy(b)
                else:
                    a, b = self.apply_transform(t, a, b) # do the transform

                    # adjust start pos for 'n' and 'w' commands
                    if cmd == 'n':
                        start += Point(0, layers[0].height() * (param - 1))
                    elif cmd == 'w':
                        start += Point(layers[0].width() * (param - 1), 0)

                if self.debug:
                    if cmd in ('halign', 'valign'):
                        print "#### Set %s=%s" % (t[1], t[0])
                    else:
                        print "#### Buckets after command %s%s:" % t
                        self.print_buckets(a, b)

                # we'll return the result in b
                layers[i].rows = b

        self.start, self.layers = start, layers

        if self.debug:
            print "<<<< END TRANSFORMATION"


    def print_buckets(self, a, b):
        """Print bucket contents A and B."""
        print '---------------- BUCKET A ----------------'
        print FileLayer.str_rows(a)
        print '---------------- BUCKET B ----------------'
        print FileLayer.str_rows(b)
        print '------------------------------------------'


    def apply_transform(self, trans, a, b):
        """
        Apply the requested transformation to 2D lists [[]] a and possibly b,
        and return the result.
        """
        b = deepcopy(b) # ensure a and b are different objects
        count, action = trans

        if action == 'sub':
            # do regex search-and-replace against every cell in B
            (pattern, replacement) = count

            # handle 'empty' patterns for the user by matching the empty string
            if pattern == '': pattern = '^$'
            elif pattern == '~': pattern = '~^$' # matches any non empty cell

            print pattern
            print replacement

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
            rot = [list(x) for x in zip(*b)] # pivot the grid (cols become rows)
            
            if action == 'rotcw':
                return self.apply_transform((1, 'fliph'), a, rot) # clockwise

            return self.apply_transform((1, 'flipv'), a, rot) # counterclockwise

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

        raise Exception, 'Unknown transformation type: %d %s' % trans

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
            raise Exception, "Unrecognized horizontal alignment code %s" % alignment

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
            raise Exception, "Unrecognized vertical alignment code %s" % alignment

        width = len(rows[0])
        rows = [[''] * width] * top + rows + [[''] * width] * bottom

        return rows        