from _graph_plotter import GraphPlotter
from ukcp_dp.constants import InputType, CONTOUR_COLOUR, CONTOUR_GREYSCALE

import matplotlib.pyplot as plt
import numpy as np

import logging

log = logging.getLogger(__name__)


class JpPlotter(GraphPlotter):
    """
    The join probability plotter class.

    This class extends BasePlotter with a _generate_graph(self).
    """

    def _generate_graph(self):
        """
        Override base class method.

        """
        log.debug('_generate_graph')

        x = self.cube_list[0].data
        x_label = self.cube_list[0].name()
        y = self.cube_list[1].data
        y_label = self.cube_list[1].name()

        h, xedges, yedges = np.histogram2d(x, y, bins=20)
        xbins = xedges[:-1] + (xedges[1] - xedges[0]) / 2
        ybins = yedges[:-1] + (yedges[1] - yedges[0]) / 2

        h = h.T

        if self.input_data.get_value(InputType.COLOUR_MODE) == 'c':
            CS = plt.contour(xbins, ybins, h, colors=CONTOUR_COLOUR)
        else:
            CS = plt.contour(xbins, ybins, h, colors=CONTOUR_GREYSCALE)
        CS.clabel(fmt='%1.0f')
        plt.xlabel(x_label)
        plt.ylabel(y_label)
