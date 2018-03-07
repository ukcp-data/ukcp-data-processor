import logging
import os

import iris
from ukcp_dp.constants import DataFormat
from ukcp_dp.file_writers._write_csv import write_csv_file
from time import gmtime, strftime


log = logging.getLogger(__name__)


def write_file(cube_list, overlay_cube, title, output_data_file_path,
               data_format, input_data, plot_type, vocab):
    log.debug(cube_list)

    if data_format == DataFormat.CSV:
        return write_csv_file(
            cube_list, overlay_cube, title, output_data_file_path, input_data,
            plot_type, vocab)

    elif data_format == DataFormat.NET_CDF:
        return _write_netcdf_file(cube_list, output_data_file_path, plot_type)

    log.debug('Finished writing file(s)')


def _write_netcdf_file(cube_list, output_data_file_path, plot_type):
    # output the data as netCDF
    log.info('Writing data to CF-netCDF file')
    file_name = _get_full_file_name(output_data_file_path, plot_type)
    iris.save(cube_list, file_name)
    return [file_name]


def _get_full_file_name(output_data_file_path, plot_type):
    timestamp = strftime("%Y-%m-%dT%H-%M-%S", gmtime())
    plot_type_string = ''
    if plot_type is not None:
        plot_type_string = '{}_'.format(plot_type.lower())
    file_name = '{plot_type}{timestamp}.nc'.format(
        plot_type=plot_type_string, timestamp=timestamp)
    return os.path.join(output_data_file_path, file_name)
