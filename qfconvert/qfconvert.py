#! /usr/bin/python

from optparse import OptionParser
import sys
import traceback
import cProfile

import blueprint
import transformer

def parse_options():
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
    options, args = parser.parse_args()
    return options, args

def main(options, args):
    infile = args[0]
    outfile = args[1] if len(args) > 1 else None

    try:
        if options.debugfile: print ">>>> BEGIN INPUT FILE PARSING"

        bp = blueprint.read_blueprint(infile, options)

        if options.debugfile:
            print '#### Parsed %s' % infile
            for layer in bp.layers:
                print (layer.grid.str_commands('') + '\n'
                    + ''.join(layer.onexit) + '\n'
                    )

        if options.transform:
            if options.debugfile:
                print "#### Transforming using transformation: %s" % \
                    options.transform

            transforms = transformer.parse_transform_str(options.transform)
            bp.layers = transformer.transform(transforms, bp.layers)

            if options.debugfile:
                for layer in bp.layers:
                    print layer.grid.str_commands('') + '\n'

        if options.debugfile: print ">>>> END INPUT FILE PARSING"

        if options.info:
            output = bp.get_info(options)
        else:
            keys = bp.plot(options)
            output = ''.join(keys)

            if options.debugsummary:
                print ">>>> BEGIN SUMMARY"
                print "---- Layers:"
                for layer in bp.layers:
                    print "#### Commands:"
                    print layer.grid.str_commands() + '\n'
                    print "#### Area labels:"
                    print layer.grid.str_area_labels() + '\n'
                    print "Initial cursor position: %s" % layer.start
                    print "Route order: %s" % ''.join(
                        [layer.grid.get_cell(plot).label
                        for plot in layer.plots]
                        )
                    print "Layer onexit keys: %s" % layer.onexit
                print "---- Overall:"
                print "Total key cost: %d" % len(keys)
                print "<<<< END SUMMARY"

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
    options, args = parse_options()

    if len(args) < 1:
        parser.print_help()

    main(options, args)

