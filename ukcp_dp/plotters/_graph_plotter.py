from _base_plotter import BasePlotter
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
from ukcp_dp.constants import InputType
import ukcp_dp.ukcp_standard_plots.plotting_general as plotgeneral


class GraphPlotter(BasePlotter):
    """
    The graph plotter class.

    This class extends BasePlotter with _generate_plot(self, cubes,
    output_path, title). This class should be extended with a
    _generate_graph(self, cubes) method to plot the map.
    """

    def _generate_plot(self, output_path, title):
        """
        Override base class method.

        @param output_path (str): the full path to the file
        @param title (str): a title for the plot
        """
        plotsettings = self._get_plot_settings(
            self.input_data.get_value(InputType.IMAGE_SIZE),
            self.input_data.get_font_size(),
            self.input_data.get_value(InputType.VARIABLE),
            self.input_data.get_value(InputType.SHOW_BOUNDARIES))

        fig, _, _ = plotgeneral.start_standard_figure(plotsettings)

        # Add the logo and metadata box
        self._add_logo(fig)
        metadata_bbox = self._add_metadata_text(fig)

        # TODO Remove water mark
        # Add a water mark
        fig.text(0.5, 0.5, 'DRAFT - NOT FOR USE',
                 fontsize=45, color='gray',
                 ha='center', va='center',  rotation=30, alpha=0.8)

        # Set the area below the metadata and allow room for the labels
        fig.add_axes(Bbox([[0.07, 0.08], [0.99, metadata_bbox.y0 - 0.06]]))

        self._generate_graph()

        # Add the title
        fig.suptitle(title, fontsize='larger')

        # Add the legend
        plt.legend(loc=self.input_data.get_value(InputType.LEGEND_POSITION))

        # Put a grid on the plot.
        plt.grid(True)

        # Output the plot
#         plotgeneral.set_standard_margins(settings=None, fig=fig)
        plotgeneral.end_figure(output_path)
        return

    def _generate_graph(self):
        """
        This method should be overridden to produce the plots.

        """
        pass
