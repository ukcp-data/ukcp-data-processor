import collections
import logging

import iris
from ukcp_dp.constants import AreaType, InputType, COLLECTION_PROB
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter, value_to_string


LOG = logging.getLogger(__name__)


class SubsetCsvWriter(BaseCsvWriter):
    """
    The subset CSV writer class.

    This class extends BaseCsvWriter with a _write_csv(self).
    """

    def _write_csv(self):
        """
        Write out the data, in CSV format, associated with three maps.
        """
        if self.input_data.get_area_type() == AreaType.BBOX:
            return self._write_x_y_csv()

        if self.input_data.get_value(InputType.COLLECTION) == COLLECTION_PROB:
            return self._write_csv_percentiles()

        return self._write_region_or_point_csv()

    def _write_x_y_csv(self):
        LOG.debug("_write_x_y_csv")
        cube = self.cube_list[0]

        # add axis titles to the header
        self.header.append("x-axis,Eastings (BNG)\n")
        self.header.append("y-axis,Northings (BNG)\n")

        # add the x values to the header
        x_values = ["--"]
        write_header = True
        output_file_list = []

        # loop over ensembles
        for ensemble_slice in cube.slices_over("ensemble_member"):
            ensemble_name = ensemble_slice.coord("ensemble_member_id").points[0]

            output_data_file_path = self._get_full_file_name(
                "_{}".format(ensemble_name)
            )
            self._write_headers(output_data_file_path)

            # loop over times
            for time_slice in ensemble_slice.slices_over("time"):
                time_str = time_slice.coord("time").cell(0).point.strftime("%Y-%m-%d")
                key_list = []

                # get the numpy representation of the sub-cube
                data = time_slice.data
                # get the coordinates for the sub-cube
                y_coords = time_slice.coord("projection_y_coordinate").points
                x_coords = time_slice.coord("projection_x_coordinate").points

                # rows of data
                for y in range(0, y_coords.shape[0]):
                    y_coord = str(y_coords[y])
                    # columns of data
                    for x in range(0, x_coords.shape[0]):
                        if write_header is True:
                            x_values.append(str(x_coords[x]))

                        value = value_to_string(data[y, x])
                        try:
                            self.data_dict[y_coord].append(value)
                        except KeyError:
                            key_list = [y_coord] + key_list
                            self.data_dict[y_coord] = [value]
                    write_header = False

                self._write_data_block(
                    output_data_file_path, key_list, time_str, x_values
                )
            output_file_list.append(output_data_file_path)

        return output_file_list

    def _write_data_block(self, output_data_file_path, key_list, time_str, x_values):
        """
        Write out the column headers and data_dict.
        """
        with open(output_data_file_path, "a") as output_data_file:
            output_data_file.write(time_str + "\n")
            line_out = ",".join(x_values) + "\n"
            output_data_file.write(line_out)
            for key in key_list:
                line_out = "{key},{values}\n".format(
                    key=key, values=",".join(self.data_dict[key])
                )
                output_data_file.write(line_out)

        # reset the data dict
        self.data_dict = collections.OrderedDict()

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
                or (percentile > 0.4 and percentile < 0.6)
                or (percentile > 1.4 and percentile < 1.6)
                or (percentile > 2.4 and percentile < 2.6)
                or (percentile > 97.4 and percentile < 97.6)
                or (percentile > 98.4 and percentile < 98.6)
                or (percentile > 99.4 and percentile < 99.6)
            ):

                percentile = format(percentile, ".1f")

            elif percentile < 1 or (percentile > 99 and percentile < 100):
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
        Slice the cube over 'ensemble_member' and 'time' and update data_dict/
        The data should be for a single region or grid square.
        """
        LOG.debug("_write_region_or_point_csv")
        cube = self.cube_list[0]

        # update the header
        self.header.append("Date")

        key_list = []
        for ensemble_slice in cube.slices_over("ensemble_member"):
            ensemble_name = str(ensemble_slice.coord("ensemble_member_id").points[0])

            # update the header
            var = self.input_data.get_value_label(InputType.VARIABLE)[0]
            self.header.append(
                "{var}({ensemble})".format(ensemble=ensemble_name, var=var)
            )

            self._write_time_cube(ensemble_slice, key_list)

        output_data_file_path = self._get_full_file_name()
        self._write_data_dict(output_data_file_path, key_list)

        return [output_data_file_path]

    def _write_time_cube(self, cube, key_list):
        """
        Slice the cube over 'time' and update data_dict
        """
        LOG.debug("_write_time_cube")
        if self.input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) in ["1hr", "3hr"]:
            LOG.debug("subdaily")
            date_format = "%Y-%m-%dT%H:%M"
        else:
            date_format = "%Y-%m-%d"
        data = cube.data[:]
        coords = cube.coord("time")[:]
        for time_ in range(0, data.shape[0]):
            value = value_to_string(data[time_])
            time_str = coords[time_].cell(0).point.strftime(date_format)
            try:
                self.data_dict[time_str].append(value)
            except KeyError:
                key_list.append(time_str)
                self.data_dict[time_str] = [value]
