from itertools import takewhile
from util import *
from math import sqrt

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __cmp__(self, other):
        if self.x == other.x and self.y == other.y:
            return 0
        elif self.x > other.x or self.y > other.y:
            return 1
        else:
            return -1

    def __str__(self):
        return "(%d, %d)" % (self.x, self.y)

    def get_coord_crossing_axis(self, direction):
        return self.y if direction.compass in ('n', 's') else self.x

    def get_coord_of_axis(self, direction):
        return self.x if direction.compass in ('n', 's') else self.y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def magnify(self, magnitude):
        return Point(self.x * magnitude, self.y * magnitude)

    def distance_to(self, other):
        return sqrt( (other.x - self.x)**2 + (other.y - self.y)**2  )

DIRECTIONS = {
    'n':  { 'index': 0, 'delta': Point( 0, -1) },
    'ne': { 'index': 1, 'delta': Point( 1, -1) },
    'e':  { 'index': 2, 'delta': Point( 1,  0) },
    'se': { 'index': 3, 'delta': Point( 1,  1) },
    's':  { 'index': 4, 'delta': Point( 0,  1) },
    'sw': { 'index': 5, 'delta': Point(-1,  1) },
    'w':  { 'index': 6, 'delta': Point(-1,  0) },
    'nw': { 'index': 7, 'delta': Point(-1, -1) }
    }

DIRECTIONS_ORDERED = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']

class Direction:

    def __init__(self, compass_dir):
        self.compass = compass_dir

    def __str__(self):
        return "{compass:%s}" % self.compass

    def index(self):
        return DIRECTIONS[self.compass]['index']

    def axis(self):
        if self.compass in ('n', 's'):
            return 'y'
        if self.compass in ('e', 'w'):
            return 'x'
        return 'xy' # should probably throw an error here

    def delta(self):
        return DIRECTIONS[self.compass]['delta']

    def opposite(self):
        return self.clockwise(4)

    def right_turn(self):
        return self.clockwise(2)

    def left_turn(self):
        return self.clockwise(6)

    def clockwise(self, steps):
        return Direction(DIRECTIONS_ORDERED[(self.index() + steps) % 8])

def get_direction_from_to(start, end):
    # get the compass direction from start to end,
    # with nw/ne/sw/se taking priority over n/s/e/w
    d = ""
    if start.y < end.y:
        d += "s"
    elif start.y > end.y:
        d += "n"

    if start.x < end.x:
        d += "e"
    elif start.x > end.x:
        d += "w"

    if d == "":
        return None
    else:
        return Direction(d)


class Area:

    def __init__(self, corner, opposite_corner):
        # Get lists of the 2 x coords and 2 y coords
        xs = [corner.x, opposite_corner.x]
        ys = [corner.y, opposite_corner.y]

        # Sort the coords lists so the northernmost
        # and westernmost coordinate is first
        xs.sort()
        ys.sort()

        # Ordered clockwise from NW corner:
        # NW, NE, SE, SW
        self.corners = [
            Point(xs[0], ys[0]),
            Point(xs[1], ys[0]),
            Point(xs[1], ys[1]),
            Point(xs[0], ys[1])
        ]


    def __cmp__(self, other):
        return cmp(self.size(), other.size())

    def __str__(self):
        return '[' + ','.join([str(c) for c in self.corners]) + '] size:' + str(self.size())

    def width(self):
        return self.corners[1].x - self.corners[0].x + 1

    def height(self):
        return self.corners[2].y - self.corners[0].y + 1

    def size(self):
        ## print "area size check width: %d height: %d size: %d" % (self.width(), self.height(), self.width() * self.height()) + " " + ' | '.join([str(c) for c in self.corners])
        return self.width() * self.height()

    def diagonal_length(self):
        return sqrt(self.width()**2 + self.height()**2)

    def opposite_corner(self, corner_pos):
        # find this corner
        #print 'look for corner opposite to %s in area %s' % (corner_pos, self)

        for i in xrange(0, 4):
            #print "comparing %s and %s" % (corner_pos, self.corners[i])
            if corner_pos == self.corners[i]:
                #print "found it, returning %s " % self.corners[(i + 2) % 4]
                return self.corners[(i + 2) % 4]
        return None

class CommandCell:

    def __init__(self, command):
        self.command = command
        self.area = None
        self.plottable = True if command not in (None, '') else False
        self.label = ''

class GridLayer:

    def __init__(self, exit_keys, grid=None, plots=None, start_pos=None):
        self.exit_keys = exit_keys
        if grid is None:
            self.grid = Grid()
        else:
            self.grid = grid

        if plots is None:
            self.plots = []
        else:
            self.plots = plots

        if start_pos is None:
            self.start_pos = Point(0, 0)
        else:
            self.start_pos = start_pos

class Grid:

    def __init__(self):
        self.cells = []
        self.width = 0
        self.height = 0

    def __str__(self):
        rowstrings = [','.join([c.command for c in row]) for row in self.cells]
        return '\n'.join(rowstrings)


    def add_cell(self, point, contents):
        """
        This method should be used for adding new cells to the grid.
        Once added to the grid, .get_cell(..) can be used to reference
        and modify it.
        """
        cell = CommandCell(contents)

        if len(contents) == 0:
            cell.label = '.' # visual identification of empty cells

        if point.y + 1 > self.height:
            self.cells.append([]) # new row
            self.height = point.y + 1

        row = self.cells[point.y]

        if point.x + 1 > len(row):
            row.append(cell)
        else:
            print """
                error: add_cell trying to add to the left
                of an existing cell (not supported)
                """
            return

        if point.x + 1 > self.width:
            self.width = point.x + 1

    "Add missing cells to rows which ended prematurely"
    def fixup(self):
        for row in self.cells:
            if len(row) < self.width:
                row.extend(
                    [CommandCell('')] * (self.width - len(row))
                    )
        return

    def get_cell(self, pos):
        if self.is_out_of_bounds(pos):
            return None
        else:
            return self.cells[pos.y][pos.x]

    def get_command(self, pos):
        cell = self.get_cell(pos)
        if cell is None:
            return ''
        else:
            return cell.command

    def is_plottable(self, pos):
        cell = self.get_cell(pos)
        if cell is None:
            return False
        else:
            return cell.plottable

    def is_out_of_bounds(self, point):
        if point.x < 0 or \
            point.y < 0 or \
            point.x >= self.width or \
            point.y >= self.height:
            return True
        return False

    def get_row(self, y):
        return self.cells[y]

    def get_col(self, x):
        return [row[x] for row in self.cells]

    def get_axis(self, index, direction):
        return self.get_col(index) if direction.axis() == 'y' else self.get_row(index)

    def get_length_of_axis(self, direction):
        return self.height if direction.axis() == 'y' else self.width

    def set_area_plottable(self, area, plottable):
        for x in range(area.corners[0].x, area.corners[1].x + 1): # NW to NE corner
            for y in range(area.corners[0].y, area.corners[3].y + 1): # NW to SW corner
                cell = self.get_cell(Point(x, y))
                cell.plottable = plottable
        return

    def set_area_label(self, area, label):
        for x in range(area.corners[0].x, area.corners[1].x + 1): # NW to NE corner
            for y in range(area.corners[0].y, area.corners[3].y + 1): # NW to SW corner
                cell = self.get_cell(Point(x, y))
                cell.label = label
        return

    def set_entire_grid_plottable(self, plottable):
        for x in range(0, self.width):
            for y in range(0, self.height):
                self.get_cell(Point(x, y)).plottable = plottable
        return

    """
    Test the given area against the grid cells to see if it is plottable.
    If any_plottable is False, we return False if any cell is unplottable, True otherwise.
    If any_plottable is True, we return True if any cell is plottable, False otherwise.
    """
    def is_area_plottable(self, area, any_plottable=False):
        # print "is area plottable?: " + str(area)
        for x in range(area.corners[0].x, area.corners[1].x + 1): # NW to NE corner
            for y in range(area.corners[0].y, area.corners[3].y + 1): # NW to SW corner
                pos = Point(x, y)
                # print "point %s plottable=%s assignedarea=%s" % (str(pos), self.get_cell(pos).plottable, str(self.get_cell(pos).area))
                if any_plottable:
                    if self.get_cell(pos).plottable:
                        return True
                else:
                    if not self.get_cell(pos).plottable:
                        return False

        if any_plottable:
            return False
        else:
            return True


    # returns true if start_point's cell forms the corner of a contiguous area,
    # including just a 1x1 area
    def is_corner(self, start_point):
        # print "checking for corner at " + str(start_point)
        cell = self.get_cell(start_point)
        if cell is None:
            # print "no cell at point " + str(start_point)
            return False

        command = cell.command

        if command == '':
            # print "empty cell"
            return False # empty cell; not a part of any area

        dirs = [Direction(d) for d in ['n', 's', 'e', 'w']]

        # if cell can not extend in any of NSEW directions, consider it a corner cell
        matches4 = sum([self.is_plottable(start_point + d.delta()) and command == self.get_command(start_point + d.delta()) for d in dirs])
        # print [command == self.get_command(start_point + d.delta()) for d in dirs]
        if matches4 == 0:
            # print "solo corner"
            return True
        elif matches4 == 4:
            # print "at intersection or interior point"
            return False

        # print "matches4 %d" % matches4

        dirs = [Direction(d) for d in ['n', 'e']]


        # see if this cell is an edge of an area
        for d in dirs:
            # # print 'edge test to %s' % d.compass

            # # print command == self.get_command(start_point + d.delta())
            # # print command == self.get_command(start_point + d.opposite().delta())
            # # print command == self.get_command(start_point + d.right_turn().delta())
            # # print command == self.get_command(start_point + d.left_turn().delta())

            if command == self.get_command(start_point + d.delta()) \
                and self.is_plottable(start_point + d.delta()) \
                and command == self.get_command(start_point + d.opposite().delta()) \
                and self.is_plottable(start_point + d.opposite().delta()):
                #      \
                # and command != self.get_command(start_point + d.right_turn().delta()) \
                # and command != self.get_command(start_point + d.left_turn().delta())
                # print "part of %s edge or interior point" % d.compass
                return False

        # print "is corner"
        return True



        # see if this cell forms a corner for any areas
        for d in dirs:
            if command == self.get_command(start_point + d.delta()) \
                and command == self.get_command(start_point + d.clockwise(1).delta()) \
                and command == self.get_command(start_point + d.clockwise(2).delta()) \
                and  (command != self.get_command(start_point + d.clockwise(3).delta()) \
                    or command != self.get_command(start_point + d.clockwise(4).delta()) \
                    ):
                # print "is corner"
                return True
            elif (command == self.get_command(start_point + d.delta())
                and command != self.get_command(start_point + d.opposite().delta())
                ):
                # print "is corner"
                return True

        # not a corner
        # print "non corner"
        return False

    def count_repeating_cells(self, start_point, direction):
        # # print "counting----------------"
        # # print start_point
        # # print direction
        command = self.get_command(start_point)
        start = start_point.get_coord_crossing_axis(direction)

        # determine sign of direction to move in for testing
        step = direction.delta().get_coord_crossing_axis(direction)

        # Get the row|col (determined by direction) which start_point is on
        axis = self.get_axis(start_point.get_coord_of_axis(direction), direction)

        # get just the segment of the axis we want, ordered in the direction we want
        if step == 1:
            axis = axis[start:self.get_length_of_axis(direction)]
        else:
            axis = axis[start::-1]

        # Count the number of cells whose command matches our starting cell's command,
        # until we encounter one that doesn't. Operates on just those cells in axis
        # which start at start_point and continue to the grid edge in the given direction.
        count = len(list(takewhile(lambda cell: cell.plottable and cell.command == command, axis)))

        # # print "dir %s start %d step %d end %d axislength %d repcount=%d" % (direction.compass, start, step, end, len(axis), count)
        return count

    def str_commands(self, column_separator):
        rowstrings = [column_separator.join(['.' if c.command == '' else c.command[0] for c in row]) + '|' for row in self.cells]
        return '\n'.join(rowstrings)

    def str_plottable(self):
        rowstrings = [''.join(['.' if c.plottable == True else 'x' for c in row])  + '|' for row in self.cells]
        return '\n'.join(rowstrings)

    def str_area_corners(self):
        rowstrings = [''.join(['x' if c.area else '.' for c in row])  + '|' for row in self.cells]
        return '\n'.join(rowstrings)

    def str_area_labels(self):
        rowstrings = [''.join(['.' if c.label == '' else c.label for c in row]) + '|' for row in self.cells]
        return '\n'.join(rowstrings)

