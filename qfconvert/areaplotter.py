"""Handles discovery of areas to be plotted by someone else."""

from log import log_routine, logmsg, loglines

from geometry import Direction, Area, add_points, scale_point
from grid import Grid
import util
import re

from errors import AreaPlotterError


class AreaPlotter:
    """Handles discovery of largest plottable areas."""

    def __init__(self, grid, buildconfig):
        self.grid = grid
        self.buildconfig = buildconfig
        self.label = '0'

        # init this for reuse later
        self.dir_pairs = []
        for d in ('e', 's', 'w', 'n'):
            direction = Direction(d)
            self.dir_pairs.append([direction, direction.right_turn()])
            self.dir_pairs.append([direction, direction.left_turn()])

        # Trivially replacing the above with the below improves performance by
        # 25%+ while increasing final keystroke count by ~10-45%
        #self.dir_pairs = [ [Direction('s'), Direction('e')] ]

    @log_routine('area', 'AREA EXPANSION')
    def expand_fixed_size_areas(self):
        """
        Expand cell commands of the form 'd(20x20)' to their corresponding
        areas (in this example a 20x20 designation of d's) and mark those
        areas as plotted.
        """
        label = self.label
        for y, row in enumerate(self.grid.rows):
            for x, cell in enumerate(row):
                # act on d(5x5) styles cells which haven't been plotted over
                m = re.match(r'(.+)\((\d+)x(\d+)\)', cell.command)
                if cell.plottable and m:
                    command = m.group(1)
                    width, height = (int(c) for c in m.group(2, 3))

                    area = Area((x, y), (x + width - 1, y + height - 1))

                    # ensure the grid is large enough to accept the expansion
                    self.grid.expand_dimensions(x + width, y + height)

                    # mark this area as plotted
                    self.grid.set_area_cells(area, False, label, command)
                    label = next_label(label)

                    # set each corner's area variable
                    for corner in area.corners:
                        cornercell = self.grid.get_cell(*corner)
                        cornercell.command = command
                        cornercell.area = area
        self.label = label
        loglines('area', lambda: Grid.str_area_labels(self.grid))
        return

    @log_routine('area', 'AREA DISCOVERY')
    def discover_areas(self):
        """
        Repeatedly plot the largest contiguous areas possible until
        there are no more areas left to plot.
        """

        testarea = Area((0, 0), (self.grid.width - 1, self.grid.height - 1))

        while True:
            loglines('area', lambda: Grid.str_area_labels(self.grid))
            logmsg('area', 'Marking largest plottable areas starting ' + \
                'with label %s' % self.label)

            self.label = self.mark_largest_plottable_areas(self.label)

            # if every single cell is non-plottable (already plotted)..
            if not self.grid.is_area_plottable(testarea, True):
                logmsg('area', 'All areas discovered:')
                loglines('area', lambda: Grid.str_area_labels(self.grid))
                return

        raise AreaPlotterError("Unable to plot all areas for unknown reason")

    def mark_largest_plottable_areas(self, label):
        """
        Find the largest plottable (available) areas in the grid
        and sort them by size descending
        """
        areas = self.find_largest_areas()

        areas.sort(key=lambda x: x.size(), reverse=True)

        # Try to plot each area starting with the largest. If an area overlaps
        # a previously placed area, do not place it.
        for area in areas:
            # not overlapping any already-plotted area?
            if self.grid.is_area_plottable(area, False):

                # mark this area as plotted
                self.grid.set_area_cells(area, False, label)
                label = next_label(label)

                # store area in grid cell for each of the area's corners
                for corner in area.corners:
                    self.grid.get_cell(*corner).area = area

        # return our label when we plotted at least 1 new area
        return label

    def find_largest_areas(self):
        """
        Finds the largest areas that can *currently* be built from each
        area-corner-cell in the grid.
        Returns a list of Areas.
        """
        areas = []

        for ypos in range(0, self.grid.height):
            for xpos in range(0, self.grid.width):
                cell = self.grid.get_cell(xpos, ypos)
                # Removing the is_corner() check below reduces final
                # keystroke count by ~3% but makes the routine ~12x slower
                if cell.plottable \
                    and self.grid.is_corner(xpos, ypos):
                    areas.append(self.find_largest_area_from(xpos, ypos))

        areas = util.uniquify(areas,
            lambda area: ''.join([str(c) for c in area.corners]))

        return areas

    def find_largest_area_from(self, x, y):
        """
        Find the largest area that can be drawn with (x, y) as one of its corners.
        Returns the Area found, which will be at least 1x1 in size.
        """

        # To start we build a list of direction pairs we'll want to test.
        # We need to check each compass direction paired with both
        # 90-degree rotations from each compass direction: NE, NW, EN,
        # ES, ...

        # These represent the 4 quadrants created by partitioning the grid
        # through the axes which pos sits on, and the inversions of each quad;
        # SE & ES is one such quad pair. Each quad overlaps at pos;
        # similarly, each quad shares two of its edges with adjacent quads.

        bestarea = Area((x, y), (x, y))

        # find the biggest area(s) formable from each dir_pair quad
        for dirs in self.dir_pairs:
            area = self.find_largest_area_in_quad(
                x, y, dirs[0], dirs[1], bestarea)
            if area is not None:
                bestarea = area

        return bestarea

    def find_largest_area_in_quad(self, x, y, dir1, dir2, bestarea):
        """
        Given the quad starting at (x, y) and formed by dir1 and dir2
        (treated as rays with (x, y) as origin), we find the max
        contiguous-cell distance along dir1, then for each position
        along dir1, we find the max contiguous-cell distance along
        dir2. This allows us to find the largest contiguous area
        constructable by travelling down dir1, then at a right angle
        along dir2 for each position.

        Returns the largest area found.
        """

        command = self.grid.get_cell(x, y).command

        # Get the min/max size that this area may be, based on the command
        sizebounds = self.buildconfig.get('sizebounds', command) \
            or (1, 1000, 1, 1000)  # default sizebounds are very large

        # Get the max width of this area on the axis defined by
        # pos and dir1 direction, and max width from
        # the dir2.
        # width and height are conceptually aligned to an
        # east(dir1) x south(dir2) quad below.
        maxwidth = self.grid.count_contiguous_cells(x, y, dir1)
        maxheight = self.grid.count_contiguous_cells(x, y, dir2)

        if maxwidth < sizebounds[0]:
            # constructions narrower than the minimum width for this
            # command are ineligible to be any larger than 1 wide
            maxwidth = 1
        elif maxwidth > sizebounds[1]:
            # don't let constructions be wider than allowed
            maxwidth = sizebounds[1]

        if maxheight < sizebounds[2]:
            # constructions shorter than the minimum height for this
            # command are ineligible to be any larger than 1 tall
            maxheight = 1
        elif maxheight > sizebounds[3]:
            # don't let constructions be taller than allowed
            maxheight = sizebounds[3]

        if maxwidth * maxheight < bestarea.size():
            return None  # couldn't be larger than the best one yet found

        if maxheight == 1 and maxwidth == 1:
            # 1x1 area, just return it
            return Area((x, y), (x, y))

        # (width x 1) sized area
        bestarea = Area((x, y),
            add_points(
                (x, y),
                scale_point(dir1.delta(), maxwidth - 1)
            )
        )

        for ydelta in range(1, maxheight):
            (xt, yt) = add_points(
                (x, y),
                scale_point(dir2.delta(), ydelta)
            )

            height = ydelta + 1
            width = self.grid.count_contiguous_cells(xt, yt, dir1)

            if width > maxwidth:
                # this row can't be wider than previous rows
                width = maxwidth
            elif width < maxwidth:
                # successive rows can't be wider than this row
                maxwidth = width

            if width * height > bestarea.size():
                bestarea = Area((x, y),
                    add_points(
                        (xt, yt),
                        scale_point(dir1.delta(), width - 1)
                    )
                )
            else:
                continue

        return bestarea


def next_label(label):
    """
    Returns the next label char by cycling through ASCII chars
    '0' through '}'.
    """
    return chr(((ord(label) - 48 + 1) % 78) + 48)
