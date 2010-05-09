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
        'designate': 'moveto cmd + setsize +'.split(),
        'allowlarge': [],
        'submenukeys': '',
        'minsize': 0,
        'maxsize': 0,
        'custom': {},
        'setsize': lambda keystroker, start, end: keystroker.setsize_standard(start, end)
         },
    'b': { # build
        'init': '^',
        'designate': 'menu cmd moveto setsize + % ++ % exitmenu'.split(),
        'allowlarge': ['Cw', 'CF', 'Cr', 'o'],
        'submenukeys': 'iweCTM',
        'minsize': 4,
        'maxsize': 10,
        'custom': {
            'p':    'cmd moveto setsize +'.split(), # farm plot
            'wf':   'cmd moveto + % + % ++ %'.split(), # metalsmith forge
            'wv':   'cmd moveto + % + % ++ %'.split(), # magma forge
            'D':    'cmd moveto + % + % ++ %'.split(), # trade depot
            'Ms':   'cmd moveto + + + + %'.split()
            },
        'setsize': lambda keystroker, start, end: keystroker.setsize_build(start, end)
        },
    'p': { # place (stockpiles)
        'init': '',
        'designate': 'moveto cmd + setsize +'.split(),
        'allowlarge': [],
        'submenukeys': '',
        'minsize': 0,
        'maxsize': 0,
        'custom': {},
        'setsize': lambda keystroker, start, end: keystroker.setsize_standard(start, end)
        },
    'q': { # query (set building/task prefs)
        'init': '',
        'designate': 'moveto cmd + setsize +'.split(),
        'allowlarge': [],
        'submenukeys': '',
        'minsize': 0,
        'maxsize': 0,
        'custom': {},
        'setsize': lambda keystroker, start, end: keystroker.setsize_standard(start, end)
        }
}


class Keystroker:

    def __init__(self, grid, build_type):
        self.grid = grid
        self.build_type = build_type
        self.current_menu = None

    def plot(self, plots):
        keys = []
        cursor = None

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
                cmdedit = re.sub(r'\{', '|{', command)
                cmdedit = re.sub(r'\}', '}|', cmdedit)
                cmdedit = re.sub(r'\!', '|!|', cmdedit)
                cmdkeys = re.split(r'\|', cmdedit)
                replacements['cmd'] = cmdkeys
                last_command = command
            else:
                replacements['cmd'] = ''

            if cursor is not None:
                replacements['moveto'] = self.move(cursor, pos)
            else:
                replacements['moveto'] = []

            setsize, newpos = BUILD_TYPE_CFG['d']['setsize'](self, pos, endpos)
            replacements['setsize'] = setsize

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
            cursor = newpos

        return keys

    def move(self, start, end):
        keys = []
        allow_backtrack = True

        # while there are moves left to make..
        while (start != end):
            direction = Direction.get_direction(start, end)

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
                # this needs to be configured somewhere based
                # on the output-mode (macros vs ahkeys)
                # for ahkeys output should probably look like
                # +6 +6 +6
                # rather than
                # +{6 3}
                # only because the former is easier to
                # express in a template form easily modifiable
                # by an end user
                # might be best to use this template style:
                    # jump_begin: '{Shift down}'
                    # jump_step: '<key>'
                    # jump_end: '{Shift up}'
                if jumps > 0:
                    keys.append("{Shift down}")
                    keys.extend(keycode * jumps)
                    keys.append("{Shift up}")
                #keys.append("+{%s %d}" % (keycode[0], jumps))

        return keys

    def setsize_standard(self, start, end):
        """
        Standard sizing mechanism for dig, place, query buildtypes.
        Returns keys, newpos:
            keys needed to make the currently-designating area the correct size
            newpos is where the cursor ends up after sizing the area
        """
        return self.move(start, end), end

    def setsize_build(self, start, end):
        """
        Standard sizing mechanism for the build buildtype.
        Returns keys, newpos:
            keys needed to make the currently-designating area the correct size
            newpos is where the cursor ends up after sizing the area
        """
        # move cursor halfway to end from start

        # TODO will not work
        midpoint = start + ((end - start) // 2)
        keys = ks.move(start, midpoint)

        # resize construction
        area = Area(start, end)
        keys += KEY_LIST['widen'] * (area.width() - 1)
        keys += KEY_LIST['heighten'] * (area.height() - 1)
        return keys
