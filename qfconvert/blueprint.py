import textwrap

from util import Struct
from areaplotter import AreaPlotter
from buildconfig import BuildConfig
from geometry import *
from keystroker import Keystroker, convert_keys
from router import Router
from transformer import *
from filereader import FileLayer
import filereader
import transformer

def get_blueprint_info(path):
    sheets = filereader.get_sheets(path)
    s = ''
    for sheet in sheets:
        (layers, build_type, start, start_comment, comment) = \
            filereader.parse_file(path, sheet[1])
        bp = Blueprint(sheet[0], layers, build_type, start, start_comment,
            comment)
        s += '---- Sheet id %d ----\n' % sheet[1]
        s += bp.get_info() + '\n'
    return s

def process_blueprint_file(path, options):
    if options.debugfile: print ">>>> BEGIN INPUT FILE PARSING"
    sheetid = options.sheetid
    (layers, build_type, start, start_comment, comment) = \
        filereader.parse_file(path, sheetid)

    if options.debugfile:
        print '#### Parsed %s' % path
        print FileLayer.str_layers(layers)

    if options.transform:
        if options.debugfile:
            print "#### Transforming with: %s" % options.transform
        transforms = transformer.parse_transform_str(options.transform)
        layers = transformer.transform(transforms, layers)

        if options.debugfile: FileLayer.str_layers(layers)

    # convert layers and other data to Blueprint
    bp = Blueprint('', layers, build_type, start, start_comment, comment)

    if options.debugfile: print ">>>> END INPUT FILE PARSING"

    keys = bp.plot(options)
    output = convert_keys(keys, options.mode, options.title)

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

    return output


class Blueprint:

    def __init__(self, name, layers, build_type, start, start_comment,
        comment):

        gridlayers = filereader.FileLayers_to_GridLayers(layers)
        (self.name, self.layers, self.build_type, self.start,
            self.start_comment, self.comment) = \
            (name, gridlayers, build_type, start, start_comment, comment)

    def plot(self, options):
        """Plots a route through the provided blueprint."""
        buildconfig = BuildConfig(self.build_type, options)
        keys = []
        start = self.start
        ks = None
        for layer in self.layers:
            grid = layer.grid
            layer.start = start

            plotter = AreaPlotter(grid, buildconfig, options.debugarea)
            plotter.expand_fixed_size_areas()  #  plot cells of d(5x5) format
            plotter.discover_areas() # find contiguous areas

            grid = plotter.grid
            router = Router(grid, options.debugrouter)
            plots, end = router.plan_route(start)
            layer.plots = plots

            # generate key sequence to render this series of plots in game
            ks = Keystroker(grid, buildconfig)
            keys += ks.plot(plots, start) + layer.onexit
            start = end

        # move cursor back to start pos
        keys += ks.move(end, self.start)

        return keys


    def get_info(self):
        cells = flatten(layer.grid.cells for layer in self.layers)
        commands = [c.command for c in cells]
        cmdset = set(commands) # uniques
        if '' in cmdset:
            cmdset.remove('')
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
            Command frequencies: %s
            """).strip() % (
                self.name,
                self.build_type,
                self.comment or '',
                self.start,
                self.start_comment or '',
                self.layers[0].grid.width,
                self.layers[0].grid.height,
                len(self.layers),
                ', '.join("%s:%d" % c for c in counts)
                )
