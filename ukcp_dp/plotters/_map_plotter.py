import logging

from _base_plotter import BasePlotter
from iris.exceptions import CoordinateNotFoundError
import matplotlib.pyplot as plt
import numpy as np
import shapefile as shp
from ukcp_dp.constants import OVERLAY_COLOUR, OVERLAY_LINE_WIDTH, \
    OVERLAY_ADMIN, OVERLAY_COASTLINE, OVERLAY_COUNTRY, OVERLAY_RIVER, \
    OVERLAY_COASTLINE_SMALL, AreaType
from ukcp_dp.plotters.utils._plotting_utils import end_figure, \
    make_standard_bar, start_standard_figure, wrap_string
from ukcp_dp.plotters.utils._region_utils import reg_from_cube


log = logging.getLogger(__name__)


class MapPlotter(BasePlotter):
    """
    The map plotter class.

    This class extends BasePlotter with _generate_plot(self, output_path,
    title). This class should be extended with a _generate_subplots(self, cube,
    plot_settings, fig) method to plot the map.
    """

    def _generate_plot(self, output_path, plot_settings, title):
        """
        Override base class method.

        @param output_path (str): the full path to the file
        @param plot_settings (StandardMap): an object containing plot settings
        @param title (str): a title for the plot
        """
        # TODO we can only produce a map for a single scenario and variable
        cube = self.cube_list[0]

        if self.input_data.get_area_type() == AreaType.BBOX:

            reg = reg_from_cube(cube, lat_name="projection_y_coordinate",
                                lon_name="projections_x_coordinate")
        else:
            # Some form of region, therefore it is the whole of UK
            reg = {'lons': [-10.9818, 2.2398], 'lats': [48.8957, 60.9531]}

        plot_settings.set_xylims(reg)

        # Turn off grid lines for maps
        plot_settings.dxgrid = 1000
        plot_settings.dygrid = 1000

        # First create the figure
        fig, _, _ = start_standard_figure(plot_settings)

        # Add the logo and metadata box
        self._add_logo(fig)

        # Call the method to generate the maps
        result = self._generate_subplots(cube, plot_settings, fig)

        # Add the title
        new_title = wrap_string(title, 110)
        fig.suptitle(new_title, fontsize='larger')

        # Add the colourbar
        make_standard_bar(plot_settings, fig,
                          bar_pos=plot_settings.bar_position,
                          colmappable=result[1])

        # Set the margins, and save/display & close the plot:
#         plotgeneral.set_standard_margins(settings=None, fig=fig)
        end_figure(output_path)

    def _generate_subplots(self, cube, plot_settings, fig):
        """
        This method should be overridden to produce the sub-plots.

        @param cube (iris cube): a cube containing the selected data
        @param plot_settings (StandardMap): an object containing plot settings
        @param fig (matplotlib.figure.Figure)
        """
        pass

    def _is_landscape(self, cube, scaling_factor=1):
        """
        Return True if the range of the x coordinates is larger than the range
        of the y coordinates multiplied by a scaling factor.

        @param cube (iris cube): a cube containing the selected data
        @param scaling_factor(int): a value to multiply the y range by

        @return a boolean, True if orientation is landscape
        """
        if self.input_data.get_area_type() != AreaType.BBOX:
            # Some form of region, therefore it is the whole of UK and we want
            # portrait
            return False

        y_coords = cube.coord('projection_y_coordinate').points
        y_range = max(y_coords) - min(y_coords)
        x_coords = cube.coord('projection_x_coordinate').points
        x_range = max(x_coords) - min(x_coords)

        if y_range * scaling_factor > x_range:
            return False
        return True

    def plot_overlay(self, overlay, hi_res=True):
        """
        Add an overlay to a map.

        @param overlay (str): the name of the overlay
        """
        if overlay is None:
            overlay = 'coast_line'

        if overlay == AreaType.COUNTRY:
            sf = shp.Reader(OVERLAY_COUNTRY)
        elif overlay == AreaType.ADMIN_REGION:
            sf = shp.Reader(OVERLAY_ADMIN)
        elif overlay == AreaType.RIVER_BASIN:
            sf = shp.Reader(OVERLAY_RIVER)
        else:
            overlay = 'coast_line'
            if hi_res is True:
                sf = shp.Reader(OVERLAY_COASTLINE)
            else:
                sf = shp.Reader(OVERLAY_COASTLINE_SMALL)

        log.debug('adding overlay for {}'.format(overlay))

        for shape in list(sf.iterShapes()):
            npoints = len(shape.points)  # total points
            nparts = len(shape.parts)  # total parts

            # loop over parts of each shape, plot separately
            for ip in range(nparts):
                i0 = shape.parts[ip]
                if ip < nparts - 1:
                    i1 = shape.parts[ip + 1] - 1
                else:
                    i1 = npoints

                seg = shape.points[i0:i1 + 1]
                x_lon = np.zeros((len(seg), 1))
                y_lat = np.zeros((len(seg), 1))
                for ip in range(len(seg)):
                    x_lon[ip] = seg[ip][0]
                    y_lat[ip] = seg[ip][1]

                plt.plot(x_lon, y_lat, color=OVERLAY_COLOUR,
                         linewidth=OVERLAY_LINE_WIDTH)
        log.debug('overlay added')
