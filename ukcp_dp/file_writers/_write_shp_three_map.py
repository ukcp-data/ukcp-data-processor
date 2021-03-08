import logging

import iris
import shapefile as shp
from ukcp_dp.constants import AreaType, InputType
from ukcp_dp.file_writers._base_shp_writer import BaseShpWriter
from ukcp_dp.spatial_files import (
    OVERLAY_ADMIN_SMALL,
    OVERLAY_COUNTRY_SMALL,
    OVERLAY_RIVER_SMALL,
)


LOG = logging.getLogger(__name__)

ET_ID = "ET_ID"
REGION = "Region"
AREA = "area"
CENTROID_X = "centroid_x"
CENTROID_Y = "centroid_y"


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
        else:
            return self._write_region_shp()

    def _write_bbox_shp(self):
        """
        Write a shapefile for gridded data defined by a bbox.
        """
        cube = self.cube_list[0]
        output_file_list = []

        resolution = self._get_resolution_m(cube)
        half_grid_size = resolution / 2

        # extract 10th, 50th and 90th percentiles as sub-cubes
        percentiles = [10, 50, 90]
        for percentile in percentiles:
            percentile_cube = cube.extract(iris.Constraint(percentile=percentile))

            # get the numpy representation of the sub-cube
            data = percentile_cube.data
            # get the coordinates for the sub-cube
            y_coords = percentile_cube.coord("projection_y_coordinate").points
            x_coords = percentile_cube.coord("projection_x_coordinate").points

            output_data_file_path = self._get_file_name("_{}".format(percentile))

            shape_writer = shp.Writer(output_data_file_path)
            shape_writer.field(
                self.input_data.get_value(InputType.VARIABLE)[0], "N", decimal=7
            )

            # define the shapefile fields
            shape_writer = shp.Writer(output_data_file_path)
            shape_writer.field("Id", "N", 6)
            shape_writer.field(
                self.input_data.get_value(InputType.VARIABLE)[0], "N", decimal=7
            )

            # rows of data
            for y in range(0, y_coords.shape[0]):
                # columns of data
                for x in range(0, x_coords.shape[0]):
                    self._write_polygon(
                        shape_writer,
                        x_coords[x],
                        y_coords[y],
                        data[y, x],
                        half_grid_size,
                    )

            shape_writer.close()
            output_file_list.append("{}.dbf".format(output_data_file_path))
            output_file_list.append("{}.shp".format(output_data_file_path))
            output_file_list.append("{}.shx".format(output_data_file_path))

            # add the prj file
            prj_file = "{}.prj".format(output_data_file_path)
            self._write_prj_file(prj_file)
            output_file_list.append(prj_file)

        return output_file_list

    def _write_polygon(self, shape_writer, x_coord, y_coord, value, half_grid_size):
        # Given the central x, y, and half_grid_size construct a polygon
        polygon = [
            [x_coord - half_grid_size, y_coord - half_grid_size],
            [x_coord - half_grid_size, y_coord + half_grid_size],
            [x_coord + half_grid_size, y_coord + half_grid_size],
            [x_coord + half_grid_size, y_coord - half_grid_size],
            [x_coord - half_grid_size, y_coord - half_grid_size],
        ]
        shape_writer.poly([polygon])
        if value == "--":
            value = None
        shape_writer.record(value)

    def _write_region_shp(self):
        """
        Write a shapefile for geographic region.
        """
        cube = self.cube_list[0]
        output_file_list = []

        spatial_representation = self.input_data.get_value(
            InputType.SPATIAL_REPRESENTATION
        )

        if spatial_representation == AreaType.ADMIN_REGION:
            region_shape_file = shp.Reader(OVERLAY_ADMIN_SMALL)

        elif spatial_representation == AreaType.COUNTRY:
            region_shape_file = shp.Reader(OVERLAY_COUNTRY_SMALL)

        elif spatial_representation == AreaType.RIVER_BASIN:
            region_shape_file = shp.Reader(OVERLAY_RIVER_SMALL)

        else:
            raise Exception(
                "spatial_representation must be one of %s, %s, %s",
                AreaType.ADMIN_REGION,
                AreaType.COUNTRY,
                AreaType.RIVER_BASIN,
            )

        var_label = self.input_data.get_value_label(InputType.VARIABLE)[0]

        # extract 10th, 50th and 90th percentiles
        percentiles = [10, 50, 90]
        for percentile in percentiles:

            percentile_cube = cube.extract(iris.Constraint(percentile=percentile))

            output_data_file_path = self._get_file_name("_{}".format(percentile))

            # define the shapefile fields
            shape_writer = shp.Writer(output_data_file_path)
            shape_writer.field(ET_ID, "N", 8)
            shape_writer.field(REGION, "C", 50)
            shape_writer.field(AREA, "F", 19, 11)
            shape_writer.field(CENTROID_X, "F", 19, 11)
            shape_writer.field(CENTROID_Y, "F", 19, 11)
            shape_writer.field("var_name", "C", 100)
            shape_writer.field("var_value", "N", decimal=7)

            # rows of data
            for region_slice in percentile_cube.slices_over("region"):
                region = str(region_slice.coords(var_name="geo_region")[0].points[0])

                region_record = self._get_region_record_from_shapefile(
                    region_shape_file, region
                )

                if region_record is None:
                    continue

                region_geometry = region_shape_file.shapeRecord(region_record.oid).shape

                self._write_region(
                    shape_writer,
                    region_geometry,
                    region_record,
                    var_label,
                    region_slice.data,
                )

            shape_writer.close()
            output_file_list.append("{}.dbf".format(output_data_file_path))
            output_file_list.append("{}.shp".format(output_data_file_path))
            output_file_list.append("{}.shx".format(output_data_file_path))

            # add the prj file
            prj_file = "{}.prj".format(output_data_file_path)
            self._write_prj_file(prj_file)
            output_file_list.append(prj_file)

        region_shape_file.close()

        return output_file_list

    def _get_region_record_from_shapefile(self, region_shape_file, region):
        for record in region_shape_file.records():
            if region in record:
                return record

    def _write_region(
        self, shape_writer, region_geometry, region_record, var_label, value
    ):
        shape_writer.shape(region_geometry)
        if value == "--":
            value = None
        shape_writer.record(
            ET_ID=region_record[ET_ID],
            Region=region_record[REGION],
            area=region_record[AREA],
            centroid_x=region_record[CENTROID_X],
            centroid_y=region_record[CENTROID_Y],
            var_name=var_label,
            var_value=value,
        )
