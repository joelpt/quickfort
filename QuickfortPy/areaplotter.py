from geometry import *
import util

class AreaPlotter:

    def __init__(self, grid, buildconfig, debug):
        self.grid = grid
        self.debug = debug
        self.buildconfig = buildconfig

    def mark_all_plottable_areas(self):
        """
        Repeatedly plot the largest areas possible until
        there are no more areas left to plot. Returns
        the plotted grid.
        """
        label = '0'
        plotted_something = False

        if self.debug: print ">>>> BEGIN AREA DISCOVERY"

        while True:
            if self.debug:
                print self.grid.str_area_labels() + '\n'
                print '#### Marking largest plottable areas starting with label %s' % label

            new_label = self.mark_largest_plottable_areas(label)

            if label != new_label:
                # 1+ areas marked this pass
                plotted_something = True
                label = new_label

            if not self.grid.is_area_plottable(Area(Point(0,0), Point(self.grid.width-1, self.grid.height-1)), True):
                if self.debug:
                    print self.grid.str_area_labels() + '\n'
                    print "#### Grid is completely plotted"
                return plotted_something

        if self.debug: print "<<<< END AREA DISCOVERY"

        # should throw an error here, we should always stop before this because of plottability test above
        return plotted_something

    def mark_largest_plottable_areas(self, initial_label):
        # Find the largest plottable (available) areas in the grid and sort them by
        # size descending
        areas = self.find_largest_areas()

        areas.sort(cmp=lambda a, b: cmp(a.size(), b.size()), reverse=True)

        label = initial_label

        # Try to plot each area starting with the largest. If an area overlaps
        # a previously placed area, do not place it.
        for area in areas:
            # not overlapping any already-plotted area?
            if self.grid.is_area_plottable(area):
                plotted_something = True

                # mark this area as unavailable for subsequent plotting
                self.grid.set_area_plottable(area, False)
                self.grid.set_area_label(area, label)

                label = chr( ((ord(label) - 48 + 1) % 78) + 48 ) # increment label character

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

        for y in range(0, self.grid.height):
            for x in range(0, self.grid.width):
                pos = Point(x, y)
                if self.grid.get_cell(pos).plottable \
                    and len(self.grid.get_command(pos)) > 0 \
                    and self.grid.is_corner(pos):
                    areas.append(self.find_largest_area_from(pos))

        areas = util.uniquify(areas, lambda area: ''.join([str(c) for c in area.corners]))
        return areas

    def find_largest_area_from(self, pos):
        """
        Build a list of direction pairs we'll want to test.
        We need to check each compass direction paired with both
        90-degree rotations from each compass direction:
        NE, NW, EN, ES, ...

        These represent the 4 quadrants created by partitioning the
        grid through the 2 axes which pos sits on, and
        the inversions of each quadrant (e.g. the pair SE & ES).
        Each quadrant includes the origin (0, 0); similarly, each
        quadrant overlaps on two edges with adjacent quadrants.
        """
        dir_pairs = []
        for d in ('e', 's', 'w', 'n'):
            direction = Direction(d)
            dir_pairs.append([direction, direction.right_turn()])
            dir_pairs.append([direction, direction.left_turn()])

        bestarea = Area(pos, pos)

        # find the biggest area(s) formable from each dir_pair quadrant
        for dirs in dir_pairs:
            area = self.find_largest_area_in_quadrant(pos, dirs[0], dirs[1], bestarea)
            if area is not None:
                bestarea = area

        return bestarea

    def find_largest_area_in_quadrant(self, pos, primary, secondary, bestarea):
        # width and height are conceptually aligned to an
        # east(primary) x south(secondary) quadrant below.

        # Get the min/max size that this area may be, based on the command
        command = self.grid.get_cell(pos).command
        sizebounds = self.buildconfig.get('sizebounds', command)

        # Get the max width of this area on the axis defined by
        # pos and primary direction, and max width from
        # the secondary
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


        # Get the coordinate of pos which the primary axis lies on
        start = pos.get_coord_of_axis(primary)

        # Determine which edge we're moving towards as we move along
        # the secondary axis
        step = secondary.delta().get_coord_crossing_axis(secondary)
        end = start + (step * (maxheight - 1))

        # (width x 1) sized area
        bestarea = Area(
            pos,
            pos + primary.delta().magnify(maxwidth - 1)
            )

        for dy in range(1, maxheight):
            check_point = pos + secondary.delta().magnify(dy)

            height = dy + 1
            width = self.grid.count_repeating_cells(check_point, primary)

            if width > maxwidth:
                # this row can't be wider than previous rows
                width = maxwidth
            elif width < maxwidth:
                # successive rows can't be wider than this row
                maxwidth = width

            if width * height > bestarea.size():
                bestarea = Area(pos, check_point + primary.delta().magnify(width - 1))
            else:
                continue

        return bestarea
