from ukcp_dp.constants import DATA_SELECTION_TYPES
from ukcp_dp.constants import InputType
from ukcp_dp.vocab_manager import get_collection_label
import os
import ukcp_dp.ukcp_standard_plots.standards_class as stds


# Import (and parse) config files
from cows_wps.utils.parse_wps_config import getWPSConfigDict
wps_config_dict = getWPSConfigDict()

# Import process-specific modules
os.environ["MPLCONFIGDIR"] = wps_config_dict.get(
    "mpl_configdir", "/tmp/.matplotlib")

import matplotlib.cbook as cbook
import matplotlib.image as image
from matplotlib.transforms import Bbox


class BasePlotter():
    """
    The base class for plotters.

    This class should be extended with a
    _generate_plot(self, input_data, cubes, output_path, title) method to plot
    the data.
    """

    def generate_plot(self, input_data, cubes, output_path, title):
        """
        Generate a plot.

        @param input_data (InputData): an object containing user defined values
        @param cubes (list(iris data cube)): a list of cubes containing the
            selected data
        @param output_path (str): the full path to the file
        @param title (str): a title for the plot
        """
        # an object containing user defined values
        self.input_data = input_data

        self._generate_plot(cubes, output_path, title)

    def _generate_plot(self, cubes, output_path, title):
        """
        This method should be overridden to produce the plots.

        @param cubes (list(iris data cube)): a list of cubes containing the
            selected data
        @param output_path (str): the full path to the file
        @param title (str): a title for the plot
        """
        pass

    def _add_logo(self, fig):
        """
        Add a logo to the plot.
        """
        image_size = self.input_data.get_value(InputType.IMAGE_SIZE)

        # select a logo
        if image_size == 600:
            logo = ('/usr/local/cows_venv_py27/local_dists/ukcp-data-processor'
                    '/public/img/UKCP_logo75px.jpg')
            v_offset = 357
        elif image_size == 900:
            logo = ('/usr/local/cows_venv_py27/local_dists/ukcp-data-processor'
                    '/public/img/UKCP_logo100px.jpg')
            v_offset = 544
        else:
            logo = ('/usr/local/cows_venv_py27/local_dists/ukcp-data-processor'
                    '/public/img/UKCP_logo150px.jpg')
            v_offset = 718

        datafile = cbook.get_sample_data(logo, asfileobj=False)
        im = image.imread(datafile)

        fig.figimage(im, 5, v_offset, zorder=3)

    def _add_metadata_text(self, fig):
        """
        Add details of the metedata to a text box.
        """
        # get the plot details
        plot_details = []
        plot_details.append('{name}: {value}'.format(
            name=self.input_data.get_area_type_label(),
            value=self.input_data.get_area_label()))

        for dst in DATA_SELECTION_TYPES:
            name = get_collection_label(dst)
            try:
                value = self.input_data.get_value_label(dst)
                plot_details.append('{name}: {value}'.format(
                    name=name, value=value))
            except KeyError:
                pass

        # now work out how to display the plot details
        count = len(plot_details)
        if count > 5:
            count = 5

        box_text = ''
        box_text_2 = ''
        for i in range(0, count):
            box_text += '\n{}'.format(plot_details[i])
            try:
                box_text_2 += '\n{}'.format(plot_details[i + 5])
            except IndexError:
                pass

        # display the plot details
        fig.text(0.15, 0.92, 'Plot Details',
                 fontsize='larger',
                 verticalalignment='top',
                 horizontalalignment='left',
                 multialignment='left')

        box_1_x_offset = 0.16
        box_1_y_offset = 0.915
        box_1 = fig.text(box_1_x_offset, box_1_y_offset, box_text,
                         verticalalignment='top',
                         horizontalalignment='left',
                         multialignment='left',
                         bbox=dict(alpha=0.0))

        fig.show()
        box_1_width = fig.transFigure.inverted().transform(
            box_1.get_bbox_patch().get_bbox().get_points())[1][0]
        box_1_hieght = fig.transFigure.inverted().transform(
            box_1.get_bbox_patch().get_bbox().get_points())[1][1]
        box_2_x_offset = box_1_x_offset + box_1_width + 0.03

        fig.text(box_2_x_offset, box_1_y_offset, box_text_2,
                 verticalalignment='top',
                 horizontalalignment='left',
                 multialignment='left')

        # add a box around the metedata
        bbox = [[box_1_x_offset - 0.02, box_1_y_offset - box_1_hieght - 0.01],
                [0.99, box_1_y_offset + 0.015]]
        ax = fig.add_axes(Bbox(bbox))
        ax.set_xticks([])
        ax.set_yticks([])

        return bbox

    def _get_plot_settings(self, cmsize, fsize, var_id):
        """
        Get the plot settings based on the variable being plotted.

        @return a StandardMap object containing plot settings
        """
        plotsettings = stds.UKCP_NAE_SEAS.copy()
        if 'tas' in var_id:
            if 'Anom' in var_id:
                plotsettings = stds.UKCP_TEMP_ANOM.copy()
            else:
                plotsettings = self._get_tas_plot_settings()
        elif 'pr' in var_id:
            if 'Anom' in var_id:
                plotsettings = stds.UKCP_PRECIP_ANOM.copy()
            else:
                plotsettings = stds.UKCP_PRECIP.copy()

        # 100 dots per cm
        plotsettings.dpi = 100
        if cmsize == 600:
            # using 100 dpi set size to 600x400
            plotsettings.cmsize = [15.24, 10.16]
        elif cmsize == 900:
            # using 100 dpi set size to 900x600
            plotsettings.cmsize = [22.86, 15.24]
        elif cmsize == 1200:
            # using 100 dpi set size to 1200x800
            plotsettings.cmsize = [30.48, 20.32]

        plotsettings.fsize = fsize

        return plotsettings

    def _get_tas_plot_settings(self):
        """
        Get the plot setting to use for tas.
        """
        UKCP_EURO = stds.UKCP_TEMP.copy()
        UKCP_EURO.vrange = [-311.0, -302.0]
        UKCP_EURO.vmid = None
        UKCP_EURO.vstep = 1.0
        UKCP_EURO.bar_orientation = 'horizontal'
        # [left,bottom, width,height]
        # UKCP_EURO.bar_position = [0.55, 0.15, 0.4, 0.03]
        UKCP_EURO.bar_position = None
        UKCP_EURO.cont = False

        return UKCP_EURO
