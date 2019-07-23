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

        for cube in self.cube_list:
            if (cube.var_name == self.input_data.get_value(
                    InputType.VARIABLE)[0]):
                x = cube.data
                x_id = self.input_data.get_value(InputType.VARIABLE)[0]
            elif (cube.var_name == self.input_data.get_value(
                    InputType.VARIABLE)[1]):
                y = cube.data
                y_id = self.input_data.get_value(InputType.VARIABLE)[1]

        h, xedges, yedges = np.histogram2d(x, y, bins=10)

        # x width and y width, and half widths
        xw = xedges[1] - xedges[0]
        yw = yedges[1] - yedges[0]
        xw_2 = xw*0
        yw_2 = yw*0

        # copy the data into the middle of an array that falls to zero at each
        # edge
        xbins = xedges[0] - xw_2 + [x*xw for x in range(0, len(xedges)+1)]
        ybins = yedges[0] - yw_2 + [y*yw for y in range(0, len(yedges)+1)]

        new_h = np.zeros([len(xbins), len(ybins)], h.dtype)
        new_h[1:-1, 1:-1] = h

        x_min, x_max = _get_limits(new_h, xbins)
        h = h.T
        y_min, y_max = _get_limits(new_h, ybins)

        ax = plt.gca()
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        levels = [10, 50, 90]
        # fill the contours
        contour_fill = plt.contourf(xbins, ybins, new_h, levels,
                                    colors=CONTOUR_FILL,
                                    extend='max', label=levels)

        # now add the lines
        plt.contour(xbins, ybins, new_h, levels, colors=CONTOUR_LINE)

        plt.xlabel(self.input_data.get_value_label(InputType.VARIABLE)[0])
        plt.ylabel(self.input_data.get_value_label(InputType.VARIABLE)[1])

        legend_box = [plt.Rectangle((0, 0), 1, 1, fc=pc.get_facecolor()[0])
                      for pc in contour_fill.collections]

        legend_font_size = self.input_data.get_font_size() * 0.7
        plt.legend(legend_box, ["Central 90% of projections",
                                "Central 50% of projections",
                                "Central 10% of projections"],
                   loc=self.input_data.get_value(InputType.LEGEND_POSITION),
                   prop={'size': legend_font_size})

        # if temp anom and pr anom, then add annotations
        if ((x_id == 'tasAnom' or y_id == 'tasAnom') and
                (x_id == 'prAnom' or y_id == 'prAnom')):

            at = AnchoredText("hotter and wetter",
                              prop=dict(color='#612020',
                                        size=self.input_data.get_font_size()),
                              frameon=False, loc=1)
            ax.add_artist(at)

            at = AnchoredText("colder and drier",
                              prop=dict(color='#2F7676',
                                        size=self.input_data.get_font_size()),
                              frameon=False, loc=3)
            ax.add_artist(at)


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
            if i + 2 >= edge_count:
                max_limit = edges[edge_count - 1]
            else:
                max_limit = edges[i + 2]
            if min_limit == 0:
                if i > 0:
                    min_limit = edges[i - 1]
                else:
                    min_limit = edges[i]
    return min_limit, max_limit
