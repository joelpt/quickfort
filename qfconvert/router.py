"""Handles route planning needed to move between areas and designate them."""

from log import log_routine, logmsg, loglines

from geometry import Direction, add_points
from grid import Grid


@log_routine('router', 'ROUTE PLANNING')
def plan_route(grid, cursor):
    """
    We assume the areas to be plotted are already loaded into grid.
    Starting from cursor, we locate the nearest area we can plot,
    and we plot it. Repeat until all areas are plotted.
    """

    plots = []

    grid.set_entire_grid_plottable(True)

    logmsg('router', 'Starting state:')
    loglines('router', lambda: Grid.str_area_labels(grid))

    while (True):
        nearest_pos = get_nearest_plottable_area_from(grid, cursor)

        if nearest_pos is None:
            # no more areas left to plot
            break
        else:
            # record this plot start-coordinates in plots
            plots.append(nearest_pos)

            # mark the plot on the grid
            cell = grid.get_cell(*nearest_pos)
            area = cell.area
            grid.set_area_cells(area, False)

            logmsg('router', 'Plotting area starting at %s, area %s' % \
                (nearest_pos, area))
            loglines('router', lambda: Grid.str_plottable(grid))

            # move cursor to the ending corner of the plotted area
            cursor = area.opposite_corner(nearest_pos)

    logmsg('router', 'Routed through all areas:')
    loglines('router', lambda: Grid.str_area_labels(grid))
    logmsg('router', 'Route replay sequence: %s' % \
            ''.join([grid.get_cell(*plot).label for plot in plots]))
    logmsg('router', 'Cursor position now: %s' % str(cursor))

    return grid, plots, cursor


def get_nearest_plottable_area_from(grid, start):
    """
    Find the nearest plottable area corner from start.
    Returns coordinate of nearest plottable area corner.
    """

    # if start is out of bounds for grid, expand dimensions of grid
    if grid.is_out_of_bounds(*start):
        grid.expand_dimensions(start[0] + 1, start[1] + 1)

    # check the cell we started in: if it is plottable, it becomes our
    # starting cheapest_area
    cell = grid.get_cell(*start)

    if cell.plottable and cell.area:
        return start

    # start with the innermost ring of cells adjacent to start, then
    # expand outward ring by ring
    for ring in xrange(1, 1 + max([grid.width, grid.height])):
        # starting position in this ring (=NW corner cell of ring)
        pos = add_points(start, (-ring, -ring))

        for direction in (Direction(d) for d in ['e', 's', 'w', 'n']):
            for _ in xrange(0, 2 * ring):
                pos = add_points(pos, direction.delta())  # step once in direction

                if grid.is_out_of_bounds(*pos):
                    continue  # outside grid bounds

                corner = grid.get_cell(*pos)

                if corner.plottable and corner.area:
                    # cell has an area that can be plotted, return it
                    return pos

    # found no position with an area we can plot
    return None
