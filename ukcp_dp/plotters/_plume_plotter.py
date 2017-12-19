from _graph_plotter import GraphPlotter
import iris
import iris.quickplot as qplt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.pyplot as plt
from ukcp_dp.constants import DATA_SOURCE_PROB, ENSEMBLE_COLOUR_PALETTE, \
    ENSEMBLE_GREYSCALE_PALETTE, ENSEMBLE_LOWLIGHT, InputType, \
    QUANTILE_COLOURS, QUANTILE_GREYSCALE

import logging
log = logging.getLogger(__name__)


class PlumePlotter(GraphPlotter):
    """
    The plume plotter class.

    This class extends BasePlotter with a _generate_graph(self).
    """

    def _generate_graph(self):
        """
        Override base class method.

        """
        log.debug('_generate_graph')

        if (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_PROB):
            # plot the percentiles
            self._plot_probability_levels(self.cube_list[0])

        else:
            # plot the ensemble members
            self._plot_ensemble(self.cube_list[0])

            if self.overlay_cube is not None:
                # add overlay
                self._plot_probability_levels(self.overlay_cube)

        # clear the title field
        plt.title('')

    def _plot_probability_levels(self, cube):
        # extract 10th, 50th and 90th percentiles
        linestyle = ['dashed', 'dashdot', 'dotted']

        percentiles = [10, 50, 90]
        for i, percentile in enumerate(percentiles):
            percentile_cube = cube.extract(
                iris.Constraint(percentile=percentile))

            if percentile_cube is None:
                raise Exception(
                    'Attempted to plot the {}th percentile, but no data found'.
                    format(percentile))

            label = '{}th Percentile'.format(percentile)

            if self.input_data.get_value(InputType.COLOUR_MODE) == 'c':
                qplt.plot(percentile_cube, label=label,
                          color=QUANTILE_COLOURS[i])
            else:
                qplt.plot(percentile_cube, label=label,
                          color=QUANTILE_GREYSCALE,
                          linestyle=linestyle[i])

    def _plot_ensemble(self, cube):

        highlighted_ensemble_members = self.input_data.get_value(
            InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS)

        if self.input_data.get_value(InputType.COLOUR_MODE) == 'c':
            cmap = ENSEMBLE_COLOUR_PALETTE
        else:
            cmap = ENSEMBLE_GREYSCALE_PALETTE
        c_norm = colors.Normalize(
            vmin=0, vmax=len(highlighted_ensemble_members))
        scalar_map = cmx.ScalarMappable(norm=c_norm, cmap=cmap)

        highlighted_counter = 1
        for ensemble_slice in cube.slices_over('Ensemble member'):
            # TODO hack to get name
            ensemble_name = 'r1i1p{}'.format(int(
                ensemble_slice.coord('Ensemble member').points[0]) + 1)

            # highlighted ensembles should be included in the legend
            if ensemble_name in highlighted_ensemble_members:
                colour_val = scalar_map.to_rgba(highlighted_counter)
                highlighted_counter += 1
                qplt.plot(ensemble_slice, label=ensemble_name,
                          color=colour_val,
                          zorder=highlighted_counter)
            else:
                qplt.plot(ensemble_slice, color=ENSEMBLE_LOWLIGHT, zorder=0)
