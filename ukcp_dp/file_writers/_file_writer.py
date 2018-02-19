import logging
import os

import iris
from ukcp_dp.file_writers._write_csv import write_csv_file


log = logging.getLogger(__name__)


def write_file(cube_list, overlay_cube, title, output_data_file_path,
               input_data, plot_type, vocab):
    log.debug(cube_list)
    _, file_extension = os.path.splitext(output_data_file_path)

    if file_extension == '.csv':
        write_csv_file(cube_list, overlay_cube, title, output_data_file_path,
                       input_data, plot_type, vocab)

    elif file_extension == '.nc':
        _write_netcdf_file(cube_list, output_data_file_path)

    else:
        raise Exception('Unknown file extension, {}, must be one of "csv" '
                        'or "nc'.format(file_extension))

    log.debug('Finished writing file')


def _write_netcdf_file(cube_list, output_data_file_path):
    # output the data as netCDF
    log.info('Writing data to CF-netCDF file')

    iris.save(cube_list, output_data_file_path)
    return
