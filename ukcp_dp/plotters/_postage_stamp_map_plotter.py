from _map_plotter import MapPlotter
import ukcp_dp.ukcp_standard_plots.mapper as maps


class PostageStampMapPlotter(MapPlotter):
    """
    The postage stamp map plotter class.

    This class extends MapPlotter with a _generate_subplots(self, cube,
    plotsettings).
    """

    def _generate_subplots(self, cube, plotsettings, fig):
        """
        Override base class method.

        @param cube (iris data cube): a cube containing the selected data
        @param plotsettings (StandardMap): an object containing plot settings
        @param fig (matplotlib.figure.Figure)
        """

        ensemble_count = len(cube.coord('Ensemble member').points)
        # work out the number of sub-plots based on orientation of the plot
        # and number of ensembles
        if self._is_landscape(cube) is True:
            if ensemble_count == 20:
                x = 6
                y = 5
                start_point = 7
                x_bar = 2
                y_bar = 5
                start_point_bar = 10
            elif ensemble_count == 15:
                x = 6
                y = 4
                start_point = 7
                x_bar = 2
                y_bar = 4
                start_point_bar = 8
            else:
                # TODO need info about CPM ensemble members
                x = 6
                y = 4
                start_point = 7
                x_bar = 2
                y_bar = 4
                start_point_bar = 8

        else:  # portrait
            if ensemble_count == 20:
                x = 8
                y = 3
                start_point = 1
                x_bar = 2
                y_bar = 3
                start_point_bar = 6
            elif ensemble_count == 15:
                x = 6
                y = 4
                start_point = 7
                x_bar = 2
                y_bar = 4
                start_point_bar = 8
            else:
                # TODO need info about CPM ensemble members
                x = 8
                y = 4
                start_point = 9
                x_bar = 2
                y_bar = 4
                start_point_bar = 8

        # NOT WORKING
        fig.subplots_adjust(top=0.59)

        for i, ensemble in enumerate(cube.slices_over('Ensemble member')):
            ax = fig.add_subplot(y, x, i + start_point,
                                 projection=plotsettings.proj)

            # Setting bar_orientation="none" here to override (prevent) drawing
            # the colorbar:
            result = maps.plot_standard_map(ensemble, plotsettings, fig=fig,
                                            ax=ax, barlab=None,
                                            bar_orientation="none",
                                            outfnames=None)
            # TODO this should come directly from the file
            # add a title
            title = 'r1i1p{n}'.format(n=i + 1)
            ax.set_title(title, fontsize='smaller')

        # add the sub plot to contain the bar
        ax = fig.add_subplot(y_bar, x_bar, start_point_bar)
        ax.axis('off')

        return result

    def _is_landscape(self, cube):
        """
        Return True if the range of the x coordinates is larger than the range
        of the y coordinates.

        @param cube (iris data cube): a cube containing the selected data

        @return a boolean, True if orientation is landscape
        """
        y_coords = cube.coord('projection_y_coordinate').points
        y_range = max(y_coords) - min(y_coords)
        x_coords = cube.coord('projection_x_coordinate').points
        x_range = max(x_coords) - min(x_coords)

        if y_range > x_range:
            return False
        return True
