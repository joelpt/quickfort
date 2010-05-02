#! /usr/bin/python

from grid_geometry import *
import csvreader
import quickfort_main
from areaplotter import AreaPlotter
from router import Router
import keystroker

__author__="joelt"
__date__ ="$May 1, 2010 10:51:38 AM$"

def process_blueprint(filename):
    # parse the .csv blueprint file
    (grid, build_type, start_pos, start_comment, comment) = csvreader.parse_csv_file(filename)

    if start_pos is None:
        start_pos = Point(0, 0)

    # plot areas to be built on the grid
    plotter = AreaPlotter(grid)
    if not plotter.mark_all_plottable_areas():
        print "nada to plotta"
        return None # throw an error?

    grid = plotter.grid

    # starting from start_pos, discover the order we will
    # plot the areas in using a sort of cheapest-route algorithm

    router = Router(grid)
    plots = router.plan_route(start_pos)
    print "plot count: %d" % len(plots)
    # generate key sequence to render this series of plots in game
    # ks = Keystroker(build_type)
    # keys = ks.plot(grid, plots)

    # return keys
    return

if __name__ == "__main__":
    path = "c:\My Dropbox\code\Quickfort\QuickfortAHK\Blueprints\Tests\odd-shape.csv"
    (grid, build_type, start_pos, start_comment, comment) = csvreader.parse_csv_file(path)
    print "grid:\n%s" % grid.str_commands('')
    print "build_type: %s" % build_type
    print "comment: %s" % comment

    process_blueprint(path)


