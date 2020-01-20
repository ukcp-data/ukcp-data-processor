import logging

import iris
import matplotlib.gridspec as gridspec
from ukcp_dp.constants import AreaType, InputType, COLLECTION_CPM, COLLECTION_RCM
from ukcp_dp.plotters._map_plotter import MapPlotter
from ukcp_dp.plotters.utils._map_utils import (
    plot_standard_map,
    plot_standard_choropleth_map,
)


LOG = logging.getLogger(__name__)


class PostageStampMapPlotter(MapPlotter):
    """
    The postage stamp map plotter class.

    This class extends MapPlotter with a _generate_subplots(self, cube,
    plot_settings).
    """

    def _generate_subplots(self, cube, plot_settings, fig):
        """
        Override base class method.

        @param cube (iris cube): a cube containing the selected data
        @param plot_settings (StandardMap): an object containing plot settings
        @param fig (matplotlib.figure.Figure)
        """
        LOG.debug("_generate_subplots")

        gs_top = 0.82
        gs_left = 0.02
        gs_right = 0.98
        gs_bottom = 0.12

        ensemble_count = len(cube.coord("ensemble_member").points)
        title_font_size = self.input_data.get_font_size()

        # work out the number of sub-plots based on orientation of the plot
        # and number of ensembles
        if self._is_landscape(cube) is True:

            if ensemble_count == 12:
                gs = gridspec.GridSpec(3, 4)
                gs.update(top=gs_top, bottom=gs_bottom, left=gs_left, right=gs_right)
                grid = [
                    gs[0, 0],
                    gs[0, 1],
                    gs[0, 2],
                    gs[0, 3],
                    gs[1, 0],
                    gs[1, 1],
                    gs[1, 2],
                    gs[1, 3],
                    gs[2, 0],
                    gs[2, 1],
                    gs[2, 2],
                    gs[2, 3],
                ]

            elif ensemble_count == 15:
                gs = gridspec.GridSpec(3, 5)
                gs.update(top=gs_top, bottom=gs_bottom, left=gs_left, right=gs_right)
                grid = [
                    gs[0, 0],
                    gs[0, 1],
                    gs[0, 2],
                    gs[0, 3],
                    gs[0, 4],
                    gs[1, 0],
                    gs[1, 1],
                    gs[1, 2],
                    gs[1, 3],
                    gs[1, 4],
                    gs[2, 0],
                    gs[2, 1],
                    gs[2, 2],
                    gs[2, 3],
                    gs[2, 4],
                ]

            else:  # ensemble_count == 28:
                gs = gridspec.GridSpec(4, 7)
                gs.update(top=gs_top, bottom=gs_bottom, left=gs_left, right=gs_right)
                grid = [
                    gs[0, 0],
                    gs[0, 1],
                    gs[0, 2],
                    gs[0, 3],
                    gs[0, 4],
                    gs[0, 5],
                    gs[0, 6],
                    gs[1, 0],
                    gs[1, 1],
                    gs[1, 2],
                    gs[1, 3],
                    gs[1, 4],
                    gs[1, 5],
                    gs[1, 6],
                    gs[2, 0],
                    gs[2, 1],
                    gs[2, 2],
                    gs[2, 3],
                    gs[2, 4],
                    gs[2, 5],
                    gs[2, 6],
                    gs[3, 0],
                    gs[3, 1],
                    gs[3, 2],
                    gs[3, 3],
                    gs[3, 4],
                    gs[3, 5],
                    gs[3, 6],
                ]

        else:  # portrait
            if ensemble_count == 12:
                gs = gridspec.GridSpec(2, 6)
                gs.update(top=gs_top, bottom=gs_bottom, left=gs_left, right=gs_right)
                grid = [
                    gs[0, 0],
                    gs[0, 1],
                    gs[0, 2],
                    gs[0, 3],
                    gs[0, 4],
                    gs[0, 5],
                    gs[1, 0],
                    gs[1, 1],
                    gs[1, 2],
                    gs[1, 3],
                    gs[1, 4],
                    gs[1, 5],
                ]

            elif ensemble_count == 15:
                gs = gridspec.GridSpec(2, 8)
                gs.update(top=gs_top, bottom=gs_bottom, left=gs_left, right=gs_right)
                grid = [
                    gs[0, 0],
                    gs[0, 1],
                    gs[0, 2],
                    gs[0, 3],
                    gs[0, 4],
                    gs[0, 5],
                    gs[0, 6],
                    gs[0, 7],
                    gs[1, 0],
                    gs[1, 1],
                    gs[1, 2],
                    gs[1, 3],
                    gs[1, 4],
                    gs[1, 5],
                    gs[1, 6],
                    gs[1, 7],
                ]

            else:  # if ensemble_count == 28:
                title_font_size = self.input_data.get_font_size() * 0.7
                gs = gridspec.GridSpec(3, 10)
                gs.update(top=gs_top, bottom=gs_bottom, left=gs_left, right=gs_right)
                grid = [
                    gs[0, 0],
                    gs[0, 1],
                    gs[0, 2],
                    gs[0, 3],
                    gs[0, 4],
                    gs[0, 5],
                    gs[0, 6],
                    gs[0, 7],
                    gs[0, 8],
                    gs[0, 9],
                    gs[1, 0],
                    gs[1, 1],
                    gs[1, 2],
                    gs[1, 3],
                    gs[1, 4],
                    gs[1, 5],
                    gs[1, 6],
                    gs[1, 7],
                    gs[1, 8],
                    gs[1, 9],
                    gs[2, 0],
                    gs[2, 1],
                    gs[2, 2],
                    gs[2, 3],
                    gs[2, 4],
                    gs[2, 5],
                    gs[2, 6],
                    gs[2, 7],
                ]

        # Position of the colour-bar Axes: [left,bottom, width,height]
        plot_settings.bar_position = [0.25, 0.08, 0.5, 0.025]

        if self.input_data.get_value(InputType.ORDER_BY_MEAN) is True:
            # order by means
            result = self._plot_maps_mean_order(
                cube, fig, grid, plot_settings, title_font_size
            )

        else:
            result = self._plot_maps_name_order(
                cube, fig, grid, plot_settings, title_font_size
            )

        return result

    def _plot_maps_mean_order(self, cube, fig, grid, plot_settings, title_font_size):
        # cube_means, key = ensemble id, value = mean
        ensemble_cube_means = {}

        if self.input_data.get_area_type() == AreaType.BBOX:

            if self.input_data.get_value(InputType.COLLECTION) in [
                COLLECTION_CPM,
                COLLECTION_RCM,
            ]:
                # RCM is on a rotated grid
                ensemble_mean_cube = cube.collapsed(
                    [
                        "projection_x_coordinate",
                        "projection_y_coordinate",
                        "grid_latitude",
                        "grid_longitude",
                    ],
                    iris.analysis.MEAN,
                )
            else:
                ensemble_mean_cube = cube.collapsed(
                    [
                        "projection_x_coordinate",
                        "projection_y_coordinate",
                        "latitude",
                        "longitude",
                    ],
                    iris.analysis.MEAN,
                )

        else:
            ensemble_mean_cube = cube.collapsed(["region"], iris.analysis.MEAN)

        for ensemble_slice in ensemble_mean_cube.slices_over("ensemble_member"):
            ensemble_id = int(ensemble_slice.coord("ensemble_member").points[0])
            ensemble_cube_means[ensemble_id] = ensemble_slice.data.item()

        # ensemble_cubes, key = mean, value = cube
        ensemble_cubes = {}

        for ensemble_slice in cube.slices_over("ensemble_member"):
            ensemble_id = int(ensemble_slice.coord("ensemble_member").points[0])
            mean_value = ensemble_cube_means[ensemble_id]
            ensemble_cubes[mean_value] = ensemble_slice

        i = 0
        for ensemble_mean in sorted(ensemble_cubes.keys()):
            result = self._plot_map(
                fig,
                grid,
                plot_settings,
                ensemble_cubes[ensemble_mean],
                i,
                title_font_size,
            )
            i += 1

        return result

    def _plot_maps_name_order(self, cube, fig, grid, plot_settings, title_font_size):
        for i, ensemble_slice in enumerate(cube.slices_over("ensemble_member")):
            result = self._plot_map(
                fig, grid, plot_settings, ensemble_slice, i, title_font_size
            )
        return result

    def _plot_map(self, fig, grid, plot_settings, ensemble_cube, i, title_font_size):
        ensemble_name = ensemble_cube.coord("ensemble_member_id").points[0]

        LOG.debug("generating postage stamp map for ensemble %s", ensemble_name)

        ax = fig.add_subplot(grid[i], projection=plot_settings.proj)

        # Setting bar_orientation="none" here to override (prevent) drawing
        # the colour bar:
        if self.input_data.get_area_type() == AreaType.BBOX:
            result = plot_standard_map(
                ensemble_cube,
                plot_settings,
                fig=fig,
                ax=ax,
                barlab=None,
                bar_orientation="none",
                outfnames=None,
            )
            # add a coast line
            self.plot_overlay("", False)
        else:
            result = plot_standard_choropleth_map(
                ensemble_cube,
                plot_settings,
                fig=fig,
                ax=ax,
                barlab=None,
                bar_orientation="none",
                outfnames=None,
                hi_res=False,
            )
            # don't need the overlay for the choropleth map as the region
            # geometry contains them.

        # add a title
        if ensemble_name.startswith("HadGEM3-GC3.05-r001i1p"):
            ensemble_name = ensemble_name.split("HadGEM3-GC3.05-r001i1p")[1]
        elif ensemble_name.startswith("HadREM3-GA705-r001i1p"):
            ensemble_name = ensemble_name.split("HadREM3-GA705-r001i1p")[1]
        elif ensemble_name.startswith("HadREM3-RA11M-r001i1p"):
            ensemble_name = ensemble_name.split("HadREM3-RA11M-r001i1p")[1]
        elif ensemble_name.endswith("-r1i1p1"):
            ensemble_name = ensemble_name.split("-r1i1p1")[0]
        ax.set_title(ensemble_name, fontdict={"fontsize": title_font_size})

        return result
