import logging

from ukcp_dp.constants import InputType
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter
from ukcp_dp.file_writers._utils import convert_to_2dp


log = logging.getLogger(__name__)


class CdfCsvWriter(BaseCsvWriter):
    """
    The CDF CSV writer class.

    This class extends BaseCsvWriter with a _write_csv(self).
    """

    def _write_csv(self):
        """
        Write out the data, in CSV format, associated with a CDF plot.
        """
        self.header.append('Percentile')
        key_list = []

        for cube in self.cube_list:
            scenario = self.vocab.get_collection_term_label(
                InputType.SCENARIO, cube.attributes['scenario'])
            # the CDF plot will be of the first variable
            var = self.input_data.get_value_label(
                InputType.VARIABLE)[0].encode('utf-8')
            self.header.append('{var}({scenario})'.format(
                scenario=scenario, var=var))
            self._read_percentile_cube(cube, key_list)

        # now write the data
        output_data_file_path = self._get_full_file_name()
        self._write_data_dict(output_data_file_path, key_list)

        return [output_data_file_path]

    def _read_percentile_cube(self, cube, key_list):
        """
        Slice the cube over 'percentile' and update data_dict
        """
        for _slice in cube.slices_over('percentile'):
            x = convert_to_2dp(_slice.data)
            y = convert_to_2dp(_slice.coord('percentile').points[0])
            try:
                self.data_dict[y].append(x)
            except KeyError:
                key_list.append(y)
                self.data_dict[y] = [x]
