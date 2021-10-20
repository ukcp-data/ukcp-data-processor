"""
This module is the entry point for writing CSV files.

"""
import logging

from ukcp_dp.constants import InputType, PlotType, COLLECTION_MARINE
from ukcp_dp.file_writers._write_csv_cdf import CdfCsvWriter
from ukcp_dp.file_writers._write_csv_jp import JpCsvWriter
from ukcp_dp.file_writers._write_csv_pdf import PdfCsvWriter
from ukcp_dp.file_writers._write_csv_plume import PlumeCsvWriter
from ukcp_dp.file_writers._write_csv_postage_stamp_map import PostageStampMapCsvWriter
from ukcp_dp.file_writers._write_csv_sample import SampleCsvWriter
from ukcp_dp.file_writers._write_csv_single_map import SingleMapCsvWriter
from ukcp_dp.file_writers._write_csv_subset import SubsetCsvWriter
from ukcp_dp.file_writers._write_csv_three_map import ThreeMapCsvWriter


LOG = logging.getLogger(__name__)


def write_csv_file(
    cube_list,
    overlay_cube,
    output_data_file_path,
    input_data,
    plot_type,
    process_version,
    vocab,
):
    """
    Output the data as csv.

    This method will decide on a CSV writer to use dependent on the value given
    for plot type.
    """
    LOG.info("Writing data to csv file")

    if plot_type is not None:

        if plot_type == PlotType.CDF_PLOT:
            csv_writer = CdfCsvWriter()

        elif plot_type == PlotType.PDF_PLOT:
            csv_writer = PdfCsvWriter()

        elif plot_type == PlotType.PLUME_PLOT:
            csv_writer = PlumeCsvWriter()

        elif plot_type == PlotType.JP_PLOT:
            csv_writer = JpCsvWriter()

        elif plot_type == PlotType.SINGLE_MAP:
            csv_writer = SingleMapCsvWriter()

        elif plot_type == PlotType.THREE_MAPS:
            csv_writer = ThreeMapCsvWriter()

        elif plot_type == PlotType.POSTAGE_STAMP_MAPS:
            csv_writer = PostageStampMapCsvWriter()

    # it is not a plot therefore it is a sample or subset

    elif input_data.get_value(InputType.SAMPLING_METHOD) is not None:
        # a bit of a fudge, need to rename plot_type
        plot_type = "sampling_{}".format(
            input_data.get_value(InputType.SAMPLING_METHOD).lower()
        )
        csv_writer = SampleCsvWriter()

    # it is a subset

    elif input_data.get_value(InputType.COLLECTION) == COLLECTION_MARINE:
        # this is a marine sebset, we can use the Plume plot code to write the
        # data
        csv_writer = PlumeCsvWriter()

    else:
        csv_writer = SubsetCsvWriter()

    return csv_writer.write_csv(
        input_data,
        cube_list,
        output_data_file_path,
        vocab,
        plot_type,
        process_version,
        overlay_cube,
    )
