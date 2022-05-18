"""
This module provides the method get_file_lists.

"""
import logging
import os

from ukcp_dp.constants import (
    DATA_SERVICE_URL,
    COLLECTION_OBS,
    COLLECTION_PROB,
    COLLECTION_CPM,
    COLLECTION_DERIVED,
    COLLECTION_GCM,
    COLLECTION_RCM,
    COLLECTION_RCM_GWL,
    COLLECTION_MARINE,
    InputType,
)

from ._land_cm import get_cm_file_list
from ._land_prob import get_prob_file_list
from ._land_obs import get_obs_file_list


LOG = logging.getLogger(__name__)


# month and day
START_MONTH_DAY = "1201"
END_MONTH_DAY = "1130"

MONTH_NUMBERS = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

VERSION = "latest"

RIVER = "river"
REGION = "region"


def get_file_lists(input_data):
    """
    Get lists of files based on the data provided in the input data.

    @param input_data (InputData): an InputData object

    @return a dict of lists of files, including their full paths
        key - 'main' or 'overlay'
        value - a dict where
            key: (str) variable name
            value: list of lists where:
                each list is a list of files per scenario, per variable,
                including their full paths
    """
    LOG.info("get_file_lists")
    file_list = {}

    # the main file list
    if input_data.get_value(InputType.COLLECTION) in [
        COLLECTION_PROB,
        COLLECTION_MARINE,
    ]:
        file_list["main"] = get_prob_file_list(input_data)

    elif input_data.get_value(InputType.COLLECTION) in [
        COLLECTION_CPM,
        COLLECTION_DERIVED,
        COLLECTION_GCM,
        COLLECTION_RCM,
        COLLECTION_RCM_GWL,
    ]:
        file_list["main"] = get_cm_file_list(input_data, None)

        if input_data.get_value(InputType.BASELINE) is not None:
            file_list["baseline"] = get_cm_file_list(
                input_data, input_data.get_value(InputType.BASELINE)
            )

    elif input_data.get_value(InputType.COLLECTION) == COLLECTION_OBS:
        file_list["main"] = get_obs_file_list(input_data)

    # the file list for an overlay of probability levels
    if (
        input_data.get_value(InputType.OVERLAY_PROBABILITY_LEVELS) is not None
        and input_data.get_value(InputType.OVERLAY_PROBABILITY_LEVELS) is True
    ):
        if input_data.get_value(InputType.COLLECTION) == COLLECTION_PROB:
            file_list_overlay = file_list["main"]
        else:
            file_list_overlay = get_prob_file_list(input_data)

        if len(file_list_overlay) == 1:
            file_list["overlay"] = file_list_overlay
        # else: we do not currently deal with more than one scenario for an
        # overlay
    return file_list


def get_absolute_paths(file_lists):
    """Take an object returned from get_file_lists and returns a flattened list
    of absolute file paths.

    @param file_list (dict): a dictionary returned from a get_file_lists call

    @return a list of absolute file paths
    """
    absolute_paths = []
    for key in file_lists:
        for variable_files in file_lists[key]:
            for file_paths in file_lists[key][variable_files]:
                for file_path in file_paths:
                    absolute_paths.append(_get_absolute_path(file_path))
    absolute_paths.sort()
    return absolute_paths


def _get_absolute_path(file_path):
    real_dir_name = os.path.dirname(os.path.realpath(file_path))
    path = os.path.join(
        os.path.abspath(file_path).replace("latest", os.path.basename(real_dir_name))
    )
    path = DATA_SERVICE_URL + path
    path = path.rstrip("*")
    return path
