from _graph_plotter import GraphPlotter
import iris
import iris.quickplot as qplt
import matplotlib.pyplot as plt
from ukcp_dp.constants import DATA_SOURCE_PROB, InputType

import logging
log = logging.getLogger(__name__)


class PlumePlotter(GraphPlotter):
    """
    The plume plotter class.

    This class extends BasePlotter with a _generate_graph(self, cube).
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
        percentiles = [10, 50, 90]
        for percentile in percentiles:
            percentile_cube = cube.extract(
                iris.Constraint(percentile=percentile))
            label = '{}th Percentile'.format(percentile)
            qplt.plot(percentile_cube, label=label)

    def _plot_ensemble(self, cube):
        highlighted_ensemble_members = self.input_data.get_value(
            InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS)

        for ensemble_slice in cube.slices_over('Ensemble member'):
            # TODO hack to get name
            ensemble_name = 'r1i1p{}'.format(int(
                ensemble_slice.coord('Ensemble member').points[0]) + 1)

            # highlighted ensembles should be included in the legend
            if ensemble_name in highlighted_ensemble_members:
                qplt.plot(ensemble_slice, label=ensemble_name)
            else:
                qplt.plot(ensemble_slice, '0.8')
