import logging

from _graph_plotter import GraphPlotter
import iris
import iris.quickplot as qplt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from ukcp_dp.constants import DATA_SOURCE_PROB, InputType, SCENARIO_COLOURS, \
    SCENARIO_GREYSCALES


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
            linestyle = ['solid', 'solid', 'solid', 'solid', 'solid']

        else:
            colours = SCENARIO_GREYSCALES
            linestyle = ['solid', 'dashed', 'dotted', 'solid', 'dashed']

        if (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_PROB):

            for i, scenario_cube in enumerate(self.cube_list):
                scenario_cube.data.sort()

                label = self.vocab.get_collection_term_label(
                    InputType.SCENARIO, scenario_cube.attributes['scenario'])
                qplt.plot(scenario_cube, scenario_cube.dim_coords[0],
                          label=label, linestyle=linestyle[i],
                          color=colours[i])

        plt.xlabel(self.input_data.get_value_label(InputType.VARIABLE)[0])

        # clear the title field
        plt.title('')
