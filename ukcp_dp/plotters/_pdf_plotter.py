from _graph_plotter import GraphPlotter
from ukcp_dp.constants import DATA_SOURCE_PROB, InputType
import iris
import iris.quickplot as qplt
import matplotlib.pyplot as plt
import numpy as np

import logging
log = logging.getLogger(__name__)


class PdfPlotter(GraphPlotter):
    """
    The pdf plotter class.

    This class extends BasePlotter with a _generate_graph(self, cube).
    """

    def _generate_graph(self):
        """
        Override base class method.

        """
        log.debug('_generate_graph')
        if (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_PROB):
            for cube in self.cube_list:
                # plot the percentiles
                cube.data.sort()
                cube = self._add_dx(cube)
                qplt.plot(self.cube_list, self.cube_list.coord(
                    'relative probability'))

        # clear the title field
        plt.title('')

    def _add_dx(self, cube):
        gradient = np.gradient(cube.coord('percentile').points, cube.data)
        gradient_dim = iris.coords.AuxCoord(
            gradient, long_name='relative probability')
        cube.add_aux_coord(gradient_dim, 0)

        return cube
