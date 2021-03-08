import logging
import os
from time import gmtime, strftime

import shapefile


log = logging.getLogger(__name__)


class BaseShpWriter(object):
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
        log.info("write_shp, %s", plot_type)
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
        if file_name_suffix is None:
            file_name_suffix = ""
        try:
            plot_type = self.plot_type.lower()
        except AttributeError:
            plot_type = "subset"
        file_name = "{plot_type}_{timestamp}{suffix}".format(
            plot_type=plot_type, timestamp=self.timestamp, suffix=file_name_suffix
        )
        return os.path.join(self.output_data_file_path, file_name)

    def _get_resolution_m(self, cube):
        resolution = cube.attributes["resolution"]
        return int(resolution.split("km")[0]) * 1000

    def _write_prj_file(self, output_data_file_path):
        prj = (
            'PROJCS["British_National_Grid",GEOGCS["GCS_OSGB_1936",'
            'DATUM["D_OSGB_1936",'
            'SPHEROID["Airy_1830",6377563.396,299.3249646]],'
            'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],'
            'PROJECTION["Transverse_Mercator"],'
            'PARAMETER["False_Easting",400000.0],'
            'PARAMETER["False_Northing",-100000.0],'
            'PARAMETER["Central_Meridian",-2.0],'
            'PARAMETER["Scale_Factor",0.9996012717],'
            'PARAMETER["Latitude_Of_Origin",49.0],'
            'UNIT["Meter",1.0]]'
        )
        with open(output_data_file_path, "w") as output_data_file:
            output_data_file.write(prj)
