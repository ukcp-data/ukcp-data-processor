import logging

from _graph_plotter import GraphPlotter
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid.anchored_artists import AnchoredText
import numpy as np
from ukcp_dp.constants import InputType, CONTOUR_LINE, CONTOUR_FILL


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
        x_id = self.input_data.get_value(InputType.VARIABLE)[0]
        y = self.cube_list[1].data
        y_id = self.input_data.get_value(InputType.VARIABLE)[1]

        h, xedges, yedges = _histogram2d(x, y)

        xbins = xedges[:-1] + (xedges[1] - xedges[0]) / 2
        ybins = yedges[:-1] + (yedges[1] - yedges[0]) / 2

        x_min, x_max = _get_limits(h, xedges)
        h = h.T
        y_min, y_max = _get_limits(h, yedges)

        ax = plt.gca()
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        levels = [10, 50, 90]
        # fill the contours
        contour_fill = plt.contourf(xbins, ybins, h, levels,
                                    colors=CONTOUR_FILL,
                                    extend='max', label=levels)

        # now add the lines
        plt.contour(xbins, ybins, h, levels, colors=CONTOUR_LINE)

        plt.xlabel(self.input_data.get_value_label(InputType.VARIABLE)[0])
        plt.ylabel(self.input_data.get_value_label(InputType.VARIABLE)[1])

        legend_box = [plt.Rectangle((0, 0), 1, 1, fc=pc.get_facecolor()[0])
                      for pc in contour_fill.collections]

        plt.legend(legend_box, ["Central 90% of projections",
                                "Central 50% of projections",
                                "Central 10% of projections"],
                   loc=self.input_data.get_value(InputType.LEGEND_POSITION))

        # if temp anom and pr anom, then add annotations
        if ((x_id == 'tasAnom' or y_id == 'tasAnom') and
                (x_id == 'prAnom' or y_id == 'prAnom')):
            font_size = self.input_data.get_font_size() + 10

            at = AnchoredText("hotter and wetter",
                              prop=dict(color='#612020', size=font_size),
                              frameon=False, loc=1)
            ax.add_artist(at)

            at = AnchoredText("colder and drier",
                              prop=dict(color='#2F7676', size=font_size),
                              frameon=False, loc=3)
            ax.add_artist(at)


def _histogram2d(x, y):
    """
    Using the default range some of the plots are getting chopped. Therefore we
    are using a custom range. The range is incrementally increased until the
    10th percentile boundary is included.
    """
    for i in range(10):
        range_factor = 1.0 + (float(i) / 10)
        range_ = [[min(x) * range_factor, max(x) * range_factor],
                  [min(y) * range_factor, max(y) * range_factor]]

        h, xedges, yedges = np.histogram2d(x, y, bins=10, range=range_)
        h1 = h.T
        if (max(h[0]) < 10 and max(h[len(h) - 1]) < 10 and
                max(h1[0]) < 10 and max(h1[len(h1) - 1]) < 10):
            break

    log.debug("Generating histogram with a range factor of {}".format(
        range_factor))
    return h, xedges, yedges


def _get_limits(data, edges):
    """
    Get the limits, defined as were the data goes above 9.
    To ensure we do not clip the image include the next bin
    """
    min_limit = 0
    max_limit = 0

    edge_count = len(edges)
    for i, row in enumerate(data):

        if max(row) > 9:
            if i + 2 > edge_count:
                max_limit = edges[i + 1]
            else:
                max_limit = edges[i + 2]
            if min_limit == 0:
                if i > 0:
                    min_limit = edges[i - 1]
                else:
                    min_limit = edges[i]
    return min_limit, max_limit
