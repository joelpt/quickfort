"""Blueprint class and associated processing functions."""

import re
import textwrap

from areaplotter import AreaPlotter
from buildconfig import BuildConfig
from filereader import FileLayer
from geometry import Point, Direction, GridLayer, Grid
from keystroker import Keystroker, convert_keys
from router import plan_route
from util import flatten
import filereader
import transformer

def get_blueprint_info(path):
    """Returns information about the blueprint at path."""
    sheets = filereader.get_sheets(path)

    s = ''
    for sheet in sheets:
        try:
            (layers, details) = \
                filereader.parse_file(path, sheet[1])
            layers = filereader.FileLayers_to_GridLayers(layers)
            bp = Blueprint(sheet[0], layers, details)
            s += '---- Sheet id %d\n' % sheet[1]
            s += bp.get_info() + '\n'
        except:
            continue # ignore blank/missing sheets

    if s:
        return s
    else:
        raise Exception, "No valid blueprints found in '%s'." % path


def process_blueprint_file(path, options):
    """
    Main routine for reading a blueprint, transforming it, and rendering
    keystrokes/macros required to plot or visualize the blueprint specified.
    """

    if options.debugfile:
        print ">>>> BEGIN INPUT FILE PARSING"

    # parse sheetid
    if options.sheetid is None:
        sheetid = 0
    elif re.match('^\d+$', options.sheetid):
        sheetid = options.sheetid
    else:
        sheetid = filereader.get_sheets(path)

    layers, details = filereader.parse_file(path, sheetid)

    if options.debugfile:
        print '#### Parsed %s' % path
        print FileLayer.str_layers(layers)

    if options.transform:
        if options.debugfile:
            print "#### Transforming with: %s" % options.transform

        start, layers = transformer.transform(
            transformer.parse_transform_str(options.transform),
            details.start,
            layers)

        if options.debugfile:
            print "#### Results of transform:"
            print FileLayer.str_layers(layers)

    layers = filereader.FileLayers_to_GridLayers(layers)

    # set startpos
    if options.startpos is not None:
        details.start = parse_startpos(options.startpos,
            layers[0].grid.width,
            layers[0].grid.height)

    # convert layers and other data to Blueprint
    bp = Blueprint('', layers, details)

    if options.debugfile:
        print "<<<< END INPUT FILE PARSING"

    # get keys/macrocode to outline or plot the blueprint
    keys = bp.outline(options) if options.visualize else bp.plot(options)
    output = convert_keys(keys, options.mode, options.title)

    if options.debugsummary:
        print ">>>> BEGIN SUMMARY"
        print "---- Layers:"
        for i, layer in enumerate(bp.layers):
            print "=" * 20 + ' Layer %d ' % i + '=' * 20
            print "Entering cursor position: %s" % layer.start
            print "\n#### Commands:"
            print str(layer.grid) + '\n'
            print "#### Area labels:"
            print Grid.str_area_labels(layer.grid) + '\n'
            print "Route order: %s" % ''.join(
                [layer.grid.get_cell(plot).label
                for plot in layer.plots]
                )
            print "Layer onexit keys: %s\n" % layer.onexit
        print "---- Overall:"
        print "Total key cost: %d" % len(keys)
        print "<<<< END SUMMARY"

    return output


def parse_startpos(start, width, height):
    """Transform startpos string like (1,1) or nw to corresponding Point."""
    m = re.match(r'\(?(\d+)[,;](\d+)\)?', start)
    if m is not None:
        new = Point( int(m.group(1)), int(m.group(2)) )
    else:
        m = re.match(r'(ne|nw|se|sw)', start.lower())
        if m is not None:
            newcorner = Direction(m.group(1)).delta()
            new = Point(newcorner.x, newcorner.y)
            new.x = max(0, new.x) * (width - 1)
            new.y = max(0, new.y) * (height - 1)
        else:
            raise Exception, "Invalid --position parameter '%s'" % start
    return new


class Blueprint:
    """
    Represents a single blueprint (csv file or sheet in xls/x file).
    Provides high level methods for plotting, outlining, and retrieving
    information about the blueprint.
    """

    def __init__(self, name, layers, details):
        self.name = name
        self.layers = layers
        self.build_type = details.build_type
        self.start = details.start
        self.start_comment = details.start_comment
        self.comment = details.comment

    def plot(self, options):
        """Plots a route through the blueprint."""
        buildconfig = BuildConfig(self.build_type)
        keys = []
        start = self.start
        ks = None
        for layer in self.layers:
            grid = layer.grid
            layer.start = start # first layer's start or last layer's exit pos

            plotter = AreaPlotter(grid, buildconfig, options.debugarea)
            plotter.expand_fixed_size_areas()  #  plot cells of d(5x5) format
            plotter.discover_areas() # find contiguous areas

            layer.grid, layer.plots, end = plan_route(
                plotter.grid, options.debugrouter, start)

            # generate key sequence to render this series of plots in game
            ks = Keystroker(grid, buildconfig)
            keys += ks.plot(layer.plots, start) + layer.onexit
            start = end

        # move cursor back to start pos x, y, z
        keys += ks.move(end, self.start, -GridLayer.zoffset(self.layers))

        return keys

    def outline(self, options):
        """
        Moves the cursor to the northwest corner, then clockwise to each
        other corner, before returning to the starting position.
        """
        buildconfig = BuildConfig('dig')
        grid = self.layers[0].grid
        ks = Keystroker(grid, buildconfig)
        keys = []

        # move to each corner beginning with NW, going clockwise, and wait
        # at each one
        lastpos = self.start
        for cornerdir in [Direction(d) for d in
                ['nw', 'ne', 'se', 'sw', 'nw'] ]:
            newpos = Point(
                max(0, cornerdir.delta().x) * (grid.width - 1),
                max(0, cornerdir.delta().y) * (grid.height - 1)
                )

            keys += ks.move(lastpos, newpos, allowjumps=False) + ['%']
            lastpos = newpos
        keys += ks.move(lastpos, self.start, allowjumps=False)

        # trim any pauses off the ends
        while keys[0] == '%':
            keys = keys[1:]
        while keys[-1] == '%':
            keys = keys[:-1]

        return keys

    def get_info(self):
        """Retrieve various bits of info about the blueprint."""
        cells = flatten(layer.grid.rows for layer in self.layers)
        commands = [c.command for c in cells]
        cmdset = set(commands) # uniques
        if '' in cmdset:
            cmdset.remove('')

        # count the number of occurrences of each command in the blueprint
        counts = [(c, commands.count(c)) for c in cmdset]
        counts.sort(key=lambda x: x[1], reverse=True)

        return textwrap.dedent("""
            Blueprint name: %s
            Build type: %s
            Comment: %s
            Start position: %s
            Start comment: %s
            First layer width: %d
            First layer height: %d
            Layer count: %d
            Command use counts: %s
            """).strip() % (
                self.name,
                self.build_type,
                self.comment or '',
                Point(self.start.x + 1, self.start.y + 1),
                self.start_comment or '',
                self.layers[0].grid.width,
                self.layers[0].grid.height,
                len(self.layers),
                ', '.join("%s:%d" % c for c in counts)
                ) + \
            "\nBlueprint preview:\n" + \
                '\n'.join(
                    Grid.str_commands(layer.grid.rows) + \
                        '\n#' + ''.join(layer.onexit)
                    for layer in self.layers
                )
