"""
This module is the entry point for writing shapefiles.

"""
import logging

from ukcp_dp.constants import PlotType
from ukcp_dp.exception import UKCPDPInvalidParameterException
from ukcp_dp.file_writers._write_shp_postage_stamp_map import PostageStampMapShpWriter
from ukcp_dp.file_writers._write_shp_single_map import SingleMapShpWriter
from ukcp_dp.file_writers._write_shp_three_map import ThreeMapShpWriter


log = logging.getLogger(__name__)


def write_shp_file(cube_list, output_data_file_path, input_data, plot_type):
    """
    Output the data as a shapefile.
    This method will decide on a shapefile writer to use dependent on the value
    given for plot type.
    @param cube_list (iris cube list): a list of cubes containing the
        selected data, one cube per scenario, per variable
    @param output_data_file_path (str): the full path to the file
    @param input_data (InputData): an object containing user defined values
    @param plot_type (PlotType): the type of the plot

    @return a list of file paths/names

    """
    log.info("Writing data to shapefile file")

    if plot_type is not None:

        if plot_type == PlotType.THREE_MAPS:
            shp_writer = ThreeMapShpWriter()

        elif plot_type == PlotType.SINGLE_MAP:
            shp_writer = SingleMapShpWriter()

        elif plot_type == PlotType.POSTAGE_STAMP_MAPS:
            shp_writer = PostageStampMapShpWriter()

        else:
            raise UKCPDPInvalidParameterException()

    else:
        raise UKCPDPInvalidParameterException()

    return shp_writer.write_shp(input_data, cube_list, output_data_file_path, plot_type)
