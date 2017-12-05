from _graph_plotter import GraphPlotter
import iris
import iris.quickplot as qplt
import matplotlib.pyplot as plt
from ukcp_dp.constants import DATA_SOURCE_PROB, InputType
from ukcp_dp.data_extractor import get_probability_levels

import logging
log = logging.getLogger(__name__)


class PlumePlotter(GraphPlotter):
    """
    The plume plotter class.

    This class extends BasePlotter with a _generate_graph(self, cube).
    """

    def _generate_graph(self, cubes):
        """
        Override base class method.

        @param cubes (list(iris data cube)): a list of cubes containing the
            selected data
        """
        log.debug('_generate_graph')

        if (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_PROB):
            # extract 10th, 50th and 90th percentiles
            cube = get_probability_levels(cubes[0])
            # plot the percentiles
            self._plot_probability_levels(cube)

        else:
            # plot the ensemble members
            self._plot_ensemble(cubes[0])

        try:
            # add overlay
            self._plot_probability_levels(cubes[1])
        except IndexError:
            # no overlay
            pass

        # clear the title field
        plt.title('')

    def _plot_probability_levels(self, cube):
        for percentile_slice in cube.slices_over('percentile'):
            label = '{}th Percentile'.format(int(
                percentile_slice.coord('percentile').points[0]))
            qplt.plot(percentile_slice, label=label)

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
