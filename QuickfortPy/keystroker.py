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
        'designate': 'moveto,cmd,+,setsize,+',
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
        cursorpos = Point(0, 0)

        replacebase = {
            '\+': '{Enter}%',
            '\+\+': '+{Enter}%wait%',
            '\%': '%wait%'
            }

        last_command = ''

        # construct the list of keystrokes required to move to each
        # successive area and build it
        for pos in plots:
            cell = grid.get_cell(pos)
            command = cell.command
            endpos = cell.area.opposite_corner(pos)

            # build replacements dict
            replacements = replacebase.copy()

            if command != last_command:
                replacements['cmd'] = command
                last_command = command
            else:
                replacements['cmd'] = ''

            replacements['moveto'] = ','.join(self.move(cursorpos, pos))
            replacements['setsize'] = ','.join(self.move(pos, endpos))
            pattern = BUILD_TYPE_CFG['d']['designate']

            # apply each replacement to our designation pattern
            for k, v in replacements.items():
                pattern = re.sub(k, v, pattern)

            # add our transformed keys to keys
            keys.extend([key for key in pattern.split(',') if key != ''])

            # move cursor pos to end corner of built area
            cursorpos = endpos

        return keys

    def move(self, start, end):
        keys = []

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

            if steps < 7:
                # render keystrokes
                keys.extend(keycode * steps)
                start += direction.delta().magnify(steps)
            else:
                jumps = (steps // 10)

                # backtracking optimization
                if steps % 10 >= 7:
                    jumps += 1

                testpos = start + direction.delta().magnify(jumps * 10)

                if not self.grid.is_out_of_bounds(testpos):
                    # shift optimization
                    keys.extend(
                        "{Shift down}", keycode * jumps, "{Shift up}")


        return keys

