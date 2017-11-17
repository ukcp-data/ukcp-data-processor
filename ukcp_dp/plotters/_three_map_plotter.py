from _map_plotter import MapPlotter
import iris
import matplotlib.gridspec as gridspec
import ukcp_dp.ukcp_standard_plots.mapper as maps


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
        gs_top = metadata_bbox.y0 - 0.06
        gs_left = 0.02
        gs_right = 0.98

        if self._is_landscape(cube) is True:
            gs = gridspec.GridSpec(2, 2)
            gs.update(top=gs_top, bottom=0.02, left=gs_left, right=gs_right)
            grid = [gs[0, 0], gs[0, 1], gs[1, 0], gs[1, 1]]
            bar_gs = gridspec.GridSpec(1, 2)
        else:  # portrait
            gs = gridspec.GridSpec(1, 3)
            grid = [gs[0, 0], gs[0, 1], gs[0, 2], gs[0, 2]]
            gs.update(top=gs_top, bottom=0.15, left=gs_left, right=gs_right)
            bar_gs = gridspec.GridSpec(1, 3)

        bar_grid = bar_gs[0, 1]
        bar_gs.update(top=0.23, bottom=0.08, left=gs_left, right=gs_right)

        titles = ['10th Percentile', '50th Percentile', '90th Percentile']
        # TODO need to plot something other than ensemble
        for i, ensemble in enumerate(cube.slices_over('Ensemble member')):
            # TODO
            if i > 2:
                break

            ax = fig.add_subplot(grid[i], projection=plotsettings.proj)

            # Setting bar_orientation="none" here to override (prevent) drawing
            # the colorbar:
            result = maps.plot_standard_map(ensemble, plotsettings, fig=fig,
                                            ax=ax, barlab=None,
                                            bar_orientation="none",
                                            outfnames=None)
            # TODO this should come directly from the file
            # add a title
            title = titles[i]
            ax.set_title(title)

        # add the sub plot to contain the bar
        ax = fig.add_subplot(bar_grid)
        ax.axis('off')

        return result
