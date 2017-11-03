import os

from ukcp_dp.constants import InputType

# Import (and parse) config files
from cows_wps.utils.parse_wps_config import getWPSConfigDict
wps_config_dict = getWPSConfigDict()

# Import process-specific modules
os.environ["MPLCONFIGDIR"] = wps_config_dict.get(
    "mpl_configdir", "/tmp/.matplotlib")

import matplotlib.pyplot as plt


class BasePlotter():
    """
    The base case for plotters.

    This class should be extended with a _generate_plot(self, cube) method to
    plot the data.
    """

    def generate_plot(self, output_path, input_data, cube, title):
        """
        Generate a plot.

        @param output_path (str): the full path to the file
        @param input_data (InputData): an object containing user defined values
        @param cube (iris data cube): an object containing the selected data
        @param title (str): a title for the plot

        @return the data used to generate the plot
        """
        # Set the image size
        self._set_figure_size(input_data.get_value(InputType.IMAGE_SIZE))

        self._generate_plot(input_data, cube)

        # Set default font size
        plt.rc('font', size=input_data.get_font_size())

        # Add the title
        plt.title(title, fontsize=input_data.get_font_size() + 2)

        # Add the legend
        plt.legend(loc=input_data.get_value(InputType.LEGEND_POSITION))

        # Put a grid on the plot.
        plt.grid(True)

        # Output the plot
        plt.savefig(output_path, dpi=100)

        return plt.gca().get_lines()

    def _generate_plot(self, input_data, cube):
        """
        This method should be overridden to produce the plots.

        @param input_data (InputData): an object containing user defined values
        @param cube (iris data cube): an object containing the selected data
        """
        pass

    def _set_figure_size(self, size):
        # Set the image size
        if size == '1200':
            plt.figure(figsize=(12, 8))
        elif size == '900':
            plt.figure(figsize=(9, 6))
        else:
            plt.figure(figsize=(6, 4))

        # TODO Remove water mark
        # Add a water mark
        fig, _ = plt.subplots()
        fig.text(0.95, 0.05, 'DRAFT - NOT FOR USE',
                 fontsize=40, color='gray',
                 ha='right', va='bottom', alpha=0.5)
