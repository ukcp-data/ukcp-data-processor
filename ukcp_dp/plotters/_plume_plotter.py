from _graph_plotter import GraphPlotter
import iris
import iris.quickplot as qplt
from matplotlib.transforms import Bbox
from ukcp_dp.constants import InputType
from ukcp_dp.vocab_manager._vocab import get_ensemble_member_set

import logging
log = logging.getLogger(__name__)


class PlumePlotter(GraphPlotter):
    """
    The plume plotter class.

    This class extends BasePlotter with a _generate_graph(self, cube).
    """

    def _generate_graph(self, cubes, fig, metadata_bbox):
        """
        Override base class method.

        @param cubes (list(iris data cube)): a list of cubes containing the
            selected data
        @param fig (matplotlib.figure.Figure)
        @param metadata_bbox (Bbox): the bbox surrounding the metadata table
        """
        log.debug('_generate_graph')
        # Set the area below the metadata and allow room for the labels
        fig.add_axes(Bbox([[0.07, 0.08], [0.99, metadata_bbox.y0 - 0.06]]))
        try:
            ensemble = self.input_data.get_value(InputType.ENSEMBLE)
            self._plot_ensemble(cubes[0],
                                self.input_data.get_value(
                                    InputType.DATA_SOURCE),
                                ensemble)
        except KeyError:
            pass

        if (self.input_data.get_value(InputType.SHOW_PROBABILITY_LEVELS) is
                True):
            self._plot_probability_levels(cubes[1])

    def _plot_probability_levels(self, cube):
        percentile_constraint = iris.Constraint(percentile=10)
        percentile_10 = cube.extract(percentile_constraint)
        percentile_constraint = iris.Constraint(percentile=50)
        percentile_50 = cube.extract(percentile_constraint)
        percentile_constraint = iris.Constraint(percentile=90)
        percentile_90 = cube.extract(percentile_constraint)

        # Now generate the plots
        qplt.plot(percentile_90, label='90th percentile')
        qplt.plot(percentile_50, label='50th percentile')
        qplt.plot(percentile_10, label='10th percentile')

    def _plot_ensemble(self, cube, data_source, ensemble):
        ensemble_members = get_ensemble_member_set(data_source)
        for member in ensemble_members:
            # hack due to incorrect values for ensemble member
            #             ensemble_constraint = iris.Constraint(
            #                 coord_values={'Ensemble member': member})
            ensemble_constraint = iris.Constraint(
                coord_values={'Ensemble member':
                              int(member.split('r1i1p')[1]) - 1})
            ensemble_cube = cube.extract(ensemble_constraint)
            if member in ensemble:
                qplt.plot(ensemble_cube, label=member)
            else:
                qplt.plot(ensemble_cube, '0.8')
