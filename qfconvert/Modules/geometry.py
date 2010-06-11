from itertools import takewhile
from util import *
from math import sqrt

class Point:

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __cmp__(self, other):
        if self.x == other.x and self.y == other.y:
            return 0
        elif self.x > other.x or self.y > other.y:
            return 1
        else:
            return -1

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        elif isinstance(other, int):
            return Point(self.x * other, self.y * other)
        else:
            raise

    def __str__(self):
        return "(%d, %d)" % (self.x, self.y)

    def get_coord_crossing_axis(self, direction):
        return self.y if direction.compass in ('n', 's') else self.x

    def get_coord_of_axis(self, direction):
        return self.x if direction.compass in ('n', 's') else self.y


    def magnify(self, magnitude):
        return Point(self.x * magnitude, self.y * magnitude)

    def distance_to(self, other):
        return sqrt( (other.x - self.x)**2 + (other.y - self.y)**2  )

    def midpoint(self, other):
        return Point(
            self.x + (other.x - self.x + 1) // 2,
            self.y + (other.y - self.y + 1) // 2
            )


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
        return 'xy'

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

    @staticmethod
    def get_direction(frompos, topos):
        # get the compass direction point from frompos to topos
        # with nw/ne/sw/se taking priority over n/s/e/w
        d = ""
        if frompos.y < topos.y:
            d += "s"
        elif frompos.y > topos.y:
            d += "n"

        if frompos.x < topos.x:
            d += "e"
        elif frompos.x > topos.x:
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
        return '[' + ','.join([str(c) for c in self.corners]) + \
            '] size:' + str(self.size())

    def width(self):
        return self.corners[1].x - self.corners[0].x + 1

    def height(self):
        return self.corners[2].y - self.corners[0].y + 1

    def size(self):
        return self.width() * self.height()

    def diagonal_length(self):
        return sqrt(self.width()**2 + self.height()**2)

    def opposite_corner(self, corner):
        for i in xrange(0, 4):
            if corner == self.corners[i]:
                return self.corners[(i + 2) % 4]
        return None


class CommandCell:

    def __init__(self, command, parentgrid):
        self.command = command
        self.area = None
        self.plottable = True if command not in (None, '') else False
        self.label = ''
        # self.parentgrid = parentgrid


class GridLayer:

    def __init__(self, onexit, grid=None, plots=None, start=None):
        self.onexit = onexit
        self.grid = grid or Grid()
        self.plots = plots or []
        self.start = start or Point(0, 0)

    @staticmethod
    def zoffset(layers):
        """determine sum z-level offset of some GridLayers"""
        return sum(
            sum(1 if x == '>' else -1 if x == '<' else 0
                for x in layer.onexit
                )
            for layer in layers
            )


class Grid:

    def __init__(self):
        self.cells = []
        self.width = 0
        self.height = 0

    def __str__(self):
        return self.str_commands()

    def add_cell(self, point, contents):
        """
        This method should be used for adding new cells to the grid.
        Once added to the grid, .get_cell(..) can be used to reference
        and modify it.
        """
        cell = CommandCell(contents, point)

        if len(contents) == 0:
            cell.label = '.' # visual identification of empty cells

        if point.y + 1 > self.height:
            self.cells.append([]) # new row
            self.height = point.y + 1
        row = self.cells[point.y]

        if point.x + 1 > len(row):
            row.append(cell)
        else:
            raise Exception, \
                "Grid.add_cell() can't add to the left of an existing cell"

        if point.x + 1 > self.width:
            self.width = point.x + 1

    def fixup(self):
        """Add missing cells to rows which ended prematurely"""
        for row in self.cells:
            if len(row) < self.width:
                row.extend(
                    [CommandCell('', self)] * (self.width - len(row))
                    )
        return

    def get_cell(self, pos):
        if self.is_out_of_bounds(pos):
            return CommandCell('', self)
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
        return False if cell is None else cell.plottable

    def is_out_of_bounds(self, point):
        if point.x < 0 or \
            point.y < 0 or \
            point.x >= self.width or \
            point.y >= self.height:
            return True
        else:
            return False

    def get_row(self, y):
        return self.cells[y]

    def get_col(self, x):
        return [row[x] for row in self.cells]

    def get_axis(self, index, direction):
        return self.get_col(index) if direction.axis() == 'y' else self.get_row(index)

    def get_length_of_axis(self, direction):
        return self.height if direction.axis() == 'y' else self.width

    def set_area_cells(self, area, plottable=None, label=None, command=None):
        for x in range(area.corners[0].x, area.corners[1].x + 1): # NW->NE
            for y in range(area.corners[0].y, area.corners[3].y + 1): # NW->SW
                cell = self.get_cell(Point(x, y))
                if plottable is not None: cell.plottable = plottable
                if label is not None: cell.label = label
                if command is not None: cell.command = command
        return

    def set_entire_grid_plottable(self, plottable):
        for x in range(0, self.width):
            for y in range(0, self.height):
                self.get_cell(Point(x, y)).plottable = plottable
        return

    def is_area_plottable(self, area, any_plottable=False):
        """
        Test the given area against the grid cells to see if it is
        plottable. If any_plottable is False, we return False if any
        cell is unplottable, True otherwise. If any_plottable is True,
        we return True if any cell is plottable, False otherwise.
        """
        for x in range(area.corners[0].x, area.corners[1].x + 1): # NW->NE
            for y in range(area.corners[0].y, area.corners[3].y + 1): # NW->SW
                pos = Point(x, y)
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


    def is_corner(self, pos):
        """
        Returns True if pos's cell forms the corner of a contiguous area,
        including just a 1x1 area.
        """
        cell = self.get_cell(pos)
        if cell is None:
            return False

        command = cell.command

        if command == '':
            return False # empty cell; not a part of any area

        dirs = (Direction(d) for d in ['n', 's', 'e', 'w'])

        # if cell can not extend in any of NSEW directions, it's a corner cell
        matches4 = sum(
            self.is_plottable(pos + d.delta())
            and command == self.get_command(pos + d.delta())
            for d in dirs
            )
        if matches4 == 0:
            # solo corner
            return True
        elif matches4 == 4:
            # at intersection or interior point
            return False

        # see if this cell is an edge of an area
        dirs = (Direction(d) for d in ['n', 'e'])
        for d in dirs:
            if command == self.get_command(pos + d.delta()) \
                and self.is_plottable(pos + d.delta()) \
                and command == self.get_command(pos + d.opposite().delta()) \
                and self.is_plottable(pos + d.opposite().delta()):
                return False

        # it's not an intersection, interior point, edge, or empty cell, so
        # it must be a corner
        return True

    def count_repeating_cells(self, pos, direction):
        command = self.get_command(pos)
        start = pos.get_coord_crossing_axis(direction)

        # determine sign of direction to move in for testing
        step = direction.delta().get_coord_crossing_axis(direction)

        # Get the row|col (determined by direction) which pos is on
        axis = self.get_axis(pos.get_coord_of_axis(direction), direction)

        # get just the segment of the axis we want, ordered in the dir we want
        if step == 1:
            axis = axis[start:self.get_length_of_axis(direction)]
        else:
            axis = axis[start::-1]

        # Count the number of cells whose command matches our
        # starting cell's command, until we encounter one that
        # doesn't. Operates on just those cells in axis which start
        # at pos and continue to the grid edge in the given
        # direction.
        count = len(
            list(
                takewhile(
                    lambda cell: cell.plottable and cell.command == command,
                    axis
                    )
                )
            )

        return count

    def str_commands(self, colsep = ''):
        return Grid.print_cells(self.cells, colsep)

    def str_plottable(self):
        rowstrings = [
            ''.join(['.' if c.plottable == True else 'x' for c in row])
            + '|' for row in self.cells
            ]
        return '\n'.join(rowstrings)

    def str_area_corners(self):
        rowstrings = [
            ''.join(['x' if c.area else '.' for c in row])
            + '|' for row in self.cells
            ]
        return '\n'.join(rowstrings)

    def str_area_labels(self):
        rowstrings = [
            ''.join(['.' if c.label == '' else c.label for c in row])
            + '|' for row in self.cells]
        return '\n'.join(rowstrings)

    @staticmethod
    def print_cells(cells, colsep = ''):
        rowstrings = [
            colsep.join(
                ['.' if c.command == '' else c.command[0] for c in row]
                )
            + '|' for row in cells
            ]
        return '\n'.join(rowstrings)

    @staticmethod
    def print_layers(grid_layers):
        for layer in grid_layers:
            print (Grid.print_cells(layer) + '\n') + (
                ''.join(layer.onexit) + '\n')
