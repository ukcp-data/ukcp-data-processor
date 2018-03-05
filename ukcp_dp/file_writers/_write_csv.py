import logging

from ukcp_dp.constants import PlotType
from ukcp_dp.file_writers._write_csv_cdf import CdfCsvWriter
from ukcp_dp.file_writers._write_csv_default import write_csv as \
    write_default_csv
from ukcp_dp.file_writers._write_csv_jp import JpCsvWriter
from ukcp_dp.file_writers._write_csv_plume import PlumeCsvWriter
from ukcp_dp.file_writers._write_csv_three_map import ThreeMapCsvWriter


log = logging.getLogger(__name__)


def write_csv_file(cube_list, overlay_cube, title, output_data_file_path,
                   input_data, plot_type, vocab):
    """
    Output the data as csv.

    This method will decide on a CSV writer to use dependent on the value given
    for plot type.
    """
    log.info('Writing data to csv file')

    if plot_type is None:
        write_default_csv(cube_list, title, output_data_file_path)

    elif plot_type == PlotType.CDF_PLOT:
        csv_writer = CdfCsvWriter()

    elif plot_type == PlotType.PLUME_PLOT:
        csv_writer = PlumeCsvWriter()

    elif plot_type == PlotType.JP_PLOT:
        csv_writer = JpCsvWriter()

    elif plot_type == PlotType.THREE_MAPS:
        csv_writer = ThreeMapCsvWriter()

    else:
        write_default_csv(cube_list, title, output_data_file_path)
        return

    return csv_writer.write_csv(input_data, cube_list, output_data_file_path,
                                vocab, plot_type, overlay_cube)
