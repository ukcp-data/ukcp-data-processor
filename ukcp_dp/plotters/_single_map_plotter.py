"""
This module contains the SingleMapPlotter class, which implements the _generate_subplots
method from the MapPlotter base class.

"""
import logging

import matplotlib.gridspec as gridspec
from ukcp_dp.constants import AreaType, InputType
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

        gs_top = 0.79
        gs_bottom = 0.14
        gs_left = 0.02
        gs_right = 0.98

        grid_spec = gridspec.GridSpec(1, 1)
        grid_spec.update(top=gs_top, bottom=gs_bottom, left=gs_left, right=gs_right)
        bar_gs = gridspec.GridSpec(1, 4)
        bar_grid = bar_gs[0, 1:-1]
        bar_gs.update(top=0.28, bottom=0.08, left=gs_left, right=gs_right)

        result = self._add_sub_plot(fig, grid_spec[0, 0], plot_settings, cube)

        # add the sub plot to contain the bar
        ax = fig.add_subplot(bar_grid)
        ax.axis("off")

        return result

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
