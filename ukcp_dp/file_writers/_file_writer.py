"""
This module provides the public entry point write_file to the file_writes package.

¬"""
import logging
import os
from time import gmtime, strftime

import iris
from iris.exceptions import CoordinateNotFoundError
from ukcp_dp.constants import DataFormat
from ukcp_dp.exception import UKCPDPInvalidParameterException
from ukcp_dp.file_writers._write_csv import write_csv_file
from ukcp_dp.file_writers._write_shp import write_shp_file


LOG = logging.getLogger(__name__)


def write_file(
    cube_list,
    overlay_cube,
    output_data_file_path,
    data_format,
    input_data,
    plot_type,
    process_version,
    vocab,
):
    """
    Write the data to file.

    @param cube_list (iris cube list): a list of cubes containing the
        selected data, one cube per scenario, per variable
    @param overlay_cube (iris cube): a cube containing the data for the overlay
    @param output_data_file_path (str): the full path to the file
    data_format,
    @param input_data (InputData): an object containing user defined values
    @param plot_type (PlotType): the type of the plot
    @param process_version (str): the version of the process generating
            this output
    @param vocab (Vocab): an instance of the ukcp_dp Vocab class

    """
    LOG.debug(cube_list)

    if data_format == DataFormat.CSV:
        return write_csv_file(
            cube_list,
            overlay_cube,
            output_data_file_path,
            input_data,
            plot_type,
            process_version,
            vocab,
        )

    if data_format == DataFormat.NET_CDF:
        return _write_netcdf_file(
            cube_list, overlay_cube, output_data_file_path, plot_type
        )

    if data_format == DataFormat.SHAPEFILE:
        return write_shp_file(cube_list, output_data_file_path, input_data, plot_type)

    raise UKCPDPInvalidParameterException("Invalid data format: {}".format(data_format))


def _write_netcdf_file(cube_list, overlay_cube, output_data_file_path, plot_type):
    # output the data as netCDF
    LOG.info("Writing data to CF-netCDF file")

    iris.config.netcdf.conventions_override = True

    file_name = _get_full_file_name(output_data_file_path, plot_type)
    file_list = []

    for inx, cube in enumerate(cube_list):
        if len(cube_list) == 1:
            cube_file_name = file_name
        else:
            cube_file_name = f"{file_name.split('.nc')[0]}_{inx+1}.nc"

        try:
            iris.save(
                cube,
                cube_file_name,
                netcdf_format="NETCDF4",
                fill_value=1e20,
                local_keys=("plot_label", "label_units", "description", "level"),
            )
            file_list.append(cube_file_name)

        except ValueError:
            # Somehow "month_number" and "year" an "season_year" values can get messed up
            # when calculating the climatology.
            # ValueError: The data type of AuxCoord <AuxCoord: year / (1) [1991]>
            # is not supported by NETCDF4_CLASSIC and its values cannot be safely
            # cast to a supported integer type.
            #
            # Writing with netcdf_format="NETCDF4" above rather than 
            # netcdf_format="NETCDF4_CLASSIC" may have fixed this issue
            #
            for coord in ["month_number", "year", "season_year"]:
                try:
                    cube.remove_coord(coord)
                except CoordinateNotFoundError:
                    pass
            iris.save(
                cube,
                cube_file_name,
                netcdf_format="NETCDF4_CLASSIC",
                fill_value=1e20,
                local_keys=("plot_label", "label_units", "description", "level"),
            )
            file_list.append(cube_file_name)

    if overlay_cube is not None:
        overlay_file_name = f"{file_name.split('.nc')[0]}_overlay.nc"
        iris.save(
            overlay_cube,
            overlay_file_name,
            netcdf_format="NETCDF4_CLASSIC",
            fill_value=1e20,
            local_keys=("plot_label", "label_units", "description", "level"),
        )
        file_list.append(overlay_file_name)

    return file_list


def _get_full_file_name(output_data_file_path, plot_type):
    timestamp = strftime("%Y-%m-%dT%H-%M-%S", gmtime())
    plot_type_string = ""
    if plot_type is not None:
        plot_type_string = "{}_".format(plot_type.lower())
    file_name = "{plot_type}{timestamp}.nc".format(
        plot_type=plot_type_string, timestamp=timestamp
    )
    return os.path.join(output_data_file_path, file_name)
