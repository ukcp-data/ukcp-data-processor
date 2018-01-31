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
        x_id = self.cube_list[0].attributes['var_id']
        x_label = self.vocab.get_collection_term_label(
            InputType.VARIABLE, x_id)
        y = self.cube_list[1].data
        y_id = self.cube_list[1].attributes['var_id']
        y_label = self.vocab.get_collection_term_label(
            InputType.VARIABLE, y_id)

        h, xedges, yedges = np.histogram2d(x, y, bins=10)
        xbins = xedges[:-1] + (xedges[1] - xedges[0]) / 2
        ybins = yedges[:-1] + (yedges[1] - yedges[0]) / 2
        h = h.T

        levels = [10, 50, 90]
        # fill the contours
        contour_fill = plt.contourf(xbins, ybins, h, levels,
                                    colors=CONTOUR_FILL,
                                    extend='max', label=levels)

        # now add the lines
        plt.contour(xbins, ybins, h, levels, colors=CONTOUR_LINE)

        plt.xlabel(x_label)
        plt.ylabel(y_label)

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
            ax = plt.gca()

            at = AnchoredText("hotter and wetter",
                              prop=dict(color='#612020', size=font_size),
                              frameon=False, loc=1)
            ax.add_artist(at)

            at = AnchoredText("colder and drier",
                              prop=dict(color='#2F7676', size=font_size),
                              frameon=False, loc=3)
            ax.add_artist(at)
