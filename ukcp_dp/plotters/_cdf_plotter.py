import logging

from _graph_plotter import GraphPlotter
import iris
import iris.quickplot as qplt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from ukcp_dp.constants import CDF_LABEL, COLLECTION_PROB, InputType, \
    SCENARIO_COLOURS, SCENARIO_GREYSCALES


log = logging.getLogger(__name__)


class CdfPlotter(GraphPlotter):
    """
    The cdf plotter class.

    This class extends BasePlotter with a _generate_graph(self).
    """

    def _generate_graph(self):
        """
        Override base class method.

        """
        log.debug('_generate_graph')

        if self.input_data.get_value(InputType.COLOUR_MODE) == 'c':
            colours = SCENARIO_COLOURS

        else:
            colours = SCENARIO_GREYSCALES

        if (self.input_data.get_value(InputType.COLLECTION) !=
                COLLECTION_PROB):
            raise Exception('A CDF plot requires probabilistic data')

        for scenario_cube in self.cube_list:
            label = self.vocab.get_collection_term_label(
                InputType.SCENARIO, scenario_cube.attributes['scenario'])
            plt.plot(
                scenario_cube.data, scenario_cube.coord('percentile').points,
                label=label,
                linestyle=colours[scenario_cube.attributes['scenario']][1],
                color=colours[scenario_cube.attributes['scenario']][0])

        plt.xlabel(self.input_data.get_value_label(InputType.VARIABLE)[0])
        plt.ylabel(CDF_LABEL)
