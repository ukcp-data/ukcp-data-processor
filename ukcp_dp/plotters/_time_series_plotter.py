"""
This module contains the TimeSeriesPlotter class, which implements the _generate_graph
method from the BasePlotter base class.

"""
import logging

import matplotlib.pyplot as plt
from ukcp_dp.constants import PERCENTILE_LINE_COLOUR, InputType
from ukcp_dp.plotters._graph_plotter import GraphPlotter
from ukcp_dp.plotters.utils._plotting_utils import get_time_series, set_x_limits

LOG = logging.getLogger(__name__)


# pylint: disable=R0903
class TimeSeriesPlotter(GraphPlotter):
    """
    The time series plotter class.

    This class extends BasePlotter with a _generate_graph(self).

    """

    def _generate_graph(self):
        """
        Override base class method.

        """
        LOG.debug("_generate_graph")
        ax = plt.gca()

        self._plot_single_line(self.cube_list[0], ax)

        # set the limits on the x axis, time axis
        set_x_limits(self.cube_list[0], ax)
        # add axis labels
        plt.xlabel("Year")

        if self.input_data.get_value(InputType.Y_AXIS_MAX) is not None:
            y_max = float(self.input_data.get_value(InputType.Y_AXIS_MAX))
            y_min = float(self.input_data.get_value(InputType.Y_AXIS_MIN))
            ax.set_ylim(y_min, y_max)

        plt.ylabel(self.input_data.get_value_label(InputType.VARIABLE)[0])

    def _plot_single_line(self, cube, ax):
        t_points = get_time_series(cube, None)

        # Set plot line width
        if self.input_data.get_value(InputType.IMAGE_SIZE) == 900:
            line_width = 0.7
        if self.input_data.get_value(InputType.IMAGE_SIZE) == 1200:
            line_width = 1
        elif self.input_data.get_value(InputType.IMAGE_SIZE) == 2400:
            line_width = 2

        if self.input_data.get_value(InputType.TIME_PERIOD) != "all":
            # if we are plotting one point a year then it is plotted on the year
            # boundary
            year_points = []
            for point in t_points:
                year_points.append(int(point))
            t_points = year_points

        ax.plot(
            t_points,
            cube.data,
            linestyle="solid",
            color=PERCENTILE_LINE_COLOUR,
            linewidth=line_width,
        )

        self.show_legend = False
