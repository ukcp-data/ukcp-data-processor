"""
This module contains the SingleMapPlotter class, which implements the _generate_subplots
method from the MapPlotter base class.

"""
import logging
import math

import iris

import matplotlib.gridspec as gridspec
from ukcp_dp.constants import AreaType, InputType, COLOUR_RANGE_STARTS_AT_ZERO
from ukcp_dp.plotters._map_plotter import MapPlotter
from ukcp_dp.plotters.utils._map_utils import (
    plot_standard_map,
    plot_standard_choropleth_map,
)


LOG = logging.getLogger(__name__)


class SingleMapPlotter(MapPlotter):
    """
    The single map plotter class.

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

        plot_settings.vrange, plot_settings.vstep = self._get_data_range(cube)
        plot_settings.vmid = _get_mid_point(
            plot_settings.vrange, self.input_data.get_value(InputType.VARIABLE)
        )

        if self._is_landscape(cube, 1.25) is True:
            gs_top = 0.79
            gs_bottom = 0.14
            gs_left = 0.02
            gs_right = 0.98

            if (
                plot_settings.vstep == 1
                and plot_settings.vrange[1] - plot_settings.vrange[0] == 2
            ):
                # special case
                # Position of the colour-bar Axes: [left,bottom, width,height]
                plot_settings.bar_position = [0.25, 0.08, 0.2, 0.025]
            else:
                # Position of the colour-bar Axes: [left,bottom, width,height]
                plot_settings.bar_position = [0.25, 0.08, 0.5, 0.025]

            plot_settings.bar_orientation = "horizontal"

        else:  # portrait
            gs_top = 0.79
            gs_bottom = 0.05
            gs_left = 0.15
            gs_right = 0.8

            if (
                plot_settings.vstep == 1
                and plot_settings.vrange[1] - plot_settings.vrange[0] == 2
            ):
                # special case
                # Position of the colour-bar Axes: [left,bottom, width,height]
                plot_settings.bar_position = [0.82, 0.25, 0.025, 0.2]
            else:
                # special case
                # Position of the colour-bar Axes: [left,bottom, width,height]
                plot_settings.bar_position = [0.82, 0.25, 0.025, 0.5]

            plot_settings.bar_orientation = "vertical"

        grid_spec = gridspec.GridSpec(1, 1)
        grid_spec.update(top=gs_top, bottom=gs_bottom, left=gs_left, right=gs_right)

        result = self._add_sub_plot(fig, grid_spec[0, 0], plot_settings, cube)

        return result

    def _get_data_range(self, cube):

        if self.input_data.get_area_type() == AreaType.BBOX:
            cube_min = cube.collapsed(
                [
                    "projection_x_coordinate",
                    "projection_y_coordinate",
                    "latitude",
                    "longitude",
                ],
                iris.analysis.MIN,
            ).data.item()
            cube_max = cube.collapsed(
                [
                    "projection_x_coordinate",
                    "projection_y_coordinate",
                    "latitude",
                    "longitude",
                ],
                iris.analysis.MAX,
            ).data.item()
        else:
            cube_min = cube.collapsed(["region"], iris.analysis.MIN).data.item()
            cube_max = cube.collapsed(["region"], iris.analysis.MAX).data.item()

        if cube_max - cube_min > 11:
            cube_min = math.floor(cube_min / 2) * 2
            cube_max = math.ceil(cube_max / 2) * 2
        else:
            cube_min = math.floor(cube_min)
            cube_max = math.ceil(cube_max)

        step = _get_data_step(cube_min, cube_max)
        if step > 2 and cube_min + (step * 10) > cube_max:
            cube_max = cube_min + (step * 10)

        if cube_min == cube_max:
            cube_max = cube_max + 2
            step = 1

        return [cube_min, cube_max], step

    def _add_sub_plot(self, fig, grid, plot_settings, data):
        ax = fig.add_subplot(grid, projection=plot_settings.proj)

        # Setting bar_orientation="none" here to override (prevent) drawing
        # the colorbar
        if self.input_data.get_area_type() == AreaType.BBOX:
            result = plot_standard_map(
                data,
                plot_settings,
                fig=fig,
                ax=ax,
                barlab=None,
                bar_orientation="none",
                outfnames=None,
            )
            self.plot_overlay(
                self.input_data.get_value(InputType.SHOW_BOUNDARIES), hi_res=True
            )
        else:
            result = plot_standard_choropleth_map(
                data,
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

        return result


def _get_data_step(min_value, max_value):
    data_range = max_value - min_value
    if data_range < 4:
        return 0.25
    if data_range < 8:
        return 0.5
    if data_range < 13:
        return 1
    return math.ceil(data_range / 20) * 2


def _get_mid_point(vrange, variable):
    if variable[0] in COLOUR_RANGE_STARTS_AT_ZERO:
        return (vrange[0] + vrange[1]) / 2
    if vrange[0] > 0:
        return vrange[0]
    if vrange[1] < 0:
        return vrange[1]
    return 0
