import logging

import iris
from ukcp_dp.constants import DATA_SOURCE_GCM, DATA_SOURCE_PROB
from ukcp_dp.constants import InputType
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter
from ukcp_dp.vocab_manager import get_ensemble_member_set

log = logging.getLogger(__name__)


class PlumeCsvWriter(BaseCsvWriter):
    """
    The cdf CSV writer class.

    This class extends BaseCsvWriter with a _write_csv(self).
    """

    def _write_csv(self):
        """
        Write out the data, in CSV format, associated with a plume plot.
        """
        self.header.append('Date')
        if (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_PROB):
            self._write_csv_plume_land_prob()
        else:
            self._write_csv_plume_other()

        # now write the data
        output_data_file_path = self._get_full_file_name()
        self._write_data_dict(output_data_file_path)

        return [output_data_file_path]

    def _write_csv_plume_land_prob(self):
        """
        Write out the data, in CSV format, associated with a plume plot for
        land_prob data.
        """
        for cube in self.cube_list:
            self._get_percentiles(cube)

    def _write_csv_plume_other(self):
        """
        Write out the data, in CSV format, associated with a plume plot.
        """
        for cube in self.cube_list:
            # there should only be one cube
            for ensemble_slice in cube.slices_over('Ensemble member'):
                # TODO hack to get name
                ensemble_name = get_ensemble_member_set(DATA_SOURCE_GCM)[
                    int(ensemble_slice.coord('Ensemble member').points[0])]
                ensemble_label = self.vocab.get_collection_term_label(
                    InputType.ENSEMBLE, ensemble_name)

                # the plume plot will be of the first variable
                var = self.input_data.get_value_label(
                    InputType.VARIABLE)[0].encode('utf-8')
                self.header.append('{var}({ensemble})'.format(
                    ensemble=ensemble_label, var=var))
                self._read_time_cube(ensemble_slice)

        # now add the data from the overlay
        if self.overlay_cube is not None:
            percentile_cube = self.overlay_cube.extract(
                iris.Constraint(percentile=10))
            self._get_percentiles(percentile_cube)
            percentile_cube = self.overlay_cube.extract(
                iris.Constraint(percentile=90))
            self._get_percentiles(percentile_cube)

    def _get_percentiles(self, cube):
        """
        Update the data dict and header with data from the cube.
        The cube is sliced over percentile then time.
        """
        for _slice in cube.slices_over('percentile'):
            percentile = str(_slice.coord('percentile').points[0])
            # the plume plot will be of the first variable
            var = self.input_data.get_value_label(
                InputType.VARIABLE)[0].encode('utf-8')
            self.header.append('{var}({percentile}th Percentile)'.format(
                percentile=percentile, var=var))
            self._read_time_cube(_slice)

    def _read_time_cube(self, cube):
        """
        Slice the cube over 'time' and update data_dict
        """
        for _slice in cube.slices_over('time'):
            with iris.FUTURE.context(cell_datetime_objects=True):
                time_str = str(_slice.coord('time').cell(0).point)
            try:
                self.data_dict[time_str].append(str(_slice.data))
            except KeyError:
                self.data_dict[time_str] = [str(_slice.data)]
