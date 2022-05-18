"""
This module provides the method get_file_lists.

"""
import logging
import os

from ukcp_dp.constants import (
    DATA_DIR,
    COLLECTION_RCM_CORDEX,
    COLLECTION_CPM,
    COLLECTION_DERIVED,
    COLLECTION_GCM,
    COLLECTION_RCM,
    InputType,
    AreaType,
)
from ukcp_dp.vocab_manager._vocab import get_ensemble_member_set


LOG = logging.getLogger(__name__)


# month and day
START_MONTH_DAY = "1201"
END_MONTH_DAY = "1130"

MONTH_NUMBERS = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

VERSION = "latest"

RIVER = "river"
REGION = "region"


def get_cm_file_list(input_data, baseline):
    """
    Get a list of files based on the data provided in the input data.

    @param input_data (InputData): an InputData object
    @param baseline (str): the baseline, may be None

    @return a dict where
        key: (str) variable name
        value: list of lists where:
            each list is a list of files per scenario, per variable, including
            their full paths
    """
    variables = input_data.get_value(InputType.VARIABLE)

    spatial_representation = _get_cm_spatial_representation(input_data)

    file_lists_per_variable = {}

    for variable in variables:
        # generate a list of files for each variable
        # we need to use the variable root and calculate the anomaly later
        variable_prefix = variable.split("Anom")[0]

        file_list_per_scenario = []
        for scenario in input_data.get_value(InputType.SCENARIO):
            # generate a list of files for each scenario

            ensemble_file_list = []
            for ensemble in input_data.get_value(InputType.ENSEMBLE):
                file_path = _get_cm_file_path(
                    input_data,
                    spatial_representation,
                    variable_prefix,
                    scenario,
                    ensemble,
                    baseline,
                )

                if input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) in [
                    "1hr",
                    "3hr",
                ]:
                    # we need lots of files
                    for year in range(
                        input_data.get_value(InputType.YEAR_MINIMUM) - 1,
                        input_data.get_value(InputType.YEAR_MAXIMUM),
                    ):
                        for month in range(0, 12):
                            if (
                                year == input_data.get_value(InputType.YEAR_MINIMUM) - 1
                                and month < 11
                            ):
                                continue
                            if (
                                year == input_data.get_value(InputType.YEAR_MAXIMUM) - 1
                                and month > 10
                            ):
                                continue
                            date_range = "{year}{month}01-{year}{month_end}30".format(
                                year=year,
                                month=MONTH_NUMBERS[month],
                                month_end=MONTH_NUMBERS[month],
                            )
                            file_name = _get_cm_file_name(
                                input_data,
                                spatial_representation,
                                variable_prefix,
                                scenario,
                                ensemble,
                                baseline,
                                date_range,
                            )
                            ensemble_file_list.append(
                                os.path.join(file_path, file_name)
                            )
                else:
                    file_name = _get_cm_file_name(
                        input_data,
                        spatial_representation,
                        variable_prefix,
                        scenario,
                        ensemble,
                        baseline,
                    )
                    ensemble_file_list.append(os.path.join(file_path, file_name))

            file_list_per_scenario.append(ensemble_file_list)

        file_lists_per_variable[variable] = file_list_per_scenario

    return file_lists_per_variable


def _get_cm_spatial_representation(input_data):
    spatial_representation = input_data.get_value(InputType.SPATIAL_REPRESENTATION)

    if spatial_representation == AreaType.RIVER_BASIN:
        spatial_representation = RIVER
    elif spatial_representation == AreaType.ADMIN_REGION:
        spatial_representation = REGION
    return spatial_representation


def _get_cm_file_path(
    input_data, spatial_representation, variable, scenario, ensemble, baseline
):
    if baseline is None and input_data.get_value(InputType.TIME_SLICE_TYPE) is None:
        temporal_average_type = input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE)

    elif (
        baseline == "b8100" or input_data.get_value(InputType.TIME_SLICE_TYPE) == "20y"
    ):
        temporal_average_type = "{}-20y".format(
            input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE)
        )

    elif (
        baseline == "b6190"
        or baseline == "b8110"
        or input_data.get_value(InputType.TIME_SLICE_TYPE) == "30y"
    ):
        temporal_average_type = "{}-30y".format(
            input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE)
        )

    else:
        temporal_average_type = input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE)

    collection = _get_collection(input_data, ensemble)

    if baseline is not None and scenario in ["gwl2", "gwl4"]:
        # we need to use the GCM RCP8.5 baseline for GWL2 and GWL4
        collection = COLLECTION_GCM
        scenario = "rcp85"

    file_path = os.path.join(
        DATA_DIR,
        collection,
        "uk",
        spatial_representation,
        scenario,
        ensemble,
        variable,
        temporal_average_type,
        VERSION,
    )

    return file_path


def _get_cm_file_name(
    input_data,
    spatial_representation,
    variable,
    scenario,
    ensemble,
    baseline,
    year=None,
):
    if baseline is None:
        if (
            input_data.get_value(InputType.TIME_SLICE_TYPE) is None
            or input_data.get_value(InputType.TIME_SLICE_TYPE) == "1y"
        ) and input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) not in [
            "1hr",
            "3hr",
        ]:
            # there will only be one file
            return "*"

        if input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) in ["1hr", "3hr"]:
            temporal_average_type = input_data.get_value(
                InputType.TEMPORAL_AVERAGE_TYPE
            )
        else:
            temporal_average_type = "{}-{}".format(
                input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE),
                input_data.get_value(InputType.TIME_SLICE_TYPE),
            )

        if input_data.get_value(InputType.COLLECTION) in [
            COLLECTION_GCM,
            COLLECTION_DERIVED,
        ]:
            date_range = "200912-209911"
        elif input_data.get_value(InputType.COLLECTION) == COLLECTION_CPM:
            if input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) in ["1hr", "3hr"]:
                date_range = "{}".format(year)
            elif input_data.get_value(InputType.YEAR_MINIMUM) == 1981:
                date_range = "198012-200011"
            elif input_data.get_value(InputType.YEAR_MINIMUM) == 2021:
                date_range = "202012-204011"
            elif input_data.get_value(InputType.YEAR_MINIMUM) == 2061:
                date_range = "206012-208011"
        else:
            date_range = "200912-207911"

    elif baseline == "b8100":
        temporal_average_type = "{}-20y".format(
            input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE)
        )
        date_range = "198012-200011"

    elif baseline == "b6190":
        temporal_average_type = "{}-30y".format(
            input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE)
        )
        date_range = "196012-199011"

    elif baseline == "b8110":
        temporal_average_type = "{}-30y".format(
            input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE)
        )
        date_range = "198012-201011"

    collection = _get_collection(input_data, ensemble)

    if baseline is not None and scenario in ["gwl2", "gwl4"]:
        # we need to use the GCM RCP8.5 baseline for GWL2 and GWL4
        collection = COLLECTION_GCM
        scenario = "rcp85"

    file_name = (
        "{variable}_{scenario}_{collection}_uk_"
        "{spatial_representation}_{ensemble}_"
        "{temporal_average_type}_{date}.nc".format(
            variable=variable,
            scenario=scenario,
            collection=collection,
            spatial_representation=spatial_representation,
            ensemble=ensemble,
            temporal_average_type=temporal_average_type,
            date=date_range,
        )
    )

    return file_name


def _get_collection(input_data, ensemble):
    collection = input_data.get_value(InputType.COLLECTION)
    if collection == COLLECTION_RCM and ensemble in get_ensemble_member_set(
        COLLECTION_RCM_CORDEX
    ):
        collection = COLLECTION_RCM_CORDEX

    return collection
