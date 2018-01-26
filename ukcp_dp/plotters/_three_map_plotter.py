from _map_plotter import MapPlotter
from ukcp_dp.constants import InputType
import iris
import matplotlib.gridspec as gridspec
import ukcp_dp.ukcp_standard_plots.mapper as maps

import logging
log = logging.getLogger(__name__)


class ThreeMapPlotter(MapPlotter):
    """
    The three map plotter class.

    This class extends MapPlotter with a _generate_subplots(self, cube,
    plotsettings).
    """

    def _generate_subplots(self, cube, plotsettings, fig, metadata_bbox):
        """
        Override base class method.

        @param cube (iris cube): a cube containing the selected data
        @param plotsettings (StandardMap): an object containing plot settings
        @param fig (matplotlib.figure.Figure)
        @param metadata_bbox (Bbox): the bbox surrounding the metadata table
        """
        log.debug('_generate_subplots')

        gs_top = metadata_bbox.y0 - 0.06
        gs_left = 0.02
        gs_right = 0.98

        if self._is_landscape(cube, 1.25) is True:
            gs = gridspec.GridSpec(2, 2)
            gs.update(top=gs_top, bottom=0.02, left=gs_left, right=gs_right)
            grid = [gs[0, 0], gs[0, 1], gs[1, 0], gs[1, 1]]
            bar_gs = gridspec.GridSpec(1, 2)
            bar_grid = bar_gs[0, 1]
        else:  # portrait
            gs = gridspec.GridSpec(1, 3)
            grid = [gs[0, 0], gs[0, 1], gs[0, 2], gs[0, 2]]
            gs.update(top=gs_top, bottom=0.15, left=gs_left, right=gs_right)
            bar_gs = gridspec.GridSpec(1, 4)
            bar_grid = bar_gs[0, 1:-1]

        bar_gs.update(top=0.23, bottom=0.08, left=gs_left, right=gs_right)

        # extract 10th, 50th and 90th percentiles
        percentiles = [10, 50, 90]
        for i, percentile in enumerate(percentiles):
            percentile_cube = cube.extract(
                iris.Constraint(percentile=percentile))
            title = '{}th Percentile'.format(percentile)
            if percentile_cube is None:
                raise Exception(
                    'Attempted to plot the {}th percentile, but no data found'.
                    format(percentile))
            result = self._add_sub_plot(
                fig, grid[i], plotsettings, title, percentile_cube)

        # add the sub plot to contain the bar
        ax = fig.add_subplot(bar_grid)
        ax.axis('off')

        return result

    def _add_sub_plot(self, fig, grid, plotsettings, title, data):
        ax = fig.add_subplot(grid, projection=plotsettings.proj)

        # Setting bar_orientation="none" here to override (prevent) drawing
        # the colorbar:
        result = maps.plot_standard_map(data, plotsettings, fig=fig,
                                        ax=ax, barlab=None,
                                        bar_orientation="none",
                                        outfnames=None)

        if self.input_data.get_value(InputType.SHOW_BOUNDARIES) is not None:
            self.plot_overlay(
                self.input_data.get_value(InputType.SHOW_BOUNDARIES))

        ax.set_title(title)

        return result
