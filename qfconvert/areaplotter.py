"""Handles discovery of areas to be plotted by someone else."""

from geometry import Point, Direction, Area
import util

class AreaPlotter:
    """Handles discovery of areas to be plotted by someone else."""

    def __init__(self, grid, buildconfig, debug):
        self.grid = grid
        self.debug = debug
        self.buildconfig = buildconfig

    def discover_areas(self):
        """
        Repeatedly plot the largest areas possible until
        there are no more areas left to plot. Returns
        True when we plotted at least one area.
        """
        label = '0'
        plotted_something = False

        if self.debug:
            print ">>>> BEGIN AREA DISCOVERY"

        while True:
            if self.debug:
                print self.grid.str_area_labels() + '\n'
                print '#### Marking largest plottable areas starting ' + \
                    'with label %s' % label

            new_label = self.mark_largest_plottable_areas(label)

            if label != new_label:
                # 1+ areas marked this pass
                plotted_something = True
                label = new_label

            testarea = Area(
                Point(0,0),
                Point(self.grid.width-1, self.grid.height-1)
                )

            if not self.grid.is_area_plottable(testarea, True):
                if self.debug:
                    print self.grid.str_area_labels() + '\n'
                    print "#### Grid is completely plotted"
                return plotted_something

        if self.debug:
            print "<<<< END AREA DISCOVERY"

        # should throw an error here, we should always stop before
        # this because of plottability test above
        return plotted_something

    def mark_largest_plottable_areas(self, initial_label):
        """
        Find the largest plottable (available) areas in the grid
        and sort them by size descending
        """
        areas = self.find_largest_areas()

        areas.sort(cmp=lambda a, b: cmp(a.size(), b.size()), reverse=True)

        label = initial_label

        # Try to plot each area starting with the largest. If an area overlaps
        # a previously placed area, do not place it.
        for area in areas:
            # not overlapping any already-plotted area?
            if self.grid.is_area_plottable(area):

                # mark this area as unavailable for subsequent plotting
                self.grid.set_area_plottable(area, False)
                self.grid.set_area_label(area, label)

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
        """
        areas = []

        for ypos in range(0, self.grid.height):
            for xpos in range(0, self.grid.width):
                pos = Point(xpos, ypos)
                if self.grid.get_cell(pos).plottable \
                    and len(self.grid.get_command(pos)) > 0 \
                    and self.grid.is_corner(pos):
                    areas.append(self.find_largest_area_from(pos))

        areas = util.uniquify(
            areas,
            lambda area: ''.join([str(c) for c in area.corners])
            )
        return areas

    def find_largest_area_from(self, pos):
        """
        Build a list of direction pairs we'll want to test.
        We need to check each compass direction paired with both
        90-degree rotations from each compass direction:
        NE, NW, EN, ES, ...

        These represent the 4 quadrants created by partitioning the
        grid through the 2 axes which pos sits on, and
        the inversions of each quad; SE & ES is one such pair.
        Each quad includes the origin (0, 0); similarly, each
        quad overlaps on two edges with adjacent quads.
        """
        dir_pairs = []
        for dir_ in ('e', 's', 'w', 'n'):
            direction = Direction(dir_)
            dir_pairs.append([direction, direction.right_turn()])
            dir_pairs.append([direction, direction.left_turn()])

        bestarea = Area(pos, pos)

        # find the biggest area(s) formable from each dir_pair quad
        for dirs in dir_pairs:
            area = self.find_largest_area_in_quad(
                pos, dirs[0], dirs[1], bestarea)
            if area is not None:
                bestarea = area

        return bestarea

    def find_largest_area_in_quad(self, pos, primary, secondary, bestarea):
        """
        Given the quad starting at corner pos and extending first
        in primary direction, then in secondary direction: return
        the largest area we can find in the quad.
        """

        command = self.grid.get_cell(pos).command

        # Get the min/max size that this area may be, based on the command
        sizebounds = self.buildconfig.get('sizebounds', command) \
            or (1, 1000, 1, 1000) # default sizebounds

        # Get the max width of this area on the axis defined by
        # pos and primary direction, and max width from
        # the secondary.
        # width and height are conceptually aligned to an
        # east(primary) x south(secondary) quad below.
        maxwidth = self.grid.count_repeating_cells(pos, primary)
        maxheight = self.grid.count_repeating_cells(pos, secondary)

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
        bestarea = Area(
            pos, pos + primary.delta().magnify(maxwidth - 1) )

        for ydelta in range(1, maxheight):
            check_point = pos + secondary.delta().magnify(ydelta)

            height = ydelta + 1
            width = self.grid.count_repeating_cells(check_point, primary)

            if width > maxwidth:
                # this row can't be wider than previous rows
                width = maxwidth
            elif width < maxwidth:
                # successive rows can't be wider than this row
                maxwidth = width

            if width * height > bestarea.size():
                bestarea = Area(
                    pos, check_point + primary.delta().magnify(width - 1))
            else:
                continue

        return bestarea


def next_label(label):
    """label character cycles through the printable ASCII chars"""
    return chr( ((ord(label) - 48 + 1) % 78) + 48 )
