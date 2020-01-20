from __future__ import unicode_literals

from matplotlib.transforms import Bbox

import matplotlib.pyplot as plt
from ukcp_dp.constants import InputType
from ukcp_dp.plotters._base_plotter import BasePlotter
from ukcp_dp.plotters.utils._plotting_utils import (
    end_figure,
    start_standard_figure,
    wrap_string,
)


class GraphPlotter(BasePlotter):
    """
    The graph plotter class.

    This class extends BasePlotter with _generate_plot(self, output_path). This
    class should be extended with a _generate_graph(self) method to plot the
    map.
    """

    def __init__(self, *args, **kwargs):
        BasePlotter.__init__(self, *args, **kwargs)
        self.line_width = None
        self.show_legend = True

    def _generate_plot(self, output_path, plot_settings):
        """
        Override base class method.

        @param output_path (str): the full path to the file
        @param plot_settings (StandardMap): an object containing plot settings
        """
        # By default we want to show the legend
        self.show_legend = True

        # Set plot line width
        if self.input_data.get_value(InputType.IMAGE_SIZE) == 900:
            self.line_width = 1
        if self.input_data.get_value(InputType.IMAGE_SIZE) == 1200:
            self.line_width = 2
        elif self.input_data.get_value(InputType.IMAGE_SIZE) == 2400:
            self.line_width = 3

        # First create the figure
        fig, _, _ = start_standard_figure(plot_settings)

        # Add the logo and metadata box
        self._add_logo(fig)

        # Set the area below the title and allow room for the labels
        # [[left, bottom], [right, top]]
        fig.add_axes(Bbox([[0.11, 0.1], [0.95, 0.82]]))
        self._generate_graph()

        # Set the title width and tick label padding
        width = 105
        ax = plt.gca()
        if self.input_data.get_value(InputType.IMAGE_SIZE) == 900:
            width = 105 - (self.input_data.get_font_size() * 3)
            ax.tick_params(axis="both", which="major", pad=5)
        if self.input_data.get_value(InputType.IMAGE_SIZE) == 1200:
            width = 100 - (self.input_data.get_font_size() * 2)
            ax.tick_params(axis="both", which="major", pad=10)
        elif self.input_data.get_value(InputType.IMAGE_SIZE) == 2400:
            width = 100 - (self.input_data.get_font_size() * 1)
            ax.tick_params(axis="both", which="major", pad=20)

        # Add the title
        new_title = wrap_string(self.title, width)
        fig.suptitle(new_title, fontsize=self.input_data.get_font_size())

        if self.show_legend is True:
            # Add the legend
            legend_font_size = self.input_data.get_font_size() * 0.7
            plt.legend(
                loc=self.input_data.get_value(InputType.LEGEND_POSITION),
                prop={"size": legend_font_size},
            )

        # Put a grid on the plot.
        plt.grid(True)

        # Output the plot
        #         plotgeneral.set_standard_margins(settings=None, fig=fig)
        end_figure(output_path)

    def _generate_graph(self):
        """
        This method should be overridden to produce the plots.

        """
