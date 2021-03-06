"""
This module contains the CdfCsvWriter class, which implements the _write_csv method
from the BaseCsvWriter base class.

"""
import logging

from ukcp_dp.constants import InputType, CDF_LABEL
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter, value_to_string


LOG = logging.getLogger(__name__)


# pylint: disable=R0903
class CdfCsvWriter(BaseCsvWriter):
    """
    The CDF CSV writer class.

    This class extends BaseCsvWriter with a _write_csv(self).

    """

    def _write_csv(self):
        """
        Write out the data, in CSV format, associated with a CDF plot.

        """
        self.header.append(CDF_LABEL)
        key_list = []

        for cube in self.cube_list:
            scenario = self.vocab.get_collection_term_label(
                InputType.SCENARIO, cube.attributes["scenario"]
            )
            # the CDF plot will be of the first variable
            var = self.input_data.get_value_label(InputType.VARIABLE)[0]
            self.header.append("{var}({scenario})".format(scenario=scenario, var=var))
            self._read_percentile_cube(cube, key_list)

        # now write the data
        output_data_file_path = self._get_full_file_name()
        self._write_data_dict(output_data_file_path, key_list)

        return [output_data_file_path]

    def _read_percentile_cube(self, cube, key_list):
        """
        Slice the cube over 'percentile' and update data_dict

        """
        for _slice in cube.slices_over("percentile"):
            value = value_to_string(_slice.data)
            # ensure the percentile is reported as no more the 2 dp
            percentile = str(round(_slice.coord("percentile").points[0], 2))
            try:
                self.data_dict[percentile].append(value)
            except KeyError:
                key_list.append(percentile)
                self.data_dict[percentile] = [value]
