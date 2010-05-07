#! /usr/bin/python

from geometry import *
import csvreader
from areaplotter import AreaPlotter
from router import Router
from keystroker import Keystroker
import sys

__author__="joelt"
__date__ ="$May 1, 2010 10:51:38 AM$"

def process_blueprint(csv, output):
    # parse the .csv blueprint file
    (layers, build_type, start_pos, start_comment, comment) = csvreader.parse_csv_file(csv)

    if not start_pos:
        start_pos = Point(0, 0)

    for layer in layers:
        print layer.grid.str_commands('') + '\n--- ^^ after parsing %s ^^ ---\n' % csv

    keys = []

    for layer in layers:
        grid = layer.grid
        layer.start_pos = start_pos
        ## plot_predefined_areas()

        # plot areas to be built on the grid
        plotter = AreaPlotter(grid)
        if not plotter.mark_all_plottable_areas():
            raise
            # print "nada to plotta"
            # return None # throw an error?

        grid = plotter.grid

        # starting from start_pos, discover the order we will
        # plot the areas in using a sort of cheapest-route algorithm

        router = Router(grid)
        (plots, start_pos) = router.plan_route(start_pos)
        layer.plots = plots
        print "plot count: %d" % len(plots)

        # generate key sequence to render this series of plots in game
        ks = Keystroker(grid, build_type)
        keys += ks.plot(plots) + ['^5']

    keystr = ''.join(keys)
    print keystr
    f = open(output, 'w')
    f.write(keystr)
    f.close()

    print '\n'*4

    for layer in layers:
        print layer.grid.str_area_labels() + '\n'
        print "Starts at: %s" % layer.start_pos
        print "route order: %s" % ''.join([layer.grid.get_cell(plot).label for plot in layer.plots]) + '\n\n'

    print keystr
    print "total key cost: %d" % len(keys)

    # return keys

    return

if __name__ == "__main__":
    for arg in sys.argv:
        print 'arg: ' + str(arg)

    if len(sys.argv) == 3:
        path = sys.argv[1]
        outpath = sys.argv[2]
    else:
        path = "d:/code/Quickfort/trunk/QuickfortAHK/Blueprints/Tests/odd-shape.csv"
        outpath = "d:/code/Quickfort/trunk/pyout.txt"

    process_blueprint(path, outpath)




