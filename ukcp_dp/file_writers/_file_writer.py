import iris
import os


def write_file(cubes, title, output_data_file_path):
    _, file_extension = os.path.splitext(output_data_file_path)

    if file_extension == '.csv':
        _write_csv_file(cubes[0], title, output_data_file_path)

    elif file_extension == '.nc':
        _write_netcdf_file(cubes[0], output_data_file_path)

    else:
        raise Exception('Unknown file extension, {}, must be one of "csv" '
                        'or "nc'.format(file_extension))


def _write_csv_file(cube, title, output_data_file_path):

    dim_coords = []
    for dm in cube.dim_coords:
        dim_coords.append(dm.var_name)

    # an array for containing one line of data
    line_out = [0] * len(dim_coords)

    with open(output_data_file_path, 'w') as output_data_file:
        # write the title
        output_data_file.write(title.replace('\n', ' '))
        output_data_file.write('\n')

        # write the header
        output_data_file.write(','.join(dim_coords))
        output_data_file.write(',')
        output_data_file.write(cube.var_name)
        output_data_file.write('\n')

        for _slice in cube.slices_over(dim_coords[0]):
            line_out[0] = str(_slice.coord(dim_coords[0]).points[0])
            _write_dim_csv(
                _slice, dim_coords[1:], line_out, 1, output_data_file)
            output_data_file.write('\n')
    return


def _write_dim_csv(cube, dim_coords, line_out, index, output_data_file):
    for _slice in cube.slices_over(dim_coords[0]):
        line_out[index] = str(_slice.coord(dim_coords[0]).points[0])
        if len(dim_coords) > 1:
            new_index = index + 1
            _write_dim_csv(
                _slice, dim_coords[1:], line_out, new_index, output_data_file)
        else:
            # write data
            output_data_file.write(','.join(line_out))
            output_data_file.write('\n')


def _write_netcdf_file(cube, output_data_file_path):
    iris.save(cube, output_data_file_path)
    return
