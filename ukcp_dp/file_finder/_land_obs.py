import logging
import os

from ukcp_dp.constants import HADUK_DIR, InputType, AreaType


LOG = logging.getLogger(__name__)

RIVER = "river"
REGION = "region"

VERSION = "latest"


def get_obs_file_list(input_data):
    LOG.info("get_obs_file_list")

    variables = input_data.get_value(InputType.VARIABLE)

    spatial_representation = _get_spatial_representation(input_data)

    file_lists_per_variable = {}

    for variable in variables:
        # generate a list of files for each variable

        # keeping for the time being to stay inline with the RCM
        file_list_per_scenario = []

        # keeping for the time being to stay inline with the RCM
        ensemble_file_list = []
        file_path = _get_file_path(input_data, spatial_representation, variable)

        if input_data.get_value(InputType.TIME_SLICE_TYPE) is None:

            # we need lots of files
            for year in range(
                input_data.get_value(InputType.YEAR_MINIMUM) - 1,
                input_data.get_value(InputType.YEAR_MAXIMUM),
            ):
                date_range = f"{year}01-{year}12"
                file_name = _get_file_name(
                    input_data, spatial_representation, variable, date_range
                )
                ensemble_file_list.append(os.path.join(file_path, file_name))
        else:
            date_ranges = _get_date_ranges(input_data)
            for date_range in date_ranges:
                file_name = _get_file_name(
                    input_data, spatial_representation, variable, date_range
                )
                ensemble_file_list.append(os.path.join(file_path, file_name))

        file_list_per_scenario.append(ensemble_file_list)

        file_lists_per_variable[variable] = file_list_per_scenario

    return file_lists_per_variable


def _get_spatial_representation(input_data):
    spatial_representation = input_data.get_value(InputType.SPATIAL_REPRESENTATION)

    if spatial_representation == AreaType.RIVER_BASIN:
        spatial_representation = RIVER
    elif spatial_representation == AreaType.ADMIN_REGION:
        spatial_representation = REGION
    return spatial_representation


def _get_file_path(input_data, spatial_representation, variable):
    temporal_average_type = _temporal_average_type(input_data)

    file_path = os.path.join(
        HADUK_DIR, spatial_representation, variable, temporal_average_type, VERSION
    )

    return file_path


def _get_file_name(input_data, spatial_representation, variable, date_range):
    temporal_average_type = _temporal_average_type(input_data)
    file_name = (
        f"{variable}_hadukgrid_uk_{spatial_representation}_"
        f"{temporal_average_type}_{date_range}.nc"
    )
    return file_name


def _temporal_average_type(input_data):
    LOG.debug("_temporal_average_type")
    LOG.debug(input_data.get_value(InputType.TIME_SLICE_TYPE))
    LOG.debug(input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE))
    if input_data.get_value(InputType.TIME_SLICE_TYPE) is None:
        temporal_average_type = input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE)

    else:
        temporal_average_type = (
            f"{input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE)}-"
            f"{input_data.get_value(InputType.TIME_SLICE_TYPE)}"
        )

    return temporal_average_type


def _get_date_ranges(input_data):
    if input_data.get_value(InputType.TIME_SLICE_TYPE) == "20y":
        return ["198101-200012"]

    if input_data.get_value(InputType.TIME_SLICE_TYPE) == "30y":
        return ["196101-199012", "198101-201012"]
