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
            cheapest_pos = self.get_cheapest_plottable_area_from(cursor, last_command)

            if cheapest_pos is None:
                # no more areas left to plot
                break
            else:
                # record this plot start-coordinates in plots
                plots.append(cheapest_pos)
                total_key_cost += len(ks.move(cursor, cheapest_pos))

                # mark the plot on the grid
                cell = self.grid.get_cell(cheapest_pos)

                if last_command != cell.command:
                    total_key_cost += 1
                last_command = cell.command

                self.grid.set_area_plottable(cell.area, False)

                if self.debug:
                    print "#### Plotting next area starting at %s, area %s" % (cheapest_pos, cell.area)
                    print self.grid.str_plottable() + '\n'

                # move cursor to the ending corner of the plotted area
                cursor = self.grid.get_cell(cheapest_pos).area.opposite_corner(cheapest_pos)
                total_key_cost += len(ks.move(cheapest_pos, cursor)) + 2

        if self.debug:
            print self.grid.str_plottable() + '\n'
            print "#### Plotted all areas"
            print self.grid.str_area_labels()
            print "Route replay sequence: %s" % ''.join([self.grid.get_cell(plot).label for plot in plots])
            print "Approx key cost: %d" % total_key_cost
            print "Cursor position now: %s" % cursor
            print "<<<< END ROUTE PLANNING"

        return (plots, cursor)

    def get_cheapest_plottable_area_from(self, start, last_command):
        cheapest_pos, cheapest_cost = None, 999999999

        # check the cell we started in: if it is plottable, it becomes our
        # starting cheapest_area
        cell = self.grid.get_cell(start)

        if cell.plottable and cell.area:
            cheapest_pos, cheapest_cost = start, 1

        # start with the innermost ring of cells adjacent to start, then
        # expand outward ring by ring
        ks = Keystroker(self.grid, 'd')

        for ring in xrange(1, 1 + max([self.grid.width, self.grid.height])):
            # if the minimum number of moves that would be required just to get to this ring
            # is more than the total cost of plotting the cheapest area found so far, stop
            # looking; any further cells would be guaranteed to cost at least as much
            if (ring >= cheapest_cost):
                break

            pos = start + Point(-ring, -ring) # starting position in ring (NW corner cell)

            for dir in (Direction(d) for d in ['e','s','w','n']):
                for step in xrange(0, 2*ring):

                    # step once in the direction of dir
                    pos += dir.delta()

                    if self.grid.is_out_of_bounds(pos):
                        # point is outside the grid so don't test further
                        continue

                    cell = self.grid.get_cell(pos)

                    if not cell.plottable:
                        # point is already plotted
                        continue

                    # determine the keystroke cost between start
                    # and where we might want to start building;
                    # weighted to reduce how much moving around
                    # we do
                    cost = len(ks.move(start, pos)) * 2
                    #cost = start.distance_to(pos) * 2

                    # if we have to switch commands between the last command
                    # and this one, add that necessary keystroke to cost
                    if last_command != cell.command:
                        cost += 1

                    # if this is already at least as expensive as cheapest_cost, don't test further
                    if cost >= cheapest_cost:
                        continue

                    # is this a area-corner cell that we can build from?
                    area = cell.area
                    if area:
                        # add a heuristic value of this area's cost-to-plot
                        # to cost; the formula used here was just determined
                        # through several empirical tests and thus is
                        # probably suboptimal in some cases
                        cost += sqrt(len(
                                   ks.move(area.corners[0], area.corners[2])
                                   ))

                        # is this area cheaper than the cheapest one yet found?
                        if cost < cheapest_cost:
                            # make this the new cheapest area
                            cheapest_pos = pos
                            cheapest_cost = cost

        # return our cheapest_pos found, if any
        return cheapest_pos


