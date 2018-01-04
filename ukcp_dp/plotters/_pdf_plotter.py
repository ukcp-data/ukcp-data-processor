from _graph_plotter import GraphPlotter
from ukcp_dp.constants import DATA_SOURCE_PROB, InputType, SCENARIO_COLOURS, \
    SCENARIO_GREYSCALE_PALETTE
import iris
import iris.quickplot as qplt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np

import logging
log = logging.getLogger(__name__)


class PdfPlotter(GraphPlotter):
    """
    The pdf plotter class.

    This class extends BasePlotter with a _generate_graph(self).
    """

    def _generate_graph(self):
        """
        Override base class method.

        """
        log.debug('_generate_graph')

        # there must be a better way to do this
        count = 0
        for _ in self.cube_list:
            count += 1

        if self.input_data.get_value(InputType.COLOUR_MODE) == 'g':
            cmap = SCENARIO_GREYSCALE_PALETTE
            c_norm = colors.Normalize(vmin=0, vmax=count)
            scalar_map = cmx.ScalarMappable(norm=c_norm, cmap=cmap)

        if (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_PROB):

            for i, cube in enumerate(self.cube_list):
                # plot the percentiles
                cube.data.sort()

                if self.input_data.get_value(InputType.COLOUR_MODE) == 'c':
                    colour_val = SCENARIO_COLOURS[i]
                else:
                    colour_val = scalar_map.to_rgba(i + 1)

                cube = self._add_dx(cube)
                qplt.plot(self.cube_list, self.cube_list.coord(
                    'relative probability'), color=colour_val)

        # clear the title field
        plt.title('')

    def _add_dx(self, cube):
        gradient = np.gradient(cube.coord('percentile').points, cube.data)
        gradient_dim = iris.coords.AuxCoord(
            gradient, long_name='relative probability')
        cube.add_aux_coord(gradient_dim, 0)

        return cube
