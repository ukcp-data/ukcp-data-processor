from _base_plotter import BasePlotter
from ukcp_dp.constants import InputType
import ukcp_dp.ukcp_common_analysis.regions as regs
import ukcp_dp.ukcp_standard_plots.plotting_general as plotgeneral


class MapPlotter(BasePlotter):
    """
    The map plotter class.

    This class extends BasePlotter with _generate_plot(self, cubes,
    output_path, title). This class should be extended with a
    _generate_map(self, cube, plotsettings, fig) method to plot the map.
    """

    def _generate_plot(self, output_path, title):
        """
        Override base class method.

        @param output_path (str): the full path to the file
        @param title (str): a title for the plot
        """
        cube = self.cube_list[0]

        plotsettings = self._get_plot_settings(
            self.input_data.get_value(InputType.IMAGE_SIZE),
            self.input_data.get_font_size(),
            self.input_data.get_value(InputType.VARIABLE),
            self.input_data.get_value(InputType.SHOW_BOUNDARIES))
        reg = regs.reg_from_cube(cube)
        plotsettings.set_xylims(reg)

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

        # Add the title ????
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

    def _is_landscape(self, cube):
        """
        Return True if the range of the x coordinates is larger than the range
        of the y coordinates.

        @param cube (iris cube): a cube containing the selected data

        @return a boolean, True if orientation is landscape
        """
        y_coords = cube.coord('projection_y_coordinate').points
        y_range = max(y_coords) - min(y_coords)
        x_coords = cube.coord('projection_x_coordinate').points
        x_range = max(x_coords) - min(x_coords)

        if y_range > x_range:
            return False
        return True
