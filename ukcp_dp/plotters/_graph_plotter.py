from __future__ import unicode_literals

from _base_plotter import BasePlotter
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
from ukcp_dp.constants import InputType
from ukcp_dp.plotters.utils._plotting_utils import end_figure, \
    start_standard_figure, wrap_string


class GraphPlotter(BasePlotter):
    """
    The graph plotter class.

    This class extends BasePlotter with _generate_plot(self, output_path). This
    class should be extended with a _generate_graph(self) method to plot the
    map.
    """

    def _generate_plot(self, output_path, plot_settings):
        """
        Override base class method.

        @param output_path (str): the full path to the file
        @param plot_settings (StandardMap): an object containing plot settings
        """
        # By default we want to show the legend
        self.show_legend = True

        # First create the figure
        fig, _, _ = start_standard_figure(plot_settings)

        # Add the logo and metadata box
        self._add_logo(fig)

        # Set the area below the title and allow room for the labels
        fig.add_axes(Bbox([[0.07, 0.08], [0.97, 0.88]]))

        self._generate_graph()

        # Add the title
        new_title = wrap_string(self.title, 110)
        fig.suptitle(new_title, fontsize='larger')

        if self.show_legend is True:
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
