"""
This module contains the PostageStampMapCsvWriter class, which implements the _write_csv
method from the BaseCsvWriter base class.

"""

import logging

from ukcp_dp.constants import AreaType, InputType
from ukcp_dp.file_writers._base_csv_map_writer import (
    BaseCsvMapWriter,
    _write_xy_data,
)
from ukcp_dp.file_writers._utils import ensemble_to_string


LOG = logging.getLogger(__name__)


# pylint: disable=R0903
class PostageStampMapCsvWriter(BaseCsvMapWriter):
    """
    The postage stamp map CSV writer class.

    This class extends BaseCsvWriter with a _write_csv(self).

    """

    def _write_csv(self):
        """
        Write out the data, in CSV format, associated with multiple maps.

        """
        if self.input_data.get_area_type() == AreaType.BBOX:
            return self._write_x_y_csv()

        return self._write_region_csv()

    def _write_x_y_csv(self):
        """
        Write out data that has multiple x and y coordinates.

        One file will be written per ensemble.

        """
        LOG.debug("_write_x_y_csv")
        cube = self.cube_list[0]

        output_file_list = []

        self._generate_xy_header(cube)

        # loop over ensembles
        for ensemble_slice in cube.slices_over("ensemble_member"):
            ensemble_no = ensemble_to_string(
                ensemble_slice.coord("ensemble_member").points[0]
            )

            LOG.debug("processing ensemble %s", ensemble_no)

            output_data_file_path = self._get_full_file_name(f"_{ensemble_no}")
            self._write_headers(output_data_file_path)

            _write_xy_data(ensemble_slice, output_data_file_path)

            output_file_list.append(output_data_file_path)

        return output_file_list

    def _write_region_csv(self):
        """
        Write out region data to a file.

        The data can have multiple regions and ensembles.

        """
        LOG.debug("_write_region_csv")

        # There should only be one cube so we only make reference to self.cube_list[0]
        cube = self.cube_list[0]

        # update the header
        self.header.append(str(cube.coords(var_name="geo_region")[0].long_name))

        var = self.input_data.get_value_label(InputType.VARIABLE)[0]

        for ensemble_coord in cube.coord("ensemble_member")[:]:
            # update the header
            self.header.append(f"{var}({ensemble_to_string(ensemble_coord.points[0])})")

        output_data_file_path = self._get_full_file_name()
        self._write_headers(output_data_file_path)

        self._write_region_data(cube, output_data_file_path)

        return [output_data_file_path]
