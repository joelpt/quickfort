"""Blueprint class and associated processing functions."""

import os
import re
import textwrap

import buildconfig
import exetest
import router
import util

from areaplotter import AreaPlotter
from buildconfig import BuildConfig
from filereader import FileLayer, FileLayers_to_GridLayers, get_sheets, parse_file, parse_command
from geometry import Point, Direction
from grid import GridLayer, Grid
from keystroker import Keystroker, convert_keys
from transformer import Transformer, parse_transform_str
from aliases import load_aliases, apply_aliases

def get_blueprint_info(path):
    """Returns information about the blueprint at path."""
    sheets = get_sheets(path)

    s = ''
    for sheet in sheets:
        try:
            (layers, details) = parse_file(path, sheet[1])
            layers = FileLayers_to_GridLayers(layers)
            bp = Blueprint(sheet[0], layers, details)
            s += '>>>> Sheet id %d\n' % sheet[1]
            s += bp.get_info() + '\n'
        except:
            continue # ignore blank/missing sheets

    if s:
        return s
    else:
        raise Exception, "No valid blueprints found in '%s'." % path


def process_blueprint_file(path, options):
    """
    Parses a blueprint file and converts it to desired output.
    """

    if options.debugfile:
        print ">>>> BEGIN INPUT FILE PARSING"

    # parse sheetid
    if options.sheetid is None:
        sheetid = 0
    elif re.match('^\d+$', str(options.sheetid)):
        sheetid = options.sheetid
    else:
        sheetid = get_sheets(path)

    # read in the blueprint
    layers, details = parse_file(path, sheetid)

    if options.debugfile:
        print '#### Parsed %s' % path
        print FileLayer.str_layers(layers)
        print "<<<< END INPUT FILE PARSING"

    return convert_blueprint(layers, details, options)


def process_blueprint_command(command, options):
    """
    Parses a QF one-line command and converts it to the desired output.
    """
    if options.debugfile:
        print ">>>> BEGIN COMMAND LINE PARSING"    

    layers, details = parse_command(command)

    if options.debugfile:
        print '#### Parsed %s' % command
        print FileLayer.str_layers(layers)
        print "<<<< END COMMAND LINE PARSING"    

    return convert_blueprint(layers, details, options)


def convert_blueprint(layers, details, options):
    """
    Transforms the provided layers if required by options, then renders
    keystrokes/macros required to plot or visualize the blueprint specified
    by layers and details and pursuant to options.
    """

    if options.debugfile:
        print ">>>> BEGIN CONVERSION"

    # apply aliases.txt to blueprint contents
    aliases = load_aliases(
        os.path.join(exetest.get_main_dir(), 'config/aliases.txt'))

    layers = apply_aliases(layers, aliases)

    # transform the blueprint
    ztransforms = []
    if options.transform:
        if options.debugtransform:
            print "#### Transforming with: %s" % options.transform

        newphase, transforms, ztransforms = \
            parse_transform_str(options.transform)

        if newphase is not None:
            details.build_type = buildconfig.get_full_build_type_name(newphase)

        tran = Transformer(layers, details.start, options.debugtransform)
        tran.transform(transforms) # do the x/y transformations
        details.start = tran.start
        layers = tran.layers

        if options.debugfile:
            print "#### Results of transform:"
            print FileLayer.str_layers(layers)

    layers = FileLayers_to_GridLayers(layers)

    if not layers: # empty blueprint handling
        raise Exception, "Blueprint appears to be empty."

    # override starting position if startpos command line option was given
    if options.startpos is not None:
        details.start = parse_startpos(options.startpos,
            layers[0].grid.width,
            layers[0].grid.height)

    # convert layers and other data to Blueprint
    bp = Blueprint('', layers, details)

    # get keys/macrocode to outline or plot the blueprint
    if options.mode == 'csv':
        bp.analyze(options)
        output = str(bp)
    else:
        if options.visualize:
            keys = bp.trace_outline(options)
        else:
            bp.analyze(options)
            keys = bp.plot(ztransforms, options)
        output = convert_keys(keys, options.mode, options.title)


    if options.debugfile:
        print "<<<< END CONVERSION"

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
        self.build_config = BuildConfig(self.build_type)
        self.start = details.start
        self.start_comment = details.start_comment
        self.comment = details.comment

    def analyze(self, options):
        """Performs contiguous area expansion and discovery in the layers."""
        for layer in self.layers:
            plotter = AreaPlotter(layer.grid, self.build_config,
                options.debugarea)
            
            plotter.expand_fixed_size_areas()  #  plot cells of d(5x5) format
            plotter.discover_areas() # find contiguous areas
            
            layer.grid = plotter.grid # update

    def plot(self, ztransforms, options):
        """Plots a route through the blueprint, then does ztransforms."""
        keys = []
        cursor = self.start
        ks = None

        for layer in self.layers:
            layer.start = cursor # first layer's start or last layer's exit pos

            # plan the cursor's route to designate all the areas
            layer.grid, layer.plots, end = router.plan_route(
                layer.grid, options.debugrouter, cursor)

            # generate key/macro sequence to render this series of plots in DF
            ks = Keystroker(layer.grid, self.build_config)
            layerkeys, cursor = ks.plot(layer.plots, cursor) 
            keys += layerkeys + layer.onexit

        # move cursor back to start pos x, y, so start==end
        keys += ks.move(cursor, self.start, 0)
        #start = end

        if len(ztransforms) > 0:
            # do z-transforms directly on keys array (much faster than actually
            # repeating and plotting those layers prior to generating keys)
            
            # relative z-layer-steps we have taken for the existing layers;
            # for single-z-layer blueprints this is 0, for blueprints with 1+ #>
            # it is >=1, and for blueprints with 1+ #< it is <=-1.
            zdelta = GridLayer.zoffset(self.layers)

            for t in ztransforms:
                count, command = t
                if count < 2:
                    continue
                
                if command not in ('d', 'u'):
                    raise Exception, 'Unrecognized ztransform ' + command
                
                # direction we want to move: 1=zdown, -1=zup
                dirsign = 1 if command == 'd' else -1

                # if we want to move in the same direction as the stack does,
                # we only need to move 1 z-level in that direction
                if dirsign * zdelta > 0: # if signs of dirsign and zdelta match
                    zdelta = 0 # 'no z-change caused by stack'

                # get keys needed to move desired number of z-levels
                # in desired z-direction; for multilevel blueprints combined
                # with a ztransform moving in the opposite direction we
                # need to move twice the height of the blueprint-stack
                # so that the subsequent repetition of the original blueprint's
                # keys can playback without overlapping onto zlevels
                # that we've already designated.
                zdistance = dirsign * (-1 + 2 * (1 + (dirsign * -zdelta)))
                zmove = ks.move(cursor, cursor, zdistance)

                # assemble repetition of z layers' keys
                keys = ((keys + zmove) * (count - 1)) + keys

        return keys

    def trace_outline(self, options):
        """
        Moves the cursor to the northwest corner, then clockwise to each
        other corner, before returning to the starting position.
        """
        buildconfig = BuildConfig('dig')
        grid = self.layers[0].grid

        plotter = AreaPlotter(grid, buildconfig, options.debugarea)
        plotter.expand_fixed_size_areas()  #  plot cells of d(5x5) format

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
        while keys and keys[0] == '%':
            keys = keys[1:]
        while keys and keys[-1] == '%':
            keys = keys[:-1]

        return keys

    def get_info(self):
        """Retrieve various bits of info about the blueprint."""
        cells = util.flatten(layer.grid.rows for layer in self.layers)
        commands = [c.command for c in cells]
        cmdset = set(commands) # uniques
        if '' in cmdset:
            cmdset.remove('')

        # count the number of occurrences of each command in the blueprint
        counts = [(c, commands.count(c)) for c in cmdset]
        counts.sort(key=lambda x: x[1], reverse=True)

        # look for the manual-mat character anywhere in the commands
        uses_manual_mats = util.is_substring_in_list(':', cmdset)

        # make a row of repeating numbers to annotate the blueprint with
        width = self.layers[0].grid.width
        numbering_row = '  ' + ('1234567890' * (width // 10))[0:width]

        # build the blueprint preview
        preview = numbering_row
        return textwrap.dedent("""
            Blueprint name: %s
            Build type: %s
            Comment: %s
            Start position: %s
            Start comment: %s
            First layer width: %d
            First layer height: %d
            Layer count: %d
            Uses manual material selection: %s
            Command use counts: %s
            """).strip() % (
                self.name,
                self.build_type,
                self.comment or '',
                Point(self.start.x + 1, self.start.y + 1),
                self.start_comment or '',
                width,
                self.layers[0].grid.height,
                len(self.layers),
                uses_manual_mats,
                ', '.join("%s:%d" % c for c in counts)
                ) + \
            "\nBlueprint preview:\n" + \
                '\n'.join(
                    Grid.str_commands(layer.grid.rows, annotate=True) + \
                        '\n#' + ''.join(layer.onexit)
                    for layer in self.layers
                )
        
    def str_header(self):
        """Output the header row for this blueprint definition."""
        out = '#' + self.build_type

        if not self.start.is_at_origin():
            out += ' start(%d; %d' % (self.start.x + 1, self.start.y + 1)
            out += '; ' + self.start_comment if self.start_comment else ''
            out += ')'
        
        if self.comment:
            out += ' ' + self.comment
        
        return out

    def __str__(self):
        """Output as CSV format."""
        
        outrows = [self.str_header()]

        for layer in self.layers:
            outrows += [Grid.str_csv(layer.grid)]
            width = layer.grid.width
            if layer.onexit:
                footer = layer.onexit + (['#'] * width)
            else:
                footer = ['#'] * (width + 1)
            outrows += [','.join(footer)]
        
        return '\n'.join(outrows)



