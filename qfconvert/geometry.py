"""
Various forms of geometry and geometry related classes used throughout
qfconvert.
"""

from math import sqrt


class Point:
    """
    Simple representation of an (x, y) Cartesian coordinate.

    In QF, the coordinate plane has an origin of (0, 0) at the top-left or
    northwest corner. All coordinates are positive integers. This
    arrangement corresponds with how cells are addressed in DF's user
    interface.
    """
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
        if isinstance(other, Point): # multiply two Points' coords together
            return Point(self.x * other.x, self.y * other.y)
        elif isinstance(other, int): # multiply self coords by other int
            return Point(self.x * other, self.y * other)
        else:
            raise

    def __str__(self):
        return "(%d, %d)" % (self.x, self.y)

    def get_coord_of_axis(self, direction):
        """
        Treating the line traced along direction as an axis,
        return that axis's coordinate from our coords.
        """
        return self.x if direction.compass in ('n', 's') else self.y

    def get_coord_crossing_axis(self, direction):
        """
        Treating the line traced along direction as an axis,
        return the perpendicular axis's coordinate from our coords.
        """
        return self.y if direction.compass in ('n', 's') else self.x

    def distance_to(self, other):
        """Returns straight-line distance between self and other."""
        return sqrt( (other.x - self.x)**2 + (other.y - self.y)**2  )

    def midpoint(self, other):
        """
        Returns integer midpoint of straight line connecting self and
        other (rounds down to work well with how DF does it).
        """
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
    """Direction represents one of the 8 compass directions: n, ne, .."""

    def __init__(self, compass_dir):
        self.compass = compass_dir

    def __str__(self):
        return "{compass:%s}" % self.compass

    def index(self):
        """
        Return index of given direction from DIRECTIONS.
        Kinda hacky but Python dicts are unordered :(
        """
        return DIRECTIONS[self.compass]['index']

    def axis(self):
        """
        Returns 'x' for e|w directions and 'y' for n|s directions.
        Returns 'xy' for other directions.
        """
        if self.compass in ('n', 's'):
            return 'y'
        if self.compass in ('e', 'w'):
            return 'x'
        return 'xy'

    def delta(self):
        """
        Get the x/y coordinate offset needed to move one unit on the
        cartesian grid towards self.compass.
        Returns offset as a Point.
        """
        return DIRECTIONS[self.compass]['delta']

    def opposite(self):
        """Returns the direction opposite this one (e -> w; ne -> sw)"""
        return self.clockwise(4)

    def right_turn(self):
        """Returns the direction 90 degrees right of this one (n -> e)"""
        return self.clockwise(2)

    def left_turn(self):
        """Returns the direction 90 degrees left of this one (n -> w)"""
        return self.clockwise(6)

    def clockwise(self, steps):
        """
        Returns the direction which is `steps` away from self in in a
        clockwise order around the compass rose.
        """
        return Direction(DIRECTIONS_ORDERED[(self.index() + steps) % 8])

    @staticmethod
    def get_direction(frompos, topos):
        """
        Returns the compass direction point from frompos to topos with
        nw/ne/sw/se taking priority over n/s/e/w
        """
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
    """Represents a rectangular area defined on the cartesian grid."""

    def __init__(self, corner, opposite_corner):
        # Get lists of the 2 x coords and 2 y coords
        xs = [corner.x, opposite_corner.x]
        ys = [corner.y, opposite_corner.y]

        # Sort coords so the northernmost and westernmost coordinate is first
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
        """Returns width of area, min 1."""
        return self.corners[1].x - self.corners[0].x + 1

    def height(self):
        """Returns height of area, min 1."""
        return self.corners[2].y - self.corners[0].y + 1

    def size(self):
        """Returns size (geometric area) of area, min 1."""
        return self.width() * self.height()

    def diagonal_length(self):
        """Returns corner-to-opposite-corner distance of area."""
        return sqrt(self.width()**2 + self.height()**2)

    def opposite_corner(self, corner):
        """Returns the opposite corner of area given param `corner`."""
        for i in xrange(0, 4):
            if corner == self.corners[i]:
                return self.corners[(i + 2) % 4]
        return None


class CommandCell:
    """CommandCell is the container used for cell info in Grid."""

    def __init__(self, command, label = None):
        self.command = command
        self.area = None
        self.plottable = True if command else False
        self.label = label or ''


class GridLayer:
    """GridLayer is the container used for a Grid z-layer and its info."""
    def __init__(self, onexit, grid=None, plots=None, start=None):
        self.onexit = onexit
        self.grid = grid or Grid()
        self.plots = plots or []
        self.start = start or Point(0, 0)

    @staticmethod
    def zoffset(layers):
        """Returns the sum z-level offset of layers' onexit values"""
        return sum(
            sum(1 if x == '>' else -1 if x == '<' else 0
                for x in layer.onexit
                )
            for layer in layers
            )


class Grid:
    """
    Represents a cartesian grid of cells corresponding to positions in
    a Dwarf Fortress map or QF blueprint.
    """

    def __init__(self, rows=None):
        """If rows is given, expects a 2d list of strings."""

        if rows is None:
            self.rows = []
            self.width, self.height = 0, 0
        else:
            self.rows = [[CommandCell(c) for c in row] for row in rows]
            self.width = len(rows[0])
            self.height = len(rows)

    def __str__(self):
        return Grid.str_commands(self.rows, '')

    def get_cell(self, pos):
        """Returns the CommandCell at pos or an empty one if out of bounds."""
        if self.is_out_of_bounds(pos):
            return CommandCell('', self)
        else:
            return self.rows[pos.y][pos.x]

    def get_command(self, pos):
        """Returns .command at pos or '' if out of bounds/empty."""
        cell = self.get_cell(pos)
        if cell is None:
            return ''
        else:
            return cell.command

    def is_plottable(self, pos):
        """Returns .plottable at pos or None if out of bounds/empty."""
        cell = self.get_cell(pos)
        return False if cell is None else cell.plottable

    def is_out_of_bounds(self, point):
        """Returns True if point is outside the bounds of grid, else False."""
        if point.x < 0 or \
            point.y < 0 or \
            point.x >= self.width or \
            point.y >= self.height:
            return True
        else:
            return False

    def get_row(self, y):
        """Returns the row with index y from the grid."""
        return self.rows[y]

    def get_col(self, x):
        """Returns the column with index x from the grid."""
        return [row[x] for row in self.rows]

    def get_axis(self, index, direction):
        """
        Returns the row with specified index for e/w direction.
        Returns the column with specified index for n/s direction.
        """

        if direction.axis() == 'y':
            return self.get_col(index)
        else:
            return self.get_row(index)

    def get_length_of_axis(self, direction):
        """
        Returns the length of the grid edge which is parallel to the
        axis formed by tracing along direction.
        """
        return self.height if direction.axis() == 'y' else self.width

    def set_area_cells(self, area, plottable=None, label=None, command=None):
        """
        Set plottable, label and/or command values for all cells that are
        within the bounds of given area.
        """
        for x in range(area.corners[0].x, area.corners[1].x + 1): # NW->NE
            for y in range(area.corners[0].y, area.corners[3].y + 1): # NW->SW
                cell = self.get_cell(Point(x, y))
                if plottable is not None:
                    cell.plottable = plottable
                if label is not None:
                    cell.label = label
                if command is not None:
                    cell.command = command
        return

    def set_entire_grid_plottable(self, plottable):
        """Set the plottable flag for all cells in the grid."""
        for x in range(0, self.width):
            for y in range(0, self.height):
                self.get_cell(Point(x, y)).plottable = plottable
        return

    def is_area_plottable(self, area, any_plottable):
        """
        Test the given area against the grid cells to see if it is
        plottable. any_plottable determines the boolean behavior:
            if any_plottable:
                returns True if *any* cell is plottable in area
            else:
                returns True only if *every* cell is plottable in area
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

        """
        The below code is commented out after determining it makes essentially
        no difference to final keystroke count while hurting performance
        a bit. It is preserved here for a conceptual understanding of the
        intent behind is_corner().

        if command == '':
            return False # empty cell; not a part of any area

        pridirs = (Direction(d) for d in ('n', 's', 'e', 'w'))
        secdirs = (Direction(d) for d in ('ne', 'nw', 'se', 'sw'))

        primatches = sum(
            c.plottable and command == c.command
            for c in (self.get_cell(pos + d.delta()) for d in pridirs)
            )

        secmatches = sum(
            c.plottable and command == c.command
            for c in (self.get_cell(pos + d.delta()) for d in secdirs)
            )

        if primatches == 0:
            # cell can't extend from any of nsew so it's an independent
            # 1 x 1 area and thus constitutes a 'corner' cell
            return True
        elif primatches == 4 and secmatches == 0:
             # at intersection, will necessarily be a part of some other
             # rectangle
             return False
        elif primatches == 4 and secmatches == 4:
            # interior point, will necessarily be a part of some other
            # rectangle
            return False
        """

        # See if this cell can be extended along either axis in both
        # directions. If so we assume this will be a non-corner cell
        # of a larger area.
        dirs = (Direction(d) for d in ['n', 'e'])
        for d in dirs:
            corner = self.get_cell(pos + d.delta())
            opp = self.get_cell(pos + d.opposite().delta())
            if command == corner.command and corner.plottable \
                and command == opp.command and opp.plottable:
                return False

        # it's not an intersection, interior point, edge, or empty cell, so
        # it must be a corner
        return True

    def count_contiguous_cells(self, pos, direction):
        """
        Starting from pos, counts the number of cells whose commands match
        pos's cell command.
        Returns count of contiguous cells.
        """

        command = self.get_cell(pos).command
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
        count = 0
        for cell in axis:
            if cell.plottable and cell.command == command:
                count += 1
            else:
                break

        return count

    @staticmethod
    def str_plottable(grid):
        """Returns grid's plottable flags as a string for display."""
        rowstrings = [
            ''.join(['.' if c.plottable else 'x' for c in row])
            + '|' for row in grid.rows
            ]
        return '\n'.join(rowstrings)

    @staticmethod
    def str_area_corners(grid):
        """Returns grid's area corner markers as a string for display."""
        rowstrings = [
            ''.join(['x' if c.area else '.' for c in row])
            + '|' for row in grid.rows
            ]
        return '\n'.join(rowstrings)

    @staticmethod
    def str_area_labels(grid):
        """Returns grid's area labels as a string for display."""
        rowstrings = [
            ''.join(['.' if c.label == '' else c.label for c in row])
            + '|' for row in grid.rows]
        return '\n'.join(rowstrings)

    @staticmethod
    def str_commands(rows, colsep = '', annotate = False):
        """
        Returns grid's commands as a string for display.
            colsep: if provided, will be placed between cells on each row
            annotate: if True, simple numbering 'rulers' will be added 
        """
        rowstrings = []
        print annotate
        if annotate:
            # draw numbering ruler along the top
            width = len(rows[0])
            rowstrings += ['  ' + ('1234567890' * (1 + width // 10))[0:width]]
            edgebar = [' +' + ('-' * width) + '+']
            rowstrings += edgebar
                

        rowstrings += [
            colsep.join(
                ['' if not annotate else str(int(str(n + 1)[-1]) % 10) + '|'] +
                ['.' if c.command == '' else c.command[0] for c in row]) + '|' 
            for n, row in enumerate(rows)
        ]

        if annotate:
            rowstrings += edgebar

        return '\n'.join(rowstrings)

