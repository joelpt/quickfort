"""Handles discovery of areas to be plotted by someone else."""

from geometry import Point, Direction, Area, Grid
import util
import re


class AreaPlotter:
    """Handles discovery of areas to be plotted by someone else."""

    def __init__(self, grid, buildconfig, debug):
        self.grid = grid
        self.debug = debug
        self.buildconfig = buildconfig
        self.label = '0'

        # init this for reuse later
        self.dir_pairs = []
        for d in ('e', 's', 'w', 'n'):
            direction = Direction(d)
            self.dir_pairs.append([direction, direction.right_turn()])
            self.dir_pairs.append([direction, direction.left_turn()])

    def expand_fixed_size_areas(self):
        """
        Expand cells like d(20x20) to their corresponding areas,
        and mark those areas as plotted.
        """
        if self.debug:
            print ">>>> BEGIN AREA EXPANSION"

        label = self.label
        for y, row in enumerate(self.grid.rows):
            for x, cell in enumerate(row):
                # act on d(5x5) format cells which haven't been plotted over
                m = re.match(r'(.+)\((\d+)x(\d+)\)', cell.command)
                if cell.plottable and m:
                    command = m.group(1)
                    width, height = (int(c) for c in m.group(2, 3))

                    area = Area(Point(x, y),
                        Point(x + width - 1, y + height - 1))

                    # mark this area as plotted
                    self.grid.set_area_cells(area, False, label, command)
                    label = next_label(label)

                    # set each corner's area variable
                    for corner in area.corners:
                        cornercell = self.grid.get_cell(corner)
                        cornercell.command = command
                        cornercell.area = area

        if self.debug:
            print Grid.str_area_labels(self.grid) + '\n'
            print "<<<< END AREA EXPANSION"
        self.label = label
        return

    def discover_areas(self):
        """
        Repeatedly plot the largest contiguous areas possible until
        there are no more areas left to plot.
        Returns True when we plotted at least one area.
        """

        if self.debug:
            print ">>>> BEGIN AREA DISCOVERY"

        testarea = Area(
            Point(0,0),
            Point(self.grid.width-1, self.grid.height-1)
            )

        while True:
            if self.debug:
                print Grid.str_area_labels(self.grid) + '\n'
                print '#### Marking largest plottable areas starting ' + \
                    'with label %s' % self.label

            self.label = self.mark_largest_plottable_areas(self.label)

            if not self.grid.is_area_plottable(testarea, True):
                if self.debug:
                    print Grid.str_area_labels(self.grid) + '\n'
                    print "#### Grid is completely plotted"
                    print "<<<< END AREA DISCOVERY"
                return

        raise Exception, "Unable to plot all areas for unknown reason"

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
                    self.grid.get_cell(corner).area = area

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
                pos = Point(xpos, ypos)
                cell = self.grid.get_cell(pos)
                if cell.plottable and cell.command and \
                    self.grid.is_corner(pos):
                    areas.append(self.find_largest_area_from(pos))

        areas = util.uniquify(areas,
            lambda area: ''.join([str(c) for c in area.corners]))

        return areas


    def find_largest_area_from(self, pos):
        """
        Find the largest area that can be drawn with pos as one of its corners.
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

        bestarea = Area(pos, pos)

        # find the biggest area(s) formable from each dir_pair quad
        for dirs in self.dir_pairs:
            area = self.find_largest_area_in_quad(
                pos, dirs[0], dirs[1], bestarea)
            if area is not None:
                bestarea = area

        return bestarea

    def find_largest_area_in_quad(self, pos, dir1, dir2, bestarea):
        """
        Given the quad starting at pos and formed by dir1 and dir2
        (treated as rays with pos as origin), we find the max
        contiguous-cell distance along dir1, then for each position
        along dir1, we find the max contiguous-cell distance along
        dir2. This allows us to find the largest contiguous area
        constructable by travelling down dir1, then at a right angle
        along dir2 for each position.

        Returns the largest area found.
        """

        command = self.grid.get_cell(pos).command

        # Get the min/max size that this area may be, based on the command
        sizebounds = self.buildconfig.get('sizebounds', command) \
            or (1, 1000, 1, 1000) # default sizebounds are very large

        # Get the max width of this area on the axis defined by
        # pos and dir1 direction, and max width from
        # the dir2.
        # width and height are conceptually aligned to an
        # east(dir1) x south(dir2) quad below.
        maxwidth = self.grid.count_contiguous_cells(pos, dir1)
        maxheight = self.grid.count_contiguous_cells(pos, dir2)

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
            return None # couldn't be larger than the best one yet found

        if maxheight == 1 and maxwidth == 1:
            # 1x1 area, just return it
            return Area(pos, pos)

        # (width x 1) sized area
        bestarea = Area( pos, pos + (dir1.delta() * (maxwidth - 1)) )

        for ydelta in range(1, maxheight):
            check_point = pos + (dir2.delta() * ydelta)

            height = ydelta + 1
            width = self.grid.count_contiguous_cells(check_point, dir1)

            if width > maxwidth:
                # this row can't be wider than previous rows
                width = maxwidth
            elif width < maxwidth:
                # successive rows can't be wider than this row
                maxwidth = width

            if width * height > bestarea.size():
                bestarea = Area(
                    pos, check_point + ( dir1.delta() * (width - 1)) )
            else:
                continue

        return bestarea


def next_label(label):
    """
    Returns the next label char by cycling through ASCII chars
    '0' through '}'.
    """
    return chr( ((ord(label) - 48 + 1) % 78) + 48 )
