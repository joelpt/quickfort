from grid_geometry import *

class Keystroker:

    keylist = {
        'n': 'n', 'ne': 'ne', 'e': 'e', 'se': 'se', 's': 's', 'sw': 'sw', 'w': 'w', 'nw': 'nw'
    }

    def __init__(self, build_type):
        self.build_type = build_type

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
            keys.extend([self.keylist[direction.compass]] * steps)

            # reduce remaining movement required by
            # the distance we just moved (move start closer to end)
            # eventually putting start at the same position as end
            start += direction.delta().magnify(steps)

        return keys

