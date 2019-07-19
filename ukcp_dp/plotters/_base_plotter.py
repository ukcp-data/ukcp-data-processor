from __future__ import unicode_literals

import logging

import matplotlib.cbook as cbook
import matplotlib.gridspec as gridspec
import matplotlib.image as image
from matplotlib.transforms import Bbox
from ukcp_dp.constants import InputType, LOGO_SMALL, LOGO_MEDIUM, LOGO_LARGE


log = logging.getLogger(__name__)


class BasePlotter(object):
    """
    The base class for plotters.

    This class should be extended with a
    _generate_plot(self, output_path) method to plot the data.
    The following variables are available to overriding methods:
        self.input_data
        self.cube_list
        self.overlay_cube
        self.title
        self.vocab
    """

    def generate_plot(self, input_data, cube_list, overlay_cube, output_path,
                      title, vocab, plot_settings):
        """
        Generate a plot.

        @param input_data (InputData): an object containing user defined values
        @param cube_list (iris cube list): a list of cubes containing the
            selected data, one cube per scenario, per variable
        @param overlay_cube (iris cube): a cube containing the data for
            the overlay
        @param output_path (str): the full path to the file
        @param title (str): a title for the plot
        @param vocab (Vocab): an instance of the ukcp_dp Vocab class
        @param plot_settings (StandardMap): an object containing plot settings
        """
        log.info('generate_plot')
        # an object containing user defined values
        self.input_data = input_data
        # an iris cube list containing one cube per scenario, per variable
        self.cube_list = cube_list
        self.overlay_cube = overlay_cube
        self.title = title
        self.vocab = vocab

        self._generate_plot(output_path, plot_settings)

    def _generate_plot(self, output_path, plot_settings):
        """
        This method should be overridden to produce the plots.

        @param output_path (str): the full path to the file
        @param plot_settings (StandardMap): an object containing plot settings
        """
        pass

    def _add_logo(self, fig):
        """
        Add a logo to the plot.
        """
        image_size = self.input_data.get_value(InputType.IMAGE_SIZE)

        # select a logo
        if image_size == 900:
            # height = 600
            logo = LOGO_SMALL
            v_offset = 551
        elif image_size == 1200:
            # height = 800
            logo = LOGO_MEDIUM
            v_offset = 730
        else:  # 2400
            # height = 1600
            logo = LOGO_LARGE
            v_offset = 1464

        datafile = cbook.get_sample_data(logo, asfileobj=False)
        im = image.imread(datafile)

        fig.figimage(im, 5, v_offset, zorder=3)
        self._add_funder_text(fig)

    def _add_funder_text(self, fig):
        """
        Add a logo to the plot.
        """
        image_size = self.input_data.get_value(InputType.IMAGE_SIZE)

        if image_size == 900:
            x = 0.78
            font_size = 10
        elif image_size == 1200:
            x = 0.80
            font_size = 12
        else:  # 2400
            x = 0.80
            font_size = 24

        textstr = 'Funded by BEIS and Defra'
        fig.text(x, 0.02, textstr, fontsize=font_size)
