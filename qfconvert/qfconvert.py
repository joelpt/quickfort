#! /usr/bin/python

from optparse import OptionParser
import traceback
import cProfile

from blueprint import process_blueprint_file


def parse_options():
    """Read options and args from command line."""
    usage = "usage: %prog [options] input_file [output_file]"
    parser = OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("-t", "--transform",
                      action="store", dest="transform", default=False,
                      help="transformation rules, e.g. 2e flipv 2s")
    parser.add_option("-m", "--mode", dest="mode", default='macro',
                      help="output mode: key or macro [default: %default]")
    parser.add_option("-T", "--title", dest='title',
                      help="title of macro")
    parser.add_option("-i", "--info",
                      action="store_true", dest="info", default=False,
                      help="output information about input_file")
    parser.add_option("-c", "--show-csv",
                      action="store_true", dest="debugfile", default=False,
                      help="show blueprint parsing steps on stdout")
    parser.add_option("-a", "--show-area",
                      action="store_true", dest="debugarea", default=False,
                      help="show area-discovery steps on stdout")
    parser.add_option("-r", "--show-route",
                      action="store_true", dest="debugrouter", default=False,
                      help="show route-planning steps on stdout")
    parser.add_option("-s", "--show-summary",
                      action="store_true", dest="debugsummary", default=False,
                      help="show summary output")
    parser.add_option("-p", "--profile",
                      action="store_true", dest="profile", default=False,
                      help="profile qfconvert performance")
    options, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        return None, None

    if options.mode not in ('key', 'macro'):
        raise Exception, \
            "Invalid mode '%s', must be either 'key' or 'macro'" % \
                options.mode

    return options, args


def run(options, args):
    infile = args[0]
    outfile = args[1] if len(args) > 1 else None

    try:
        output = process_blueprint_file(infile, options)

        if outfile:
            with open(outfile, 'w') as outf:
                outf.write(output)
        else:
            print output
    except Exception as ex:
        traceback.print_exc()
        if outfile:
            with open(outfile, 'w') as outf:
                outf.write('Exception: ' + str(ex))
    return

def main():
    options, args = parse_options()

    if args is not None:
        if options.profile:
            cProfile.run('run(options, args)')
        else:
            run(options, args)

if __name__ == "__main__":
    main()
