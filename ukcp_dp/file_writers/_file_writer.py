import iris
import os

import logging
log = logging.getLogger(__name__)


def write_file(cube_list, title, output_data_file_path):
    log.debug(cube_list)
    _, file_extension = os.path.splitext(output_data_file_path)

    if file_extension == '.csv':
        _write_csv_file(cube_list, title, output_data_file_path)

    elif file_extension == '.nc':
        _write_netcdf_file(cube_list, output_data_file_path)

    else:
        raise Exception('Unknown file extension, {}, must be one of "csv" '
                        'or "nc'.format(file_extension))

    log.debug('Finished writing file')


def _write_csv_file(cube_list, title, output_data_file_path):
    # output the data as csv
    log.info('Writing data to csv file')
    with open(output_data_file_path, 'w') as output_data_file:
        for cube in cube_list:
            _write_csv_cube(cube, title, output_data_file)


def _write_csv_cube(cube, title, output_data_file):
    # we need a list of the names of the dimensions
    # use long names were available
    dim_names = []
    for dm in cube.dim_coords:
        if dm.long_name is not None:
            dim_names.append(dm.long_name)
        else:
            dim_names.append(dm.var_name)

    # an array for containing one line of data
    # the '+ 1' is to allow for the variable
    line_out = [0] * (len(dim_names) + 1)

    # write the title
    output_data_file.write(title.encode('utf-8').replace('\n', ' '))
    output_data_file.write('\n')

    # write the header
    output_data_file.write(','.join(dim_names))
    output_data_file.write(',')
    output_data_file.write(cube.long_name)
    output_data_file.write('\n')

    _write_dim_csv(cube, dim_names, line_out, 0, output_data_file)
    return


def _write_dim_csv(cube, dim_names, line_out, index, output_data_file):
    # update the line_out for the current level in the dimensional hierarchy
    # then go down another level or add the data
    for _slice in cube.slices_over(dim_names[0]):
        line_out[index] = _get_value(_slice, dim_names)

        if len(dim_names) > 1:
            # descend to the next dimension
            new_index = index + 1
            _write_dim_csv(
                _slice, dim_names[1:], line_out, new_index, output_data_file)
        else:
            # write data
            # we have come all the way down the  dimensional hierarchy so there
            # should only be one data value
            line_out[index + 1] = str(_slice.data)
            output_data_file.write(','.join(line_out))
            output_data_file.write('\n')


def _get_value(_slice, dim_names):
    if dim_names[0] == 'time':
        with iris.FUTURE.context(cell_datetime_objects=True):
            return str(_slice.coord(dim_names[0]).cell(0))
    else:
        return str(_slice.coord(dim_names[0]).points[0])


def _write_netcdf_file(cube_list, output_data_file_path):
    # output the data as netCDF
    log.info('Writing data to CF-netCDF file')

    iris.save(cube_list, output_data_file_path)
    return
