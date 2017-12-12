from _graph_plotter import GraphPlotter
import iris
import iris.quickplot as qplt
import matplotlib.pyplot as plt
from ukcp_dp.constants import DATA_SOURCE_PROB, InputType

import logging
log = logging.getLogger(__name__)


class CdfPlotter(GraphPlotter):
    """
    The cdf plotter class.

    This class extends BasePlotter with a _generate_graph(self, cube).
    """

    def _generate_graph(self):
        """
        Override base class method.

        """
        log.debug('_generate_graph')

        if (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_PROB):

            for scenario_cube in self.cube_list:
                scenario_cube.data.sort()
                # plot the percentiles
                qplt.plot(scenario_cube, scenario_cube.dim_coords[0])

        # clear the title field
        plt.title('')
