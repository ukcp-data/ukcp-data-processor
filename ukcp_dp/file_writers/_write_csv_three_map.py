"""
This module contains the ThreeMapCsvWriter class, which implements the _write_csv method
from the BaseCsvWriter base class.

"""
import logging

import iris
from ukcp_dp.constants import AreaType, InputType
from ukcp_dp.file_writers._base_csv_writer import value_to_string
from ukcp_dp.file_writers._base_csv_map_writer import BaseCsvMapWriter, _write_xy_data


LOG = logging.getLogger(__name__)


# pylint: disable=R0903
class ThreeMapCsvWriter(BaseCsvMapWriter):
    """
    The three map CSV writer class.

    This class extends BaseCsvWriter with a _write_csv(self).

    """

    def _write_csv(self):
        """
        Write out the data, in CSV format, associated with three maps.

        """
        if self.input_data.get_area_type() == AreaType.BBOX:
            return self._write_x_y_csv()

        return self._write_region_csv()

    def _write_x_y_csv(self):
        """
        Write out data that has multiple x and y coordinates.

        One file will be written per percentile.

        """
        LOG.debug("_write_x_y_csv")
        cube = self.cube_list[0]

        output_file_list = []

        self._generate_xy_header(cube)

        # extract 10th, 50th and 90th percentiles as sub-cubes
        percentiles = [10, 50, 90]
        for percentile in percentiles:
            percentile_cube = cube.extract(iris.Constraint(percentile=percentile))

            output_data_file_path = self._get_full_file_name(f"_{percentile}")
            self._write_headers(output_data_file_path)

            _write_xy_data(percentile_cube, output_data_file_path)

            output_file_list.append(output_data_file_path)

        return output_file_list

    def _write_region_csv(self):
        """
        Write out region data to a file.

        The data can have multiple regions and percentiles. N.B. only the 10th, 50th
        and 90th percentiles are output, there may be additional percentiles in the
        cube.

        """
        LOG.debug("_write_region_csv")

        # There should only be one cube so we only make reference to self.cube_list[0]
        cube = self.cube_list[0]

        # update the header
        self.header.append(str(cube.coords(var_name="geo_region")[0].long_name))

        var = self.input_data.get_value_label(InputType.VARIABLE)[0]

        # extract 10th, 50th and 90th percentiles
        percentiles = [10, 50, 90]
        key_list = []
        for percentile in percentiles:
            # update the header
            self.header.append(f"{var}({percentile}th Percentile)")

        output_data_file_path = self._get_full_file_name()
        self._write_headers(output_data_file_path)

        for percentile in percentiles:

            percentile_cube = cube.extract(iris.Constraint(percentile=percentile))

            # rows of data
            for region_slice in percentile_cube.slices_over("region"):
                region = str(region_slice.coords(var_name="geo_region")[0].points[0])

                value = value_to_string(region_slice.data)
                try:
                    self.data_dict[region].append(value)
                except KeyError:
                    key_list = [region] + key_list
                    self.data_dict[region] = [value]

        output_data_file_path = self._get_full_file_name()
        self._write_data_dict(output_data_file_path, key_list)

        return [output_data_file_path]
