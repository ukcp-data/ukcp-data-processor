"""
This module contains the BaseShpWriter, a base class for shapefile writers.

"""
import logging
import os
from time import gmtime, strftime

from iris.exceptions import CoordinateNotFoundError
import numpy.ma as ma
import shapefile as shp
from ukcp_dp.constants import AreaType, InputType, COLLECTION_MARINE
from ukcp_dp.exception import UKCPDPInvalidParameterException
from ukcp_dp.spatial_files import (
    OVERLAY_ADMIN,
    OVERLAY_COUNTRY_AGGREGATED,
    OVERLAY_RIVER,
)


LOG = logging.getLogger(__name__)


AREA = "area"
CENTROID_X = "centroid_x"
CENTROID_Y = "centroid_y"
ET_ID = "ET_ID"
REGION = "Region"
VAR_NAME = "var_name"
VAR_VALUE = "var_value"


# pylint: disable=R0903
class BaseShpWriter:
    """
    The base class for shapefile writers.

    This class should be extended with a
    _write_shp(self) method to format the data.
    The following variables are available to overriding methods:
        self.input_data
        self.cube_list
        self.output_data_file_path
        self.plot_type
        self.timestamp

    """

    def __init__(self):
        self.input_data = None
        self.cube_list = None
        self.output_data_file_path = None
        self.timestamp = None
        self.plot_type = None

    def write_shp(self, input_data, cube_list, output_data_file_path, plot_type):
        """
        Write a shapefile file.

        @param input_data (InputData): an object containing user defined values
        @param cube_list (iris cube list): a list of cubes containing the
            selected data, one cube per scenario, per variable
        @param output_data_file_path (str): the full path to the file
        @param plot_type (PlotType): the type of the plot

        @return a list of file paths/names

        """
        LOG.info("write_shp, %s", plot_type)
        # an object containing user defined values
        self.input_data = input_data
        # an iris cube list
        self.cube_list = cube_list
        self.output_data_file_path = output_data_file_path
        self.timestamp = strftime("%Y-%m-%dT%H-%M-%S", gmtime())
        self.plot_type = plot_type

        return self._write_shp()

    def _write_shp(self):
        """
        This method should be overridden to write the data to one or more files
        and pass back a list of file names.

        @return a list of file paths/names

        """

    def _get_file_name(self, file_name_suffix=None):
        """
        Get a file name based on the plot type, the time and the file_name_suffix.

        @param file_name_suffix (str): the suffix to add to the file path, maybe None

        @return a str containing the full path to the file

        """
        if file_name_suffix is None:
            file_name_suffix = ""

        try:
            plot_type = self.plot_type.lower()
        except AttributeError:
            # not a plot so must be a subset
            plot_type = "subset"

        file_name = f"{plot_type}_{self.timestamp}{file_name_suffix}"
        return os.path.join(self.output_data_file_path, file_name)

    def _get_region_shape_file(self):
        """
        Get a region shapefile based on the spatial representation.

        @return a shp.Reader object for the selected region

        """
        spatial_representation = self.input_data.get_value(
            InputType.SPATIAL_REPRESENTATION
        )

        if spatial_representation == AreaType.ADMIN_REGION:
            region_shape_file = shp.Reader(OVERLAY_ADMIN)

        elif spatial_representation == AreaType.COUNTRY:
            region_shape_file = shp.Reader(OVERLAY_COUNTRY_AGGREGATED)

        elif spatial_representation == AreaType.RIVER_BASIN:
            region_shape_file = shp.Reader(OVERLAY_RIVER)

        else:
            raise UKCPDPInvalidParameterException(
                f"spatial_representation must be one of {AreaType.ADMIN_REGION}, "
                f"{AreaType.COUNTRY}, {AreaType.RIVER_BASIN}"
            )

        return region_shape_file

    def _write_prj_file(self, cube, prj_file):
        """
        Write the projection information to a file based on the collection type.

        @param prj_file (str): the full path to the projection file

        """
        if self.input_data.get_value(InputType.COLLECTION) == COLLECTION_MARINE:
            _write_marine_prj_file(prj_file)
        else:
            _write_land_prj_file(cube, prj_file)

    def _write_bbox_data(
        self, area, cube, half_grid_size, output_data_file, output_file_list, var_label
    ):
        """
        Write the data for a bbox to a shapefile.

        @param area (float): the area of a grid square
        @param cube (iris cube): a cube containing the selected data
        @param half_grid_size (float): half the width of the grid square
        @param output_data_file (str): the full path to the file
        @param output_file_list (list): the list to add the file paths of the new files
                to
        @param var_label (str): the label to use for the variable in the shapefile

        """
        # get the numpy representation of the sub-cube
        data = cube.data
        # get the coordinates for the sub-cube
        y_coords = cube.coord("projection_y_coordinate").points
        x_coords = cube.coord("projection_x_coordinate").points

        try:
            shape_writer = shp.Writer(output_data_file)
            _write_bbox_field_desc(shape_writer)

            # rows of data
            for y_coord in range(0, y_coords.shape[0]):
                # columns of data
                for x_coord in range(0, x_coords.shape[0]):

                    if not ma.is_masked(data[y_coord, x_coord]):
                        _write_polygon(
                            shape_writer,
                            x_coords[x_coord],
                            y_coords[y_coord],
                            half_grid_size,
                        )
                        _write_bbox_record(
                            shape_writer,
                            x_coords[x_coord],
                            y_coords[y_coord],
                            area,
                            var_label,
                            data[y_coord, x_coord],
                        )

        finally:
            shape_writer.close()

        output_file_list.append(f"{output_data_file}.dbf")
        output_file_list.append(f"{output_data_file}.shp")
        output_file_list.append(f"{output_data_file}.shx")

        # add the prj file
        prj_file = f"{output_data_file}.prj"
        self._write_prj_file(cube, prj_file)
        output_file_list.append(prj_file)

    def _write_region_data(
        self, cube, output_data_file, output_file_list, region_shape_file, var_label
    ):
        """
        Write the data for a region to a shapefile.

        @param cube (iris cube): a cube containing the selected data
        @param half_grid_size (float): half the width of the grid square
        @param output_data_file (str): the full path to the file
        @param output_file_list (list): the list to add the file paths of the new files
                to
        @param region_shape_file(shp.Reader):the region shapefile
        @param var_label (str): the label to use for the variable in the shapefile

        """
        try:
            # define the shapefile fields
            shape_writer = shp.Writer(output_data_file)
            _write_region_field_desc(shape_writer)

            # rows of data
            for region_slice in cube.slices_over("region"):

                region = str(region_slice.coords(var_name="geo_region")[0].points[0])
                # correct for error in net-cdf files
                if region == "Orkney and Shetlands":
                    region = "Orkney and Shetland"

                region_record = _get_region_record_from_shapefile(
                    region_shape_file, region
                )

                if region_record is None:
                    continue

                region_geometry = region_shape_file.shapeRecord(region_record.oid).shape

                if not ma.is_masked(region_slice.data):
                    _write_region_record(
                        shape_writer,
                        region_geometry,
                        region_record,
                        var_label,
                        region_slice.data,
                    )
        finally:
            shape_writer.close()

        output_file_list.append(f"{output_data_file}.dbf")
        output_file_list.append(f"{output_data_file}.shp")
        output_file_list.append(f"{output_data_file}.shx")

        # add the prj file
        prj_file = f"{output_data_file}.prj"
        self._write_prj_file(cube, prj_file)
        output_file_list.append(prj_file)


def _get_region_record_from_shapefile(region_shape_file, region):
    for record in region_shape_file.records():
        if region in record:
            return record
    LOG.error("region: %s not found in shape file", region)
    return None


def _get_resolution_m(cube):
    resolution = cube.attributes["resolution"]
    return int(resolution.split("km")[0]) * 1000


def _write_polygon(shape_writer, x_coord, y_coord, half_grid_size):
    # Given the central x, y, and half_grid_size construct a polygon
    polygon = [
        [x_coord - half_grid_size, y_coord - half_grid_size],
        [x_coord - half_grid_size, y_coord + half_grid_size],
        [x_coord + half_grid_size, y_coord + half_grid_size],
        [x_coord + half_grid_size, y_coord - half_grid_size],
        [x_coord - half_grid_size, y_coord - half_grid_size],
    ]
    shape_writer.poly([polygon])


def _write_bbox_record(shape_writer, x_coord, y_coord, area, var_label, value):
    shape_writer.record(
        centroid_x=x_coord,
        centroid_y=y_coord,
        area=area,
        var_name=var_label,
        var_value=value,
    )


def _write_region_record(
    shape_writer, region_geometry, region_record, var_label, value
):
    shape_writer.shape(region_geometry)
    shape_writer.record(
        ET_ID=region_record[ET_ID],
        Region=region_record[REGION],
        area=region_record[AREA],
        centroid_x=region_record[CENTROID_X],
        centroid_y=region_record[CENTROID_Y],
        var_name=var_label,
        var_value=value,
    )


def _write_bbox_field_desc(shape_writer):
    # define the shapefile fields
    shape_writer.field(CENTROID_X, "N", 9)
    shape_writer.field(CENTROID_Y, "N", 9)
    shape_writer.field(AREA, "N", 9)
    shape_writer.field(VAR_NAME, "C", 100)
    shape_writer.field(VAR_VALUE, "N", decimal=7)


def _write_region_field_desc(shape_writer):
    # define the shapefile fields
    shape_writer.field(ET_ID, "N", 8)
    shape_writer.field(REGION, "C", 50)
    shape_writer.field(CENTROID_X, "N", 9)
    shape_writer.field(CENTROID_Y, "N", 9)
    shape_writer.field(AREA, "N", 9)
    shape_writer.field(VAR_NAME, "C", 100)
    shape_writer.field(VAR_VALUE, "N", decimal=7)


def _write_land_prj_file(cube, prj_file):
    """
    Write the projection file for land data.

    Where possible data will be used from the cube.

    @param prj_file (str): the full path to the projection file

    """
    try:
        longitude_of_prime_meridian = (
            cube.coord_system().ellipsoid.longitude_of_prime_meridian
        )
        semi_major_axis = cube.coord_system().ellipsoid.semi_major_axis
        false_easting = cube.coord_system().false_easting
        false_northing = cube.coord_system().false_northing
        grid_mapping_name = cube.coord_system().grid_mapping_name
        latitude_of_projection_origin = (
            cube.coord_system().latitude_of_projection_origin
        )
        longitude_of_central_meridian = (
            cube.coord_system().longitude_of_central_meridian
        )
        scale_factor_at_central_meridian = (
            cube.coord_system().scale_factor_at_central_meridian
        )

    except (AttributeError, CoordinateNotFoundError):
        longitude_of_prime_meridian = "0.0"
        semi_major_axis = "6377563.396"
        false_easting = "400000.0"
        false_northing = "-100000.0"
        grid_mapping_name = "Transverse_Mercator"
        latitude_of_projection_origin = "49.0"
        longitude_of_central_meridian = "-2.0"
        scale_factor_at_central_meridian = "0.9996012717"

    prj = (
        'PROJCS["British_National_Grid",'
        'GEOGCS["GCS_OSGB_1936",'
        'DATUM["D_OSGB_1936",'
        f'SPHEROID["Airy_1830",{semi_major_axis},299.3249646]],'
        f'PRIMEM["Greenwich",{longitude_of_prime_meridian}],'
        'UNIT["Degree",0.0174532925199433]],'
        f'PROJECTION["{grid_mapping_name}"],'
        f'PARAMETER["False_Easting",{false_easting}],'
        f'PARAMETER["False_Northing",{false_northing}],'
        f'PARAMETER["Central_Meridian",{longitude_of_central_meridian}],'
        f'PARAMETER["Scale_Factor",{scale_factor_at_central_meridian}],'
        f'PARAMETER["Latitude_Of_Origin",{latitude_of_projection_origin}],'
        'UNIT["Meter",1.0]]'
    )

    with open(prj_file, "w") as output_data_file:
        output_data_file.write(prj)


def _write_marine_prj_file(prj_file):
    """
    Write the projection file for land data.

    @param prj_file (str): the full path to the projection file

    """
    prj = (
        'GEOGCS["GCS_WGS_1984",'
        'DATUM["WGS_1984",'
        'SPHEROID["WGS_84",6378137.0,298.257223563]],'
        'PRIMEM["Greenwich",0.0],'
        'UNIT["Degree",0.0174532925199433]]'
    )

    with open(prj_file, "w") as output_data_file:
        output_data_file.write(prj)
