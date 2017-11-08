from _base_plotter import BasePlotter
import iris
import iris.quickplot as qplt
from ukcp_dp.constants import InputType
from ukcp_dp.vocab_manager._vocab import get_ensemble_member_set


class PlumePlotter(BasePlotter):
    """
    The plume plotter class.

    This class extends BasePlotter with a _generate_plot(self, cube).
    """

    def _generate_plot(self, input_data, cubes):
        """
        Override base class method.

        @param input_data (InputData): an object containing user defined values
        @param cubes (list(iris data cube)): a list of cubes containing the
            selected data
        """
        try:
            ensemble = input_data.get_value(InputType.ENSEMBLE)
            self._plot_ensemble(cubes[0],
                                input_data.get_value(InputType.DATA_SOURCE),
                                ensemble)
        except KeyError:
            pass

        if input_data.get_value(InputType.SHOW_PROBABILITY_LEVELS) is True:
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
