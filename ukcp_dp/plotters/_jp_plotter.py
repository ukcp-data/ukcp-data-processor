from _graph_plotter import GraphPlotter
from ukcp_dp.constants import InputType, CONTOUR_LINE, CONTOUR_FILL

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

        h, xedges, yedges = np.histogram2d(x, y, bins=10)
        xbins = xedges[:-1] + (xedges[1] - xedges[0]) / 2
        ybins = yedges[:-1] + (yedges[1] - yedges[0]) / 2
        h = h.T

        levels = [10, 50, 90]
        # fill the contours
        plt.contourf(xbins, ybins, h, levels, colors=CONTOUR_FILL,
                     extend='max')

        # now add the lines
        plt.contour(xbins, ybins, h, levels, colors=CONTOUR_LINE)

        plt.xlabel(x_label)
        plt.ylabel(y_label)
