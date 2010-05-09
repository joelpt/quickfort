from geometry import *
import util

class AreaPlotter:

    def __init__(self, grid, debug):
        self.grid = grid
        self.debug = debug

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
                point = Point(x, y)
                if self.grid.get_cell(point).plottable \
                    and len(self.grid.get_command(point)) > 0 \
                    and self.grid.is_corner(point):
                    areas.append(self.find_largest_area_from_point(point))

        areas = util.uniquify(areas, lambda area: ''.join([str(c) for c in area.corners]))
        return areas

    def find_largest_area_from_point(self, start_point):
        """
        Build a list of direction pairs we'll want to test.
        We need to check each compass direction paired with both
        90-degree rotations from each compass direction:
        NE, NW, EN, ES, ...

        These represent the 4 quadrants created by partitioning the
        grid through the 2 axes which start_point sits on, and
        the inversions of each quadrant (e.g. the pair SE & ES).
        Each quadrant includes the origin (0, 0); similarly, each
        quadrant overlaps on two edges with adjacent quadrants.
        """
        dir_pairs = []
        for d in ('e', 's', 'w', 'n'):
            direction = Direction(d)
            dir_pairs.append([direction, direction.right_turn()])
            dir_pairs.append([direction, direction.left_turn()])

        best_area = Area(start_point, start_point)

        # find the biggest area(s) formable from each dir_pair quadrant
        for dirs in dir_pairs:
            area = self.find_largest_area_in_quadrant(start_point, dirs[0], dirs[1], best_area)
            if area is not None:
                best_area = area

        return best_area

    def find_largest_area_in_quadrant(self, start_point, primary, secondary, best_area):
        # width and height are conceptually aligned to an
        # east(primary) x south(secondary) quadrant below.

        # Get the max width of this area on the axis defined by
        # start_point and primary direction, and max width from
        # the secondary
        max_width = self.grid.count_repeating_cells(start_point, primary)
        max_height = self.grid.count_repeating_cells(start_point, secondary)

        if max_width * max_height < best_area.size():
            return None

        # Get the coordinate of start_point which the primary axis lies on
        start = start_point.get_coord_of_axis(primary)

        # Determine which edge we're moving towards as we move along
        # the secondary axis
        step = secondary.delta().get_coord_crossing_axis(secondary)
        end = start + (step * (max_height - 1))

        # (width x 1) sized area
        best_area = Area(
            start_point,
            start_point + primary.delta().magnify(max_width - 1)
            )

        for dy in range(1, max_height):
            check_point = start_point + secondary.delta().magnify(dy)

            height = dy + 1
            width = self.grid.count_repeating_cells(check_point, primary)

            if width > max_width:
                # this row can't be wider than previous rows
                width = max_width
            elif width < max_width:
                # successive rows can't be wider than this row
                max_width = width

            if width * height > best_area.size():
                best_area = Area(start_point, check_point + primary.delta().magnify(width - 1))
            else:
                continue

        return best_area
