from __future__ import unicode_literals

from _base_plotter import BasePlotter
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
from ukcp_dp.constants import InputType
from ukcp_dp.plotters.utils._plotting_utils import end_figure, \
    start_standard_figure


class GraphPlotter(BasePlotter):
    """
    The graph plotter class.

    This class extends BasePlotter with _generate_plot(self, output_path,
    title). This class should be extended with a _generate_graph(self) method
    to plot the map.
    """

    def _generate_plot(self, output_path, plot_settings, title):
        """
        Override base class method.

        @param output_path (str): the full path to the file
        @param plot_settings (StandardMap): an object containing plot settings
        @param title (str): a title for the plot
        """
        # First create the figure
        fig, _, _ = start_standard_figure(plot_settings)

        # Add the logo and metadata box
        self._add_logo(fig)

        # Set the area below the title and allow room for the labels
        fig.add_axes(Bbox([[0.07, 0.08], [0.97, 0.88]]))

        self._generate_graph()

        # Add the title
        fig.suptitle(title, fontsize='larger')

        # Add the legend
        plt.legend(loc=self.input_data.get_value(InputType.LEGEND_POSITION))

        # Put a grid on the plot.
        plt.grid(True)

        # Output the plot
#         plotgeneral.set_standard_margins(settings=None, fig=fig)
        end_figure(output_path)
        return

    def _generate_graph(self):
        """
        This method should be overridden to produce the plots.

        """
        pass
