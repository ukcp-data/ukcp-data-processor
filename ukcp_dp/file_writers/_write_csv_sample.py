import logging

from ukcp_dp.constants import InputType
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter
from ukcp_dp.file_writers._utils import round_variable


log = logging.getLogger(__name__)


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
        self.header.append('sample id')
        key_list = []

        for i, cube in enumerate(self.cube_list):
            variable = self.input_data.get_value_label(
                InputType.VARIABLE)[i].encode('utf-8')
            # add the variable label to the header
            self.header.append(variable)

            for sample_slice in cube.slices_over('sample'):
                sample_id = int(sample_slice.coord('sample').points[0])
                value = round_variable(self.input_data.get_value(
                    InputType.VARIABLE)[i], sample_slice.data)

                try:
                    self.data_dict[sample_id].append(value)
                except KeyError:
                    key_list.append(sample_id)
                    self.data_dict[sample_id] = [value]

        output_data_file_path = self._get_full_file_name()
        self._write_data_dict(output_data_file_path, key_list)

        return [output_data_file_path]
