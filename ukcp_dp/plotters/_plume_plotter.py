from _graph_plotter import GraphPlotter
import iris
import iris.quickplot as qplt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.pyplot as plt
from ukcp_dp.constants import DATA_SOURCE_PROB, InputType, OVERLAY_COLOURMAP

import logging
log = logging.getLogger(__name__)


class PlumePlotter(GraphPlotter):
    """
    The plume plotter class.

    This class extends BasePlotter with a _generate_graph(self, cube).
    """

    def _generate_graph(self, cmap):
        """
        Override base class method.

        @param cmap(LinearSegmentedColormap): colour map to use with plot
        """
        log.debug('_generate_graph')

        if (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_PROB):
            # plot the percentiles
            self._plot_probability_levels(self.cube_list[0], cmap)

        else:
            # plot the ensemble members
            self._plot_ensemble(self.cube_list[0], cmap)

        if self.overlay_cube is not None:
            # add overlay
            cmap = plt.get_cmap(OVERLAY_COLOURMAP)

            self._plot_probability_levels(self.overlay_cube, cmap)

        # clear the title field
        plt.title('')

    def _plot_probability_levels(self, cube, cmap):
        # extract 10th, 50th and 90th percentiles
        cNorm = colors.Normalize(vmin=0, vmax=3)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)

        percentiles = [10, 50, 90]
        for i, percentile in enumerate(percentiles):
            percentile_cube = cube.extract(
                iris.Constraint(percentile=percentile))
            if percentile_cube is None:
                raise Exception(
                    'Attempted to plot the {}th percentile, but no data found'.
                    format(percentile))
            label = '{}th Percentile'.format(percentile)
            colorVal = scalarMap.to_rgba(i + 1)
            qplt.plot(percentile_cube, label=label, color=colorVal)

    def _plot_ensemble(self, cube, cmap):

        highlighted_ensemble_members = self.input_data.get_value(
            InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS)

        cNorm = colors.Normalize(
            vmin=0, vmax=len(highlighted_ensemble_members))
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)

        for i, ensemble_slice in enumerate(
                cube.slices_over('Ensemble member')):
            # TODO hack to get name
            ensemble_name = 'r1i1p{}'.format(int(
                ensemble_slice.coord('Ensemble member').points[0]) + 1)

            # highlighted ensembles should be included in the legend
            if ensemble_name in highlighted_ensemble_members:
                colorVal = scalarMap.to_rgba(i + 1)
                qplt.plot(ensemble_slice, label=ensemble_name, color=colorVal)
            else:
                qplt.plot(ensemble_slice, '0.8')
