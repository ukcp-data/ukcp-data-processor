import logging

import iris
from ukcp_dp.constants import InputType
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter, value_to_string


LOG = logging.getLogger(__name__)


class SampleCsvWriter(BaseCsvWriter):
    """
    The sample data CSV writer class.

    This class extends BaseCsvWriter with a _write_csv(self).
    """

    def _write_csv(self):
        """
        Write out the data, in CSV format, associated with sample.
        """

        # add the label to the header
        if self.input_data.get_value(InputType.TIME_PERIOD) == "all":
            self.header.append("Date")
        else:
            self.header.append("sample id")

        key_list = []

        for i, cube in enumerate(self.cube_list):
            if self.input_data.get_value(InputType.TIME_PERIOD) == "all":
                self._write_sample_with_date(cube, i, key_list)
            else:
                self._write_sample(cube, i, key_list)

        output_data_file_path = self._get_full_file_name()
        self._write_data_dict(output_data_file_path, key_list)

        return [output_data_file_path]

    def _write_sample(self, cube, i, key_list):
        # add the variable label to the header
        self.header.append(self.input_data.get_value_label(InputType.VARIABLE)[i])

        for sample_slice in cube.slices_over("sample"):
            sample_id = int(sample_slice.coord("sample").points[0])
            value = value_to_string(sample_slice.data)

            try:
                self.data_dict[sample_id].append(value)
            except KeyError:
                key_list.append(sample_id)
                self.data_dict[sample_id] = [value]

    def _write_sample_with_date(self, cube, i, key_list):
        """
        Write out the data, in CSV format.
        """
        for sample_slice in cube.slices_over("sample"):
            sample_id = int(sample_slice.coord("sample").points[0])

            var = self.input_data.get_value_label(InputType.VARIABLE)[i]
            self.header.append(
                "{var}(sample {sample_id})".format(sample_id=sample_id, var=var)
            )
            self._write_time_cube(sample_slice, key_list)

    def _write_time_cube(self, cube, key_list):
        """
        Slice the cube over 'time' and update data_dict
        """
        data = cube.data[:]
        coords = cube.coord("time")[:]
        for time_ in range(0, data.shape[0]):
            value = value_to_string(data[time_])
            time_str = coords[time_].cell(0).point.strftime("%Y-%m-%d")
            try:
                self.data_dict[time_str].append(value)
            except KeyError:
                key_list.append(time_str)
                self.data_dict[time_str] = [value]
