from geometry import *
from util import *
from keystroker import Keystroker

def get_cost(keystroker, cursor_pos, start_pos, last_command, cell):
    # determine the distance (roughly equal to keystroke cost) between start_pos
    # and where we might want to start building
    # cost = start_pos.distance_to(pos) * 2

    # determine the keystroke cost to move to the area start corner where
    # we want to build
    cost = ks.move(cursor_pos, start_pos)

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
    area = cell.area
    cost += 2 + sqrt(len(
                keystroker.move(area.corners[0], area.corners[1])
                ))
    return cost


class Router:

    def __init__(self, grid):
        self.grid = grid

    def plan_route(self, cursor_pos):
        """
        We assume the areas to be plotted are already loaded into grid.
        Starting from cursor_pos, we locate the nearest/smallest area
        we can plot, and we plot it. Repeat until all areas are plotted.
        """

        ks = Keystroker(self.grid, 'd')
        plots = []
        total_move_cost = 0
        total_key_cost = 0
        total_movekey_cost = 0
        last_command = ''
        cost_weight_delta = Point(0, 0)
        center = Point(self.grid.width // 2, self.grid.height // 2)

        self.grid.set_entire_grid_plottable(True)

        while (True):
            #print "pre build pos %s" % cursor_pos
            cheapest_pos = self.get_cheapest_plottable_area_from(cursor_pos, last_command)

            if cheapest_pos is None:
                # no more areas left to plot
                break
            else:
                #print "cheapest_pos %s %s" % (cheapest_pos, self.grid.get_cell(cheapest_pos).area)
                # record this plot start-coordinates in plots
                plots.append(cheapest_pos)
                total_move_cost += cursor_pos.distance_to(cheapest_pos)
                total_key_cost += len(ks.move(cursor_pos, cheapest_pos))
                total_movekey_cost += len(ks.move(cursor_pos, cheapest_pos))
                # mark the plot on the grid
                cell = self.grid.get_cell(cheapest_pos)
                if last_command != cell.command:
                    total_key_cost += 1
                last_command = cell.command
                self.grid.set_area_plottable(cell.area, False)
                #d = get_direction_from_to(center, cheapest_pos)
                #if d is not None: cost_weight_delta += d.delta()
                # print "new plot recorded starting at %s for area %s" % (cheapest_pos, cell.area)
                #print self.grid.str_plottable() + '\n'

                # move cursor_pos to the ending corner of the plotted area
                cursor_pos = self.grid.get_cell(cheapest_pos).area.opposite_corner(cheapest_pos)
                #print "post build pos %s" % cursor_pos
                # print "------------------ new cursor pos %s ------------------------" % cursor_pos
                total_move_cost += cheapest_pos.distance_to(cursor_pos)
                total_key_cost += len(ks.move(cheapest_pos, cursor_pos)) + 2
        print self.grid.str_area_labels()
        print "route order: %s" % ''.join([self.grid.get_cell(plot).label for plot in plots])
        print "movecost %f" % total_move_cost
        print "keycost %f" % total_key_cost
        print "movekeys required between areas %f" % total_movekey_cost
        print "exiting pos %s" % cursor_pos
        return (plots, cursor_pos)

    def new_find_cheapest(self, start_pos, last_command):
        # buid list of all cells
        cells = flatten(self.grid.cells)

        # collect all the area-corners
        areacells = [c for c in cells if c.area]

        while areacells:
            # get the cheapest area-corner cell to build from here
            cell = min(areacells, key=lambda c: get_cost(start_pos, last_command, cell))
            pos = cell.parentgrid
            # remove the 4 area-corners that make up this area from areacells
            for corner in cell.area.corners:
                areacells.remove(corner)

            # find the cheapest one from here
            # include command-switching cost,
            # move cost, and area construction
            # cost (or odd ass variation of it)

            # optimization: break upon finding
            #  one that's larger than this one

            # plot it? should not be needed if
            # just working off areas list;
            # remove the other corners from areas




    def get_cheapest_plottable_area_from(self, start_pos, last_command):
        cheapest_pos = None
        cheapest_area = None
        cheapest_cost = 9999999

        # check the cell we started in: if it is plottable, it becomes our
        # starting cheapest_area
        cell = self.grid.get_cell(start_pos)

        if cell.plottable and cell.area:
            cheapest_pos = start_pos
            cheapest_cost = 1 # sqrt(cell.area.diagonal_length())
            cheapest_area = cell.area

        ## print '--------'
        # start with the innermost ring of cells adjacent to start_pos, then
        # expand outward ring by ring
        ks = Keystroker(self.grid, 'd')

        for ring in xrange(1, 1 + max([self.grid.width, self.grid.height])):

            # if the minimum number of moves that would be required just to get to this ring
            # is more than the total cost of plotting the cheapest area found so far, stop
            # looking; any further cells would be guaranteed to cost at least as much
            if (ring >= cheapest_cost):
                break

            pos = start_pos + Point(-ring, -ring) # starting position in ring (NW corner cell)

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

                    # determine the distance (roughly equal to keystroke cost) between start_pos
                    # and where we might want to start building
                    cost = start_pos.distance_to(pos) * 2
                    # cost = len(ks.move(start_pos, pos))

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


