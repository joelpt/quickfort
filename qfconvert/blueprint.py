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


def process_blueprint_file(path, options):
    if options.debugfile: print ">>>> BEGIN INPUT FILE PARSING"

    (layers, build_type, start, start_comment, comment) = \
        filereader.parse_file(path)

    if options.debugfile:
        print '#### Parsed %s' % path
        print FileLayer.str_layers(layers)

    if options.transform:
        if options.debugfile:
            print "#### Transforming with: %s" % options.transform
        transforms = transformer.parse_transform_str(options.transform)
        layers = transformer.transform(transforms, layers)

        if options.debugfile: FileLayer.print_layers(layers)

    # convert layers and other data to Blueprint
    bp = Blueprint(layers, build_type, start, start_comment, comment)

    if options.debugfile: print ">>>> END INPUT FILE PARSING"

    if options.info:
        output = bp.get_info()
    else:
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

    def __init__(self, layers, build_type, start, start_comment, comment):
        gridlayers = filereader.FileLayers_to_GridLayers(layers)
        (self.layers, self.build_type, self.start,
            self.start_comment, self.comment) = \
            (gridlayers, build_type, start, start_comment, comment)

    def plot(self, options):
        """Plots a route through the provided blueprint."""
        buildconfig = BuildConfig(self.build_type, options)
        keys = []
        start = self.start
        ks = None
        for layer in self.layers:
            grid = layer.grid
            layer.start = start

            ## TODO plot_predefined_areas()

            # plot areas to be built on the grid
            plotter = AreaPlotter(grid, buildconfig, options.debugarea)
            if not plotter.discover_areas():
                raise

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
        return textwrap.dedent("""
            Build type: %s
            Comment: %s
            Start position: %s
            Start comment: %s
            First layer width: %d
            First layer height: %d
            Layer count: %d
            """).strip() % (
                self.build_type,
                self.comment or '',
                self.start,
                self.start_comment or '',
                self.layers[0].grid.width,
                self.layers[0].grid.height,
                len(self.layers)
                )
