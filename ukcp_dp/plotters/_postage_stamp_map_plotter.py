import logging

import iris

from _map_plotter import MapPlotter
import matplotlib.gridspec as gridspec
from ukcp_dp.constants import AreaType, InputType
import ukcp_dp.ukcp_standard_plots.mapper as maps
from ukcp_dp.plotters._map_plotter import _plot_standard_choropleth_map


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

        ensemble_count = len(cube.coord('ensemble_member').points)

        # work out the number of sub-plots based on orientation of the plot
        # and number of ensembles
        if self._is_landscape(cube) is True:

            if ensemble_count == 12:
                gs = gridspec.GridSpec(3, 4)
                gs.update(top=gs_top, bottom=0.10, left=gs_left,
                          right=gs_right)
                grid = [gs[0, 0], gs[0, 1], gs[0, 2], gs[0, 3],
                        gs[1, 0], gs[1, 1], gs[1, 2], gs[1, 3],
                        gs[2, 0], gs[2, 1], gs[2, 2], gs[2, 3]]

            else:  # ensemble_count == 28:
                gs = gridspec.GridSpec(4, 7)
                gs.update(top=gs_top, bottom=0.10, left=gs_left,
                          right=gs_right)
                grid = [gs[0, 0], gs[0, 1], gs[0, 2], gs[0, 3], gs[0, 4],
                        gs[0, 5], gs[0, 6],
                        gs[1, 0], gs[1, 1], gs[1, 2], gs[1, 3], gs[1, 4],
                        gs[1, 5], gs[1, 6],
                        gs[2, 0], gs[2, 1], gs[2, 2], gs[2, 3], gs[2, 4],
                        gs[2, 5], gs[2, 6],
                        gs[3, 0], gs[3, 1], gs[3, 2], gs[3, 3], gs[3, 4],
                        gs[3, 5], gs[3, 6]]

        else:  # portrait
            if ensemble_count == 12:
                gs = gridspec.GridSpec(2, 6)
                gs.update(top=gs_top, bottom=0.10, left=gs_left,
                          right=gs_right)
                grid = [gs[0, 0], gs[0, 1], gs[0, 2], gs[0, 3], gs[0, 4],
                        gs[0, 5],
                        gs[1, 0], gs[1, 1], gs[1, 2], gs[1, 3], gs[1, 4],
                        gs[1, 5]]

            else:  # if ensemble_count == 28:
                gs = gridspec.GridSpec(3, 10)
                gs.update(top=gs_top, bottom=0.10, left=gs_left,
                          right=gs_right)
                grid = [gs[0, 0], gs[0, 1], gs[0, 2], gs[0, 3], gs[0, 4],
                        gs[0, 5], gs[0, 6], gs[0, 7], gs[0, 8], gs[0, 9],
                        gs[1, 0], gs[1, 1], gs[1, 2], gs[1, 3], gs[1, 4],
                        gs[1, 5], gs[1, 6], gs[1, 7], gs[1, 8], gs[1, 9],
                        gs[2, 0], gs[2, 1], gs[2, 2], gs[2, 3], gs[2, 4],
                        gs[2, 5], gs[2, 6], gs[2, 7]]

        # define the location for the colour bar
        bar_gs = gridspec.GridSpec(1, 3)
        bar_grid = bar_gs[0, 0]
        bar_gs.update(top=0.23, bottom=0.05, left=gs_left, right=gs_right)

        if self.input_data.get_value(InputType.ORDER_BY_MEAN) is True:
            # order by means
            result = self._plot_maps_mean_order(cube, fig, grid, plotsettings)

        else:
            result = self._plot_maps_name_order(cube, fig, grid, plotsettings)

        # add the sub plot to contain the bar
        ax = fig.add_subplot(bar_grid)
        ax.axis('off')

        return result

    def _plot_maps_mean_order(self, cube, fig, grid, plotsettings):
        # cube_means, key = ensemble id, value = mean
        ensemble_cube_means = {}

        if self.input_data.get_area_type() == AreaType.BBOX:
            ensemble_mean_cube = cube.collapsed(
                ['projection_x_coordinate', 'projection_y_coordinate', 'latitude',
                 'longitude'], iris.analysis.MEAN)
        else:
            ensemble_mean_cube = cube.collapsed(
                ['region'], iris.analysis.MEAN)

        for ensemble_slice in ensemble_mean_cube.slices_over(
                'ensemble_member'):
            ensemble_id = int(
                ensemble_slice.coord('ensemble_member').points[0])
            ensemble_cube_means[ensemble_id] = ensemble_slice.data.item()

        # ensemble_cubes, key = mean, value = cube
        ensemble_cubes = {}

        for ensemble_slice in cube.slices_over('ensemble_member'):
            ensemble_id = int(
                ensemble_slice.coord('ensemble_member').points[0])
            mean_value = ensemble_cube_means[ensemble_id]
            ensemble_cubes[mean_value] = ensemble_slice

        i = 0
        for ensemble_mean in sorted(ensemble_cubes.keys()):
            result = self._plot_map(
                fig, grid, plotsettings, ensemble_cubes[ensemble_mean], i)
            i += 1

        return result

    def _plot_maps_name_order(self, cube, fig, grid, plotsettings):
        for i, ensemble_slice in enumerate(
                cube.slices_over('ensemble_member')):
            result = self._plot_map(fig, grid, plotsettings, ensemble_slice, i)
        return result

    def _plot_map(self, fig, grid, plotsettings, ensemble_cube, i):
        ensemble_name = ensemble_cube.coord('ensemble_member_id').points[0]

        log.debug('generating postage stamp map for ensemble {}'.
                  format(ensemble_name))

        ax = fig.add_subplot(grid[i], projection=plotsettings.proj)

        # Setting bar_orientation="none" here to override (prevent) drawing
        # the colour bar:
        if self.input_data.get_area_type() == AreaType.BBOX:
            result = maps.plot_standard_map(ensemble_cube, plotsettings,
                                            fig=fig,
                                            ax=ax, barlab=None,
                                            bar_orientation="none",
                                            outfnames=None)
        else:
            result = _plot_standard_choropleth_map(ensemble_cube, plotsettings, fig=fig,
                                                   ax=ax, barlab=None,
                                                   bar_orientation="none",
                                                   outfnames=None)

        # add a title
        if ensemble_name.startswith('HadGEM3-GC3.05-r001i1p'):
            ensemble_name = ensemble_name.split('HadGEM3-GC3.05-r001i1p')[1]
        elif ensemble_name.endswith('-r1i1p1'):
            ensemble_name = ensemble_name.split('-r1i1p1')[0]
        title = "Member: {}".format(ensemble_name)
        ax.set_title(title, fontdict={'fontsize': 'medium'})

        # add a coast line
        self.plot_overlay('', False)

        return result
