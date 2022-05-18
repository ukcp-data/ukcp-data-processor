"""
This module provides the method get_file_lists.

"""
import logging
import os

from ukcp_dp.constants import (
    DATA_DIR,
    COLLECTION_PROB,
    COLLECTION_PROB_MIN_YEAR,
    COLLECTION_MARINE,
    InputType,
    OTHER_MAX_YEAR,
    AreaType,
    TemporalAverageType,
)


LOG = logging.getLogger(__name__)


# month and day
START_MONTH_DAY = "1201"
END_MONTH_DAY = "1130"

MONTH_NUMBERS = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

VERSION = "latest"

RIVER = "river"
REGION = "region"


def get_prob_file_list(input_data):
    """
    Get a list of files based on the data provided in the input data. As this
    may be the file list for the overlay, some fields are not from the user
    input.

    @param input_data (InputData): an InputData object

    @return a dict where
        key: (str) variable name
        value: list of lists where:
            each list is a list of files per scenario, per variable, including
            their full paths
    """
    variables = input_data.get_value(InputType.VARIABLE)

    spatial_representation = _get_prob_spatial_representation(input_data)

    file_lists_per_variable = {}

    # if this is a selection for on overlay then the dates will not have been
    # validated against this dataset. Check the dates and adjust the minimum if
    # needed
    year_maximum = input_data.get_value(InputType.YEAR_MAXIMUM)
    year_minimum = input_data.get_value(InputType.YEAR_MINIMUM)
    if year_maximum < COLLECTION_PROB_MIN_YEAR:
        return {}

    if year_minimum < COLLECTION_PROB_MIN_YEAR:
        year_minimum = COLLECTION_PROB_MIN_YEAR

    # December's data is included with the next year so if a single year has
    # been selected
    if year_minimum == year_maximum:
        year_maximum = year_maximum + 1

    for variable in variables:
        # generate a list of files for each variable
        # NB the marine data are all annual

        file_list_per_scenario = []
        for scenario in input_data.get_value(InputType.SCENARIO):
            file_list_per_scenario.extend(
                _get_file_list_per_scenario(
                    input_data,
                    scenario,
                    spatial_representation,
                    variable,
                    year_minimum,
                    year_maximum,
                )
            )

        file_lists_per_variable[variable] = file_list_per_scenario

    return file_lists_per_variable


def _get_file_list_per_scenario(
    input_data, scenario, spatial_representation, variable, year_minimum, year_maximum
):
    # generate a list of files for each scenario
    file_list_per_data_type = []
    for data_type in input_data.get_value(InputType.DATA_TYPE):
        file_path = _get_prob_file_path(
            data_type, input_data, scenario, spatial_representation, variable
        )

        if (
            input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE)
            == TemporalAverageType.ANNUAL
            or spatial_representation != "25km"
            or (input_data.get_value(InputType.COLLECTION) == COLLECTION_MARINE)
        ):
            # current thinking is that there will only be one file
            file_name = "*"
            file_list_per_data_type.append([os.path.join(file_path, file_name)])

        elif input_data.get_value(InputType.TIME_SLICE_TYPE) == "1y":
            scenario_file_list = []

            for year in range(year_minimum, (year_maximum + 1)):
                # We cannot check for COLLECTION_PROB as this may be an
                # overlay
                if (
                    input_data.get_value(InputType.COLLECTION) != COLLECTION_MARINE
                    and year == OTHER_MAX_YEAR
                ):
                    # there is not data for December of the last year
                    continue
                file_name = _get_prob_file_name_for_year(
                    data_type,
                    input_data,
                    scenario,
                    spatial_representation,
                    variable,
                    year,
                )
                scenario_file_list.append(os.path.join(file_path, file_name))

            file_list_per_data_type.append(scenario_file_list)

        else:
            # InputType.TIME_SLICE_TYPE) == '20y' or '30y'
            file_name = _get_prob_file_name_for_slice(
                data_type, input_data, scenario, spatial_representation, variable
            )
            file_list_per_data_type.append([os.path.join(file_path, file_name)])

    return file_list_per_data_type


def _get_prob_spatial_representation(input_data):
    spatial_representation = input_data.get_value(InputType.SPATIAL_REPRESENTATION)

    if spatial_representation == AreaType.RIVER_BASIN:
        spatial_representation = RIVER
    elif spatial_representation == AreaType.ADMIN_REGION:
        spatial_representation = REGION
    elif spatial_representation == AreaType.COUNTRY:
        pass
    else:
        # we cannot rely on the input value as this file list may be for the
        # overlay
        spatial_representation = "25km"

    return spatial_representation


def _get_prob_file_path(
    data_type, input_data, scenario, spatial_representation, variable
):

    if input_data.get_value(InputType.COLLECTION) == COLLECTION_MARINE:

        file_path = os.path.join(
            DATA_DIR,
            COLLECTION_MARINE,
            input_data.get_value(InputType.METHOD),
            scenario,
            variable,
            VERSION,
        )
    else:

        file_path = os.path.join(
            DATA_DIR,
            COLLECTION_PROB,
            "uk",
            spatial_representation,
            scenario,
            data_type,
            input_data.get_value(InputType.BASELINE),
            input_data.get_value(InputType.TIME_SLICE_TYPE),
            variable,
            input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE),
            VERSION,
        )

    return file_path


def _get_prob_file_name_for_year(
    data_type, input_data, scenario, spatial_representation, variable, year
):

    # input_data.get_value(InputType.TIME_SLICE_TYPE) == '1y':
    # the year starts in December, so subtract 1 from the year
    start_date = "{year}{mon_day}".format(year=year - 1, mon_day=START_MONTH_DAY)
    end_date = "{year}{mon_day}".format(year=year, mon_day=END_MONTH_DAY)

    return _get_prob_file_name(
        data_type,
        input_data,
        scenario,
        spatial_representation,
        variable,
        start_date,
        end_date,
    )


def _get_prob_file_name_for_slice(
    data_type, input_data, scenario, spatial_representation, variable
):
    # input_data.get_value(InputType.TIME_SLICE_TYPE) == 20y or 30y
    start_date = "20091201"
    end_date = "20991130"

    return _get_prob_file_name(
        data_type,
        input_data,
        scenario,
        spatial_representation,
        variable,
        start_date,
        end_date,
    )


def _get_prob_file_name(
    data_type,
    input_data,
    scenario,
    spatial_representation,
    variable,
    start_date,
    end_date,
):

    return_period = input_data.get_value(InputType.RETURN_PERIOD)

    if return_period is None:
        file_name = (
            "{variable}_{scenario}_{collection}_uk_"
            "{spatial_representation}_{data_type}_{baseline}_"
            "{time_slice_type}_{temporal_type}_{start_data}-"
            "{end_date}.nc".format(
                variable=variable,
                scenario=scenario,
                collection=COLLECTION_PROB,
                spatial_representation=spatial_representation,
                data_type=data_type,
                baseline=input_data.get_value(InputType.BASELINE),
                time_slice_type=input_data.get_value(InputType.TIME_SLICE_TYPE),
                temporal_type=input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE),
                start_data=start_date,
                end_date=end_date,
            )
        )

    else:
        file_name = (
            "{variable}_{return_period}_{scenario}_{collection}_uk_"
            "{spatial_representation}_{data_type}_{baseline}_"
            "{time_slice_type}_{temporal_type}_{start_data}-"
            "{end_date}.nc".format(
                variable=variable,
                return_period=return_period,
                scenario=scenario,
                collection=COLLECTION_PROB,
                spatial_representation=spatial_representation,
                data_type=data_type,
                baseline=input_data.get_value(InputType.BASELINE),
                time_slice_type=input_data.get_value(InputType.TIME_SLICE_TYPE),
                temporal_type=input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE),
                start_data=start_date,
                end_date=end_date,
            )
        )

    return file_name
