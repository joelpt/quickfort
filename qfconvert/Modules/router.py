import sys

from geometry import *
from util import *
from keystroker import Keystroker

class Router:

    def __init__(self, grid, debug):
        self.grid = grid
        self.debug = debug

    def plan_route(self, cursor):
        """
        We assume the areas to be plotted are already loaded into grid.
        Starting from cursor, we locate the nearest/smallest area
        we can plot, and we plot it. Repeat until all areas are plotted.
        """

        ks = Keystroker(self.grid, 'd')
        plots = []
        total_move_cost = 0
        total_key_cost = 0
        total_movekey_cost = 0
        last_command = ''

        self.grid.set_entire_grid_plottable(True)

        if self.debug:
            print self.grid.str_area_labels() + '\n'
            print ">>>> BEGIN ROUTE PLANNING"

        while (True):
            nearest_pos = self.get_nearest_plottable_area_from(cursor)

            if nearest_pos is None:
                # no more areas left to plot
                break
            else:
                # record this plot start-coordinates in plots
                plots.append(nearest_pos)

                # mark the plot on the grid
                cell = self.grid.get_cell(nearest_pos)
                area = cell.area
                self.grid.set_area_cells(area, False)

                if self.debug:
                    print "#### Plotting area starting at %s, area %s" % (
                        nearest_pos, area)
                    print self.grid.str_plottable() + '\n'

                # move cursor to the ending corner of the plotted area
                cursor = area.opposite_corner(nearest_pos)

        if self.debug:
            print self.grid.str_plottable() + '\n'
            print "#### Plotted all areas"
            print self.grid.str_area_labels()
            print "Route replay sequence: %s" % \
                ''.join([self.grid.get_cell(plot).label for plot in plots])
            print "Cursor position now: %s" % cursor
            print "<<<< END ROUTE PLANNING"

        return (plots, cursor)

    def get_nearest_plottable_area_from(self, start):
        nearest_pos, cheapest_cost = None, 999999999

        # check the cell we started in: if it is plottable, it becomes our
        # starting cheapest_area
        cell = self.grid.get_cell(start)

        if cell.plottable and cell.area:
            return start

        # start with the innermost ring of cells adjacent to start, then
        # expand outward ring by ring
        for ring in xrange(1, 1 + max([self.grid.width, self.grid.height])):
            # starting position in this ring (=NW corner cell of ring)
            pos = start + Point(-ring, -ring)

            for dir in (Direction(d) for d in ['e','s','w','n']):
                for step in xrange(0, 2*ring):

                    # step once in the direction of dir
                    pos += dir.delta()

                    if self.grid.is_out_of_bounds(pos):
                        # point is outside the grid so don't test further
                        continue

                    cell = self.grid.get_cell(pos)

                    if not cell.plottable or not cell.area:
                        # cell is already plotted or is not an area
                        continue

                    return pos

        # found no position with an area to build from
        return None


