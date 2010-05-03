from grid_geometry import *

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
    'n': 'n', 'ne': 'ne', 'e': 'e', 'se': 'se', 's': 's', 'sw': 'sw', 'w': 'w', 'nw': 'nw'
}

BUILD_TYPE_CFG = {
    'd': {
        'init': '',
        'designate': '<moveto><submenu><command><commit><setsize><commit>',
        'begin': '!',
        'commit': '!',
        'max_edge_length': 0,
        'setsizefun': lambda self, start, end: self.setsize_dig(start, end)
         },
    'b': {
        'init': '^',
        'designate': '<command><moveto><setsize><commit><commitextra>',
        'commit': '!',
        'max_edge_length': 10,
        'setsizefun': lambda self, start, end: self.setsize_build(start, end)
        }
}

def setsize_dig(self, start, end):
    return ks.move(start, end)

def setsize_build(self, start, end):
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

    def __init__(self, build_type):
        self.build_type = build_type
        self.current_menu = None


    def plot(self, grid, plots):
        keys = ""
        cursor_pos = Point(0, 0)

        # construct the list of keystrokes required to move to each
        # successive area and build it
        for plot_start in plots:
            cell = grid.get_cell(plot_start)
            plot_end = cell.area.opposite_corner(plot_start)

            # move to the start point
            keys += self.move(cursor_pos, plot_start)

            # plot the area
            #keys += ks.begin_designate(cell.command)
            keys += ks.move(cursor_pos, plot_end)
            #keys += ks.end_designate()

            cursor_pos = plot_end

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

            # render keystrokes
            keys.extend([KEY_LIST[direction.compass]] * steps)

            # reduce remaining movement required by
            # the distance we just moved (move start closer to end)
            # eventually putting start at the same position as end
            start += direction.delta().magnify(steps)

        return keys

