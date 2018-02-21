import logging

from _base_plotter import BasePlotter
from ukcp_dp.constants import OVERLAY_COLOUR, OVERLAY_LINE_WIDTH, \
    OVERLAY_ADMIN, OVERLAY_COASTLINE, OVERLAY_COUNTRY, OVERLAY_RIVER, \
    OVERLAY_COASTLINE_SMALL
import matplotlib.pyplot as plt
import numpy as np
import shapefile as shp
import ukcp_dp.ukcp_common_analysis.regions as regs
import ukcp_dp.ukcp_standard_plots.plotting_general as plotgeneral


log = logging.getLogger(__name__)


class MapPlotter(BasePlotter):
    """
    The map plotter class.

    This class extends BasePlotter with _generate_plot(self, output_path,
    title). This class should be extended with a _generate_subplots(self, cube,
    plotsettings, fig, metadata_bbox) method to plot the map.
    """

    def _generate_plot(self, output_path, plotsettings, title):
        """
        Override base class method.

        @param output_path (str): the full path to the file
        @param plotsettings (StandardMap): an object containing plot settings
        @param title (str): a title for the plot
        """
        # TODO we can only produce a map for a single scenario and variable
        cube = self.cube_list[0]

        reg = regs.reg_from_cube(cube)
        plotsettings.set_xylims(reg)

        # Turn off grid lines for maps
        plotsettings.dxgrid = 1000
        plotsettings.dygrid = 1000

        # First create the figure
        fig, _, _ = plotgeneral.start_standard_figure(plotsettings)

        # Add the logo and metadata box
        self._add_logo(fig)
        metadata_bbox = self._add_metadata_text(fig)

        # Call the method to generate the maps
        result = self._generate_subplots(
            cube, plotsettings, fig, metadata_bbox)

        # TODO Remove water mark
        # Add a water mark
        fig.text(0.5, 0.5, 'DRAFT - NOT FOR USE',
                 fontsize=45, color='gray',
                 ha='center', va='center',  rotation=30, alpha=0.8)

        # Add the title
        fig.suptitle(title, fontsize='larger')

        # Add the colourbar
        plotgeneral.make_standard_bar(plotsettings, fig,
                                      bar_pos=plotsettings.bar_position,
                                      colmappable=result[1])

        # Set the margins, and save/display & close the plot:
#         plotgeneral.set_standard_margins(settings=None, fig=fig)
        plotgeneral.end_figure(output_path)

    def _generate_subplots(self, cube, plotsettings, fig, metadata_bbox):
        """
        This method should be overridden to produce the sub-plots.

        @param cube (iris cube): a cube containing the selected data
        @param plotsettings (StandardMap): an object containing plot settings
        @param fig (matplotlib.figure.Figure)
        @param metadata_bbox (Bbox): the bbox surrounding the metadata table
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

        if overlay == 'country':
            sf = shp.Reader(OVERLAY_COUNTRY)
        elif overlay == 'admin_region':
            sf = shp.Reader(OVERLAY_ADMIN)
        elif overlay == 'river_basin':
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
                if ip < nparts-1:
                    i1 = shape.parts[ip+1]-1
                else:
                    i1 = npoints

                seg = shape.points[i0:i1+1]
                x_lon = np.zeros((len(seg), 1))
                y_lat = np.zeros((len(seg), 1))
                for ip in range(len(seg)):
                    x_lon[ip] = seg[ip][0]
                    y_lat[ip] = seg[ip][1]

                plt.plot(x_lon, y_lat, color=OVERLAY_COLOUR,
                         linewidth=OVERLAY_LINE_WIDTH)
        log.debug('overlay added')
