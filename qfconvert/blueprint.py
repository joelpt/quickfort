from util import Struct
from areaplotter import AreaPlotter
from buildconfig import BuildConfig
from geometry import *
from keystroker import Keystroker
from router import Router
from transformer import *
import filereader


def read_blueprint(path, options):
    """read the specified blueprint file into a new Blueprint"""
    bp = filereader.parse_file(path)
    # print len(bp.layers)
    if not bp.start:
        bp.start = Point(0, 0)
    return bp


class Blueprint (Struct):

    layers = None
    build_type = None
    start = None
    start_comment = None
    comment = None

    def plot(self, options):
        """Plots a route through the provided blueprint."""
        buildconfig = BuildConfig(self.build_type, options)
        keys = []
        start = self.start
        for layer in self.layers:
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
