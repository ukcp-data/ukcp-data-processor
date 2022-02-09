"""
This module contains the BaseCsvWriter, a base class for map CSV writers.

"""
from datetime import datetime
import logging

import numpy as np
from ukcp_dp.constants import InputType, COLLECTION_OBS
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter


LOG = logging.getLogger(__name__)


# pylint: disable=R0903
class BaseCsvMapWriter(BaseCsvWriter):
    """
    The base class for map CSV writers.

    This class provides common functionality for the map CSV writers.

    """

    def _write_csv(self):
        """
        This method should be overridden to produce the column headers in
        self.header and put the data in self.data_dict.

        It should write the data to one or more files and pass back a list of
        file names. The _write_data_dict method has been provided to write the
        data to a file

        self._write_data_dict(output_data_file_path)

        @return a list of file names

        """
        raise NotImplementedError

    def _generate_xy_header(self, cube):

        # add axis titles to the header
        self.header.append("x-axis,Eastings (BNG)\n")
        self.header.append("y-axis,Northings (BNG)\n")

        # add the x values to the header
        self.header.append("--")
        x_coords = cube.coord("projection_x_coordinate").points
        for x_coord in range(0, x_coords.shape[0]):
            self.header.append(str(x_coords[x_coord]))

    def _write_region_data(self, cube, output_data_file_path):
        """
        Loop over the regions and write the values to a file.

        """
        LOG.debug("_write_region_data")

        start_time = datetime.now()
        data = cube.data[:]
        end_time = datetime.now()
        LOG.debug("data extracted from cube in %s", end_time - start_time)

        geo_region_coords = cube.coord(var_name="geo_region")[:]

        data = np.transpose(data)

        with open(output_data_file_path, "a") as output_data_file:

            for geo_region in range(data.shape[0] - 1, -1, -1):
                if self.input_data.get_value(InputType.COLLECTION) == COLLECTION_OBS:
                    output_data_file.write(
                        f"{geo_region_coords[geo_region].cell(0).point},"
                        f"{data[:][geo_region]}"
                        "\n"
                    )
                else:
                    output_data_file.write(
                        f"{geo_region_coords[geo_region].cell(0).point},"
                        f"{','.join(['%s' % num for num in data[:][geo_region]])}"
                        "\n"
                    )

        LOG.debug("data written to file")


def _write_xy_data(cube, output_data_file_path):
    """
    Write out x y data from the cube.

    @param cube (iris cube): the cube containing the x y data
    @param output_data_file_path (str): the file path and name to write the data to

    """
    start_time = datetime.now()
    # get the numpy representation of the sub-cube
    data = cube.data[:]
    end_time = datetime.now()
    LOG.debug("data extracted from cube in %s", end_time - start_time)

    y_coords = cube.coord("projection_y_coordinate")[:]

    with open(output_data_file_path, "a") as output_data_file:
        # rows of data
        for y_coord in range(data.shape[0] - 1, -1, -1):
            output_data_file.write(
                f"{y_coords[y_coord].cell(0).point},"
                f"{','.join(['%s' % num for num in data[:][y_coord]])}"
                "\n"
            )
