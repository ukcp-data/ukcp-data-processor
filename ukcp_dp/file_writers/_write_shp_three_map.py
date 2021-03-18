"""
This module contains the ThreeMapShpWriter class, which implements the _write_shp method
from the BaseShpWriter base class.

"""
import logging

import iris
from ukcp_dp.constants import AreaType, InputType
from ukcp_dp.file_writers._base_shp_writer import BaseShpWriter, _get_resolution_m


LOG = logging.getLogger(__name__)


# pylint: disable=R0903
class ThreeMapShpWriter(BaseShpWriter):
    """
    The three map shapefile writer class.

    This class extends BaseShpWriter with a _write_shp(self).

    """

    def _write_shp(self):
        """
        Write out the data, in shapefile format, associated with three maps.

        @return a list of file paths/names

        """
        if self.input_data.get_area_type() == AreaType.BBOX:
            return self._write_bbox_shp()

        return self._write_region_shp()

    def _write_bbox_shp(self):
        """
        Write a shapefile for gridded data defined by a bbox.

        """
        cube = self.cube_list[0]
        output_file_list = []
        resolution = _get_resolution_m(cube)
        half_grid_size = resolution / 2
        area = resolution * resolution
        var_label = self.input_data.get_value_label(InputType.VARIABLE)[0]

        # extract 10th, 50th and 90th percentiles as sub-cubes
        percentiles = [10, 50, 90]
        for percentile in percentiles:
            percentile_cube = cube.extract(iris.Constraint(percentile=percentile))
            output_data_file = self._get_file_name(f"_{percentile}")

            self._write_bbox_data(
                area,
                percentile_cube,
                half_grid_size,
                output_data_file,
                output_file_list,
                var_label,
            )

        return output_file_list

    def _write_region_shp(self):
        """
        Write a shapefile for geographic region.

        """
        cube = self.cube_list[0]
        output_file_list = []
        region_shape_file = self._get_region_shape_file()
        var_label = self.input_data.get_value_label(InputType.VARIABLE)[0]

        # extract 10th, 50th and 90th percentiles
        percentiles = [10, 50, 90]
        for percentile in percentiles:

            percentile_cube = cube.extract(iris.Constraint(percentile=percentile))
            output_data_file = self._get_file_name(f"_{percentile}")

            self._write_region_data(
                percentile_cube,
                output_data_file,
                output_file_list,
                region_shape_file,
                var_label,
            )

        region_shape_file.close()

        return output_file_list
