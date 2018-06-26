from __future__ import unicode_literals

import logging
import math

import matplotlib.cbook as cbook
import matplotlib.gridspec as gridspec
import matplotlib.image as image
from matplotlib.transforms import Bbox
from ukcp_dp.constants import DATA_SELECTION_TYPES, InputType, \
    LOGO_SMALL, LOGO_MEDIUM, LOGO_LARGE
from ukcp_dp.plotters.utils import _standards_class as stds


log = logging.getLogger(__name__)


class BasePlotter(object):
    """
    The base class for plotters.

    This class should be extended with a
    _generate_plot(self, output_path, title) method to plot
    the data.
    The following variables are available to overriding methods:
        self.input_data
        self.cube_list
        self.overlay_cube
    """

    def generate_plot(self, input_data, cube_list, overlay_cube, output_path,
                      title, vocab):
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
        """
        log.info('generate_plot')
        # an object containing user defined values
        self.input_data = input_data
        # an iris cube list containing one cube per scenario, per variable
        self.cube_list = cube_list
        self.overlay_cube = overlay_cube
        self.vocab = vocab

        # The plot settings are customised to the first variable in the list
        # We may want to change this in the future
        plotsettings = self._get_plot_settings(
            self.input_data.get_value(InputType.IMAGE_SIZE),
            self.input_data.get_font_size(),
            self.input_data.get_value(InputType.VARIABLE)[0])

        self._generate_plot(output_path, plotsettings, title)

    def _generate_plot(self, output_path, plotsettings, title):
        """
        This method should be overridden to produce the plots.

        @param output_path (str): the full path to the file
        @param plotsettings (StandardMap): an object containing plot settings
        @param title (str): a title for the plot
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
            x = 0.85
            font_size = 18

        textstr = 'Funded by BEIS and Defra'
        fig.text(x, 0.02, textstr, fontsize=font_size)

    def _add_metadata_text(self, fig):
        """
        Generate a table containing details of the metedata.

        @param fig (matplotlib.figure.Figure)

        @return a Bbox surrounding the metadata table
        """
        # get the plot details
        plot_details = []
        plot_details.append('{name}: {value}'.format(
            name=self.input_data.get_area_type_label(),
            value=self.input_data.get_area_label()))

        data_selection_types = list(DATA_SELECTION_TYPES)

        # we do not want to display year min, year max as well as year
        if (self.input_data.get_value(InputType.YEAR_MINIMUM) ==
                self.input_data.get_value(InputType.YEAR_MAXIMUM)):
            data_selection_types.remove(InputType.YEAR_MINIMUM)
            data_selection_types.remove(InputType.YEAR_MAXIMUM)
        else:
            data_selection_types.remove(InputType.YEAR)

        # only show if True
        if (self.input_data.get_value(InputType.OVERLAY_PROBABILITY_LEVELS)
                is None or
                self.input_data.get_value(InputType.OVERLAY_PROBABILITY_LEVELS)
                is False):
            data_selection_types.remove(InputType.OVERLAY_PROBABILITY_LEVELS)

        for dst in data_selection_types:
            name = self.vocab.get_collection_label(dst)
            try:
                value = self.input_data.get_value_label(dst)
                if isinstance(value, list):
                    value = ', '.join(value)
                plot_details.append('{name}: {value}'.format(
                    name=name, value=value))
            except KeyError:
                pass

        # now work out how to display the plot details
        line_count = len(plot_details)
        column_two_line_count = 5
        if line_count > 5:
            line_count = int(math.ceil(line_count / 2.0))
            column_two_line_count = line_count

        # unable to format the alignment of the column header, it is included
        # as a normal row
        cell_text = [['Plot Details', '']]

        # populate the cells
        for i in range(0, line_count):
            cell = [_wrap(plot_details[i],
                          self.input_data.get_value(InputType.FONT_SIZE))]
            try:
                cell.append(_wrap(plot_details[i + column_two_line_count],
                                  self.input_data.get_value(
                                      InputType.FONT_SIZE)))
            except IndexError:
                cell.append('')
            cell_text.append(cell)

        gs = gridspec.GridSpec(1, 1)
        gs.update(top=0.92, bottom=0.8, left=0.16, right=0.99)

        # create axes to put the table on
        ax = fig.add_subplot(gs[0, 0])
        ax.axis("off")

        # create the table
        the_table = ax.table(cellText=cell_text,
                             cellLoc='left',
                             loc='upper right')

        the_table.auto_set_font_size(False)
        the_table.set_fontsize(self.input_data.get_font_size() - 2)

        line_adjuster = _get_line_adjuster()

        for i, cell in enumerate(the_table.properties()['children']):
            if i < 2:
                # header row
                cell.set_facecolor('silver')
                cell.set_text_props(weight='bold')
            # remove cell boarders
            cell.set_linewidth(0)
            cell.PAD = 0.02
            cell.set_text_props(horizontalalignment='left')
            cell.set_text_props(wrap=True)

            lines_in_cell = len(cell.get_text().get_text().split('\n'))

            # set the cell height
            cell.set_height((cell.get_height() +
                             line_adjuster
                             [self.input_data.get_value(InputType.IMAGE_SIZE)]
                             [self.input_data.get_value(InputType.FONT_SIZE)]
                             [lines_in_cell]))
        # get the bbox of the table
        fig.show()
        renderer = fig.canvas.get_renderer()
        bbox = (the_table.get_window_extent(renderer).
                inverse_transformed(fig.transFigure))

        # add a box around the table
        ax = fig.add_axes(Bbox(bbox), axis_bgcolor='none')
        ax.set_xticks([])
        ax.set_yticks([])
        return bbox

    def _get_plot_settings(self, cmsize, fsize, var_id):
        """
        Get the plot settings based on the variable being plotted.

        @return a StandardMap object containing plot settings
        """
        # tas, tasmax, tasmin
        if 'tas' in var_id:
            # Mean air temperature at 1.5m (C)
            # Maximum air temperature at 1.5m (C)
            # Minimum air temperature at 1.5m (C)
            if 'Anom' in var_id:
                plotsettings = stds.UKCP_TEMP_ANOM.copy()
            else:
                plotsettings = stds.UKCP_TEMP.copy()

        elif 'pr' in var_id:
            # Precipitation rate (mm/day)
            if 'Anom' in var_id:
                plotsettings = stds.UKCP_PRECIP_ANOM.copy()
            else:
                plotsettings = stds.UKCP_PRECIP.copy()

        elif 'sfcWind' in var_id:
            # Wind speed at 10m (m s-1)
            if 'Anom' in var_id:
                plotsettings = stds.UKCP_WIND_ANOM.copy()
            else:
                plotsettings = stds.UKCP_WIND.copy()

        elif 'uas' in var_id:
            # Eastward wind at 10m (m s-1)
            if 'Anom' in var_id:
                plotsettings = stds.UKCP_WIND_EASTWARD_ANOM.copy()
            else:
                plotsettings = stds.UKCP_WIND_EASTWARD.copy()

        elif 'vas' in var_id:
            # Northward wind at 10m (m s-1)
            if 'Anom' in var_id:
                plotsettings = stds.UKCP_WIND_NORTHWARD_ANOM.copy()
            else:
                plotsettings = stds.UKCP_WIND_NORTHWARD.copy()

        elif 'clt' in var_id:
            # Total cloud (%)
            if 'Anom' in var_id:
                # TODO check BIAS is the correct thing to use
                plotsettings = stds.UKCP_CLOUDFRAC_MONTHLY_BIAS.copy()
            else:
                plotsettings = stds.UKCP_CLOUDFRAC_MONTHLY.copy()

        elif 'hurs' in var_id:
            # Relative humidity at 1.5m (%)
            if 'Anom' in var_id:
                # TODO do we need an ANOM version?
                plotsettings = stds.UKCP_RELATIVE_HUMIDITY.copy()
            else:
                plotsettings = stds.UKCP_RELATIVE_HUMIDITY.copy()

        elif 'huss' in var_id:
            # Specific humidity at 1.5m (1)
            if 'Anom' in var_id:
                # TODO do we need an ANOM version?
                plotsettings = stds.UKCP_SPECIFIC_HUMIDITY.copy()
            else:
                plotsettings = stds.UKCP_SPECIFIC_HUMIDITY.copy()

        elif 'psl' in var_id:
            # Sea level pressure (hPa)
            if 'Anom' in var_id:
                plotsettings = stds.UKCP_PMSL_ANOM.copy()
            else:
                # TODO do we need a non-ANOM version?
                plotsettings = stds.UKCP_PMSL_ANOM.copy()

        elif 'rls' in var_id:
            # Net Surface long wave flux (W m-2)
            if 'Anom' in var_id:
                # TODO check BIAS is the correct thing to use
                plotsettings = stds.UKCP_LWRAD_NET_MONTHLY_BIAS.copy()
            else:
                plotsettings = stds.UKCP_LWRAD_NET_MONTHLY.copy()

        elif 'rsds' in var_id:
            # Total downward shortwave flux anomaly (W m-2)
            if 'Anom' in var_id:
                # TODO check BIAS is the correct thing to use
                plotsettings = stds.UKCP_SWRAD_DOWN_MONTHLY_BIAS.copy()
            else:
                plotsettings = stds.UKCP_SWRAD_DOWN_MONTHLY.copy()

        elif 'rss' in var_id:
            # Net Surface short wave flux (W m-2)
            if 'Anom' in var_id:
                # TODO check BIAS is the correct thing to use
                plotsettings = stds.UKCP_SWRAD_NET_MONTHLY_BIAS.copy()
            else:
                plotsettings = stds.UKCP_SWRAD_NET_MONTHLY.copy()

        else:
            plotsettings = stds.UKCPNEAT.copy()

        plotsettings.bar_orientation = 'horizontal'

        plotsettings.default_barlabel = self.vocab.get_collection_term_label(
            InputType.VARIABLE, var_id)

        # remove coast line, it is added back later with any over layers
        plotsettings.coastlw = 0

        # remove country boarders, we may put them back later
        plotsettings.countrylcol = None

        # 100 dots per cm
        plotsettings.dpi = 100
        plotsettings.dpi_display = 100
        if cmsize == 900:
            # using 100 dpi set size to 900x600
            plotsettings.cmsize = [22.86, 15.24]
        elif cmsize == 1200:
            # using 100 dpi set size to 1200x800
            plotsettings.cmsize = [30.48, 20.32]
        elif cmsize == 2400:
            # using 100 dpi set size to 2400x1600
            plotsettings.cmsize = [60.96, 40.64]

        plotsettings.fsize = fsize

        return plotsettings


def _wrap(text, font_size):
    if font_size == 's':
        cell_width = 90
    elif font_size == 'm':
        cell_width = 75
    else:
        cell_width = 68

    if len(text) < cell_width:
        return text

    ssv = text.split(' ')
    lines = ''
    line = ''
    for bit in ssv:
        if len(line) + len(bit) < cell_width:
            line += ' {}'.format(bit)
        else:
            lines += '\n{}'.format(line)
            line = bit

    # add the residue
    lines += '\n{}'.format(line)
    result = lines.split('\n', 1)[1]
    return result


def _get_line_adjuster():
    line_adjuster = {900:
                     {
                         's':
                         {1: -0.08,
                          2: -0.02,
                          3: 0.02,
                          4: 0.06,
                          5: 0.10},
                         'm':
                         {1: -0.02,
                          2: 0.09,
                          3: 0.2,
                          4: 0.38,
                          5: 0.60},
                         'l':
                         {1: 0.04,
                          2: 0.18,
                          3: 0.34,
                          4: 0.54,
                          5: 0.90}
                     },
                     1200:
                     {
                         's':
                         {1: -0.04,
                          2: 0.0,
                          3: 0.08,
                          4: 0.16,
                          5: 0.24},
                         'm':
                         {1: 0,
                          2: 0.1,
                          3: 0.2,
                          4: 0.3,
                          5: 0.4},
                         'l':
                         {1: 0.04,
                          2: 0.2,
                          3: 0.4,
                          4: 0.6,
                          5: 0.8}
                     },
                     2400:
                     {
                         's':
                         {1: -0.04,
                          2: 0.0,
                          3: 0.08,
                          4: 0.16,
                          5: 0.24},
                         'm':
                         {1: 0,
                          2: 0.07,
                          3: 0.15,
                          4: 0.3,
                          5: 0.45},
                         'l':
                         {1: 0.04,
                          2: 0.1,
                          3: 0.2,
                          4: 0.3,
                          5: 0.4}
                     },
                     }
    return line_adjuster
