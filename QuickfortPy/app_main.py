#! /usr/bin/python

import sys
import re
from optparse import OptionParser

from geometry import *
import csvreader
from areaplotter import AreaPlotter
from router import Router
from keystroker import Keystroker
from transformer import Transformer

def process_blueprint(csvpath, options):
    if options.debugcsv: print ">>>> BEGIN CSV PARSING"

    # parse the .csv blueprint file
    (layers, build_type, start, start_comment, comment) = csvreader.parse_csv_file(csvpath)

    if not start:
        start = Point(0, 0)

    if options.debugcsv:
        print '#### Parsed %s' % csvpath
        for layer in layers:
            print layer.grid.str_commands('') + '\n'

    if options.transform:
        print "#### Transforming using transformation: %s" % options.transform
        layers = Transformer(layers, options.transform).transform()
        for layer in layers:
            print layer.grid.str_commands('') + '\n'

    if options.debugcsv: print ">>>> END CSV PARSING"

    keys = []

    for layer in layers:
        grid = layer.grid
        layer.start = start

        ## TODO plot_predefined_areas()

        # plot areas to be built on the grid
        plotter = AreaPlotter(grid, options.debugarea)
        if not plotter.mark_all_plottable_areas():
            raise

        grid = plotter.grid

        # starting from start, discover the order we will
        # plot the areas in using a sort of cheapest-route algorithm

        router = Router(grid, options.debugrouter)
        plots, start = router.plan_route(start)
        layer.plots = plots

        # generate key sequence to render this series of plots in game
        ks = Keystroker(grid, build_type)
        keys += ks.plot(plots) + ['^5']

    if options.debugsummary:
        print ">>>> BEGIN SUMMARY"
        for layer in layers:
            print layer.grid.str_area_labels() + '\n'
            print "Initial cursor position: %s" % layer.start
            print "Route order: %s" % ''.join([layer.grid.get_cell(plot).label for plot in layer.plots])
            print "Total key cost: %d" % len(keys)
        print "<<<< END SUMMARY"

    return ''.join(keys)


def main():
    usage = "usage: %prog [options] csv_file [output_file]"
    parser = OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("-t", "--transform",
                      action="store", dest="transform", default=False,
                      help="transformation rules, e.g. -t 2e;flipv;2s")
    parser.add_option("-c", "--show-csv",
                      action="store_true", dest="debugcsv", default=False,
                      help="show parsed blueprint on stdout after reading")
    parser.add_option("-a", "--show-area",
                      action="store_true", dest="debugarea", default=False,
                      help="show area-discovery steps on stdout")
    parser.add_option("-r", "--show-route",
                      action="store_true", dest="debugrouter", default=False,
                      help="show route-planning steps on stdout")
    parser.add_option("-s", "--show-summary",
                      action="store_true", dest="debugsummary", default=False,
                      help="show summary output")
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        return

    keystr = process_blueprint(args[0], options)

    if len(args) > 1:
        f = open(args[1], 'w')
        f.write(keystr)
        f.close()
    else:
        print keystr

    return

if __name__ == "__main__":
    main()
