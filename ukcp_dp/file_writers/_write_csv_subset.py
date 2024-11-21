"""
This module contains the SubsetCsvWriter class, which implements the _write_csv method
from the BaseCsvWriter base class.

"""
from datetime import datetime
import logging

from ukcp_dp.constants import AreaType, InputType, COLLECTION_OBS, COLLECTION_PROB
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter


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

        One file will be written per ensemble or a single file for observations.

        """
        LOG.debug("_write_x_y_csv")
        cube = self.cube_list[0]

        # add axis titles to the header
        self.header.append("x-axis,Eastings (BNG)\n")
        self.header.append("y-axis,Northings (BNG)\n")

        # add the x values to the header
        column_headers = ["--"]
        x_coords = cube.coord("projection_x_coordinate").points
        for x_coord in range(0, x_coords.shape[0]):
            column_headers.append(str(x_coords[x_coord]))

        if self.input_data.get_value(InputType.COLLECTION) == COLLECTION_OBS:
            output_file_list = self._write_had_obs_data(cube, column_headers)
        else:
            output_file_list = self._write_model_data(cube, column_headers)

        return output_file_list

    def _write_model_data(self, cube, column_headers):
        """
        Extract the model data.

        """
        output_file_list = []

        # loop over ensembles
        for ensemble_slice in cube.slices_over("ensemble_member"):
            ensemble_name = ensemble_slice.coord("ensemble_member").points[0]

            LOG.debug("processing ensemble %s", ensemble_name)

            if ensemble_name < 10:
                ensemble_no = f"0{ensemble_name}"
            else:
                ensemble_no = str(ensemble_name)

            output_data_file_path = self._get_full_file_name(f"_{ensemble_no}")
            self._write_headers(output_data_file_path)

            with open(output_data_file_path, "a") as output_data_file:
                self._write_data_block(ensemble_slice, output_data_file, column_headers)

            output_file_list.append(output_data_file_path)

        return output_file_list

    def _write_had_obs_data(self, cube, column_headers):
        """
        Extract the observation data.

        """
        output_file_list = []

        output_data_file_path = self._get_full_file_name()
        self._write_headers(output_data_file_path)

        with open(output_data_file_path, "a") as output_data_file:
            self._write_data_block(cube, output_data_file, column_headers)

        output_file_list.append(output_data_file_path)

        return output_file_list

    def _write_data_block(self, cube, output_data_file, column_headers):
        """
        Write out the column headers and data.

        """
        y_coords = cube.coord("projection_y_coordinate")[:]

        time_index = None
        for i, coord in enumerate(cube.coords(dim_coords=True)):
            if coord.name() == "time":
                time_index = i
            elif coord.name() == "projection_y_coordinate":
                y_index = i

        if time_index is None:
            self._write_data_block_single_time(
                column_headers, cube, output_data_file, y_coords, y_index
            )
        else:
            self._write_data_block_time_series(
                column_headers, cube, output_data_file, time_index, y_coords, y_index
            )

        LOG.debug("data written to file")

    def _write_data_block_single_time(
        self, column_headers, cube, output_data_file, y_coords, y_index
    ):
        """
        Write out the column headers and data where there is only one time value.

        """
        data = self._get_data(cube)
        output_data_file.write(f"{','.join(column_headers)}\n")

        # rows of data
        for y_coord in range(data.shape[y_index] - 1, -1, -1):
            if y_index == 0:
                line = (
                    f"{y_coords[y_coord].cell(0).point},"
                    f"{','.join(['%s' % num for num in data[y_coord, :]])}"
                    "\n"
                )
            else:
                line = (
                    f"{y_coords[y_coord].cell(0).point},"
                    f"{','.join(['%s' % num for num in data[: ,y_coord]])}"
                    "\n"
                )

            output_data_file.write(line)

    def _write_data_block_time_series(
        self, column_headers, cube, output_data_file, time_index, y_coords, y_index
    ):
        """
        Write out the column headers and data where there are multiple time values.


        """
        data = self._get_data(cube)
        time_coords = cube.coord("time")[:]

        for time_ in range(0, data.shape[time_index]):
            output_data_file.write(
                f"{time_coords[time_].cell(0).point.strftime('%Y-%m-%d')}\n"
            )

            output_data_file.write(f"{','.join(column_headers)}\n")

            # rows of data
            for y_coord in range(data.shape[y_index] - 1, -1, -1):
                if time_index == 0:
                    if y_index == 1:
                        line = (
                            f"{y_coords[y_coord].cell(0).point},"
                            f"{','.join(['%s' % num for num in data[time_, y_coord]])}"
                            "\n"
                        )
                    else:
                        line = (
                            f"{y_coords[y_coord].cell(0).point},"
                            f"{','.join(['%s' % num for num in data[time_, : ,y_coord]])}"
                            "\n"
                        )

                elif time_index == 2:
                    if y_index == 0:
                        line = (
                            f"{y_coords[y_coord].cell(0).point},"
                            f"{','.join(['%s' % num for num in data[y_coord, : ,time_]])}"
                            "\n"
                        )
                    else:
                        line = (
                            f"{y_coords[y_coord].cell(0).point},"
                            f"{','.join(['%s' % num for num in data[: ,y_coord, time_]])}"
                            "\n"
                        )

                output_data_file.write(line)

    def _write_csv_percentiles(self):
        """
        Write out the data, in CSV format for land_prob and marine-sim data.

        """
        output_file_list = []

        for cube in self.cube_list:
            output_file_list.append(self._get_percentiles(cube))

        return output_file_list

    def _get_percentiles(self, cube):
        """
        Write out the data, in CSV format for land_prob and marine-sim data.

        """
        LOG.debug("_get_percentiles")
        for _slice in cube.slices_over("percentile"):
            percentile = _slice.coord("percentile").points[0]
            # the plume plot will be of the first variable
            var = self.input_data.get_value_label(InputType.VARIABLE)[0]

            percentile = _fromat_percentile(percentile)

            # update the header
            self.header.append(
                "{var}({percentile} Percentile)".format(percentile=percentile, var=var)
            )

        output_data_file_path = self._get_full_file_name()
        self._write_headers(output_data_file_path)

        self._write_data(cube, output_data_file_path)

        return output_data_file_path

    def _write_region_or_point_csv(self):
        """
        Write out time series data to a file.

        The data should be for a single region or grid square. There may be one or
        more ensembles. If the collection is HadGrid UK then there can be multiple
        regions but no ensembles

        """
        LOG.debug("_write_region_or_point_csv")

        # update the header
        self.header.append("Date")

        var = self.input_data.get_value_label(InputType.VARIABLE)[0]

        # update the header
        if self.input_data.get_value(InputType.COLLECTION) == COLLECTION_OBS:
            if self.input_data.get_area() == "all":
                if self.input_data.get_area_type() == AreaType.ADMIN_REGION:
                    region_coord_name = "Administrative Region"
                elif self.input_data.get_area_type() == AreaType.COUNTRY:
                    region_coord_name = "Country"
                elif self.input_data.get_area_type() == AreaType.RIVER_BASIN:
                    region_coord_name = "River Basin"
                for region_coord in self.cube_list[0].coord(region_coord_name)[:]:
                    self.header.append(f"{var}({str(region_coord.points[0])})")
            else:
                self.header.append(f"{var}")
        else:
            # There should only be one cube so we only make reference to
            # self.cube_list[0]
            for ensemble_coord in self.cube_list[0].coord("ensemble_member_id")[:]:
                self.header.append(f"{var}({str(ensemble_coord.points[0])})")

        output_data_file_path = self._get_full_file_name()
        self._write_headers(output_data_file_path)

        self._write_data(self.cube_list[0], output_data_file_path)

        return [output_data_file_path]

    def _write_data(self, cube, output_data_file_path):
        """
        Loop over the time and write the values to a file.

        """
        LOG.debug("_write_data")
        if self.input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) in ["1hr", "3hr"]:
            date_format = "%Y-%m-%dT%H:%M"
        else:
            date_format = "%Y-%m-%d"

        dim_coords = []
        for coord in cube.coords(dim_coords=True):
            dim_coords.append(coord.name())

        if "time" not in dim_coords:
            self._region_or_point_csv_for_single_time(
                cube, date_format, output_data_file_path
            )
        else:
            self._region_or_point_csv_for_time_series(
                cube, date_format, output_data_file_path
            )

        LOG.debug("data written to file")

    def _region_or_point_csv_for_single_time(
        self, cube, date_format, output_data_file_path
    ):
        """
        Get the region or point data where there is only one time value.

        """
        time_coord = cube.coord("time")

        try:
            data = ",".join("%s" % num for num in self._get_data(cube))
        except IndexError:
            data = cube.data

        with open(output_data_file_path, "a") as output_data_file:
            output_data_file.write(
                f"{time_coord.cell(0).point.strftime(date_format)},{data}\n"
            )

    def _region_or_point_csv_for_time_series(
        self, cube, date_format, output_data_file_path
    ):
        """
        Get the region or point data where there are multiple time values.

        """
        data = self._get_data(cube)
        time_coords = cube.coord("time")[:]

        secondary_index = None
        for i, coord in enumerate(cube.coords(dim_coords=True)):
            if coord.name() == "time":
                time_index = i
            elif coord.name() in ["region", "ensemble_member_id", "percentile"]:
                secondary_index = i

        with open(output_data_file_path, "a") as output_data_file:

            for time_ in range(0, data.shape[time_index]):
                time_formated = time_coords[time_].cell(0).point.strftime(date_format)

                if time_index == 0:
                    if secondary_index is None:
                        data_formated = data[time_]
                    if secondary_index == 1:
                        data_formated = ",".join("%s" % num for num in data[time_])
                else:
                    data_formated = ",".join("%s" % num for num in data[:, time_])

                output_data_file.write(f"{time_formated},{data_formated}\n")

    def _get_data(self, cube):
        """
        Extract the data from the cube.

        """
        start_time = datetime.now()
        data = cube.data[:]
        end_time = datetime.now()
        LOG.debug("data extracted from cube in %s", end_time - start_time)
        return data


def _fromat_percentile(percentile):
    """
    Format the percentile depending on its value.

    """
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
    return percentile
