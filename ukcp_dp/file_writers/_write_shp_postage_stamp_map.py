"""
This module contains the ThreeMapShpWriter class, which implements the _write_shp method
from the BaseShpWriter base class.

"""
import logging

import shapefile as shp
from ukcp_dp.constants import AreaType, InputType
from ukcp_dp.file_writers._base_shp_writer import BaseShpWriter, _get_resolution_m


LOG = logging.getLogger(__name__)


# pylint: disable=R0903
class PostageStampMapShpWriter(BaseShpWriter):
    """
    The postage stamp map shapefile writer class.

    This class extends BaseShpWriter with a _write_shp(self).

    """

    def _write_shp(self):
        """
        Write out the data, in shapefile format, associated with postage stamp
        maps.

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
        var_label = self.input_data.get_value_label(InputType.VARIABLE)[0]

        for ensemble_slice in cube.slices_over("ensemble_member"):
            ensemble_name = ensemble_slice.coord("ensemble_member_id").points[0]
            ensemble_name = ensemble_name.replace(".", "_")
            output_data_file = self._get_file_name(f"_{ensemble_name}")

            self._write_bbox_data(
                ensemble_slice,
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
        region_shape_files = self._get_region_shape_files()
        var_label = self.input_data.get_value_label(InputType.VARIABLE)[0]

        for file in region_shape_files:
            LOG.debug("Loading shapefile: %s", file)

            with shp.Reader(file) as region_shape_file:
                for ensemble_slice in cube.slices_over("ensemble_member"):

                    ensemble_name = str(
                        ensemble_slice.coord("ensemble_member_id").points[0]
                    )

                    ensemble_name = ensemble_name.replace(".", "_")
                    output_data_file = self._get_file_name(f"_{ensemble_name}")
                    file_bit = file.split("-")[-2]
                    if len(region_shape_files) > 1:
                        suffix = f"_{file_bit}_{ensemble_name}"
                    else:
                        suffix = f"_{ensemble_name}"

                    output_data_file = self._get_file_name(suffix)

                    self._write_region_data(
                        ensemble_slice,
                        output_data_file,
                        output_file_list,
                        region_shape_file,
                        var_label,
                    )

        return output_file_list
