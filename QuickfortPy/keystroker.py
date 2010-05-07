from geometry import *
import re
from itertools import takewhile

"""
KEY_LIST = {
        'n':config['KeyUp'],
        'ne':config['KeyUpRight'],
        'e':config['KeyRight'],
        'se':config['KeyDownRight'],
        's':config['KeyDown'],
        'sw':config['KeyDownLeft'],
        'w':config['KeyLeft'],
        'nw':config['KeyUpLeft'],
        'u':config['KeyUpZ'],
        'd':config['KeyDownZ'],
        '!':config['KeyCommit'],
        '^':config['KeyExitMenu']
    }
"""

KEY_LIST = {
    'n': '8', 'ne': '9', 'e': '6', 'se': '3', 's': '2', 'sw': '1', 'w': '4', 'nw': '7'
}

BUILD_TYPE_CFG = {
    'd': { # dig
        'init': '',
        'designate': ['moveto','cmd','+','setsize','+'],
        'allowlarge': [],
        'submenukeys': '',
        'minsize': 0,
        'maxsize': 0,
        'custom': {},
        'setsizefun': lambda keystroker, start, end: keystroker.setsize_standard(start, end)
         },
    'b': { # build
        'init': '^',
        'designate': 'menu cmd moveto setsize + % ++ % exitmenu',
        'allowlarge': ['Cw', 'CF', 'Cr', 'o'],
        'submenukeys': 'iweCTM',
        'minsize': 4,
        'maxsize': 10,
        'custom': {
            'p': 'cmd moveto setsize +', # farm plot
            'wf': 'cmd moveto + % + % ++ %', # metalsmith forge
            'wv': 'cmd moveto + % + % ++ %', # magma forge
            'D': 'cmd moveto + % + % ++ %', # trade depot
            'Ms': 'cmd moveto + + + + %'
            },
        'setsizefun': lambda keystroker, start, end: keystroker.setsize_build(start, end)
        },
    'p': { # place (stockpiles)
        'init': '',
        'designate': 'moveto cmd + setsize +',
        'allowlarge': [],
        'submenukeys': '',
        'minsize': 0,
        'maxsize': 0,
        'custom': {},
        'setsizefun': lambda keystroker, start, end: keystroker.setsize_standard(start, end)
        },
    'q': { # query (set building/task prefs)
        'init': '',
        'designate': 'moveto cmd + setsize +',
        'allowlarge': [],
        'submenukeys': '',
        'minsize': 0,
        'maxsize': 0,
        'custom': {},
        'setsizefun': lambda keystroker, start, end: keystroker.setsize_standard(start, end)
        }
}


def setsize_standard(ks, start, end):
    return ks.move(start, end)

def setsize_build(ks, start, end):
    # move cursor halfway to end from start
    # this would work if i could figure out how to
    # implement division in Point vs an int instead of another Point
    midpoint = start + ((end - start) // 2)
    keys = ks.move(start, midpoint)

    # resize construction
    area = Area(start, end)
    keys += KEY_LIST['widen'] * (area.width() - 1)
    keys += KEY_LIST['heighten'] * (area.height() - 1)
    return keys

class Keystroker:

    def __init__(self, grid, build_type):
        self.grid = grid
        self.build_type = build_type
        self.current_menu = None


    def plot(self, plots):
        keys = []
        cursorpos = None

        replacebase = {
            '+': ['{Enter}'], # , '%'],
            '++': ['+{Enter}', '%wait%'],
            '%': ['%wait%']
            }

        last_command = ''

        # construct the list of keystrokes required to move to each
        # successive area and build it
        for pos in plots:
            cell = self.grid.get_cell(pos)
            command = cell.command
            endpos = cell.area.opposite_corner(pos)

            # build replacements dict
            replacements = replacebase.copy()

            if command != last_command:
                replacements['cmd'] = command
                last_command = command
            else:
                replacements['cmd'] = ''

            if cursorpos is not None:
                replacements['moveto'] = self.move(cursorpos, pos)
            else:
                replacements['moveto'] = []


            replacements['setsize'] = self.move(pos, endpos)
            pattern = BUILD_TYPE_CFG['d']['designate']
            newkeys = []

            # do pattern replacements (and throw away empty elements)
            for p in pattern:
                if p in replacements:
                    newkeys.extend(replacements[p])
                else:
                    newkeys.append(p)

            # add our transformed keys to keys
            keys.extend(newkeys)

            # move cursor pos to end corner of built area
            cursorpos = endpos

        return keys

    def move(self, start, end):
        keys = []
        allow_backtrack = True

        # while there are moves left to make..
        while (start != end):
            # get the compass direction from start to end,
            # with nw/ne/sw/se taking priority over n/s/e/w
            direction = get_direction_from_to(start, end)

            # Get x and y component of distance between start and end
            dx = abs(start.x - end.x)
            dy = abs(start.y - end.y)

            if dx == 0:
                steps = dy # moving on y axis only
            elif dy == 0:
                steps = dx # moving on x axis only
            else:
                # determine max diagonal steps we can take
                # in this direction without going too far
                steps = min([dx, dy])

            keycode = [KEY_LIST[direction.compass]]
            move = direction.delta()
            # print "%s dir, %s to %s, dx %d dy %d steps %d" % (keycode, start, end, dx, dy, steps)
            if steps < 8 or not allow_backtrack:
                # render keystrokes
                keys.extend(keycode * steps)
                start = start + (move * steps)
                allow_backtrack = True
            else:
                jumps = (steps // 10)
                leftover = steps % 10
                jumpmove = move * 10

                # backtracking optimization
                if leftover >= 8:
                    # test if jumping an extra 10-unit step
                    # would put us outside of the bounds of
                    # the blueprint (want to prevent)
                    test = start + (jumpmove * (jumps + 1))

                    if self.grid.is_out_of_bounds(test):
                        # just move there normally
                        keys.extend(keycode * leftover)
                        start = start + (move * steps)
                        # don't try to do this next iteration
                        allow_backtrack = False
                    else:
                        # permit overjump/backtracking movement
                        jumps +=1
                        start = start + (jumpmove * jumps)
                        allow_backtrack = True
                else:
                    # move the last few cells needed when using
                    # jumpmoves to land on the right spot
                    keys.extend(keycode * leftover)
                    start = start + (move * steps)
                    allow_backtrack = True

                # shift optimization
                keys.append("{Shift down}")
                keys.extend(keycode * jumps)
                keys.append("{Shift up}")

        return keys

