from geometry import *
from util import *
from keystroker import Keystroker

def get_cost(keystroker, cursor, start, last_command, cell):
    # print cursor
    # print start
    # print last_command
    # print cell
    # determine the distance (roughly equal to keystroke cost) between start
    # and where we might want to start building
    # cost = start.distance_to(pos) * 2

    # determine the keystroke cost to move to the area start corner where
    # we want to build
    cost = len(keystroker.move(cursor, start))

    # if we have to switch commands between the last command and this one
    # add to cost
    if last_command != cell.command:
        cost += 1

    # if this is already at least as expensive as cheapest_cost, don't test further
    # if cost >= cheapest_cost:
    #     ## print 'costs more %f than cheapest cost %f' % (cost, cheapest_cost)
    #     continue

    # add this area's cost-to-plot
    #cost += sqrt(area.diagonal_length())
    #cost += area.diagonal_length()
    cost += 2 + sqrt(len(
            keystroker.move(cell.area.corners[0], cell.area.corners[2])
            ))
    return cost


class Router:

    def __init__(self, grid, debug):
        self.grid = grid
        self.debug = debug

    def plan_route2(self, cursor):
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
            print "Total key cost: %d" % total_key_cost
            print "Cursor position now: %s" % cursor
            print "<<<< END ROUTE PLANNING"

        return (plots, cursor)

    # def new_find_cheapest(self, start, last_command):
    # def get_cheapest_plottable_area_from(self, start, last_command):
    def plan_route(self, cursor):
        ks = Keystroker(self.grid, 'd')
        plots = []
        last_command = ''

        # buid list of all cells
        cells = flatten(self.grid.cells)

        # collect a list of distinct area-corners
        areacells = flatten([corner for corner in [c.area.corners for c in cells if c.area]])
        areacells = uniquify(areacells, lambda x: str(x))

        while areacells:
            # get the cheapest area-corner cell to build from cursor
            pos = min(areacells, key=lambda c: get_cost(ks, cursor, c, last_command, self.grid.get_cell(c)))
            cell = self.grid.get_cell(pos)

            # record found pos in plots
            plots.append(pos)

            # update cursor location
            cursor = cell.area.opposite_corner(pos)

            # remove the 4 area-corners that make up this area from areacells
            for corner in cell.area.corners:
                if corner in areacells: areacells.remove(corner)

            ## TODO return plots,cursor and make this plan_route instead of get_cheapest_..()
            ## TODO compare speeds before and after as well as keycounts
            # find the cheapest one from here
            # include command-switching cost,
            # move cost, and area construction
            # cost (or odd ass variation of it)

            # optimization: break upon finding
            #  one that's larger than this one

            # plot it? should not be needed if
            # just working off areas list;
            # remove the other corners from areas
        return plots, cursor



    def get_cheapest_plottable_area_from(self, start, last_command):
        cheapest_pos = None
        cheapest_area = None
        cheapest_cost = 9999999

        # check the cell we started in: if it is plottable, it becomes our
        # starting cheapest_area
        cell = self.grid.get_cell(start)

        if cell.plottable and cell.area:
            cheapest_pos = start
            cheapest_cost = 1 # sqrt(cell.area.diagonal_length())
            cheapest_area = cell.area

        ## print '--------'
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

                    # determine the distance (roughly equal to keystroke cost) between start
                    # and where we might want to start building
                    cost = start.distance_to(pos) * 2
                    # cost = len(ks.move(start, pos))

                    # if we have to switch commands between the last command and this one
                    # add to cost
                    if last_command != cell.command:
                        cost += 1

                    # if this is already at least as expensive as cheapest_cost, don't test further
                    if cost >= cheapest_cost:
                        ## print 'costs more %f than cheapest cost %f' % (cost, cheapest_cost)
                        continue

                    # is this a area-corner cell that we can build from?
                    area = cell.area
                    if area:
                        # add this area's cost-to-plot
                        #cost += sqrt(area.diagonal_length())
                        #cost += area.diagonal_length()
                        cost += 2 + sqrt(len(
                                    ks.move(area.corners[0], area.corners[1])
                                    ))


                        ## print "areasize cost %f" % area.diagonal_length()
                        # is this area cheaper than the cheapest one yet found?
                        if cost < cheapest_cost:
                            ## print "found our new cheapest area! %s %f " % (pos, cost)
                            ## print str(area)
                            # make this the new cheapest area
                            cheapest_pos = pos
                            cheapest_area = area
                            cheapest_cost = cost

        # if cheapest_pos is None:
        #     # print "found no cheapest pos"
        # else:
        #     # print "ending cheapest area " + str(cheapest_area)
        #     # print "ending cheapest cost " + str(cheapest_cost)
        #     # print "ending cheapest pos " + str(cheapest_pos)
        # # print '--------'

        # return our cheapest_pos found, if any
        return cheapest_pos


