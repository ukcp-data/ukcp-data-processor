from _graph_plotter import GraphPlotter
import iris
import iris.quickplot as qplt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.pyplot as plt
from ukcp_dp.constants import DATA_SOURCE_PROB, InputType

import logging
log = logging.getLogger(__name__)


class CdfPlotter(GraphPlotter):
    """
    The cdf plotter class.

    This class extends BasePlotter with a _generate_graph(self).
    """

    def _generate_graph(self, cmap):
        """
        Override base class method.

        @param cmap(LinearSegmentedColormap): colour map to use with plot
        """
        log.debug('_generate_graph')

        # there must be a better way to do this
        count = 0
        for _ in self.cube_list:
            count += 1

        cNorm = colors.Normalize(vmin=0, vmax=count)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)

        if (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_PROB):

            for i, scenario_cube in enumerate(self.cube_list):
                scenario_cube.data.sort()
                colorVal = scalarMap.to_rgba(i + 1)
                qplt.plot(scenario_cube, scenario_cube.dim_coords[0],
                          label=scenario_cube.attributes['scenario'],
                          color=colorVal)

        # clear the title field
        plt.title('')
