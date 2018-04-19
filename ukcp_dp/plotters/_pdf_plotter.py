import logging

from _graph_plotter import GraphPlotter
import iris
import iris.quickplot as qplt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
from ukcp_dp.constants import DATA_SOURCE_PROB, InputType, SCENARIO_COLOURS, \
    SCENARIO_GREYSCALES


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

        if self.input_data.get_value(InputType.COLOUR_MODE) == 'c':
            colours = SCENARIO_COLOURS

        else:
            colours = SCENARIO_GREYSCALES

        if (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_PROB):

            for cube in self.cube_list:
                # plot the percentiles
                cube.data.sort()

                cube = self._add_dx(cube)
                qplt.plot(self.cube_list, self.cube_list.coord(
                    'relative probability'),
                    linestyle=colours[cube.attributes['scenario']][1],
                    color=colours[cube.attributes['scenario']][0])

        plt.xlabel(self.input_data.get_value_label(InputType.VARIABLE)[0])

        # clear the title field
        plt.title('')

    def _add_dx(self, cube):
        gradient = np.gradient(cube.coord('percentile').points, cube.data)
        gradient_dim = iris.coords.AuxCoord(
            gradient, long_name='relative probability')
        cube.add_aux_coord(gradient_dim, 0)

        return cube
