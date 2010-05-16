#! /usr/bin/python

import sys
import re
from optparse import OptionParser
import textwrap
import traceback

from geometry import *
import filereader
from areaplotter import AreaPlotter
from router import Router
from keystroker import Keystroker
from transformer import Transformer
from buildconfig import BuildConfig

def parse_blueprint(path, options):
    if options.debugfile: print ">>>> BEGIN INPUT FILE PARSING"

    # parse the .csv blueprint file
    (layers, build_type, start, start_comment, comment) = \
        filereader.parse_file(path)

    if not start:
        start = Point(0, 0)

    if options.debugfile:
        print '#### Parsed %s' % path
        for layer in layers:
            print (layer.grid.str_commands('') + '\n'
                + ''.join(layer.onexit) + '\n'
                )

    if options.transform:
        print "#### Transforming using transformation: %s" % \
            options.transform
        transforms = Transformer.parse_transform_str(options.transform)
        layers = Transformer.transform(transforms, layers)
        for layer in layers:
            print layer.grid.str_commands('') + '\n'

    if options.debugfile: print ">>>> END INPUT FILE PARSING"
    return (layers, build_type, start, start_comment, comment)

def process_blueprint(path, options):
    (layers, build_type, start, start_comment, comment) = \
        parse_blueprint(path, options)

    buildconfig = BuildConfig(build_type, options)
    keys = []

    for layer in layers:
        grid = layer.grid
        layer.start = start

        ## TODO plot_predefined_areas()

        # plot areas to be built on the grid
        plotter = AreaPlotter(grid, buildconfig, options.debugarea)
        if not plotter.mark_all_plottable_areas():
            raise

        grid = plotter.grid
        # print 'before routing:'
        # print grid.str_commands('')
        # starting from start, discover the order we will
        # plot the areas in using a sort of cheapest-route algorithm

        router = Router(grid, options.debugrouter)
        plots, end = router.plan_route(start)
        layer.plots = plots

        # generate key sequence to render this series of plots in game
        ks = Keystroker(grid, buildconfig)
        keys += ks.plot(plots, start) + layer.onexit
        start = end

    keys = ks.translate(keys)

    if options.debugsummary:
        print ">>>> BEGIN SUMMARY"
        for layer in layers:
            print "#### Commands:"
            print layer.grid.str_commands() + '\n'
            print "#### Area labels:"
            print layer.grid.str_area_labels() + '\n'
            print "Initial cursor position: %s" % layer.start
            print "Route order: %s" % ''.join(
                [layer.grid.get_cell(plot).label
                for plot in layer.plots]
                )
            print "Total key cost: %d" % len(keys)
        print "<<<< END SUMMARY"

    return ''.join(keys)

def get_info(path, options):
    (layers, build_type, start, start_comment, comment) = \
        parse_blueprint(path, options)

    s = textwrap.dedent("""
        Build type: %s
        Comment: %s
        Start position: %s
        Start comment: %s
        First layer width: %d
        First layer height: %d
        Layer count: %d
        """).strip() % (
            build_type,
            comment or '',
            start,
            start_comment or '',
            layers[0].grid.width,
            layers[0].grid.height,
            len(layers)
            )

    return s

def main():
    usage = "usage: %prog [options] input_file [output_file]"
    parser = OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("-i", "--info",
                      action="store_true", dest="info", default=False,
                      help="output information about input_file")
    parser.add_option("-t", "--transform",
                      action="store", dest="transform", default=False,
                      help="transformation rules, e.g. -t flipv 2e fliph 2s")
    parser.add_option("-c", "--show-csv",
                      action="store_true", dest="debugfile", default=False,
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

    infile = args[0]
    outfile = args[1] if len(args) > 1 else None

    try:
        if options.info:
            output = get_info(infile, options)
        else:
            output = process_blueprint(infile, options)

        if outfile:
            with open(outfile, 'w') as f:
                f.write(output)
        else:
            print output

    except Exception as ex:
        traceback.print_exc()
        if outfile:
            with open(outfile, 'w') as f:
                f.write('Exception: ' + str(ex))

    return

if __name__ == "__main__":
        main()

