from grid_geometry import *
import util

class AreaPlotter:

    def __init__(self, grid):
        self.grid = grid

    def mark_all_plottable_areas(self):
        # Repeatedly plot the largest areas possible until
        # there are no more areas left to plot. Returns
        # the plotted grid.
        label = '0'
        plotted_something = False

        while True:
            print '---------------------------------- mark largest plottable areas with label %s ----------------------------------' % label
            new_label = self.mark_largest_plottable_areas(label)
            # print self.grid.str_commands('') + '\n'
            # print self.grid.str_plottable() + '\n'
            # print self.grid.str_area_corners() + '\n'
            print self.grid.str_area_labels() + '\n'

            if label != new_label:
                # 1+ areas marked this pass
                plotted_something = True
                label = new_label

            if not self.grid.is_area_plottable(Area(Point(0,0), Point(self.grid.width-1, self.grid.height-1)), True):
                print "grid is completely plotted"
                return plotted_something

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
            # print "******************************** Plotting area " + str(area)
            # not overlapping any already-plotted area?
            if self.grid.is_area_plottable(area):
                plotted_something = True

                # mark this area as unavailable for subsequent plotting
                self.grid.set_area_plottable(area, False)
                self.grid.set_area_label(area, label)

                label = chr( ((ord(label) - 48 + 1) % 78) + 48 ) # increment label character

                # print "found and marking area: " + ' | '.join([str(c) for c in area.corners])
                # store area in grid cell for each of the area's corners
                for corner in area.corners:
                    # print "trying to place a corner: %s" % corner
                    self.grid.get_cell(corner).area = area

        # return our label when we plotted at least 1 new area
        return label


    def find_largest_areas(self):
        # find the largest areas that can currently be built from each
        # area-corner-cell in the grid
        areas = []

        for y in range(0, self.grid.height):
            for x in range(0, self.grid.width):
                point = Point(x, y)
                # print "============================= testing %s '%s' gridwidth %d gridheight %d plottable %s " % (str(point), self.grid.get_command(point), self.grid.width, self.grid.height, self.grid.get_cell(point).plottable)
                if self.grid.get_cell(point).plottable \
                    and len(self.grid.get_command(point)) > 0 \
                    and self.grid.is_corner(point):
                    areas.append(self.find_largest_area_from_point(point))

        areas = util.uniquify(areas, lambda area: ''.join([str(c) for c in area.corners]))
        # print "results of find largest areas pass after uniquify:"
        # print len(areas)
        # print '\n'.join([str(a) for a in areas])
        return areas

    def find_largest_area_from_point(self, start_point):

        # Build a list of direction pairs we'll want to test.
        # We need to check each compass direction paired with both
        # 90-degree rotations from each compass direction:
        # NE, NW, EN, ES, ...
        # These represent the 4 quadrants created by partitioning the
        # grid through the 2 axes which start_point sits on, and
        # the inversions of each quadrant (e.g. the pair SE & ES).
        # Each quadrant includes the origin (0, 0); similarly, each
        # quadrant overlaps on two edges with adjacent quadrants.
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

        # print best_area
        return best_area
        # # print len(areas)
        # # print '\n'.join([str(a) for a in areas])
        # areas = util.uniquify(areas, lambda area: ''.join([str(c) for c in area.corners]))

        # # print len(areas)
        # # print '\n'.join([str(a) for a in areas])

        # return areas

    def find_largest_area_in_quadrant(self, start_point, primary, secondary, best_area):

        # width and height are conceptually aligned to an
        # east(primary) x south(secondary) quadrant below.

        # Get the max width of this area on the axis defined by
        # start_point and primary direction, and max width from
        # the secondary
        # # print "FLA@##$@$@$@$"
        # # print start_point
        # # print primary
        # # print secondary
        # # print "FLA---------^"
        max_width = self.grid.count_repeating_cells(start_point, primary)
        max_height = self.grid.count_repeating_cells(start_point, secondary)
        #if max_width > 50 and max_height > 5:
        # if start_point.x == 0:
        #     print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ leftedge %s %d %d' % (start_point, max_width, max_height)
        # print ">>>>>>>>> quadrant hunt: quad %s/%s max_width/height %d %d " % (primary.compass, secondary.compass, max_width, max_height)
        if max_width * max_height < best_area.size():
            # print "<<<<<<<< aborting this quadrant test because the best area found so far is larger than this one - i am %d and best is %d" % (max_width * max_height, best_area.size())
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
        # print "default width x 1 sized best_area:"
        # print [str(c) for c in best_area.corners]

        for dy in range(1, max_height):
            check_point = start_point + secondary.delta().magnify(dy)

            height = dy + 1
            width = self.grid.count_repeating_cells(check_point, primary)
            # print "found a bar at dy %d (traversing %s axis) with a %s-length of %d start 1 end %d oldstep %d starting at %s" % (dy, secondary.compass, primary.compass,width, max_height, step, str(check_point))

            if width > max_width:
                # this row can't be wider than previous rows
                width = max_width
                # print "this row can't be wider than previous rows"
            elif width < max_width:
                # successive rows can't be wider than this row
                max_width = width
                # print "successive rows can't be wider than this row"

            if width * height > best_area.size():
                # this area is the biggest we've found yet
                best_area = Area(start_point, check_point + primary.delta().magnify(width - 1))

                # print "this area is the biggest we've found yet:"
                # print [str(c) for c in best_area.corners]
                # print "which has size %d " % best_area.size()
            else:
                continue
                # print "found area of size %d is not more than the best area's size %d" % (width*height, best_area.size())

        return best_area


