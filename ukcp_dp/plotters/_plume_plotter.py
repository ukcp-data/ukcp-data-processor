from _base_plotter import BasePlotter
import iris
import iris.quickplot as qplt
from ukcp_dp.constants import InputType
from ukcp_dp.vocab_manager._vocab import get_collection_term_label


class PlumePlotter(BasePlotter):
    """
    The plume plotter class.

    This class extends BasePlotter with a _generate_plot(self, cube).
    """

    def _generate_plot(self, input_data, cube):
        """
        Override base class method.

        @param input_data (InputData): an object containing user defined values
        @param cube (iris data cube): an object containing the selected data
        """
        self.cube = cube

        if input_data.get_value(InputType.SHOW_PROBABILITY_LEVELS) is True:
            self._plot_probability_levels()

        try:
            ensemble = input_data.get_value(InputType.ENSEMBLE)
            self._plot_ensemble(ensemble)
        except KeyError:
            pass

    def _plot_probability_levels(self):
        percentile_constraint = iris.Constraint(percentile=10)
        percentile_10 = self.cube.extract(percentile_constraint)
        percentile_constraint = iris.Constraint(percentile=50)
        percentile_50 = self.cube.extract(percentile_constraint)
        percentile_constraint = iris.Constraint(percentile=90)
        percentile_90 = self.cube.extract(percentile_constraint)

        # Now generate the plots
        qplt.plot(percentile_90, label='90th percentile')
        qplt.plot(percentile_50, label='50th percentile')
        qplt.plot(percentile_10, label='10th percentile')

    def _plot_ensemble(self, data_source, ensemble):
        # TODO whole method is a hack

        ensemble_members = get_collection_term_label('ensemble_member_set',
                                                     data_source)
        count = 12
        for member in ensemble_members:
            count += 5
            if count > 89:
                count = 11

            percentile_constraint = iris.Constraint(percentile=count)
            percentile_cube = None
            while percentile_cube is None:
                percentile_constraint = iris.Constraint(percentile=count)
                percentile_cube = self.cube.extract(percentile_constraint)
                count += 1
                if count > 89:
                    count = 11

            if member in ensemble:
                qplt.plot(percentile_cube, label=member)
            else:
                qplt.plot(percentile_cube, '0.8')
