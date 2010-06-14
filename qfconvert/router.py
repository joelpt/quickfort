"""Handles route planning needed to move between areas and designate them."""

from geometry import Direction, Point, Grid


def plan_route(grid, debug, cursor):
    """
    We assume the areas to be plotted are already loaded into grid.
    Starting from cursor, we locate the nearest/smallest area
    we can plot, and we plot it. Repeat until all areas are plotted.
    """

    plots = []

    grid.set_entire_grid_plottable(True)

    if debug:
        print Grid.str_area_labels(grid) + '\n'
        print ">>>> BEGIN ROUTE PLANNING"

    while (True):
        nearest_pos = get_nearest_plottable_area_from(grid, cursor)

        if nearest_pos is None:
            # no more areas left to plot
            break
        else:
            # record this plot start-coordinates in plots
            plots.append(nearest_pos)

            # mark the plot on the grid
            cell = grid.get_cell(nearest_pos)
            area = cell.area
            grid.set_area_cells(area, False)

            if debug:
                print "#### Plotting area starting at %s, area %s" % (
                    nearest_pos, area)
                print Grid.str_plottable(grid) + '\n'

            # move cursor to the ending corner of the plotted area
            cursor = area.opposite_corner(nearest_pos)

    if debug:
        print Grid.str_plottable(grid) + '\n'
        print "#### Plotted all areas"
        print Grid.str_area_labels(grid)
        print "Route replay sequence: %s" % \
            ''.join([grid.get_cell(plot).label for plot in plots])
        print "Cursor position now: %s" % cursor
        print "<<<< END ROUTE PLANNING"

    return grid, plots, cursor


def get_nearest_plottable_area_from(grid, start):
    """
    Find the nearest plottable area corner from start.
    Returns coordinate of nearest plottable area corner.
    """

    # check the cell we started in: if it is plottable, it becomes our
    # starting cheapest_area
    cell = grid.get_cell(start)

    if cell.plottable and cell.area:
        return start

    # start with the innermost ring of cells adjacent to start, then
    # expand outward ring by ring
    for ring in xrange(1, 1 + max([grid.width, grid.height])):
        # starting position in this ring (=NW corner cell of ring)
        pos = start + Point(-ring, -ring)

        for direction in (Direction(d) for d in ['e', 's', 'w', 'n']):
            for _ in xrange(0, 2*ring):
                pos += direction.delta() # step once in direction

                if grid.is_out_of_bounds(pos):
                    continue # outside grid bounds

                corner = grid.get_cell(pos)

                if corner.plottable and corner.area:
                    # cell has an area that can be plotted, return it
                    return pos

    # found no position with an area we can plot
    return None


