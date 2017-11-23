from _map_plotter import MapPlotter
import iris
import matplotlib.gridspec as gridspec
from ukcp_dp.constants import InputType
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

        @param cube (iris data cube): a cube containing the selected data
        @param plotsettings (StandardMap): an object containing plot settings
        @param fig (matplotlib.figure.Figure)
        @param metadata_bbox (Bbox): the bbox surrounding the metadata table
        """
        log.debug('_generate_subplots')
        gs_top = metadata_bbox.y0 - 0.06
        gs_left = 0.02
        gs_right = 0.98

        if self._is_landscape(cube) is True:
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

        titles = ['10th Percentile', '50th Percentile', '90th Percentile']
        if self.input_data.get_value(InputType.DATA_SOURCE) == 'land-prob':
            for i, percentile in enumerate([10, 50, 90]):
                result = self._add_sub_plot(
                    fig, grid[i], plotsettings, titles[i],
                    cube.extract(iris.Constraint(percentile=percentile)))

        else:
            # TODO need to calculate and plot percentiles
            for i, ensemble in enumerate(cube.slices_over('Ensemble member')):
                # TODO
                if i > 2:
                    break
                result = self._add_sub_plot(
                    fig, grid[i], plotsettings, titles[i], ensemble)

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
        # TODO this should come directly from the file
        # add a title
        ax.set_title(title)

        return result
