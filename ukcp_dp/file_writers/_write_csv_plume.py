"""
This module contains the PlumeCsvWriter class, which implements the _write_csv method
from the BaseCsvWriter base class.

"""

import logging

import iris
from ukcp_dp.constants import COLLECTION_MARINE, COLLECTION_OBS, COLLECTION_PROB
from ukcp_dp.constants import InputType, EXTREME_SEA_LEVEL
from ukcp_dp.file_writers._base_csv_writer import (
    BaseCsvWriter,
    value_to_string,
)
from ukcp_dp.file_writers._utils import ensemble_to_string


LOG = logging.getLogger(__name__)


# pylint: disable=R0903
class PlumeCsvWriter(BaseCsvWriter):
    """
    The plume CSV writer class.

    This class extends BaseCsvWriter with a _write_csv(self).

    """

    def _write_csv(self):
        """
        Write out the data, in CSV format, associated with a plume plot.

        """
        if self.input_data.get_value(
            InputType.COLLECTION
        ) == COLLECTION_MARINE and self.input_data.get_value(
            InputType.METHOD
        ).startswith(
            EXTREME_SEA_LEVEL
        ):
            self.header.append("Return period(years)")
        else:
            self.header.append("Date")
        key_list = []

        if (
            self.input_data.get_value(InputType.COLLECTION) == COLLECTION_PROB
            or self.input_data.get_value(InputType.COLLECTION) == COLLECTION_MARINE
        ):
            self._write_csv_plume_percentiles(key_list)
        else:
            self._write_csv_plume_data(key_list)

        # now write the data
        output_data_file_path = self._get_full_file_name()
        self._write_data_dict(output_data_file_path, key_list)

        return [output_data_file_path]

    def _write_csv_plume_percentiles(self, key_list):
        """
        Write out the data, in CSV format, associated with a plume plot for
        land_prob and marine-sim data.

        """
        for cube in self.cube_list:
            if self.input_data.get_value(InputType.COLLECTION) == COLLECTION_PROB:
                for percentile in [5, 10, 25, 50, 75, 90, 95]:
                    percentile_cube = cube.extract(
                        iris.Constraint(percentile=percentile)
                    )
                    self._get_percentiles(percentile_cube, key_list)
            else:
                self._get_percentiles(cube, key_list)

    def _write_csv_plume_data(self, key_list):
        """
        Write out the data, in CSV format, associated with a plume plot.

        """
        for cube in self.cube_list:
            # there should only be one cube

            if self.input_data.get_value(InputType.COLLECTION) == COLLECTION_OBS:
                self._write_had_obs_data(cube, key_list)
            else:
                self._write_model_data(cube, key_list)

        # now add the data from the overlay
        if self.overlay_cube is not None:
            percentile_cube = self.overlay_cube.extract(iris.Constraint(percentile=10))
            self._get_percentiles(percentile_cube, key_list)
            percentile_cube = self.overlay_cube.extract(iris.Constraint(percentile=90))
            self._get_percentiles(percentile_cube, key_list)

    def _write_model_data(self, cube, key_list):
        """
        Extract the model data.

        """
        for ensemble_slice in cube.slices_over("ensemble_member"):
            ensemble_no = ensemble_to_string(
                ensemble_slice.coord("ensemble_member").points[0]
            )

            # the plume plot will be of the first variable
            var = self.input_data.get_value_label(InputType.VARIABLE)[0]
            self.header.append(f"{var}({ensemble_no})")
            self._read_x_cube(ensemble_slice, key_list)

    def _write_had_obs_data(self, cube, key_list):
        """
        Extract the observation data.

        """
        # the plume plot will be of the first variable
        var = self.input_data.get_value_label(InputType.VARIABLE)[0]
        self.header.append(var)
        self._read_x_cube(cube, key_list)

    def _get_percentiles(self, cube, key_list):
        """
        Update the data dict and header with data from the cube.
        The cube is sliced over percentile then time.

        """
        for _slice in cube.slices_over("percentile"):
            percentile = str(_slice.coord("percentile").points[0])
            # the plume plot will be of the first variable
            var = self.input_data.get_value_label(InputType.VARIABLE)[0]
            self.header.append(f"{var}({int(float(percentile))}th Percentile)")
            self._read_x_cube(_slice, key_list)

    def _read_x_cube(self, cube, key_list):
        if self.input_data.get_value(
            InputType.COLLECTION
        ) == COLLECTION_MARINE and self.input_data.get_value(
            InputType.METHOD
        ).startswith(
            EXTREME_SEA_LEVEL
        ):
            self._read_returnlevel_cube(cube, key_list)
        else:
            self._read_time_cube(cube, key_list)

    def _read_returnlevel_cube(self, cube, key_list):
        """
        Slice the cube over 'return_period' and update data_dict

        """
        data = cube.data[:]
        coords = cube.coord("return_period")[:]
        for period in range(0, data.shape[0]):
            value = value_to_string(
                data[period], self.input_data.get_value(InputType.VARIABLE)[0]
            )
            time_str = int(round(coords[period].cell(0).point))
            try:
                self.data_dict[time_str].append(value)
            except KeyError:
                key_list.append(time_str)
                self.data_dict[time_str] = [value]

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
