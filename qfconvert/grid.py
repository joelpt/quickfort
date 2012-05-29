"""Main storage classes for blueprint data used throughout qfconvert."""

import numpy

from geometry import Direction, add_points, get_coord_crossing_axis, get_coord_along_axis
from operator import itemgetter


class CommandCell:
    """CommandCell is the container used for cell info in Grid."""

    def __init__(self, command, label=None):
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
        self.start = start or (0, 0)

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
            self.rows = numpy.array([[CommandCell(c) for c in row] for row in rows])
            self.width = len(rows[0])
            self.height = len(rows)

    def __str__(self):
        return Grid.str_commands(self.rows, '')

    def get_cell(self, x, y):
        """Returns the CommandCell from the Grid in row x, col y."""
        return self.rows[y, x]

    def is_out_of_bounds(self, x, y):
        """Returns True if (x, y) is outside the bounds of grid, else False."""
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return True
        else:
            return False

    def get_row(self, y):
        """Returns the row with index y from the grid."""
        return self.rows[y]

    def get_col(self, x):
        """Returns the column with index x from the grid."""
        return self.rows[:, x]

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

    def expand_dimensions(self, width, height):
        """
        Expands the maximum dimensions of the grid to width x height.
        New cells are added to the right and bottom as needed.
        Contraction is not supported.
        """

        # add empty rows to bottom if required
        if height > self.height:
            self.rows = numpy.vstack((self.rows, [
                [CommandCell('') for x in range(self.width)]
                for y in range(height - self.height)
            ]))
            self.height = height

        # add empty columns to right if required
        if width > self.width:
            newcells = [[CommandCell('') for x in range(width - self.width)]
                for y in range(self.height)
            ]
            self.rows = numpy.hstack((self.rows, newcells))
            self.width = width

        return

    def set_area_cells(self, area, plottable=None, label=None, command=None):
        """
        Set plottable, label and/or command values for all cells that are
        within the bounds of given area.
        """
        for x in range(area.corners[0][0], area.corners[1][0] + 1):  # NW->NE
            for y in range(area.corners[0][1], area.corners[3][1] + 1):  # NW->SW
                cell = self.get_cell(x, y)
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
                self.get_cell(x, y).plottable = plottable
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
        for x in range(area.corners[0][0], area.corners[1][0] + 1):  # NW->NE
            for y in range(area.corners[0][1], area.corners[3][1] + 1):  # NW->SW
                if any_plottable:
                    if self.get_cell(x, y).plottable:
                        return True
                else:
                    if not self.get_cell(x, y).plottable:
                        return False

        if any_plottable:
            return False
        else:
            return True

    def is_corner(self, x, y):
        """
        Returns True if (x, y)'s cell *could* be the corner of a larger
        rectangle. This is just a quick heuristic test and is definitely
        not fully accurate. A more comprehensive test could be done here,
        which would be likely to slow things down but produce a better
        (fewer-keystroke) final result by Quickfort (in fact, this test
        used to be quite accurate but also quite slow).
        """
        command = self.get_cell(x, y).command
        if x > 0:
            test = self.get_cell(x - 1, y)
            if test.plottable and test.command == command:
                return False

        if y > 0:
            test = self.get_cell(x, y - 1)
            if test.plottable and test.command == command:
                return False

        return True

    def count_contiguous_cells(self, x, y, direction):
        """
        Starting from (x, y), counts the number of cells whose commands match
        (x, y)'s cell command.
        Returns count of contiguous cells.
        """

        command = self.get_cell(x, y).command
        point = (x, y)
        start = get_coord_crossing_axis(point, direction)

        # determine sign of direction to move in for testing
        step = get_coord_crossing_axis(direction.delta(), direction)

        # Get the row|col (determined by direction) which pos is on
        axis = self.get_axis(get_coord_along_axis(point, direction), direction)

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
    def str_csv(grid):
        """Returns grid's command cells in csv format."""
        rowstrings = [
            ','.join([c.command for c in row] + ['#'])
            for row in grid.rows]
        return '\n'.join(rowstrings)

    @staticmethod
    def str_commands(rows, colsep='', annotate=False):
        """
        Returns grid's commands as a pretty formatted table for display.
            colsep: if provided, will be placed between cells on each row
            annotate: if True, simple numbering 'rulers' will be added
        """
        rowstrings = []

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
