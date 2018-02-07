import logging

from _map_plotter import MapPlotter
import matplotlib.gridspec as gridspec
from ukcp_dp.constants import InputType
import ukcp_dp.ukcp_standard_plots.mapper as maps


log = logging.getLogger(__name__)


class PostageStampMapPlotter(MapPlotter):
    """
    The postage stamp map plotter class.

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

        ensemble_count = len(cube.coord('Ensemble member').points)

        # work out the number of sub-plots based on orientation of the plot
        # and number of ensembles
        if self._is_landscape(cube) is True:
            if ensemble_count == 20:
                gs = gridspec.GridSpec(4, 6)
                gs.update(top=gs_top, bottom=0.02, left=gs_left,
                          right=gs_right)
                grid = [gs[0, 0], gs[0, 1], gs[0, 2], gs[0, 3], gs[0, 4],
                        gs[0, 5],
                        gs[1, 0], gs[1, 1], gs[1, 2], gs[1, 3], gs[1, 4],
                        gs[1, 5],
                        gs[2, 0], gs[2, 1], gs[2, 2], gs[2, 3], gs[2, 4],
                        gs[2, 5],
                        gs[3, 0], gs[3, 1]]

            elif ensemble_count == 15:
                gs = gridspec.GridSpec(3, 6)
                gs.update(top=gs_top, bottom=0.02, left=gs_left,
                          right=gs_right)
                grid = [gs[0, 0], gs[0, 1], gs[0, 2], gs[0, 3], gs[0, 4],
                        gs[0, 5],
                        gs[1, 0], gs[1, 1], gs[1, 2], gs[1, 3], gs[1, 4],
                        gs[1, 5],
                        gs[2, 0], gs[2, 1], gs[2, 2]]
            else:
                gs = gridspec.GridSpec(2, 5)
                gs.update(top=gs_top, bottom=0.13, left=gs_left,
                          right=gs_right)
                grid = [gs[0, 0], gs[0, 1], gs[0, 2], gs[0, 3], gs[0, 4],
                        gs[1, 0], gs[1, 1], gs[1, 2], gs[1, 3], gs[1, 4]]

        else:  # portrait
            if ensemble_count == 20:
                gs = gridspec.GridSpec(3, 8)
                gs.update(top=gs_top, bottom=0.02, left=gs_left,
                          right=gs_right)
                grid = [gs[0, 0], gs[0, 1], gs[0, 2], gs[0, 3], gs[0, 4],
                        gs[0, 5], gs[0, 6], gs[0, 7],
                        gs[1, 0], gs[1, 1], gs[1, 2], gs[1, 3], gs[1, 4],
                        gs[1, 5], gs[1, 6], gs[1, 7],
                        gs[2, 0], gs[2, 1], gs[2, 2], gs[2, 3]]

            elif ensemble_count == 15:
                gs = gridspec.GridSpec(2, 8)
                gs.update(top=gs_top, bottom=0.1, left=gs_left, right=gs_right)
                grid = [gs[0, 0], gs[0, 1], gs[0, 2], gs[0, 3], gs[0, 4],
                        gs[0, 5], gs[0, 6], gs[0, 7],
                        gs[1, 0], gs[1, 1], gs[1, 2], gs[1, 3], gs[1, 4],
                        gs[1, 5], gs[1, 6]]

            else:
                gs = gridspec.GridSpec(2, 5)
                gs.update(top=gs_top, bottom=0.13, left=gs_left,
                          right=gs_right)
                grid = [gs[0, 0], gs[0, 1], gs[0, 2], gs[0, 3], gs[0, 4],
                        gs[1, 0], gs[1, 1], gs[1, 2], gs[1, 3], gs[1, 4]]

        # define the location for the colour bar
        bar_gs = gridspec.GridSpec(1, 2)
        bar_grid = bar_gs[0, 1]
        bar_gs.update(top=0.23, bottom=0.08, left=gs_left, right=gs_right)

        for i, ensemble in enumerate(cube.slices_over('Ensemble member')):
            # TODO need a better way to get the ensemble_name
            ensemble_name = 'r1i1p{n}'.format(
                n=int(ensemble.coord('Ensemble member').points[0] + 1))

            log.debug('generating postage stamp map for ensemble {}'.
                      format(ensemble_name))

            ax = fig.add_subplot(grid[i], projection=plotsettings.proj)

            # Setting bar_orientation="none" here to override (prevent) drawing
            # the colour bar:
            result = maps.plot_standard_map(ensemble, plotsettings, fig=fig,
                                            ax=ax, barlab=None,
                                            bar_orientation="none",
                                            outfnames=None)
            # add a title
            title = self.vocab.get_collection_term_label(
                InputType.ENSEMBLE, ensemble_name)
            ax.set_title(title)

            # add a coast line
            self.plot_overlay('', False)

        # add the sub plot to contain the bar
        ax = fig.add_subplot(bar_grid)
        ax.axis('off')

        return result
