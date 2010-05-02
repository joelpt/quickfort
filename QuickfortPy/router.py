from grid_geometry import *
from util import *
from keystroker import Keystroker

class Router:

    def __init__(self, grid):
        self.grid = grid

    def plan_route(self, cursor_pos):
        """
        We assume the areas to be plotted are already loaded into grid.
        Starting from cursor_pos, we locate the nearest/smallest area
        we can plot, and we plot it. Repeat until all areas are plotted.
        """

        ks = Keystroker('d')
        plots = []
        total_move_cost = 0
        total_key_cost = 0
        total_movekey_cost = 0
        last_command = ''
        cost_weight_delta = Point(0, 0)
        center = Point(self.grid.width // 2, self.grid.height // 2)

        self.grid.set_entire_grid_plottable(True)

        while (True):
            cheapest_pos = self.get_cheapest_plottable_area_from(cursor_pos, last_command)

            if cheapest_pos is None:
                # no more areas left to plot
                break
            else:
                # record this plot start-coordinates in plots
                plots.append(cheapest_pos)
                total_move_cost += cursor_pos.distance_to(cheapest_pos)
                total_key_cost += len(ks.move(cursor_pos, cheapest_pos))
                total_movekey_cost += len(ks.move(cursor_pos, cheapest_pos))
                # mark the plot on the grid
                cell = self.grid.get_cell(cheapest_pos)
                last_command = cell.command
                self.grid.set_area_plottable(cell.area, False)
                #d = get_direction_from_to(center, cheapest_pos)
                #if d is not None: cost_weight_delta += d.delta()
                # print "new plot recorded starting at %s for area %s" % (cheapest_pos, cell.area)
                #print self.grid.str_plottable() + '\n'

                # move cursor_pos to the ending corner of the plotted area
                cursor_pos = self.grid.get_cell(cheapest_pos).area.opposite_corner(cheapest_pos)
                # print "------------------ new cursor pos %s ------------------------" % cursor_pos
                total_move_cost += cheapest_pos.distance_to(cursor_pos)
                total_key_cost += len(ks.move(cheapest_pos, cursor_pos)) + 2
        print self.grid.str_area_labels()
        print "route order: %s" % ''.join([self.grid.get_cell(plot).label for plot in plots])
        print "movecost %f" % total_move_cost
        print "keycost %f" % total_key_cost
        print "movekeys required between areas %f" % total_movekey_cost
        return plots

    def get_cheapest_plottable_area_from(self, start_pos, last_command):
        ks = Keystroker('d')

        cheapest_pos = None
        cheapest_area = None
        cheapest_cost = 9999999

        # print start_pos
        # check the cell we started in: if it is plottable, it becomes our starting
        # cheapest_area
        area = self.grid.get_cell(start_pos).area
        if area is not None and self.grid.is_plottable(start_pos):
            cheapest_pos = start_pos
            cheapest_cost = area.diagonal_length()
            #cheapest_cost = ks.move(area.corners[0], area.corners[1])
            cheapest_area = area

        # print "starting cheapest area " + str(cheapest_area)
        # print "starting cheapest cost " + str(cheapest_cost)
        # print '--------'
        # start with the innermost ring of cells adjacent to start_pos, then
        # expand outward ring by ring
        for ring in xrange(1, max([self.grid.width, self.grid.height])):
            ## print "ring %d cheapest_cost %f" % (ring, cheapest_cost)
            # if the minimum number of moves that would be required just to get to this ring
            # is more than the total cost of plotting the cheapest area found so far, stop
            # looking; any further cells would be guaranteed to cost at least as much
            if (ring >= cheapest_cost):
                ## print "ring %d costs more than cheapest_cost %f, quitting ring loop" % (ring, cheapest_cost)
                break

            pos = start_pos + Point(-ring, -ring) # starting position in ring (NW corner cell)
            ## print "starting ring walk at %s " % str(pos)

            for dir in [Direction(d) for d in ['e','s','w','n']]:
                for step in xrange(0, 2*ring):
                    # step once in the direction of dir
                    ## print "entering pos=" + str(pos)
                    pos += dir.delta()
                    ## print "now at pos=%s, step=%d, delta=%s" % (pos, step, dir.delta())

                    if self.grid.is_out_of_bounds(pos):
                        ## print "point is outside the grid so don't test further"
                        continue

                    if not self.grid.is_plottable(pos):
                        ## print "point is already plotted"
                        continue

                    # determine the distance (roughly equal to keystroke cost) between start_pos
                    # and where we might want to start building
                    cost = start_pos.distance_to(pos) * 2

                    # if we have to switch commands between the last command and this one
                    # add to cost
                    if last_command != self.grid.get_command(pos):
                        cost += 0

                    # halve initial move cost if it would be a move in the direction of
                    # cost_weight_delta; this biases the algorithm to continue filling in
                    # areas in the quadrant which is most filled in.

                    # d1 = get_direction_from_to(start_pos, cost_weight_delta)
                    # d2 = get_direction_from_to(start_pos, pos)
                    # if d1 is not None and d2 is not None and d1.compass == d2.compass:
                    #     cost /= 2


                    #cost = len(ks.move(start_pos, pos))
                    #cost = 0
                    ## print "moveto cost %f" % cost

                    # if this is already at least as expensive as cheapest_cost, don't test further
                    if cost >= cheapest_cost:
                        ## print 'costs more %f than cheapest cost %f' % (cost, cheapest_cost)
                        continue

                    # is this a area-corner cell that we can build from?
                    area = self.grid.get_cell(pos).area
                    if area is not None:
                        # add this area's cost
                        #cost += sqrt(area.diagonal_length())
                        #cost -= area.diagonal_length()
                        cost -= len(ks.move(area.corners[0], area.corners[1])) + 2


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


