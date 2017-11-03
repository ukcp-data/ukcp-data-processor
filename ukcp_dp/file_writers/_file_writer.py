import iris
import os


def write_file(cube, title, output_data_file_path):
    _, file_extension = os.path.splitext(output_data_file_path)

    if file_extension == '.csv':
        _write_csv_file(cube, title, output_data_file_path)

    elif file_extension == '.nc':
        _write_netcdf_file(cube, output_data_file_path)

    else:
        raise Exception('Unknown file extension, {}, must be one of "csv" '
                        'or "nc'.format(file_extension))


def _write_csv_file(cube, title, output_data_file_path):

#     dim_1_name = (cube.coords(dim_coords=True)[0].name())
#     dim_1_points = cube.coord(dim_1_name).points
    dim_1_points = cube.coord('time').points

    with open(output_data_file_path, 'w') as f:
        f.write(title.replace('\n', ' '))
        f.write('\n')

        for dim_1_point in dim_1_points:
            # TODO make 'time' dynamic
            dim_1_cube = cube.extract(iris.Constraint(time=dim_1_point))
            f.write(str(dim_1_point))

            for dim in dim_1_cube.coords(dim_coords=True):

                for dim_2_point in dim_1_cube.coord(dim.name()).points:
                    # TODO make 'percentile' dynamic
                    cube_1 = dim_1_cube.extract(
                        iris.Constraint(percentile=dim_2_point))
                    f.write(',')
                    f.write(str(cube_1.data))

            f.write('\n')

    return


def _write_netcdf_file(cubes, output_data_file_path):
    iris.save(cubes, output_data_file_path)
    return
