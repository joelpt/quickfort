"""Blueprint class and associated processing functions."""

import os
import re
import textwrap

import aliases
import buildconfig
import exetest
import filereader
import keystroker
import router
import transformer
import util

from copy import deepcopy

from log import log_routine, logmsg, loglines
from areaplotter import AreaPlotter
from buildconfig import BuildConfig
from filereader import FileLayer, FileLayers_to_GridLayers
from geometry import Direction, add_points
from grid import GridLayer, Grid
from keystroker import Keystroker
from transformer import Transformer

from errors import BlueprintError, ParametersError


def get_blueprint_info(path, transform_str):
    """
    Returns information about the blueprint at path. If transform_str
    is given, blueprint will be transformed accordingly before returning.
    """
    sheets = filereader.get_sheet_names(path)

    newphase, transforms, ztransforms = \
        transformer.parse_transform_str(transform_str)

    result = ''
    for sheet in sheets:
        try:
            (layers, details) = filereader.parse_file(path, sheet[1])

            # transform the blueprint
            if transforms is not None:
                logmsg('transform', 'Transforming with: %s' % transform_str)

                if newphase is not None:
                    details['build_type'] = buildconfig.get_full_build_type_name(newphase)

                tran = Transformer(layers, details['start'])
                tran.transform(transforms)  # do the x/y transformations
                details['start'] = tran.start
                layers = tran.layers

                logmsg('transform', 'Results of transform:')
                loglines('transform', lambda: FileLayer.str_layers(layers))

            layers = FileLayers_to_GridLayers(layers)
            bp = Blueprint(sheet[0], layers, details)

            # perform any requested z-transforms
            if ztransforms is not None:
                layers = bp.repeat_ztransforms(ztransforms, bp.layers,
                    Blueprint.repeater_layers)
                bp.layers = layers

            formatted = bp.get_info()

            # add this sheet's info to the result string
            result += '>>>> Sheet id %d\n' % sheet[1]
            result += formatted + '\n'
        except BlueprintError as ex:
            continue    # ignore blank/missing sheets

    if result:
        return result
    else:
        raise BlueprintError("No valid blueprints found in '%s'." % path)


@log_routine('file', 'INPUT FILE SOURCE PROCESSING')
def process_blueprint_file(path, sheetid, startpos, transform_str,
    output_mode, output_title, visualize):
    """
    Parses a blueprint file and converts it to desired output.
    """

    # parse sheetid
    if sheetid is None:
        sheetid = 0
    elif not re.match('^\d+$', str(sheetid)):
        # TODO Fix this so it works
        sheetid = filereader.get_sheet_names(path)[1]

    # read in the blueprint
    layers, details = filereader.parse_file(path, sheetid)

    logmsg('file', 'Parsed %s' % path)
    loglines('file', lambda: FileLayer.str_layers(layers))

    return convert_blueprint(layers, details, startpos, transform_str,
        output_mode, output_title, visualize)


@log_routine('file', 'COMMAND LINE SOURCE PROCESSING')
def process_blueprint_command(command, startpos, transform_str, output_mode,
    output_title, visualize):
    """
    Parses a QF one-line command and converts it to the desired output.
    """

    layers, details = filereader.parse_command(command)

    logmsg('file', 'Parsed %s' % command)
    loglines('file', lambda: FileLayer.str_layers(layers))

    return convert_blueprint(layers, details, startpos, transform_str,
        output_mode, output_title, visualize)


@log_routine('file', 'BLUEPRINT CONVERSION')
def convert_blueprint(layers, details, startpos, transform_str,
    output_mode, output_title, visualize):
    """
    Transforms the provided layers if required by transform_str, then renders
    keystrokes/macros required to plot or visualize the blueprint specified
    by layers and details and pursuant to args.
    """

    # apply aliases.txt to blueprint contents
    # TODO abstract this better
    alii = aliases.load_aliases(
        os.path.join(exetest.get_main_dir(), 'config/aliases.txt'))

    layers = aliases.apply_aliases(layers, alii)

    # transform the blueprint
    ztransforms = []
    if transform_str:
        logmsg('transform', 'Transforming with: %s' % transform_str)

        newphase, transforms, ztransforms = \
            transformer.parse_transform_str(transform_str)

        if newphase is not None:
            details['build_type'] = buildconfig.get_full_build_type_name(newphase)

        tran = Transformer(layers, details['start'])
        tran.transform(transforms)  # do the x/y transformations
        details['start'] = tran.start
        layers = tran.layers

        logmsg('file', 'Results of transform:')
        loglines('file', lambda: FileLayer.str_layers(layers))

    layers = FileLayers_to_GridLayers(layers)

    if not layers:  # empty blueprint handling
        raise BlueprintError("Blueprint appears to be empty.")

    # override starting position if startpos command line option was given
    if startpos is not None:
        details['start'] = parse_startpos(startpos,
            layers[0].grid.width,
            layers[0].grid.height)

    # convert layers and other data to Blueprint
    bp = Blueprint('', layers, details)

    # get keys/macrocode to outline or plot the blueprint
    keys = []
    if output_mode == 'csv':
        bp.analyze()
        # perform any awaiting z-transforms
        layers = bp.repeat_ztransforms(ztransforms, bp.layers,
            Blueprint.repeater_layers)
        bp.layers = layers
        output = str(bp)
    else:
        if visualize:
            keys = bp.trace_outline()
        else:
            bp.analyze()
            keys = bp.plot(ztransforms)
        output = keystroker.convert_keys(keys, output_mode, output_title)

    loglines('summary', lambda: str_summary(bp, keys))

    return output


def str_summary(bp, keys):
    s = ">>>> BEGIN SUMMARY\n"
    s += "---- Layers:\n"
    for i, layer in enumerate(bp.layers):
        s += '\n'.join([
            "=" * 20 + ' Layer %d ' % i + '=' * 20,
            "Entering cursor position: %s" % str(layer.start),
            "#### Commands:",
            str(layer.grid),
            "#### Area labels:",
            Grid.str_area_labels(layer.grid),
            "Route order: %s" % ''.join(
                [layer.grid.get_cell(x, y).label
                    for x, y in layer.plots]
                ),
            "Layer onexit keys: %s" % layer.onexit,
            ""
            ])
    s += "\n---- Overall:\n"
    s += "Total key cost: %d" % len(keys) + '\n'
    s += "<<<< END SUMMARY"
    return s


def parse_startpos(start, width, height):
    """Transform startpos string like (1,1) or nw to corresponding Point."""

    # try (#,#) type syntax
    m = re.match(r'\(?(\d+)[,;](\d+)\)?', start)
    if m is not None:
        return (int(m.group(1)), int(m.group(2)))

    # try corner-coordinate syntax
    m = re.match(r'(ne|nw|se|sw)', start.lower())
    if m is not None:
        # convert corner String -> Direction -> (x, y) then magnify (x, y)
        # by width and height to get the corner coordinate we want
        (x, y) = Direction(m.group(1)).delta()
        point = (
            max(0, x) * (width - 1),
            max(0, y) * (height - 1)
        )

        return point

    raise ParametersError("Invalid --position parameter '%s'" % start)


class Blueprint:
    """
    Represents a single blueprint (csv file or sheet in xls/x file).
    Provides high level methods for plotting, outlining, and retrieving
    information about the blueprint.
    """

    def __init__(self, name, layers, details):
        self.name = name
        self.layers = layers
        self.build_type = details['build_type']
        self.build_config = BuildConfig(self.build_type)
        self.start = details['start']
        self.start_comment = details['start_comment']
        self.comment = details['comment']

    def analyze(self):
        """Performs contiguous area expansion and discovery in the layers."""
        for layer in self.layers:
            plotter = AreaPlotter(layer.grid, self.build_config)

            plotter.expand_fixed_size_areas()   # plot cells of d(5x5) format
            plotter.discover_areas()            # find contiguous areas

            layer.grid = plotter.grid           # update

    def plot(self, ztransforms):
        """Plots a route through the blueprint, then does ztransforms."""
        keys = []
        cursor = self.start
        ks = None

        for layer in self.layers:
            layer.start = cursor  # first layer's start or last layer's exit pos

            # plan the cursor's route to designate all the areas
            layer.grid, layer.plots, end = router.plan_route(
                layer.grid, cursor)

            # generate key/macro sequence to render this series of plots in DF
            ks = Keystroker(layer.grid, self.build_config)
            layerkeys, cursor = ks.plot(layer.plots, cursor)
            keys += layerkeys + layer.onexit

        # move cursor back to start pos x, y, so start==end
        keys += ks.move(cursor, self.start, 0)
        #start = end

        # perform any awaiting z-transforms
        keys = self.repeat_ztransforms(ztransforms, keys, self.repeater_keys)

        return keys

    def repeat_ztransforms(self, ztransforms, data, repeatfun):
        """
        Performs ztransform repetitions given some ztransforms [('2', 'd'),..],
        initial data, and a repeatfun (Function) to appply for each ztransform.
        The output of each ztransform is fed as input to the next.
        """
        if len(ztransforms) == 0:
            return data

        zdelta = GridLayer.zoffset(self.layers)
        for t in ztransforms:
            count, command = t
            if count < 2:
                continue

            if command not in ('d', 'u'):
                raise ParametersError('Unrecognized ztransform ' + command)

            # direction we want to move: 1=zdown, -1=zup
            dirsign = 1 if command == 'd' else -1

            # if we want to move in the same direction as the stack does,
            # we only need to move 1 z-level in that direction
            if dirsign * zdelta > 0:  # if signs of dirsign and zdelta match...
                zdelta = 0  # 'no z-change caused by stack'

            # with a ztransform moving in the opposite direction we
            # need to move twice the height of the blueprint-stack
            # so that the subsequent repetition of the original blueprint's
            # keys can playback without overlapping onto zlevels
            # that we'll have already designated
            zdistance = dirsign * (-1 + 2 * (1 + (dirsign * -zdelta)))

            # apply fn given the z-distance required to travel
            data = repeatfun(data, zdistance, count)
            zdelta = ((zdelta + 1) * count) - 1

        return data

    @staticmethod
    def repeater_keys(keys, zdistance, reps):
        zmove = Keystroker.get_z_moves(zdistance)
        # assemble repetition of z layers' keys
        keys = ((keys + zmove) * (reps - 1)) + keys

        return keys

    @staticmethod
    def repeater_layers(layers, zdistance, reps):
        zmove = Keystroker.get_z_moves(zdistance)
        newlayers = []
        for x in range(1, reps):
            newlayers += deepcopy(layers)
            newlayers[-1].onexit = zmove
        newlayers += deepcopy(layers)
        return newlayers

    def trace_outline(self):
        """
        Moves the cursor to the northwest corner, then clockwise to each
        other corner, before returning to the starting position.
        """
        buildconfig = BuildConfig('dig')
        grid = self.layers[0].grid

        plotter = AreaPlotter(grid, buildconfig)
        plotter.expand_fixed_size_areas()  # plot cells of d(5x5) format

        ks = Keystroker(grid, buildconfig)
        keys = []

        # move to each corner beginning with NW, going clockwise, and wait
        # at each one
        lastpos = self.start
        for cornerdir in [Direction(d) for d in ['nw', 'ne', 'se', 'sw', 'nw']]:
            (x, y) = cornerdir.delta()
            newpos = (
                max(0, x) * (grid.width - 1),
                max(0, y) * (grid.height - 1)
            )

            keys += ks.move(lastpos, newpos, allowjumps=False) + ['%']
            lastpos = newpos
        keys += ks.move(lastpos, self.start, allowjumps=False)

        # trim any pauses off the ends
        while keys and keys[0] == '%':
            keys = keys[1:]
        while keys and keys[-1] == '%':
            keys = keys[:-1]

        # if the result is no keys, return a single wait key
        keys += ['%']

        return keys

    def get_info(self):
        """Retrieve various bits of info about the blueprint."""
        rowsets = [layer.grid.rows for layer in self.layers]
        cells = map(lambda r: r.flatten(), rowsets)
        if len(cells) == 0:
            raise BlueprintError('No row data in blueprint.')
        commands = [c.command for c in cells[0]]
        cmdset = set(commands)  # uniques
        if '' in cmdset:
            cmdset.remove('')

        # count the number of occurrences of each command in the blueprint
        counts = [(c, commands.count(c)) for c in cmdset]
        counts.sort(key=lambda x: x[1], reverse=True)

        # look for the manual-mat character anywhere in the commands,
        # and check that phase=build (the only mode that we'll support
        # manual material selection with right now)
        uses_manual_mats = util.is_substring_in_list(':', cmdset) and \
            self.build_type == 'build'

        # make a row of repeating numbers to annotate the blueprint with
        width = self.layers[0].grid.width

        # build the blueprint preview
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
                add_points(self.start, (1, 1)),
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

        if self.start != (0, 0):
            out += ' start(%d; %d' % (self.start[0] + 1, self.start[1] + 1)
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
                footer = [''.join(layer.onexit)] + (['#'] * width)
            else:
                footer = ['#'] * (width + 1)
            outrows += [','.join(footer)]

        return '\n'.join(outrows)
