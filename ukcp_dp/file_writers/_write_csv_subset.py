"""
This module contains the SubsetCsvWriter class, which implements the _write_csv method
from the BaseCsvWriter base class.

"""
from datetime import datetime
import logging

import numpy as np
from ukcp_dp.constants import AreaType, InputType, COLLECTION_PROB
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter, value_to_string


LOG = logging.getLogger(__name__)


# pylint: disable=R0903
class SubsetCsvWriter(BaseCsvWriter):
    """
    The subset CSV writer class.

    This class extends BaseCsvWriter with a _write_csv(self).

    """

    def _write_csv(self):
        """
        Write out the data, in CSV format, associated with data subsets.

        """
        if self.input_data.get_area_type() == AreaType.BBOX:
            return self._write_x_y_csv()

        if self.input_data.get_value(InputType.COLLECTION) == COLLECTION_PROB:
            return self._write_csv_percentiles()

        return self._write_region_or_point_csv()

    def _write_x_y_csv(self):
        """
        Write out data that has multiple time and x and y coordinates.

        One file will be written per ensemble.

        """
        LOG.debug("_write_x_y_csv")
        cube = self.cube_list[0]

        # add axis titles to the header
        self.header.append("x-axis,Eastings (BNG)\n")
        self.header.append("y-axis,Northings (BNG)\n")

        output_file_list = []

        # add the x values to the header
        column_headers = ["--"]
        x_coords = cube.coord("projection_x_coordinate").points
        for x_coord in range(0, x_coords.shape[0]):
            column_headers.append(str(x_coords[x_coord]))

        # loop over ensembles
        for ensemble_slice in cube.slices_over("ensemble_member"):
            ensemble_name = ensemble_slice.coord("ensemble_member_id").points[0]

            LOG.debug("processing ensemble %s", ensemble_name)

            output_data_file_path = self._get_full_file_name(f"_{ensemble_name}")
            self._write_headers(output_data_file_path)

            with open(output_data_file_path, "a") as output_data_file:
                self._write_data_block(ensemble_slice, output_data_file, column_headers)

            output_file_list.append(output_data_file_path)

        return output_file_list

    def _write_data_block(self, cube, output_data_file, column_headers):
        """
        Write out the column headers and data.

        """
        start_time = datetime.now()
        # get the numpy representation of the sub-cube
        data = cube.data[:]
        end_time = datetime.now()
        LOG.debug("data extracted from cube in %s", end_time - start_time)

        time_coords = cube.coord("time")[:]
        y_coords = cube.coord("projection_y_coordinate")[:]

        for time_ in range(0, data.shape[0]):
            output_data_file.write(
                f"{time_coords[time_].cell(0).point.strftime('%Y-%m-%d')}\n"
            )

            output_data_file.write(f"{','.join(column_headers)}\n")

            # rows of data
            for y_coord in range(data.shape[1] - 1, -1, -1):
                output_data_file.write(
                    f"{y_coords[y_coord].cell(0).point},"
                    f"{','.join(['%s' % num for num in data[:][time_][y_coord]])}"
                    "\n"
                )

        LOG.debug("data written to file")

    def _write_csv_percentiles(self):
        """
        Write out the data, in CSV format, associated with a plume plot for
        land_prob and marine-sim data.

        """
        key_list = []
        for cube in self.cube_list:
            self._get_percentiles(cube, key_list)

        output_data_file_path = self._get_full_file_name()
        self._write_data_dict(output_data_file_path, key_list)

        return [output_data_file_path]

    def _get_percentiles(self, cube, key_list):
        """
        Update the data dict and header with data from the cube.
        The cube is sliced over percentile then time.

        """
        for _slice in cube.slices_over("percentile"):
            percentile = _slice.coord("percentile").points[0]
            # the plume plot will be of the first variable
            var = self.input_data.get_value_label(InputType.VARIABLE)[0]

            if (
                percentile < 0.2
                or (0.4 < percentile < 0.6)
                or (1.4 < percentile < 1.6)
                or (2.4 < percentile < 2.6)
                or (97.4 < percentile < 97.6)
                or (98.4 < percentile < 98.6)
                or (99.4 < percentile < 99.6)
            ):

                percentile = format(percentile, ".1f")

            elif percentile < 1 or (99 < percentile < 100):
                percentile = format(percentile, ".2f")

            else:
                percentile = format(percentile, ".0f")

            if "." in percentile:
                pass
            elif percentile.endswith("1") and percentile != "11":
                percentile = "{}st".format(percentile)
            elif percentile.endswith("2") and percentile != "12":
                percentile = "{}nd".format(percentile)
            elif percentile.endswith("3") and percentile != "13":
                percentile = "{}rd".format(percentile)
            else:
                percentile = "{}th".format(percentile)

            self.header.append(
                "{var}({percentile} Percentile)".format(percentile=percentile, var=var)
            )
            self._read_time_cube(_slice, key_list)

    def _read_time_cube(self, cube, key_list):
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

    def _write_region_or_point_csv(self):
        """
        Write out time series data to a file.

        The data should be for a single region or grid square. There may be one or
        more ensembles.

        """
        LOG.debug("_write_region_or_point_csv")

        # update the header
        self.header.append("Date")

        var = self.input_data.get_value_label(InputType.VARIABLE)[0]

        # There should only be one cube so we only make reference to self.cube_list[0]
        for ensemble_coord in self.cube_list[0].coord("ensemble_member_id")[:]:
            # update the header
            self.header.append(f"{var}({str(ensemble_coord.points[0])})")

        output_data_file_path = self._get_full_file_name()
        self._write_headers(output_data_file_path)

        self._write_region_or_point_data(self.cube_list[0], output_data_file_path)

        return [output_data_file_path]

    def _write_region_or_point_data(self, cube, output_data_file_path):
        """
        Loop over the time and write the values to a file.

        """
        LOG.debug("_write_region_or_point_data")
        if self.input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) in ["1hr", "3hr"]:
            date_format = "%Y-%m-%dT%H:%M"
        else:
            date_format = "%Y-%m-%d"

        start_time = datetime.now()
        data = cube.data[:]
        end_time = datetime.now()
        LOG.debug("data extracted from cube in %s", end_time - start_time)

        time_coords = cube.coord("time")[:]
        data = np.transpose(data)

        with open(output_data_file_path, "a") as output_data_file:

            for time_ in range(0, data.shape[0]):
                output_data_file.write(
                    f"{time_coords[time_].cell(0).point.strftime(date_format)},"
                    f"{','.join(['%s' % num for num in data[:][time_]])}"
                    "\n"
                )

        LOG.debug("data written to file")
