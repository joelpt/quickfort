#! /usr/bin/python

"""Main entry point for qfconvert."""

import sys

from optparse import OptionParser
import traceback
import cProfile

import blueprint

version = '2.01'

def parse_options(argv):
    """Read options and args from argv (the command line parameters)."""
    usage = "usage: %prog [options] [input_file] [output_file]"
    parser = OptionParser(usage=usage, version="%prog " + version)
    parser.add_option("-s", "--sheetid",
                      dest="sheetid", default=None,
                      help="worksheet index for xls/xlsx files [default: 0]")
    parser.add_option("-p", "--position",
                      dest="startpos", default=None,
                      help="starting position [one of: (x,y) ne nw se sw]")
    parser.add_option("-t", "--transform",
                      dest="transform", default=False,
                      help="transformation rules, e.g. 2e flipv 2s")
    parser.add_option("-m", "--mode",
                      dest="mode", default='macro',
                      help="output mode: key or macro [default: %default]")
    parser.add_option("-c", "--command",
                      dest='command',
                      help="Eval QF one-line command instead of input_file")
    parser.add_option("-T", "--title",
                      dest='title',
                      help="title of output macro")
    parser.add_option("-i", "--info",
                      action="store_true", dest="info", default=False,
                      help="output information about input_file")
    parser.add_option("-v", "--visualize",
                      action="store_true", dest="visualize", default=False,
                      help="just moves cursor around blueprint's perimeter")
    parser.add_option("-C", "--show-csv-parse",
                      action="store_true", dest="debugfile", default=False,
                      help="show blueprint parsing steps on stdout")
    parser.add_option("-X", "--show-transforms",
                      action="store_true", dest="debugtransform", default=False,
                      help="show transform steps on stdout")
    parser.add_option("-A", "--show-area",
                      action="store_true", dest="debugarea", default=False,
                      help="show area-discovery steps on stdout")
    parser.add_option("-R", "--show-route",
                      action="store_true", dest="debugrouter", default=False,
                      help="show route-planning steps on stdout")
    parser.add_option("-S", "--show-summary",
                      action="store_true", dest="debugsummary", default=False,
                      help="show summary output")
    parser.add_option("-P", "--profile",
                      action="store_true", dest="profile", default=False,
                      help="profile qfconvert performance")
    options, args = parser.parse_args(args=argv)

    if options.mode not in ('key', 'macro'):
        raise Exception, \
            "Invalid mode '%s', must be either 'key' or 'macro'" % \
                options.mode

    if options.command is not None:
        options.infile = None
        options.outfile = args[0] if len(args) > 0 else None
        return options

    if len(args) < 1:
        parser.print_help()
        return None

    options.infile = args[0]
    options.outfile = args[1] if len(args) > 1 else None

    if options.sheetid is not None:
        try:
            options.sheetid = int(options.sheetid)
        except:
            raise Exception, "sheetid must be numeric, not '%s'" % \
                options.sheetid

    return options


def run():
    """Perform filereading/conversion work and output result."""
    global options

    try:
        if options.command:
            output = blueprint.process_blueprint_command(options.command, options)
        elif options.info:
            output = blueprint.get_blueprint_info(options.infile)
        else:
            output = blueprint.process_blueprint_file(options.infile, options)

        if options.outfile:
            with open(options.outfile, 'w') as outf:
                outf.write(output)
        else:
            print output
    except Exception as ex:
        traceback.print_exc()
        if options.outfile:
            with open(options.outfile, 'w') as outf:
                outf.write('Exception: ' + str(ex))
    return


def main(argv=sys.argv[1:]):
    """Parse options file, parse and convert blueprint, and output result."""
    global options

    try:
        options = parse_options(argv)

        if options is None:
            return

        if options.profile:
            cProfile.run('run()')
        else:
            run()
    except Exception as ex:
        print 'Error: ' + str(ex)


if __name__ == "__main__":
    main()
